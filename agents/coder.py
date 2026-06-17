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

Write ONE complete Python script that solves the TASK.

Very important rules:
- Follow the TASK exactly, do not invent extra features.
- Do NOT build a calculator or REPL unless the task explicitly says so.
- Return ONLY Python code.
- Do NOT include markdown fences.
- Do NOT include explanations, comments, or docstrings.
- Do NOT include assert statements or tests.
- If input is needed, read it once using input().
- Handle invalid input with clear error messages and exit.

TASK:
{task}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()