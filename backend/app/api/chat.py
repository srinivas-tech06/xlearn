"""Chat API — Main interaction endpoint. Upgraded with memory + RAG + mentor support."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, QuizAnswerRequest
from app.agents.orchestrator import orchestrator
from app.models.user import User
from app.models.student_state import StudentState
from app.models.learning_history import LearningInteraction
from app.services.gamification import gamification_service
from app.services.memory_service import memory_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Main chat endpoint — processes user message through the full agent pipeline."""
    import traceback
    try:
        user = await _get_or_create_user(db, request.user_id)
        state = await _get_or_create_state(db, user.id)
        user_state = {
            "understanding": state.understanding,
            "confidence": state.confidence,
            "engagement": state.engagement,
            "retention": state.retention,
        }

        # Load memory context
        weak_topics = await memory_service.get_weak_topics(db, user.id, limit=3)
        due_reviews = await memory_service.get_due_reviews(db, user.id)

        context = {
            "current_topic": request.context,
            "session_count": user.total_sessions,
            "last_action": None,
        }

        # Process through upgraded orchestrator
        response = await orchestrator.process(
            message=request.message,
            user_state=user_state,
            context=context,
            mentor=request.mentor or "direct",
            weak_topics=weak_topics,
            due_reviews=due_reviews,
        )

        # Update student state
        if response.feedback:
            state.understanding = response.feedback.understanding
            state.confidence = response.feedback.confidence
            state.engagement = response.feedback.engagement
            state.retention = response.feedback.retention

        # Award XP
        xp_earned = response.xp_earned
        user.xp += xp_earned
        user.level = gamification_service.calculate_level(user.xp)
        user.total_sessions += 1

        # Update memory for the current topic
        topic = request.context or orchestrator._extract_topic(request.message)
        if topic and topic != "the current topic":
            await memory_service.record_interaction(
                db=db,
                user_id=user.id,
                topic=topic,
                subject="",
                was_correct=True,  # Chat = learning, not testing
                was_confused=any(w in request.message.lower() for w in ["confused", "don't understand", "help", "stuck"])
            )
            response.memory_updated = True

        # Log interaction
        interaction = LearningInteraction(
            user_id=user.id,
            interaction_type="chat",
            agent_action=response.agent_action,
            user_message=request.message,
            ai_response=response.content[:500],
            topic=topic or "",
            xp_awarded=xp_earned,
        )
        db.add(interaction)
        await db.flush()

        return response
    except Exception as e:
        traceback.print_exc()
        raise


@router.post("/quiz-answer", response_model=ChatResponse)
async def submit_quiz_answer(request: QuizAnswerRequest, db: AsyncSession = Depends(get_db)):
    """Process a quiz answer and update memory/spaced repetition."""
    user = await _get_or_create_user(db, request.user_id)
    state = await _get_or_create_state(db, user.id)

    user_state = {
        "understanding": state.understanding,
        "confidence": state.confidence,
        "engagement": state.engagement,
        "retention": state.retention,
    }

    is_correct = request.selected_option_id == request.correct_option_id
    response = await orchestrator.process_quiz_answer(is_correct, request.topic, user_state)

    # Update state
    if response.feedback:
        state.understanding = response.feedback.understanding
        state.confidence = response.feedback.confidence
        state.engagement = response.feedback.engagement
        state.retention = response.feedback.retention

    # Award XP
    xp = gamification_service.award_xp("QUIZ_CORRECT" if is_correct else "QUIZ_WRONG")
    response.xp_earned = xp
    user.xp += xp
    user.level = gamification_service.calculate_level(user.xp)

    # Update spaced repetition memory for quiz topic
    if request.topic:
        await memory_service.record_interaction(
            db=db,
            user_id=user.id,
            topic=request.topic,
            subject="",
            was_correct=is_correct,
            was_confused=not is_correct,
        )

    # Log
    interaction = LearningInteraction(
        user_id=user.id,
        interaction_type="quiz",
        agent_action="QUIZ_ANSWER",
        user_message=f"Answer: {request.selected_option_id}",
        topic=request.topic,
        score=100 if is_correct else 0,
        xp_awarded=xp,
    )
    db.add(interaction)
    await db.flush()

    return response


async def _get_or_create_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, name="Learner")
        db.add(user)
        await db.flush()
    return user


async def _get_or_create_state(db: AsyncSession, user_id: int) -> StudentState:
    result = await db.execute(select(StudentState).where(StudentState.user_id == user_id))
    state = result.scalar_one_or_none()
    if not state:
        state = StudentState(user_id=user_id)
        db.add(state)
        await db.flush()
    return state
