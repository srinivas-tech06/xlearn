from fastapi import APIRouter
from app.api.chat import router as chat_router
from app.api.roadmap import router as roadmap_router
from app.api.progress import router as progress_router
from app.api.user import router as user_router
from app.api.gamification import router as gamification_router
from app.api.memory import router as memory_router
from app.api.llm import router as llm_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat_router)
api_router.include_router(roadmap_router)
api_router.include_router(progress_router)
api_router.include_router(user_router)
api_router.include_router(gamification_router)
api_router.include_router(memory_router)
api_router.include_router(llm_router)

