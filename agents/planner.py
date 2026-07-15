# agents/planner.py
# Planner Agent - breaks a user request into concrete coding sub-tasks.

from agents.llm_client import chat


class PlannerAgent:
    def create_tasks(self, spec: str) -> list[str]:
        prompt = f"""You are a planning agent for a software team.

Break the user's coding request into 2-4 clear, concrete implementation tasks.

User request:
{spec}

Return ONLY a numbered list, one task per line. No extra text.
"""
        text = chat(prompt)
        lines = text.splitlines()

        tasks = []
        for line in lines:
            cleaned = line.lstrip(" 0123456789.)-").strip()
            if cleaned:
                tasks.append(cleaned)

        return tasks or [spec]
