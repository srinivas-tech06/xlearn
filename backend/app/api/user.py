"""User API — User management."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserResponse)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = User(name=data.name, email=data.email, current_goal=data.current_goal)
    db.add(user)
    await db.flush()
    return UserResponse(
        id=user.id, name=user.name, email=user.email,
        level=user.level, xp=user.xp, streak=user.streak,
        total_sessions=user.total_sessions, current_goal=user.current_goal,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, name="Learner")
        db.add(user)
        await db.flush()
    return UserResponse(
        id=user.id, name=user.name, email=user.email,
        level=user.level, xp=user.xp, streak=user.streak,
        total_sessions=user.total_sessions, current_goal=user.current_goal,
    )
