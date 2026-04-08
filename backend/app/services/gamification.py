"""
Gamification Service — XP, levels, badges, and streaks.
"""

LEVEL_TITLES = {
    1: "Novice",
    2: "Apprentice",
    3: "Scholar",
    4: "Practitioner",
    5: "Expert",
    6: "Master",
    7: "Grandmaster",
    8: "Legend",
}

BADGE_DEFINITIONS = [
    {"id": "first_step", "name": "First Step", "icon": "🚀", "description": "Started your learning journey", "condition": "sessions >= 1"},
    {"id": "streak_3", "name": "On Fire", "icon": "🔥", "description": "3-day learning streak", "condition": "streak >= 3"},
    {"id": "streak_7", "name": "Week Warrior", "icon": "⚡", "description": "7-day learning streak", "condition": "streak >= 7"},
    {"id": "streak_30", "name": "Unstoppable", "icon": "💎", "description": "30-day learning streak", "condition": "streak >= 30"},
    {"id": "quiz_master", "name": "Quiz Master", "icon": "🎯", "description": "10 quizzes answered correctly", "condition": "correct_quizzes >= 10"},
    {"id": "perfect_quiz", "name": "Perfect Score", "icon": "💯", "description": "Got 100% on a quiz", "condition": "perfect_quiz"},
    {"id": "first_module", "name": "Module Complete", "icon": "📚", "description": "Completed your first module", "condition": "modules_completed >= 1"},
    {"id": "ten_concepts", "name": "Knowledge Seeker", "icon": "💡", "description": "Learned 10 concepts", "condition": "topics_completed >= 10"},
    {"id": "challenger", "name": "Challenge Champion", "icon": "🏆", "description": "Completed 5 challenges", "condition": "challenges >= 5"},
    {"id": "xp_500", "name": "Rising Star", "icon": "⭐", "description": "Earned 500 XP", "condition": "xp >= 500"},
    {"id": "xp_1000", "name": "Shining Bright", "icon": "🌟", "description": "Earned 1000 XP", "condition": "xp >= 1000"},
]

XP_PER_LEVEL = 100


class GamificationService:
    def calculate_level(self, xp: int) -> int:
        return max(1, (xp // XP_PER_LEVEL) + 1)

    def get_level_title(self, level: int) -> str:
        if level >= 8:
            return LEVEL_TITLES[8]
        return LEVEL_TITLES.get(level, "Novice")

    def xp_to_next_level(self, xp: int) -> int:
        current_level = self.calculate_level(xp)
        next_level_xp = current_level * XP_PER_LEVEL
        return next_level_xp - xp

    def xp_progress_percent(self, xp: int) -> float:
        xp_in_level = xp % XP_PER_LEVEL
        return (xp_in_level / XP_PER_LEVEL) * 100

    def check_badges(self, user_stats: dict) -> list:
        """Check which badges the user has earned."""
        earned = []
        xp = user_stats.get("xp", 0)
        streak = user_stats.get("streak", 0)
        sessions = user_stats.get("total_sessions", 0)
        correct_quizzes = user_stats.get("correct_quizzes", 0)
        topics_completed = user_stats.get("topics_completed", 0)
        modules_completed = user_stats.get("modules_completed", 0)
        challenges = user_stats.get("challenges", 0)
        perfect_quiz = user_stats.get("perfect_quiz", False)

        for badge in BADGE_DEFINITIONS:
            condition = badge["condition"]
            if self._evaluate_condition(condition, locals()):
                earned.append({
                    "id": badge["id"],
                    "name": badge["name"],
                    "icon": badge["icon"],
                    "description": badge["description"],
                    "earned": True
                })

        return earned

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except Exception:
            return False

    def award_xp(self, action: str, is_correct: bool = True) -> int:
        """Calculate XP to award for an action."""
        xp_table = {
            "EXPLAIN": 5,
            "QUIZ_CORRECT": 15,
            "QUIZ_WRONG": 2,
            "CHALLENGE": 25,
            "REVISE": 5,
            "RETEACH": 5,
            "MOTIVATE": 5,
            "MODULE_COMPLETE": 50,
            "STREAK_BONUS": 10,
        }
        return xp_table.get(action, 5)


gamification_service = GamificationService()
