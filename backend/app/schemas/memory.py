"""Memory system schemas."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MemoryEntry(BaseModel):
    id: int
    topic: str
    subject: Optional[str] = None
    strength: float
    repetitions: int
    mistake_count: int
    confusion_count: int
    correct_count: int
    interval_days: float
    next_review: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class WeakTopic(BaseModel):
    topic: str
    strength: float
    mistake_count: int
    reason: str  # "low_strength", "frequent_mistakes", "due_review"


class ScheduledReview(BaseModel):
    topic: str
    subject: Optional[str] = None
    due_date: str
    overdue_days: int
    strength: float
    priority: str  # "urgent", "today", "upcoming"


class MemoryOverview(BaseModel):
    weak_topics: List[WeakTopic]
    due_reviews: List[ScheduledReview]
    mastered_topics: List[str]
    total_topics_seen: int
    avg_strength: float


class MemoryUpdateRequest(BaseModel):
    user_id: int = 1
    topic: str
    subject: Optional[str] = None
    was_correct: bool
    was_confused: bool = False
