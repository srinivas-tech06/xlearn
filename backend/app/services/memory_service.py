"""
Long-Term Memory Service — tracks per-topic understanding, mistakes, and learning patterns.
Uses the SM-2 spaced repetition algorithm to schedule reviews.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.memory import UserMemory
from app.schemas.memory import WeakTopic, ScheduledReview, MemoryOverview


class MemoryService:
    """Manages per-user, per-topic learning memory with spaced repetition."""

    # SM-2 constants
    MIN_EASE = 1.3
    INITIAL_INTERVAL = 1  # days

    async def get_or_create(
        self, db: AsyncSession, user_id: int, topic: str, subject: str = ""
    ) -> UserMemory:
        """Get or create a memory record for a user-topic pair."""
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.topic == topic.lower().strip()
            )
        )
        mem = result.scalar_one_or_none()
        if not mem:
            mem = UserMemory(
                user_id=user_id,
                topic=topic.lower().strip(),
                subject=subject,
                next_review=datetime.utcnow() + timedelta(days=1)
            )
            db.add(mem)
            await db.flush()
        return mem

    async def record_interaction(
        self,
        db: AsyncSession,
        user_id: int,
        topic: str,
        subject: str = "",
        was_correct: bool = True,
        was_confused: bool = False,
        quality: int = None,  # SM-2 quality 0-5 (None = auto-compute)
    ) -> UserMemory:
        """Record an interaction and update SM-2 state."""
        mem = await self.get_or_create(db, user_id, topic, subject)

        # Track counts
        if was_correct:
            mem.correct_count += 1
        else:
            mem.mistake_count += 1
        if was_confused:
            mem.confusion_count += 1

        # Compute SM-2 quality if not provided
        if quality is None:
            if was_confused:
                quality = 1
            elif not was_correct:
                quality = 2
            elif was_correct and not was_confused:
                quality = 4 if mem.correct_count > 2 else 3

        # Apply SM-2 algorithm
        if quality >= 3:
            # Successful recall
            if mem.repetitions == 0:
                interval = 1
            elif mem.repetitions == 1:
                interval = 6
            else:
                interval = mem.interval_days * mem.ease_factor
            mem.repetitions += 1
        else:
            # Failed recall — reset
            mem.repetitions = 0
            interval = 1

        # Update ease factor
        mem.ease_factor = max(
            self.MIN_EASE,
            mem.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )
        mem.interval_days = max(1, round(interval))

        # Update strength (0.0 → 1.0)
        total = mem.correct_count + mem.mistake_count
        if total > 0:
            accuracy = mem.correct_count / total
            repetition_bonus = min(0.3, mem.repetitions * 0.05)
            mem.strength = min(1.0, accuracy * 0.7 + repetition_bonus)

        mem.last_seen = datetime.utcnow()
        mem.next_review = datetime.utcnow() + timedelta(days=mem.interval_days)
        return mem

    async def get_weak_topics(
        self, db: AsyncSession, user_id: int, limit: int = 5
    ) -> List[WeakTopic]:
        """Get topics where the user struggles the most."""
        result = await db.execute(
            select(UserMemory).where(UserMemory.user_id == user_id)
            .order_by(UserMemory.strength.asc())
        )
        memories = result.scalars().all()

        weak = []
        for mem in memories:
            reason = ""
            if mem.strength < 0.4:
                reason = "low_strength"
            elif mem.mistake_count > mem.correct_count:
                reason = "frequent_mistakes"
            elif mem.confusion_count > 2:
                reason = "often_confused"
            else:
                continue

            weak.append(WeakTopic(
                topic=mem.topic,
                strength=round(mem.strength, 2),
                mistake_count=mem.mistake_count,
                reason=reason
            ))
            if len(weak) >= limit:
                break
        return weak

    async def get_due_reviews(
        self, db: AsyncSession, user_id: int
    ) -> List[ScheduledReview]:
        """Get topics that are due for spaced repetition review."""
        now = datetime.utcnow()
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.next_review <= now + timedelta(days=2),
                UserMemory.strength < 0.95  # Not fully mastered
            ).order_by(UserMemory.next_review.asc())
        )
        memories = result.scalars().all()

        reviews = []
        for mem in memories:
            if mem.next_review:
                overdue_days = max(0, (now - mem.next_review).days)
                if mem.next_review < now - timedelta(days=1):
                    priority = "urgent"
                elif mem.next_review.date() == now.date():
                    priority = "today"
                else:
                    priority = "upcoming"

                reviews.append(ScheduledReview(
                    topic=mem.topic,
                    subject=mem.subject,
                    due_date=mem.next_review.strftime("%Y-%m-%d"),
                    overdue_days=overdue_days,
                    strength=round(mem.strength, 2),
                    priority=priority
                ))
        return reviews

    async def get_overview(
        self, db: AsyncSession, user_id: int
    ) -> MemoryOverview:
        """Get complete memory overview for dashboard."""
        result = await db.execute(
            select(UserMemory).where(UserMemory.user_id == user_id)
        )
        memories = result.scalars().all()

        weak = await self.get_weak_topics(db, user_id)
        due = await self.get_due_reviews(db, user_id)

        mastered = [m.topic for m in memories if m.strength >= 0.85]
        avg_strength = (
            sum(m.strength for m in memories) / len(memories)
            if memories else 0.0
        )

        return MemoryOverview(
            weak_topics=weak,
            due_reviews=due,
            mastered_topics=mastered,
            total_topics_seen=len(memories),
            avg_strength=round(avg_strength, 2)
        )

    def get_memory_context(self, weak_topics: List[WeakTopic]) -> str:
        """Format memory context string for injection into prompts."""
        if not weak_topics:
            return ""
        topics_str = ", ".join([f"**{t.topic}**" for t in weak_topics[:3]])
        return f"[Memory: User struggles with {topics_str}. Focus on clarity and connect to prior mistakes.]"


memory_service = MemoryService()
