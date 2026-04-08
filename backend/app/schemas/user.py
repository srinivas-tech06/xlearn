from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class UserCreate(BaseModel):
    name: str = "Learner"
    email: Optional[str] = None
    current_goal: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    level: int
    xp: int
    streak: int
    total_sessions: int
    current_goal: Optional[str] = None


class StudentStateResponse(BaseModel):
    understanding: float
    confidence: float
    engagement: float
    retention: float
    difficulty_level: int


class DailyProgressResponse(BaseModel):
    date: str
    sessions_completed: int
    xp_earned: int
    topics_covered: int
    quizzes_taken: int
    quizzes_correct: int
    time_spent_minutes: int
    completion_level: float


class CalendarEntry(BaseModel):
    date: str
    completion_level: float
    xp_earned: int


class ProgressOverview(BaseModel):
    user: UserResponse
    state: StudentStateResponse
    today: Optional[DailyProgressResponse] = None
    calendar: List[CalendarEntry] = []
    weekly_xp: int = 0
    total_topics: int = 0
    completed_topics: int = 0


class GamificationResponse(BaseModel):
    xp: int
    level: int
    level_title: str
    xp_to_next_level: int
    xp_progress_percent: float
    streak: int
    badges: List[dict] = []
