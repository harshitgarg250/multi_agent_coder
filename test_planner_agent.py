# test_planner_agent.py
# PlannerAgent calls the LLM, so we mock agents.planner.chat instead of
# hitting the real Groq API. This keeps tests fast, free, and runnable
# in CI without an API key.

from agents.planner import PlannerAgent


def test_create_tasks_parses_numbered_list(monkeypatch):
    fake_response = (
        "1. Write a function to validate the input string\n"
        "2. Implement the palindrome check ignoring spaces and case\n"
        "3. Add a small CLI to test the function"
    )
    monkeypatch.setattr("agents.planner.chat", lambda *a, **k: fake_response)

    agent = PlannerAgent()
    tasks = agent.create_tasks("Check if a string is a palindrome")

    assert len(tasks) == 3
    assert tasks[0] == "Write a function to validate the input string"
    assert tasks[2] == "Add a small CLI to test the function"


def test_create_tasks_strips_bullet_characters(monkeypatch):
    fake_response = "- Task one\n) Task two\n. Task three"
    monkeypatch.setattr("agents.planner.chat", lambda *a, **k: fake_response)

    agent = PlannerAgent()
    tasks = agent.create_tasks("Some spec")

    assert "Task one" in tasks
    assert "Task two" in tasks
    assert "Task three" in tasks


def test_create_tasks_falls_back_to_spec_when_empty(monkeypatch):
    monkeypatch.setattr("agents.planner.chat", lambda *a, **k: "")

    agent = PlannerAgent()
    spec = "Build a calculator"
    tasks = agent.create_tasks(spec)

    assert tasks == [spec]


def test_create_tasks_ignores_blank_lines(monkeypatch):
    fake_response = "1. First task\n\n\n2. Second task\n"
    monkeypatch.setattr("agents.planner.chat", lambda *a, **k: fake_response)

    agent = PlannerAgent()
    tasks = agent.create_tasks("Some spec")

    assert tasks == ["First task", "Second task"]
