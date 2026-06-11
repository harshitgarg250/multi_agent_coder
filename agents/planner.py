# agents/planner.py
# Planner Agent using Ollama

import ollama

MODEL_NAME = "llama3.2"

class PlannerAgent:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def plan_tasks(self, spec: str) -> list[str]:
        prompt = f"""
You are a planning agent. Break the user's coding request into 2-4 clear coding tasks.

User request:
{spec}

Return only a numbered list, one task per line.
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"].strip()
        lines = text.splitlines()

        tasks = []
        for line in lines:
            cleaned = line.lstrip(" 0123456789.)-").strip()
            if cleaned:
                tasks.append(cleaned)

        return tasks