"""Long-term memory model — per-topic strength and spaced repetition scheduling."""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.database import Base


class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    topic = Column(String(300), nullable=False)
    subject = Column(String(200), nullable=True)

    # SM-2 spaced repetition fields
    strength = Column(Float, default=0.0)       # 0.0 (unknown) → 1.0 (mastered)
    repetitions = Column(Integer, default=0)    # number of successful reviews
    ease_factor = Column(Float, default=2.5)    # SM-2 ease factor
    interval_days = Column(Float, default=1.0)  # days until next review

    # Mistake and confusion tracking
    mistake_count = Column(Integer, default=0)
    confusion_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)

    # Timestamps
    first_seen = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())
    next_review = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
