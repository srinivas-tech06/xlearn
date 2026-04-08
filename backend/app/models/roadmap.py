from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from app.core.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String(500), nullable=False)
    timeframe = Column(String(100), default="4 weeks")
    status = Column(String(50), default="active")
    overall_progress = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RoadmapModule(Base):
    __tablename__ = "roadmap_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    status = Column(String(50), default="locked")  # locked, active, completed
    progress = Column(Float, default=0.0)
    estimated_hours = Column(Float, default=2.0)
    created_at = Column(DateTime, server_default=func.now())


class RoadmapTopic(Base):
    __tablename__ = "roadmap_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("roadmap_modules.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    difficulty = Column(Integer, default=2)
    xp_reward = Column(Integer, default=10)
