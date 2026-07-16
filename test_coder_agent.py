# test_coder_agent.py
# CoderAgent calls the LLM, so agents.coder.chat is mocked.

from agents.coder import CoderAgent


def test_generate_code_first_attempt_returns_llm_output(monkeypatch):
    fake_code = "def reverse_string(s):\n    return s[::-1]"
    monkeypatch.setattr("agents.coder.chat", lambda *a, **k: fake_code)

    agent = CoderAgent()
    code = agent.generate_code("Write a function to reverse a string")

    assert code == fake_code


def test_generate_code_uses_revision_prompt_when_critique_given(monkeypatch):
    captured_prompt = {}

    def fake_chat(prompt, *a, **k):
        captured_prompt["value"] = prompt
        return "def reverse_string(s):\n    return s[::-1] if s else ''"

    monkeypatch.setattr("agents.coder.chat", fake_chat)

    agent = CoderAgent()
    agent.generate_code(
        task="Write a function to reverse a string",
        previous_code="def reverse_string(s):\n    return s[::-1]",
        critique="NEEDS_FIX\n- Does not handle empty string input",
    )

    prompt = captured_prompt["value"]
    assert "revising your own code" in prompt
    assert "Does not handle empty string input" in prompt


def test_generate_code_without_critique_uses_fresh_prompt(monkeypatch):
    captured_prompt = {}

    def fake_chat(prompt, *a, **k):
        captured_prompt["value"] = prompt
        return "print('hello')"

    monkeypatch.setattr("agents.coder.chat", fake_chat)

    agent = CoderAgent()
    agent.generate_code(task="Print hello")

    prompt = captured_prompt["value"]
    assert "senior Python developer" in prompt
    assert "revising" not in prompt


def test_generate_code_strips_whitespace(monkeypatch):
    monkeypatch.setattr("agents.coder.chat", lambda *a, **k: "  print(1)  \n")

    agent = CoderAgent()
    code = agent.generate_code("Print 1")

    assert code == "print(1)"
