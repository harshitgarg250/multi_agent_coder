from agents.critic import CriticAgent

if __name__ == "__main__":
    agent = CriticAgent()

    print("=== CriticAgent Test ===")
    task = "Write a Python function to reverse a string"
    code = """def reverse_string(s):
    # Use slicing to reverse the input string
    return s[::-1]"""

    review = agent.review_code(task, code)

    print("\n--- Review ---")
    print(review)
    print("\n=== End ===")