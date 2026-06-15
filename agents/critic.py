# agents/critic.py
# Critic Agent using Ollama

import ollama

MODEL_NAME = "llama3.2"

class CriticAgent:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def review(self, task: str, code: str, test_result: dict | None = None) -> str:
        prompt = f"""
You are a strict code reviewer.

Task:
{task}

Code:
{code}

Return 3-5 short bullet points.
Mention bugs, missing edge cases, or say if it looks good.
Do not add extra explanation outside the bullets.
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()