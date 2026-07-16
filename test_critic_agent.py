# test_critic_agent.py
# CriticAgent calls the LLM, so agents.critic.chat is mocked.
# is_approved() is a pure function so it's tested directly with no mocking.

from agents.critic import CriticAgent


def test_review_returns_approved_when_llm_approves(monkeypatch):
    monkeypatch.setattr(
        "agents.critic.chat",
        lambda *a, **k: "APPROVED\nThe code correctly reverses the string.",
    )

    agent = CriticAgent()
    review = agent.review("Reverse a string", "def f(s): return s[::-1]")

    assert agent.is_approved(review)


def test_review_returns_needs_fix_when_llm_flags_issue(monkeypatch):
    monkeypatch.setattr(
        "agents.critic.chat",
        lambda *a, **k: "NEEDS_FIX\n- Does not handle None input\n- Missing docstring",
    )

    agent = CriticAgent()
    review = agent.review("Reverse a string", "def f(s): return s[::-1]")

    assert not agent.is_approved(review)


def test_review_includes_test_result_summary_in_prompt(monkeypatch):
    captured_prompt = {}

    def fake_chat(prompt, *a, **k):
        captured_prompt["value"] = prompt
        return "APPROVED\nLooks good."

    monkeypatch.setattr("agents.critic.chat", fake_chat)

    agent = CriticAgent()
    test_result = {"success": False, "exit_code": 1, "stderr": "IndexError: list index out of range"}
    agent.review("Some task", "some code", test_result)

    prompt = captured_prompt["value"]
    assert "success=False" in prompt
    assert "IndexError" in prompt


def test_is_approved_is_case_insensitive():
    agent = CriticAgent()
    assert agent.is_approved("approved\nGreat job.")
    assert agent.is_approved("  APPROVED - looks correct")
    assert not agent.is_approved("NEEDS_FIX\n- bug here")
    assert not agent.is_approved("Not sure about this one")
