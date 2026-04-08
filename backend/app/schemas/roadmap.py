from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TopicSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: str = ""
    order: int = 0
    status: str = "pending"
    difficulty: int = 2
    xp_reward: int = 10


class ModuleSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: str = ""
    order: int = 0
    status: str = "locked"
    progress: float = 0.0
    estimated_hours: float = 2.0
    topics: List[TopicSchema] = []


class RoadmapRequest(BaseModel):
    goal: str
    timeframe: str = "4 weeks"
    user_id: int = 1


class RoadmapResponse(BaseModel):
    id: Optional[int] = None
    goal: str
    timeframe: str
    status: str = "active"
    overall_progress: float = 0.0
    modules: List[ModuleSchema] = []


class RoadmapUpdateRequest(BaseModel):
    module_id: Optional[int] = None
    topic_id: Optional[int] = None
    status: Optional[str] = None
