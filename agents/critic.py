# agents/critic.py
# Critic Agent - reviews code and decides APPROVED vs NEEDS_FIX.
# The verdict word is what drives the self-correction loop in the pipeline.

from agents.llm_client import chat


class CriticAgent:
    def review(self, task: str, code: str, test_result: dict | None = None) -> str:
        test_summary = ""
        if test_result is not None:
            test_summary = (
                f"\nExecution result: success={test_result.get('success')}, "
                f"exit_code={test_result.get('exit_code')}\n"
                f"stderr: {test_result.get('stderr', '')[:300]}"
            )

        prompt = f"""You are a strict senior code reviewer.

Task:
{task}

Code:
{code}
{test_summary}

Decide if this code correctly and robustly solves the task.

- If YES: start your reply with the single word APPROVED, then 1-2
  sentences justifying it.
- If NO: start your reply with the single word NEEDS_FIX, then 3-5
  short bullet points describing the bugs, missing edge cases, or
  runtime errors that must be fixed.
"""
        return chat(prompt)

    def is_approved(self, review_text: str) -> bool:
        return review_text.strip().upper().startswith("APPROVED")
