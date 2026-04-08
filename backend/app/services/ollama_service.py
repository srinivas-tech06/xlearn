"""
Ollama Service Layer — Local LLM inference via Ollama.
Handles streaming/non-streaming, timeouts, retries, and health checks.
"""
import httpx
import json
import asyncio
from typing import Optional, AsyncIterator
from app.core import settings


class OllamaService:
    """
    Manages all communication with a local Ollama instance.
    Endpoint: http://localhost:11434
    Supports: llama3, mistral, codellama, phi3, gemma, etc.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self._available: Optional[bool] = None  # cached health status

    # ─────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────
    async def health_check(self, force: bool = False) -> bool:
        """Check if Ollama is running. Cached after first check unless forced."""
        if self._available is not None and not force:
            return self._available
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                self._available = resp.status_code == 200
        except Exception:
            self._available = False
        return self._available

    async def list_models(self) -> list[str]:
        """Return list of locally available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def model_available(self, model: str) -> bool:
        """Check if a specific model is pulled and ready."""
        models = await self.list_models()
        return any(model in m for m in models)

    # ─────────────────────────────────────────────────────────────
    # Core Generation
    # ─────────────────────────────────────────────────────────────
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        retries: int = 2,
    ) -> str:
        """
        Generate a response from a local Ollama model.
        Auto-selects model, handles retries, validates response.
        """
        target_model = model or self.model

        # Build the full prompt with system instruction
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        payload = {
            "model": target_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            }
        }

        last_error = None
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    text = data.get("response", "").strip()

                    # Validate response quality
                    if self._is_valid_response(text):
                        return text
                    else:
                        print(f"[Ollama] Low-quality response on attempt {attempt+1}, retrying...")
                        last_error = "low_quality"

            except httpx.TimeoutException:
                print(f"[Ollama] Timeout on attempt {attempt+1}/{retries+1}")
                last_error = "timeout"
            except httpx.HTTPStatusError as e:
                print(f"[Ollama] HTTP error {e.response.status_code}: {e}")
                last_error = f"http_{e.response.status_code}"
                break  # Don't retry on 4xx errors (bad model name etc)
            except Exception as e:
                print(f"[Ollama] Error on attempt {attempt+1}: {e}")
                last_error = str(e)

            if attempt < retries:
                await asyncio.sleep(0.5 * (attempt + 1))  # exponential backoff

        raise RuntimeError(f"Ollama generation failed after {retries+1} attempts. Last error: {last_error}")

    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: str = "",
    ) -> AsyncIterator[str]:
        """Stream tokens from Ollama. Yields text chunks as they arrive."""
        target_model = model or self.model
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        payload = {
            "model": target_model,
            "prompt": full_prompt,
            "stream": True,
            "options": {"temperature": 0.7}
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            if token := chunk.get("response", ""):
                                yield token
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

    # ─────────────────────────────────────────────────────────────
    # Smart Model Selection
    # ─────────────────────────────────────────────────────────────
    def select_model_for_task(self, task_type: str) -> str:
        """
        Choose the best available local model for a given task.
        - Simple queries → lighter model (mistral, phi3)
        - Code tasks → codellama
        - Complex reasoning → llama3
        """
        model_preferences = {
            "EXPLAIN":   [self.model, "llama3", "mistral"],
            "QUIZ":      [self.model, "mistral", "llama3"],
            "CHALLENGE": [self.model, "llama3", "codellama"],
            "RETEACH":   ["mistral", self.model, "llama3"],
            "REVISE":    ["mistral", self.model],
            "MOTIVATE":  ["mistral", self.model],
            "CODE":      ["codellama", "llama3", self.model],
        }
        return model_preferences.get(task_type, [self.model])[0]

    # ─────────────────────────────────────────────────────────────
    # Response Validation
    # ─────────────────────────────────────────────────────────────
    def _is_valid_response(self, text: str) -> bool:
        """Basic quality checks on Ollama response."""
        if not text or len(text.strip()) < 20:
            return False
        # Check it's not just repeated tokens (Ollama hallucination pattern)
        words = text.split()
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.2:
                return False
        return True

    def estimate_complexity(self, prompt: str) -> str:
        """Estimate task complexity: simple | medium | complex."""
        prompt_lower = prompt.lower()
        complex_signals = ["compare", "analyze", "design", "evaluate", "explain in depth",
                           "advanced", "challenge", "architecture", "trade-off", "difference between"]
        simple_signals = ["what is", "define", "list", "quick", "brief", "simple"]

        if any(s in prompt_lower for s in complex_signals):
            return "complex"
        if any(s in prompt_lower for s in simple_signals):
            return "simple"
        return "medium"


# Singleton
ollama_service = OllamaService()
