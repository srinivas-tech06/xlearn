"""Gamification API — XP, levels, badges."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.schemas.user import GamificationResponse
from app.models.user import User
from app.models.learning_history import LearningInteraction
from app.services.gamification import gamification_service

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/{user_id}", response_model=GamificationResponse)
async def get_gamification(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, name="Learner")
        db.add(user)
        await db.flush()

    # Count quizzes correct
    result = await db.execute(
        select(func.count()).where(
            LearningInteraction.user_id == user_id,
            LearningInteraction.interaction_type == "quiz",
            LearningInteraction.score >= 80
        )
    )
    correct_quizzes = result.scalar() or 0

    user_stats = {
        "xp": user.xp,
        "streak": user.streak,
        "total_sessions": user.total_sessions,
        "correct_quizzes": correct_quizzes,
        "topics_completed": 0,
        "modules_completed": 0,
        "challenges": 0,
        "perfect_quiz": False,
    }

    badges = gamification_service.check_badges(user_stats)
    level = gamification_service.calculate_level(user.xp)

    return GamificationResponse(
        xp=user.xp,
        level=level,
        level_title=gamification_service.get_level_title(level),
        xp_to_next_level=gamification_service.xp_to_next_level(user.xp),
        xp_progress_percent=gamification_service.xp_progress_percent(user.xp),
        streak=user.streak,
        badges=badges,
    )
