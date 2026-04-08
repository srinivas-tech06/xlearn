from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from app.core.database import Base


class StudentState(Base):
    __tablename__ = "student_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    understanding = Column(Float, default=50.0)
    confidence = Column(Float, default=50.0)
    engagement = Column(Float, default=70.0)
    retention = Column(Float, default=50.0)
    current_topic = Column(Integer, nullable=True)
    difficulty_level = Column(Integer, default=2)  # 1=easy, 2=medium, 3=hard
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
