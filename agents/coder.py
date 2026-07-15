# agents/coder.py
# Coder Agent - generates AND revises Python code.
# Generalized: no longer hardcoded to one task type. Supports a
# "revision mode" where it fixes its own previous output using
# the Critic's feedback (this is what makes the pipeline "multi-agent").

from agents.llm_client import chat


class CoderAgent:
    def generate_code(
        self,
        task: str,
        previous_code: str | None = None,
        critique: str | None = None,
    ) -> str:
        """
        task: natural-language coding task
        previous_code / critique: if provided, the agent revises its
            earlier attempt instead of starting from scratch.
        """
        if previous_code and critique:
            prompt = f"""You are a senior Python developer revising your own code
based on a code review.

Original task:
{task}

Your previous code:
{previous_code}

Reviewer feedback:
{critique}

Rewrite the COMPLETE corrected Python script, addressing every point
in the feedback. Keep what already worked.

Rules:
- Return ONLY Python code. No markdown fences, no explanations.
- Handle invalid/empty input gracefully with a clear message.
"""
        else:
            prompt = f"""You are a senior Python developer.

Write ONE complete, general-purpose Python script that solves this task:
{task}

Rules:
- Return ONLY Python code. No markdown fences, no explanations.
- If the task needs input, read it from stdin.
- Handle invalid or empty input gracefully with a clear message.
- Keep the code clean, idiomatic, and reasonably commented.
"""
        return chat(prompt).strip()
