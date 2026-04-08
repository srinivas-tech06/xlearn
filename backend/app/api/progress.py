"""Progress API — Track and view learning progress."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.student_state import StudentState
from app.models.progress import DailyProgress
from app.models.learning_history import LearningInteraction
from app.schemas.user import ProgressOverview, UserResponse, StudentStateResponse, DailyProgressResponse, CalendarEntry

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}", response_model=ProgressOverview)
async def get_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get comprehensive progress overview."""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, name="Learner")
        db.add(user)
        await db.flush()

    # Get state
    result = await db.execute(select(StudentState).where(StudentState.user_id == user_id))
    state = result.scalar_one_or_none()
    if not state:
        state = StudentState(user_id=user_id)
        db.add(state)
        await db.flush()

    # Get today's progress
    today = date.today()
    result = await db.execute(
        select(DailyProgress).where(
            DailyProgress.user_id == user_id,
            DailyProgress.date == today
        )
    )
    today_progress = result.scalar_one_or_none()

    # Get calendar (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    result = await db.execute(
        select(DailyProgress).where(
            DailyProgress.user_id == user_id,
            DailyProgress.date >= thirty_days_ago
        ).order_by(DailyProgress.date)
    )
    daily_records = result.scalars().all()

    # Weekly XP
    week_ago = today - timedelta(days=7)
    result = await db.execute(
        select(func.sum(DailyProgress.xp_earned)).where(
            DailyProgress.user_id == user_id,
            DailyProgress.date >= week_ago
        )
    )
    weekly_xp = result.scalar() or 0

    # Build calendar entries (fill in empty days)
    calendar = []
    daily_map = {str(r.date): r for r in daily_records}
    for i in range(30):
        d = today - timedelta(days=29-i)
        record = daily_map.get(str(d))
        calendar.append(CalendarEntry(
            date=str(d),
            completion_level=record.completion_level if record else 0,
            xp_earned=record.xp_earned if record else 0,
        ))

    return ProgressOverview(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            level=user.level,
            xp=user.xp,
            streak=user.streak,
            total_sessions=user.total_sessions,
            current_goal=user.current_goal,
        ),
        state=StudentStateResponse(
            understanding=state.understanding,
            confidence=state.confidence,
            engagement=state.engagement,
            retention=state.retention,
            difficulty_level=state.difficulty_level,
        ),
        today=DailyProgressResponse(
            date=str(today),
            sessions_completed=today_progress.sessions_completed if today_progress else 0,
            xp_earned=today_progress.xp_earned if today_progress else 0,
            topics_covered=today_progress.topics_covered if today_progress else 0,
            quizzes_taken=today_progress.quizzes_taken if today_progress else 0,
            quizzes_correct=today_progress.quizzes_correct if today_progress else 0,
            time_spent_minutes=today_progress.time_spent_minutes if today_progress else 0,
            completion_level=today_progress.completion_level if today_progress else 0,
        ),
        calendar=calendar,
        weekly_xp=weekly_xp,
    )
