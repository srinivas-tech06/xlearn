"""
Orchestrator Agent — The brain that coordinates all other agents.
Upgraded with: RAG tool, memory reader, confusion detection, spaced repetition triggers.
"""
from app.agents.teaching import teaching_agent
from app.agents.state_analyzer import state_analyzer_agent
from app.agents.decision import decision_agent
from app.agents.roadmap import roadmap_agent
from app.agents.progress import progress_agent
from app.schemas.chat import ChatResponse, QuizData, FeedbackData, NextStepData
from app.services.rag_engine import rag_engine


class OrchestratorAgent:
    """
    Execution loop for every user interaction:
    1. RAG: Retrieve relevant knowledge context
    2. Memory: Load user weak topics / confusion history
    3. Analyze user input + state
    4. Detect intent (explicit) or let Decision Agent decide
    5. Execute teaching action with full context
    6. Update state + compose structured response
    7. Adapt next step
    """

    async def process(
        self,
        message: str,
        user_state: dict,
        context: dict = None,
        mentor: str = "direct",
        weak_topics: list = None,
        due_reviews: list = None,
    ) -> ChatResponse:
        context = context or {}
        weak_topics = weak_topics or []
        due_reviews = due_reviews or []

        topic = context.get("current_topic") or self._extract_topic(message)

        # Step 1: RAG — retrieve relevant context
        rag_docs = rag_engine.retrieve(f"{topic} {message}", k=2)
        rag_context = rag_engine.format_context(rag_docs) if rag_docs else ""

        # Step 2: Memory context
        from app.services.memory_service import memory_service
        memory_context = memory_service.get_memory_context(weak_topics)

        # Step 3: Check if spaced repetition review is due
        if due_reviews and self._is_casual_message(message):
            due_topic = due_reviews[0]
            action = "REVISE"
            topic = due_topic.topic
        else:
            # Step 3b: Analyze state
            interaction = {
                "type": "chat",
                "score": context.get("last_score"),
                "consecutive_sessions": context.get("session_count", 1),
            }
            updated_state = state_analyzer_agent.analyze(interaction, user_state)

            # Step 4: Detect intent or use Decision Agent
            decision_context = {
                "is_new_topic": self._is_new_topic(message),
                "last_action": context.get("last_action"),
            }
            action = decision_agent.decide(updated_state, decision_context)
            user_intent = self._detect_intent(message)
            if user_intent:
                action = user_intent

        # Re-analyze state if not already done
        interaction = {
            "type": "chat",
            "score": context.get("last_score"),
            "consecutive_sessions": context.get("session_count", 1),
        }
        updated_state = state_analyzer_agent.analyze(interaction, user_state)

        # Step 5: Execute action with full context
        response = await self._execute_action(
            action, topic, updated_state,
            memory_context=memory_context,
            rag_context=rag_context,
            mentor=mentor
        )

        # Step 6: Build feedback
        feedback = FeedbackData(
            understanding=updated_state["understanding"],
            confidence=updated_state["confidence"],
            engagement=updated_state["engagement"],
            retention=updated_state["retention"],
            message=decision_agent.get_action_description(action)
        )
        response.feedback = feedback

        # Attach RAG sources
        response.rag_sources = [
            {"topic": d["topic"], "subject": d["subject"]}
            for d in rag_docs[:2]
        ] if rag_docs else []

        # Step 7: Next step
        next_action = self._get_next_action(action, updated_state)
        response.next_step = NextStepData(
            action=next_action,
            topic=topic,
            description=decision_agent.get_action_description(next_action)
        )

        return response

    async def process_quiz_answer(
        self, is_correct: bool, topic: str, user_state: dict, mentor: str = "direct"
    ) -> ChatResponse:
        score = 100 if is_correct else 0
        xp = 15 if is_correct else 2

        interaction = {"type": "quiz", "score": score}
        updated_state = state_analyzer_agent.analyze(interaction, user_state)

        if is_correct:
            content = f"""🧠 **EXPLANATION**
🎉 **Correct!** Excellent work on **{topic}**.

❓ **QUICK CHECK**
Can you explain *why* that answer is correct in your own words?

📊 **YOUR PROGRESS**
Your accuracy on {topic} is improving. Strength +10% ⬆️

⚡ **NEXT STEP**
Let's go deeper — ready for an advanced concept in {topic}?"""
        else:
            rag_docs = rag_engine.retrieve(topic, k=1)
            rag_hint = rag_engine.format_context(rag_docs) if rag_docs else ""
            content = f"""🧠 **EXPLANATION**
Not quite — let me clarify **{topic}** for you.

{rag_hint}

❓ **QUICK CHECK**
What was your reasoning for that answer? Understanding *why* you chose it helps us learn.

📊 **YOUR PROGRESS**
Mistakes are how we grow! This has been noted to revisit.

⚡ **NEXT STEP**
I'll schedule a review of {topic} in 2 days via spaced repetition."""

        action = decision_agent.decide(updated_state, {"last_action": "QUIZ", "is_new_topic": False})
        feedback = FeedbackData(
            understanding=updated_state["understanding"],
            confidence=updated_state["confidence"],
            engagement=updated_state["engagement"],
            retention=updated_state["retention"],
            message="Great job!" if is_correct else "Learning from mistakes!"
        )

        return ChatResponse(
            agent_action="QUIZ_FEEDBACK",
            content=content,
            feedback=feedback,
            next_step=NextStepData(
                action=action,
                topic=topic,
                description=decision_agent.get_action_description(action)
            ),
            xp_earned=xp,
            message_type="feedback",
            rag_sources=[]
        )

    async def _execute_action(
        self, action: str, topic: str, state: dict,
        memory_context: str = "", rag_context: str = "", mentor: str = "direct"
    ) -> ChatResponse:
        difficulty = state_analyzer_agent.get_difficulty_recommendation(state)

        if action == "EXPLAIN":
            content = await teaching_agent.explain(topic, depth=difficulty, memory_context=memory_context, rag_context=rag_context, mentor=mentor)
            return ChatResponse(agent_action="EXPLAIN", content=content, xp_earned=5, message_type="explanation", rag_sources=[])

        elif action == "QUIZ":
            content = "Let's test your understanding! 🧠"
            quiz = await teaching_agent.quiz(topic, difficulty=difficulty, mentor=mentor)
            return ChatResponse(agent_action="QUIZ", content=content, quiz=quiz, xp_earned=0, message_type="quiz", rag_sources=[])

        elif action == "RETEACH":
            content = await teaching_agent.reteach(topic, memory_context=memory_context, rag_context=rag_context, mentor=mentor)
            return ChatResponse(agent_action="RETEACH", content=content, xp_earned=5, message_type="explanation", rag_sources=[])

        elif action == "CHALLENGE":
            content = await teaching_agent.challenge(topic, mentor=mentor)
            return ChatResponse(agent_action="CHALLENGE", content=content, xp_earned=0, message_type="challenge", rag_sources=[])

        elif action == "REVISE":
            content = await teaching_agent.revise(topic, memory_context=memory_context, mentor=mentor)
            return ChatResponse(agent_action="REVISE", content=content, xp_earned=5, message_type="explanation", rag_sources=[])

        elif action == "MOTIVATE":
            content = await teaching_agent.motivate(topic, mentor=mentor)
            return ChatResponse(agent_action="MOTIVATE", content=content, xp_earned=5, message_type="motivation", rag_sources=[])

        else:
            content = await teaching_agent.explain(topic, depth=difficulty, memory_context=memory_context, rag_context=rag_context, mentor=mentor)
            return ChatResponse(agent_action="EXPLAIN", content=content, xp_earned=5, message_type="explanation", rag_sources=[])

    def _detect_intent(self, message: str) -> str | None:
        msg = message.lower()
        if any(kw in msg for kw in ["quiz", "test me", "test my", "question", "practice", "question me"]):
            return "QUIZ"
        if any(kw in msg for kw in ["explain", "what is", "how does", "teach", "learn", "tell me"]):
            return "EXPLAIN"
        if any(kw in msg for kw in ["challenge", "hard", "advanced", "difficult", "push me"]):
            return "CHALLENGE"
        if any(kw in msg for kw in ["review", "revise", "recap", "summary", "remind me"]):
            return "REVISE"
        if any(kw in msg for kw in ["confused", "don't understand", "help", "stuck", "again", "simpler"]):
            return "RETEACH"
        if any(kw in msg for kw in ["motivate", "encourage", "feeling bad", "give up"]):
            return "MOTIVATE"
        return None

    def _is_casual_message(self, message: str) -> bool:
        """Detect if message is a general greeting or casual input."""
        msg = message.lower().strip()
        casual = ["hi", "hello", "hey", "start", "begin", "ready", "ok", "let's go", "continue"]
        return any(msg == c or msg.startswith(c + " ") for c in casual) or len(msg.split()) <= 2

    def _is_new_topic(self, message: str) -> bool:
        kws = ["learn", "start", "begin", "new", "teach me", "what is", "introduce", "explain", "how to"]
        return any(kw in message.lower() for kw in kws)

    def _extract_topic(self, message: str) -> str:
        stop = {"what", "how", "does", "this", "that", "with", "about", "learn", "teach",
                "explain", "want", "need", "help", "please", "could", "would", "should",
                "know", "understand", "tell", "more", "like", "just", "some", "also"}
        words = [w for w in message.strip().split() if len(w) > 3 and w.lower() not in stop]
        return " ".join(words[:4]) if words else "the current topic"

    def _get_next_action(self, current_action: str, state: dict) -> str:
        flow = {
            "EXPLAIN": "QUIZ",
            "QUIZ": "EXPLAIN",
            "RETEACH": "QUIZ",
            "CHALLENGE": "EXPLAIN",
            "REVISE": "QUIZ",
            "MOTIVATE": "EXPLAIN",
            "QUIZ_FEEDBACK": "EXPLAIN",
        }
        return flow.get(current_action, "EXPLAIN")


orchestrator = OrchestratorAgent()
