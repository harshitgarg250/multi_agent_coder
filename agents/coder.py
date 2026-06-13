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
You are a senior software engineer.

Your job:
- Write Python code that completes the TASK below.
- Return ONLY Python code.
- Do NOT include markdown fences (no ```).
- Do NOT include explanations, comments outside code, or alternative versions.
- Do NOT print example calls unless the TASK explicitly asks for them.
- Make sure the code is syntactically valid and can run as-is.

TASK:
{task}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()