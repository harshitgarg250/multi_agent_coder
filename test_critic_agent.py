# test_critic_agent.py
from agents.critic import CriticAgent

if __name__ == "__main__":
    agent = CriticAgent()
    print("=== CriticAgent Test ===")
    task = "Write a Python function to reverse a string"
    code = "def reverse_string(s):\n    return s[::-1]"
    review = agent.review(task, code)
    print("\n--- Review ---")
    print(review)
    print("Approved:", agent.is_approved(review))
