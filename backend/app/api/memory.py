"""
Memory API — endpoints for user memory and spaced repetition system.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.memory import MemoryOverview, MemoryUpdateRequest, MemoryEntry
from app.services.memory_service import memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/{user_id}", response_model=MemoryOverview)
async def get_memory(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get complete memory overview: weak topics, due reviews, mastered."""
    return await memory_service.get_overview(db, user_id)


@router.post("/update")
async def update_memory(request: MemoryUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Record an interaction and update topic memory/spaced repetition."""
    mem = await memory_service.record_interaction(
        db=db,
        user_id=request.user_id,
        topic=request.topic,
        subject=request.subject or "",
        was_correct=request.was_correct,
        was_confused=request.was_confused,
    )
    return {
        "topic": mem.topic,
        "strength": round(mem.strength, 2),
        "next_review": mem.next_review.isoformat() if mem.next_review else None,
        "interval_days": mem.interval_days,
    }
