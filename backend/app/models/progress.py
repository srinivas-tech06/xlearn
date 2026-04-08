from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, func
from app.core.database import Base


class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    sessions_completed = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    topics_covered = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)
    quizzes_correct = Column(Integer, default=0)
    time_spent_minutes = Column(Integer, default=0)
    completion_level = Column(Float, default=0.0)  # 0-100
    created_at = Column(DateTime, server_default=func.now())
