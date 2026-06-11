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
        return: code-only string
        """
        prompt = f"""
You are a coding assistant. Generate clean, working code.

Task:
{task}

Rules:
- Only generate code.
- Use Python by default unless specified.
- Add short comments in code.
- Do not add explanation outside the code.
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()