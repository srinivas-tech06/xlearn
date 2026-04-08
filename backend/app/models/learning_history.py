from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, func
from app.core.database import Base


class LearningInteraction(Base):
    __tablename__ = "learning_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # chat, quiz, challenge
    agent_action = Column(String(50), nullable=False)  # EXPLAIN, QUIZ, RETEACH, etc.
    user_message = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    topic = Column(String(200), nullable=True)
    score = Column(Float, nullable=True)  # quiz score 0-100
    xp_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
