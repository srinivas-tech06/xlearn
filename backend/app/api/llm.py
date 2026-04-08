"""
LLM Status API — Exposes router health, active backend, model info, and cache stats.
Also allows runtime configuration of routing mode.
"""
from fastapi import APIRouter
from app.services.llm_router import llm_router
from app.services.cache import response_cache
from app.core import settings

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status")
async def get_llm_status():
    """Get full health status of all LLM backends and routing mode."""
    return await llm_router.check_health()


@router.get("/models")
async def get_available_models():
    """List locally available Ollama models."""
    from app.services.ollama_service import ollama_service
    is_online = await ollama_service.health_check(force=True)
    local_models = await ollama_service.list_models() if is_online else []
    return {
        "ollama_online": is_online,
        "local_models": local_models,
        "configured_model": settings.OLLAMA_MODEL,
        "cloud_model": settings.LLM_MODEL if settings.cloud_available else None,
        "cloud_provider": settings.LLM_PROVIDER if settings.cloud_available else None,
    }


@router.post("/routing-mode")
async def set_routing_mode(mode: str):
    """
    Dynamically change routing mode at runtime.
    Valid values: auto | ollama_only | cloud_only | fallback_only
    """
    valid_modes = ["auto", "ollama_only", "cloud_only", "fallback_only"]
    if mode not in valid_modes:
        return {"error": f"Invalid mode. Choose from: {valid_modes}"}
    settings.LLM_ROUTING_MODE = mode
    # Invalidate cache so new mode takes effect immediately
    response_cache.clear()
    return {
        "routing_mode": mode,
        "privacy_mode": settings.PRIVACY_MODE,
        "cache_cleared": True,
        "message": f"Routing mode set to '{mode}'"
    }


@router.post("/privacy-mode")
async def toggle_privacy_mode(enabled: bool):
    """Toggle privacy mode — forces local Ollama, disables all cloud calls."""
    settings.PRIVACY_MODE = enabled
    response_cache.clear()
    return {
        "privacy_mode": settings.PRIVACY_MODE,
        "effect": "All inference is now local (Ollama only)" if enabled else "Cloud LLM re-enabled",
        "cache_cleared": True,
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get response cache statistics."""
    return response_cache.stats


@router.post("/cache/clear")
async def clear_cache():
    """Manually clear the response cache."""
    response_cache.clear()
    return {"cleared": True, "message": "Response cache has been cleared."}


@router.post("/ping-ollama")
async def ping_ollama():
    """Force a fresh health check against the Ollama server."""
    from app.services.ollama_service import ollama_service
    is_ok = await ollama_service.health_check(force=True)
    models = await ollama_service.list_models() if is_ok else []
    return {
        "ollama_available": is_ok,
        "url": settings.OLLAMA_URL,
        "models": models,
        "message": "✅ Ollama is running" if is_ok else "❌ Ollama not reachable — install from https://ollama.ai"
    }
