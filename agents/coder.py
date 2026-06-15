# agents/coder.py
# Coder Agent using Ollama (llama3.2)

import ollama

MODEL_NAME = "llama3.2"

class CoderAgent:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def generate_code(self, task: str) -> str:
        """
        task: a single coding task in natural language
        return: Python code as plain text (no markdown, no explanations)
        """
        prompt = f"""
You are a senior Python developer.

Write ONE complete Python script for this TASK.

Rules:
- Return ONLY Python code.
- Do NOT include markdown fences.
- Do NOT include comments outside code.
- Do NOT add assert statements at the bottom.
- Do NOT add demo test values unless the task explicitly asks for them.
- The script must read input from the user if needed.
- Handle invalid input gracefully.
- The code should be correct for the given task.

TASK:
{task}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()