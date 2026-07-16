# test_tester_agent.py
# Real pytest assertions for TesterAgent. No mocking needed here since
# TesterAgent only runs subprocess code locally — no LLM calls involved.

from agents.tester import TesterAgent


def test_successful_code_execution():
    agent = TesterAgent()
    code = "print(2 + 3)"
    result = agent.run_code(code)

    assert result["success"] is True
    assert result["exit_code"] == 0
    assert "5" in result["stdout"]
    assert result["stderr"] == ""


def test_failing_code_execution():
    agent = TesterAgent()
    code = "1 / 0"
    result = agent.run_code(code)

    assert result["success"] is False
    assert result["exit_code"] != 0
    assert "ZeroDivisionError" in result["stderr"]


def test_reads_stdin_input():
    agent = TesterAgent()
    code = "name = input()\nprint(f'Hello, {name}!')"
    result = agent.run_code(code, input_data="World\n")

    assert result["success"] is True
    assert "Hello, World!" in result["stdout"]


def test_timeout_is_handled():
    agent = TesterAgent()
    code = "import time\ntime.sleep(30)"
    result = agent.run_code(code)

    assert result["success"] is False
    assert result["exit_code"] is None
    assert "timed out" in result["stderr"].lower()


def test_clean_code_strips_markdown_fences():
    agent = TesterAgent()
    fenced_code = "```python\nprint('hello')\n```"
    cleaned = agent.clean_code(fenced_code)

    assert cleaned == "print('hello')"
    assert "```" not in cleaned


def test_clean_code_leaves_plain_code_unchanged():
    agent = TesterAgent()
    plain_code = "print('hello')"
    cleaned = agent.clean_code(plain_code)

    assert cleaned == "print('hello')"
