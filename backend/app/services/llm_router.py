"""
Hybrid LLM Router — Intelligent routing between Ollama (local), Cloud (OpenAI/Gemini),
and Template Fallback. Includes response caching, privacy mode, and quality validation.

Routing Decision Tree:
  Privacy Mode ON → Ollama only → Fallback
  
  Auto Mode:
    Ollama available AND (offline OR simple task) → Ollama → Fallback
    Cloud available AND complex task → Cloud → Ollama → Fallback
    Neither → Fallback

  ollama_only  → Ollama → Fallback
  cloud_only   → Cloud  → Fallback
  fallback_only → Fallback
"""
import httpx
import json
import random
import asyncio
from typing import Optional
from app.core import settings
from app.services.ollama_service import ollama_service
from app.services.cache import response_cache


# ─────────────────────────────────────────────────────────────
# System prompt: forces structured 4-part response format
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI teaching assistant in an adaptive learning platform.

ALWAYS respond in this exact 4-part format:

🧠 **EXPLANATION**
[Clear, engaging explanation with analogy or real example]

❓ **QUICK CHECK**
[One focused question to test understanding]

📊 **YOUR PROGRESS**
[Brief, encouraging feedback on the learner's position in mastering this topic]

⚡ **NEXT STEP**
[Specific, actionable next step]

Be concise, clear, and pedagogically effective. Adapt depth to the learner's level."""


class HybridLLMRouter:
    """
    Single entry point for all LLM calls across the system.
    Agents call router.generate() — they never talk to Ollama or cloud directly.
    """

    def __init__(self):
        self._ollama_healthy: Optional[bool] = None
        self._last_health_check: float = 0.0
        self._health_cache_ttl: float = 30.0  # recheck Ollama every 30s

    # ─────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        context: dict = None,
    ) -> str:
        """
        Main entry point. Routes to the best available LLM, with caching.
        context keys: action, topic, mentor, memory_context, rag_context
        """
        context = context or {}
        action = context.get("action", "EXPLAIN")
        topic = context.get("topic", "")
        sys_prompt = system_prompt or SYSTEM_PROMPT

        # 1. Check cache first
        cache_key_model = f"{settings.LLM_ROUTING_MODE}:{action}"
        cached = response_cache.get(cache_key_model, prompt)
        if cached:
            print(f"[Router] 🎯 Cache HIT for action={action}")
            return cached

        # 2. Route based on mode
        mode = settings.LLM_ROUTING_MODE
        if settings.PRIVACY_MODE:
            mode = "ollama_only"
        
        result = await self._route(prompt, sys_prompt, context, mode, action)

        # 3. Cache successful result
        if result:
            response_cache.set(cache_key_model, prompt, result)

        return result

    async def check_health(self) -> dict:
        """Return current health status of all backends."""
        import time
        ollama_ok = await self._check_ollama_health()
        return {
            "ollama": {
                "available": ollama_ok,
                "url": settings.OLLAMA_URL,
                "model": settings.OLLAMA_MODEL,
            },
            "cloud": {
                "available": settings.cloud_available,
                "provider": settings.LLM_PROVIDER,
                "model": settings.LLM_MODEL,
            },
            "routing_mode": "privacy_mode (ollama_only)" if settings.PRIVACY_MODE else settings.LLM_ROUTING_MODE,
            "cache": response_cache.stats,
            "active_backend": self._determine_active_backend(ollama_ok),
        }

    # ─────────────────────────────────────────────────────────────
    # Routing Logic
    # ─────────────────────────────────────────────────────────────
    async def _route(
        self, prompt: str, sys_prompt: str, context: dict, mode: str, action: str
    ) -> str:
        complexity = ollama_service.estimate_complexity(prompt)
        
        if mode == "ollama_only":
            return await self._try_ollama(prompt, sys_prompt, action) \
                or self._fallback_generate(prompt, context)

        elif mode == "cloud_only":
            return await self._try_cloud(prompt, sys_prompt) \
                or self._fallback_generate(prompt, context)

        elif mode == "fallback_only":
            return self._fallback_generate(prompt, context)

        else:  # auto — intelligent routing
            return await self._auto_route(prompt, sys_prompt, context, action, complexity)

    async def _auto_route(
        self, prompt: str, sys_prompt: str, context: dict, action: str, complexity: str
    ) -> str:
        """
        Auto routing decision:
        - Complex tasks → prefer cloud if available
        - Simple/medium tasks → prefer Ollama (faster, private)
        - Always fall back gracefully
        """
        ollama_ok = await self._check_ollama_health()
        cloud_ok = settings.cloud_available

        # Route complex tasks to cloud when available
        if complexity == "complex" and cloud_ok:
            print(f"[Router] 🌐 Cloud (complex task, action={action})")
            result = await self._try_cloud(prompt, sys_prompt)
            if result:
                return result
            # Cloud failed → try Ollama
            if ollama_ok:
                print(f"[Router] ⬇️  Falling back to Ollama")
                result = await self._try_ollama(prompt, sys_prompt, action)
                if result:
                    return result
        
        # Prefer Ollama for simple/medium tasks (faster, private)
        elif ollama_ok:
            print(f"[Router] 🦙 Ollama (action={action}, complexity={complexity})")
            result = await self._try_ollama(prompt, sys_prompt, action)
            if result:
                return result
            # Ollama failed → try cloud
            if cloud_ok:
                print(f"[Router] ⬆️  Escalating to cloud")
                result = await self._try_cloud(prompt, sys_prompt)
                if result:
                    return result
        
        # Cloud only (no Ollama)
        elif cloud_ok:
            print(f"[Router] 🌐 Cloud-only (Ollama unavailable, action={action})")
            result = await self._try_cloud(prompt, sys_prompt)
            if result:
                return result

        # All live AI backends failed → template fallback
        print(f"[Router] 📋 Template fallback (action={action})")
        return self._fallback_generate(prompt, context)

    # ─────────────────────────────────────────────────────────────
    # Backend Callers
    # ─────────────────────────────────────────────────────────────
    async def _try_ollama(self, prompt: str, sys_prompt: str, action: str) -> Optional[str]:
        """Call Ollama. Returns None on any failure."""
        if not settings.OLLAMA_ENABLED:
            return None
        try:
            model = ollama_service.select_model_for_task(action)
            response = await ollama_service.generate(
                prompt=prompt,
                model=model,
                system_prompt=sys_prompt,
                temperature=0.7,
                max_tokens=1500,
                retries=1,
            )
            return response if response else None
        except Exception as e:
            print(f"[Router] Ollama failed: {e}")
            self._ollama_healthy = False  # invalidate health cache
            return None

    async def _try_cloud(self, prompt: str, sys_prompt: str) -> Optional[str]:
        """Call cloud LLM (OpenAI or Gemini). Returns None on any failure."""
        if not settings.cloud_available:
            return None
        try:
            if settings.LLM_PROVIDER == "gemini":
                return await self._call_gemini(prompt, sys_prompt)
            else:
                return await self._call_openai(prompt, sys_prompt)
        except Exception as e:
            print(f"[Router] Cloud ({settings.LLM_PROVIDER}) failed: {e}")
            return None

    async def _call_openai(self, prompt: str, sys_prompt: str) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                }
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _call_gemini(self, prompt: str, sys_prompt: str) -> str:
        full_prompt = f"{sys_prompt}\n\n{prompt}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/{settings.LLM_MODEL}:generateContent"
                f"?key={settings.LLM_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
                }
            )
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    # ─────────────────────────────────────────────────────────────
    # Health Check (with TTL caching)
    # ─────────────────────────────────────────────────────────────
    async def _check_ollama_health(self) -> bool:
        import time
        if not settings.OLLAMA_ENABLED:
            return False
        now = time.time()
        if self._ollama_healthy is not None and (now - self._last_health_check) < self._health_cache_ttl:
            return self._ollama_healthy
        self._ollama_healthy = await ollama_service.health_check(force=True)
        self._last_health_check = now
        return self._ollama_healthy

    def _determine_active_backend(self, ollama_ok: bool) -> str:
        if settings.PRIVACY_MODE:
            return "ollama (privacy mode)" if ollama_ok else "fallback (privacy mode)"
        mode = settings.LLM_ROUTING_MODE
        if mode == "ollama_only":
            return "ollama" if ollama_ok else "fallback"
        if mode == "cloud_only":
            return "cloud" if settings.cloud_available else "fallback"
        if mode == "fallback_only":
            return "fallback"
        # auto
        if ollama_ok and not settings.cloud_available:
            return "ollama (auto)"
        if settings.cloud_available and not ollama_ok:
            return "cloud (auto)"
        if ollama_ok and settings.cloud_available:
            return "ollama+cloud (auto, hybrid)"
        return "fallback (no AI backends)"

    # ─────────────────────────────────────────────────────────────
    # Template Fallback Engine (zero-dependency)
    # ─────────────────────────────────────────────────────────────
    def _fallback_generate(self, prompt: str, context: dict) -> str:
        action = context.get("action", "EXPLAIN")
        topic = context.get("topic", self._extract_topic(prompt))
        mentor = context.get("mentor", "direct")
        memory_context = context.get("memory_context", "")
        rag_context = context.get("rag_context", "")

        if action == "QUIZ":
            return self._generate_quiz(topic)
        elif action == "RETEACH":
            return self._generate_4part(topic, "reteach", mentor, memory_context, rag_context)
        elif action == "CHALLENGE":
            return self._generate_4part(topic, "challenge", mentor, "", "")
        elif action == "REVISE":
            return self._generate_4part(topic, "revise", mentor, memory_context, "")
        elif action == "MOTIVATE":
            return self._generate_4part(topic, "motivate", mentor, "", "")
        else:
            return self._generate_4part(topic, "explain", mentor, memory_context, rag_context)

    def _extract_topic(self, prompt: str) -> str:
        stop = {"what", "how", "does", "this", "that", "with", "about", "learn", "teach",
                "explain", "want", "need", "help", "please", "could", "would", "should",
                "know", "understand", "tell", "more", "like", "just", "some", "also"}
        words = [w for w in prompt.strip().split() if len(w) > 3 and w.lower() not in stop]
        return " ".join(words[:4]) if words else "this concept"

    def _generate_4part(self, topic: str, mode: str, mentor: str, memory_context: str, rag_context: str) -> str:
        rag_section = f"\n\n{rag_context}" if rag_context else ""
        memory_note = f"\n\n> 💭 *{memory_context}*" if memory_context else ""

        explanations = {
            "explain": f"""Let me break down **{topic}** clearly.

## 🎯 What Is {topic.capitalize()}?

{topic.capitalize()} is a core concept that follows consistent, learnable patterns. Think of it like **building blocks** — each piece has a specific role, and combined correctly, they create something powerful.{rag_section}{memory_note}

## 📝 Core Mechanics

**Step 1 — Understand the Input**: What are you working with?
**Step 2 — Apply the Rules**: What transformation or logic happens?  
**Step 3 — Verify the Output**: Does it match expectations?

## 💡 Key Principles
- **Consistency**: {topic.capitalize()} follows predictable rules
- **Decomposition**: Break complexity into smaller, solvable pieces
- **Practice**: Every expert got here through deliberate repetition""",

            "reteach": f"""Let's approach **{topic}** from a fresh angle. 🔄{memory_note}

Forget everything — at its core, {topic} is about **one key principle**: cause and effect.

**Simple Mental Model:**
```
[Input] → [{topic.capitalize()} Rules] → [Output]
```

Think of it like a **recipe**:
- 🥕 Ingredients = your inputs
- 👨‍🍳 Cooking process = {topic} in action  
- 🍽️ Final dish = your result

The recipe (rules of {topic}) stays consistent — you just follow each step.""",

            "challenge": f"""**Advanced Challenge: {topic.capitalize()}** 🔥

You're thinking like a senior engineer now. Here's a real scenario:

**The Trade-off Problem:**
You must choose between two approaches to implement {topic}:
- **Option A**: Simple implementation, O(n²) complexity, highly readable
- **Option B**: Complex implementation, O(n log n), harder to maintain

For a production system handling **10 million daily requests**, analyze:
1. Which do you choose, and why?
2. What metrics would inform this decision?
3. How does team expertise factor into the choice?

This is how expert decisions are made — not just "what's correct" but "what's *right for this context*".""",

            "revise": f"""**Spaced Repetition Review: {topic.capitalize()}** 📝{memory_note}

Active recall time. Cover your notes and answer from memory:

**Key Points to Reconstruct:**
✅ What is the core definition of {topic}?
✅ What problem does {topic} solve?
✅ What are 2 common pitfalls to avoid?
✅ Give one real-world example of {topic} in use

**Memory Anchors:**
🔑 The "why" matters more than the "how"
🔑 Connect {topic} to something you already know
🔑 The best test: can you teach it to someone else?""",

            "motivate": random.choice([
                f"""You're learning **{topic}**, and that already puts you ahead. 🌟

**The science of learning your brain right now:**
- Confusion = neural rewiring happening ✅
- Mistakes = the exact data your brain needs ✅
- Showing up = the habit that compounds forever ✅

Every expert you admire was once exactly where you are. The only difference? They kept going.

**Your stats:**
🔥 You've been consistent
🎯 You're engaging with hard material  
🧠 You're building real expertise — not just surface knowledge

The compound interest of daily learning is **unstoppable**."""
            ])
        }

        explanation = explanations.get(mode, explanations["explain"])
        quick_check = self._get_quick_check(topic, mode)
        progress_note = self._get_progress_note(topic)
        next_step = self._get_next_step(topic, mode)

        return f"""🧠 **EXPLANATION**
{explanation}

❓ **QUICK CHECK**
{quick_check}

📊 **YOUR PROGRESS**
{progress_note}

⚡ **NEXT STEP**
{next_step}"""

    def _get_quick_check(self, topic: str, mode: str) -> str:
        checks = {
            "revise": f"Without notes: explain **{topic}** in 2-3 sentences, then give one real example.",
            "challenge": f"Design a minimal implementation of {topic} for 1M concurrent users. Name your top 3 decisions.",
            "motivate": f"What's one specific part of **{topic}** where you feel most uncertain right now?",
        }
        default = random.choice([
            f"In your own words: what problem does **{topic}** solve, and when would you use it?",
            f"Give a real-world example of **{topic}** in action — from your own thinking, not from memory.",
            f"What would break if you removed **{topic}** from a system that depends on it?",
        ])
        return checks.get(mode, default)

    def _get_progress_note(self, topic: str) -> str:
        return random.choice([
            f"You're actively engaging with **{topic}** — every interaction builds neural pathways 🧠. Each session compounds.",
            f"Asking questions about **{topic}** shows strong metacognitive awareness. You're learning how to learn.",
            f"Your learning depth in **{topic}** is growing. Consistency here beats any single cram session.",
        ])

    def _get_next_step(self, topic: str, mode: str) -> str:
        if mode in ["explain", "reteach"]:
            return f"→ Test yourself: say **\"Quiz me on {topic}\"** for an interactive question\n→ Or go deeper: **\"Give me an advanced challenge on {topic}\"**"
        elif mode == "challenge":
            return f"→ Explore optimization: **\"Explain optimization strategies for {topic}\"**\n→ Or practice: **\"Quiz me on {topic} edge cases\"**"
        elif mode == "revise":
            return f"→ Confirm retention: **\"Quiz me on {topic}\"**\n→ Or continue: **\"What's next after {topic}?\"**"
        else:
            return f"→ Keep going: **\"Teach me the next concept after {topic}\"**\n→ Or practice: **\"Quiz me on {topic}\"**"

    def _generate_quiz(self, topic: str) -> str:
        return json.dumps({
            "question": f"Which statement best describes the core principle of {topic}?",
            "options": [
                {"id": "a", "text": f"{topic.capitalize()} involves decomposing complex problems into structured, manageable components", "is_correct": True},
                {"id": "b", "text": f"{topic.capitalize()} only applies in theoretical academic contexts", "is_correct": False},
                {"id": "c", "text": f"{topic.capitalize()} requires memorizing all edge cases before applying it", "is_correct": False},
                {"id": "d", "text": f"{topic.capitalize()} is a deprecated approach with no modern relevance", "is_correct": False}
            ],
            "explanation": f"The foundation of {topic} is systematic decomposition — breaking complex challenges into structured, understandable parts that can each be solved independently."
        })


# Singleton — replaces the old llm_router
llm_router = HybridLLMRouter()
