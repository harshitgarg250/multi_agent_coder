# test_tester_agent.py

from agents.tester import TesterAgent

if __name__ == "__main__":
    agent = TesterAgent()

    print("=== TesterAgent Test (PASS case) ===")
    code_ok = """
def add(a, b):
    return a + b

print(add(2, 3))
"""
    success, output = agent.run_code(code_ok)
    print("Success:", success)
    print("Output:\n", output)

    print("\n=== TesterAgent Test (FAIL case) ===")
    code_fail = """
def divide(a, b):
    return a / b

print(divide(1, 0))
"""
    success2, output2 = agent.run_code(code_fail)
    print("Success:", success2)
    print("Output:\n", output2)