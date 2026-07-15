# test_tester_agent.py
from agents.tester import TesterAgent

if __name__ == "__main__":
    agent = TesterAgent()

    print("=== TesterAgent Test (PASS case) ===")
    code_ok = "def add(a, b):\n    return a + b\n\nprint(add(2, 3))"
    result = agent.run_code(code_ok)
    print(result)

    print("\n=== TesterAgent Test (FAIL case) ===")
    code_fail = "def divide(a, b):\n    return a / b\n\nprint(divide(1, 0))"
    result2 = agent.run_code(code_fail)
    print(result2)
