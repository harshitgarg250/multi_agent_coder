# test_coder_agent.py
from agents.coder import CoderAgent

if __name__ == "__main__":
    agent = CoderAgent()
    print("=== CoderAgent Test ===")
    task = "Write a Python function to reverse a string, with a small CLI to try it."
    code = agent.generate_code(task)
    print("\n--- Generated Code ---")
    print(code)
