"""
Teaching Agent — Explains concepts, generates quizzes, adapts depth.
Upgraded with: RAG context injection, mentor personalities, structured 4-part responses.
"""
import json
import random
from app.services.llm_router import llm_router
from app.schemas.chat import QuizData, QuizOption


MENTOR_PERSONALITIES = {
    "socratic": {
        "name": "Socratic",
        "icon": "🧠",
        "style": "You guide through probing questions. Never give direct answers — ask questions that lead the student to discover answers themselves.",
        "color": "purple"
    },
    "direct": {
        "name": "Direct",
        "icon": "🎯",
        "style": "You are concise and precise. Give structured bullet-point answers. No fluff. Facts first, then application.",
        "color": "cyan"
    },
    "storyteller": {
        "name": "Storyteller",
        "icon": "📖",
        "style": "You teach through analogies, stories, and real-world examples. Make every concept feel like a narrative.",
        "color": "orange"
    },
    "motivator": {
        "name": "Motivator",
        "icon": "🚀",
        "style": "You are energetic and encouraging. Celebrate small wins. Build confidence first, knowledge second.",
        "color": "green"
    }
}


class TeachingAgent:
    def _build_4part_prompt(self, action: str, topic: str, depth_label: str, memory_context: str, rag_context: str, mentor: str) -> str:
        """Build a prompt that generates the structured 4-part response format."""
        mentor_style = MENTOR_PERSONALITIES.get(mentor, MENTOR_PERSONALITIES["direct"])["style"]
        parts = [
            f"Mentor style: {mentor_style}",
            f"Memory context: {memory_context}" if memory_context else "",
            rag_context if rag_context else "",
            f"\nTask: {action} about '{topic}' at {depth_label} level.",
            "\nRespond in EXACTLY this 4-part format:",
            "\n🧠 **EXPLANATION**\n[Clear explanation with analogy or example]",
            "\n❓ **QUICK CHECK**\n[One question to test understanding]",
            "\n📊 **YOUR PROGRESS**\n[Brief encouraging feedback on where they are in learning this]",
            "\n⚡ **NEXT STEP**\n[What to study or do next]"
        ]
        return "\n".join(p for p in parts if p)

    async def explain(self, topic: str, depth: int = 2, memory_context: str = "", rag_context: str = "", mentor: str = "direct") -> str:
        depth_label = {1: "beginner-friendly", 2: "intermediate", 3: "advanced"}.get(depth, "intermediate")
        prompt = self._build_4part_prompt("EXPLAIN", topic, depth_label, memory_context, rag_context, mentor)
        context = {"action": "EXPLAIN", "topic": topic, "mentor": mentor, "memory_context": memory_context, "rag_context": rag_context}
        return await llm_router.generate(prompt, context=context)

    async def quiz(self, topic: str, difficulty: int = 2, mentor: str = "direct") -> QuizData:
        context = {"action": "QUIZ", "topic": topic}
        raw = await llm_router.generate(
            f"Generate a {['easy','medium','hard'][difficulty-1]} multiple-choice quiz question about {topic}. Return JSON only.",
            context=context
        )
        try:
            data = json.loads(raw)
            options = [QuizOption(**opt) for opt in data.get("options", [])]
            return QuizData(
                question=data.get("question", f"What is a key concept in {topic}?"),
                options=options,
                explanation=data.get("explanation", ""),
                difficulty=difficulty,
                xp_reward=10 * difficulty
            )
        except (json.JSONDecodeError, KeyError):
            return self._fallback_quiz(topic, difficulty)

    async def reteach(self, topic: str, memory_context: str = "", rag_context: str = "", mentor: str = "direct") -> str:
        prompt = self._build_4part_prompt("RE-EXPLAIN (simpler)", topic, "beginner", memory_context, rag_context, mentor)
        context = {"action": "RETEACH", "topic": topic, "mentor": mentor}
        return await llm_router.generate(prompt, context=context)

    async def challenge(self, topic: str, mentor: str = "direct") -> str:
        prompt = self._build_4part_prompt("ADVANCED CHALLENGE", topic, "expert", "", "", mentor)
        context = {"action": "CHALLENGE", "topic": topic}
        return await llm_router.generate(prompt, context=context)

    async def revise(self, topic: str, memory_context: str = "", mentor: str = "direct") -> str:
        prompt = self._build_4part_prompt("SPACED REPETITION REVISION", topic, "intermediate", memory_context, "", mentor)
        context = {"action": "REVISE", "topic": topic}
        return await llm_router.generate(prompt, context=context)

    async def motivate(self, topic: str, mentor: str = "motivator") -> str:
        prompt = self._build_4part_prompt("MOTIVATE about learning", topic, "", "", "", mentor)
        context = {"action": "MOTIVATE", "topic": topic}
        return await llm_router.generate(prompt, context=context)

    def _fallback_quiz(self, topic: str, difficulty: int) -> QuizData:
        return QuizData(
            question=f"Which statement about {topic} is most accurate?",
            options=[
                QuizOption(id="a", text=f"{topic.capitalize()} uses structured decomposition to solve complex problems", is_correct=True),
                QuizOption(id="b", text=f"{topic.capitalize()} has no practical real-world applications", is_correct=False),
                QuizOption(id="c", text=f"{topic.capitalize()} can only be learned through memorization alone", is_correct=False),
                QuizOption(id="d", text=f"{topic.capitalize()} is completely unrelated to other computing concepts", is_correct=False),
            ],
            explanation=f"The core of {topic} is systematic problem decomposition — breaking complexity into manageable, understandable pieces.",
            difficulty=difficulty,
            xp_reward=10 * difficulty
        )


teaching_agent = TeachingAgent()
