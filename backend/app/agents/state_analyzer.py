"""
State Analyzer Agent — Maintains and updates student learning metrics.
"""


class StateAnalyzerAgent:
    def analyze(self, interaction: dict, current_state: dict) -> dict:
        """
        Update student state based on interaction data.
        interaction: {type, score, time_taken, hesitation, engagement_signals}
        current_state: {understanding, confidence, engagement, retention}
        """
        state = {
            "understanding": current_state.get("understanding", 50.0),
            "confidence": current_state.get("confidence", 50.0),
            "engagement": current_state.get("engagement", 70.0),
            "retention": current_state.get("retention", 50.0),
        }

        interaction_type = interaction.get("type", "chat")
        score = interaction.get("score", None)

        if interaction_type == "quiz":
            if score is not None:
                if score >= 80:
                    state["understanding"] = min(100, state["understanding"] + 8)
                    state["confidence"] = min(100, state["confidence"] + 10)
                    state["retention"] = min(100, state["retention"] + 5)
                elif score >= 50:
                    state["understanding"] = min(100, state["understanding"] + 3)
                    state["confidence"] = min(100, state["confidence"] + 2)
                    state["retention"] = min(100, state["retention"] + 2)
                else:
                    state["understanding"] = max(0, state["understanding"] - 5)
                    state["confidence"] = max(0, state["confidence"] - 8)
                    state["retention"] = max(0, state["retention"] - 3)

        elif interaction_type == "chat":
            state["engagement"] = min(100, state["engagement"] + 3)
            state["understanding"] = min(100, state["understanding"] + 1)

        elif interaction_type == "challenge":
            if score and score >= 70:
                state["understanding"] = min(100, state["understanding"] + 12)
                state["confidence"] = min(100, state["confidence"] + 15)
                state["retention"] = min(100, state["retention"] + 8)
            else:
                state["confidence"] = max(0, state["confidence"] - 3)

        elif interaction_type == "revision":
            state["retention"] = min(100, state["retention"] + 10)
            state["understanding"] = min(100, state["understanding"] + 3)

        # Engagement decay prevention
        if interaction.get("consecutive_sessions", 0) > 0:
            state["engagement"] = min(100, state["engagement"] + 2)

        # Natural decay (slight) for retention to simulate forgetting curve
        state["retention"] = max(0, state["retention"] - 0.5)

        # Round all values
        for key in state:
            state[key] = round(state[key], 1)

        return state

    def get_difficulty_recommendation(self, state: dict) -> int:
        """Return recommended difficulty level (1-3) based on state."""
        understanding = state.get("understanding", 50)
        confidence = state.get("confidence", 50)
        avg = (understanding + confidence) / 2

        if avg > 75:
            return 3  # hard
        elif avg > 40:
            return 2  # medium
        else:
            return 1  # easy


state_analyzer_agent = StateAnalyzerAgent()
