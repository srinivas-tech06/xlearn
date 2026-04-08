"""
Decision Agent — Decides the next best action based on student state.
"""


class DecisionAgent:
    def decide(self, state: dict, context: dict = None) -> str:
        """
        Analyze state and decide action:
        EXPLAIN, QUIZ, RETEACH, CHALLENGE, REVISE, MOTIVATE
        """
        understanding = state.get("understanding", 50)
        confidence = state.get("confidence", 50)
        engagement = state.get("engagement", 70)
        retention = state.get("retention", 50)

        context = context or {}
        is_new_topic = context.get("is_new_topic", True)
        last_action = context.get("last_action", None)

        # Priority-based decision tree
        if confidence < 30:
            return "MOTIVATE"

        if is_new_topic or (understanding < 30 and last_action != "RETEACH"):
            return "EXPLAIN"

        if understanding < 40:
            return "RETEACH"

        if retention < 40 and last_action != "REVISE":
            return "REVISE"

        if understanding > 85 and confidence > 80:
            return "CHALLENGE"

        if 40 <= understanding <= 75:
            return "QUIZ"

        if understanding > 75 and retention > 60:
            return "CHALLENGE"

        # Default progression
        if last_action == "EXPLAIN":
            return "QUIZ"
        elif last_action == "QUIZ":
            return "EXPLAIN"

        return "EXPLAIN"

    def get_action_description(self, action: str) -> str:
        descriptions = {
            "EXPLAIN": "Teaching you a new concept with clear explanations",
            "QUIZ": "Testing your understanding with a quick question",
            "RETEACH": "Let's try a different approach to help you understand",
            "CHALLENGE": "You're doing great! Here's an advanced challenge",
            "REVISE": "Time for a quick review to strengthen your memory",
            "MOTIVATE": "A little encouragement to boost your confidence"
        }
        return descriptions.get(action, "Continuing your learning journey")


decision_agent = DecisionAgent()
