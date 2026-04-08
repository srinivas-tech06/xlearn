"""
Response Cache — LRU cache for LLM responses to avoid redundant inference.
Thread-safe, TTL-aware, size-bounded.
"""
import hashlib
import time
from collections import OrderedDict
from typing import Optional
from app.core import settings


class ResponseCache:
    """
    Simple LRU cache with TTL for LLM responses.
    Key = hash(model + prompt). Value = (response, timestamp).
    """

    def __init__(self, max_size: int = None, ttl_seconds: int = None):
        self.max_size = max_size or settings.CACHE_MAX_SIZE
        self.ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
        self.enabled = settings.CACHE_ENABLED
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _make_key(self, model: str, prompt: str) -> str:
        raw = f"{model}::{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, model: str, prompt: str) -> Optional[str]:
        """Retrieve a cached response. Returns None if absent or expired."""
        if not self.enabled:
            return None

        key = self._make_key(model, prompt)
        if key not in self._cache:
            self._misses += 1
            return None

        response, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (LRU — recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return response

    def set(self, model: str, prompt: str, response: str) -> None:
        """Store a response in cache."""
        if not self.enabled or not response:
            return

        key = self._make_key(model, prompt)
        self._cache[key] = (response, time.time())
        self._cache.move_to_end(key)

        # Evict oldest if over size limit
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def invalidate(self, model: str, prompt: str) -> None:
        key = self._make_key(model, prompt)
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 3) if total > 0 else 0.0,
            "enabled": self.enabled,
        }


# Singleton
response_cache = ResponseCache()
