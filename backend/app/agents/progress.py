"""
Progress Agent — Tracks daily progress, streaks, and generates next-day plans.
"""
from datetime import date, timedelta


class ProgressAgent:
    def track(self, session_data: dict, current_progress: dict) -> dict:
        """
        Update daily progress with session data.
        session_data: {xp_earned, topics_covered, quiz_taken, quiz_correct, time_minutes}
        """
        progress = {
            "date": str(date.today()),
            "sessions_completed": current_progress.get("sessions_completed", 0) + 1,
            "xp_earned": current_progress.get("xp_earned", 0) + session_data.get("xp_earned", 0),
            "topics_covered": current_progress.get("topics_covered", 0) + session_data.get("topics_covered", 0),
            "quizzes_taken": current_progress.get("quizzes_taken", 0) + (1 if session_data.get("quiz_taken") else 0),
            "quizzes_correct": current_progress.get("quizzes_correct", 0) + (1 if session_data.get("quiz_correct") else 0),
            "time_spent_minutes": current_progress.get("time_spent_minutes", 0) + session_data.get("time_minutes", 5),
        }

        # Calculate completion level (0-100)
        daily_xp_goal = 100
        progress["completion_level"] = min(100, (progress["xp_earned"] / daily_xp_goal) * 100)

        return progress

    def calculate_streak(self, daily_records: list) -> int:
        """Calculate consecutive learning days streak."""
        if not daily_records:
            return 0

        today = date.today()
        streak = 0

        for i in range(len(daily_records)):
            check_date = today - timedelta(days=i)
            if any(r.get("date") == str(check_date) and r.get("sessions_completed", 0) > 0
                   for r in daily_records):
                streak += 1
            else:
                break

        return streak

    def plan_next_day(self, state: dict, roadmap: dict) -> dict:
        """Generate a learning plan for the next session."""
        understanding = state.get("understanding", 50)
        retention = state.get("retention", 50)

        tasks = []

        if retention < 50:
            tasks.append({
                "type": "revision",
                "title": "Quick Review",
                "description": "Review previous concepts to strengthen retention",
                "priority": "high",
                "estimated_minutes": 10
            })

        tasks.append({
            "type": "learn",
            "title": "New Material",
            "description": "Continue learning from your roadmap",
            "priority": "medium",
            "estimated_minutes": 20
        })

        tasks.append({
            "type": "practice",
            "title": "Practice Quiz",
            "description": "Test your understanding with questions",
            "priority": "medium",
            "estimated_minutes": 10
        })

        if understanding > 70:
            tasks.append({
                "type": "challenge",
                "title": "Challenge Mode",
                "description": "Push your limits with advanced problems",
                "priority": "low",
                "estimated_minutes": 15
            })

        return {
            "date": str(date.today() + timedelta(days=1)),
            "tasks": tasks,
            "estimated_total_minutes": sum(t["estimated_minutes"] for t in tasks),
            "xp_potential": len(tasks) * 25
        }


progress_agent = ProgressAgent()
