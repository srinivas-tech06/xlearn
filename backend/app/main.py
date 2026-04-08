"""
AI Powered Learning Assistant — FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings
from app.core.database import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 AI Powered Learning Assistant starting up...")
    print(f"📡 LLM Available: {settings.llm_available}")
    if not settings.llm_available:
        print("⚡ Running in FALLBACK mode — using template-based AI responses")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 AI Powered Learning Assistant shutting down...")


app = FastAPI(
    title="AI Powered Learning Assistant",
    description="Multi-agent autonomous learning system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": "AI Powered Learning Assistant",
        "version": "1.0.0",
        "status": "running",
        "llm_mode": "api" if settings.llm_available else "fallback",
        "agents": [
            "🧠 Teaching Agent",
            "📊 State Analyzer Agent",
            "🗺️ Roadmap Agent",
            "📅 Progress Agent",
            "🧩 Decision Agent",
            "⚡ Orchestrator Agent",
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "llm_available": settings.llm_available}
