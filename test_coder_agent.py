# test_coder_agent.py

from agents.coder import CoderAgent

if __name__ == "__main__":
    agent = CoderAgent()

    print("=== CoderAgent Test ===")
    user_task = "Write a Python function to reverse a string"
    code = agent.generate_code(user_task)

    print("\n--- Generated Code ---")
    print(code)
    print("\n=== End ===")