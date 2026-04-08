from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class QuizOption(BaseModel):
    id: str
    text: str
    is_correct: bool = False


class QuizData(BaseModel):
    question: str
    options: List[QuizOption]
    explanation: str = ""
    difficulty: int = 2
    xp_reward: int = 10


class FeedbackData(BaseModel):
    understanding: float
    confidence: float
    engagement: float
    retention: float
    message: str = ""


class NextStepData(BaseModel):
    action: str
    topic: str = ""
    description: str = ""


class ChatRequest(BaseModel):
    message: str
    user_id: int = 1
    context: Optional[str] = None
    quiz_answer: Optional[str] = None
    mentor: Optional[str] = "direct"  # socratic, direct, storyteller, motivator


class ChatResponse(BaseModel):
    agent_action: str
    content: str
    quiz: Optional[QuizData] = None
    feedback: Optional[FeedbackData] = None
    next_step: Optional[NextStepData] = None
    xp_earned: int = 0
    message_type: str = "explanation"  # explanation, quiz, feedback, challenge, motivation
    rag_sources: Optional[List[dict]] = None  # Retrieved knowledge sources
    memory_updated: bool = False


class QuizAnswerRequest(BaseModel):
    user_id: int = 1
    quiz_question: str
    selected_option_id: str
    correct_option_id: str
    topic: str = ""
