# test_security_critic_agent.py
# Real pytest-based tests (not print-based) for the SecurityCriticAgent.
# Run with: pytest test_security_critic_agent.py -v

from agents.security_critic import SecurityCriticAgent


def test_detects_hardcoded_api_key():
    code = 'GROQ_API_KEY = "gsk_abcdefghij1234567890ABCDEFG"\n'
    report = SecurityCriticAgent().scan(code)
    assert not report.passed
    assert any(f.rule == "hardcoded-secret" for f in report.findings)


def test_detects_eval_usage():
    code = "user_input = input()\nresult = eval(user_input)\n"
    report = SecurityCriticAgent().scan(code)
    assert not report.passed
    assert any(f.rule == "dangerous-builtin" for f in report.findings)


def test_detects_shell_true():
    code = (
        "import subprocess\n"
        "subprocess.run(user_cmd, shell=True)\n"
    )
    report = SecurityCriticAgent().scan(code)
    assert not report.passed
    assert any(f.rule == "shell-injection-risk" for f in report.findings)


def test_detects_sql_injection_risk():
    code = (
        "def get_user(cursor, name):\n"
        "    cursor.execute(f\"SELECT * FROM users WHERE name = '{name}'\")\n"
    )
    report = SecurityCriticAgent().scan(code)
    assert not report.passed
    assert any(f.rule == "sql-injection-risk" for f in report.findings)


def test_clean_code_passes():
    code = (
        "def add(a, b):\n"
        "    '''Add two numbers.'''\n"
        "    return a + b\n"
    )
    report = SecurityCriticAgent().scan(code)
    assert report.passed
    assert report.findings == []


def test_parameterized_query_does_not_trigger_false_positive():
    code = (
        "def get_user(cursor, name):\n"
        "    cursor.execute(\"SELECT * FROM users WHERE name = ?\", (name,))\n"
    )
    report = SecurityCriticAgent().scan(code)
    assert report.passed
