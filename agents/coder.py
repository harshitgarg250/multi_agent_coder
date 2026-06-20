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

Write ONE complete Python script for the TASK.

Rules:
- Return ONLY Python code.
- Do NOT use map() for stored values.
- Do NOT use iterators when you need len(), indexing, min(), or max().
- Convert input into a list of integers.
- Handle empty input gracefully.
- Handle invalid input with a clear error message.
- Print average, minimum, and maximum.
- Do NOT include markdown fences.
- Do NOT include explanations or tests.

TASK:
{task}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()