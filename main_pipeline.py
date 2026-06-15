from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.critic import CriticAgent

def run_simple_pipeline(user_query: str):
    coder = CoderAgent()
    tester = TesterAgent()
    critic = CriticAgent()

    prompt = f"""
Write ONE complete Python script that fulfills this requirement:

{user_query}

Rules:
- Read numbers from user input (single line, space separated).
- Handle invalid (non-numeric) values gracefully.
- If no valid numbers are provided, print a clear message and exit.
- Compute and print average, minimum, and maximum of the valid numbers.
- Do NOT include markdown fences or explanations. Only Python code.
- Do NOT add assert statements.
"""

    code = coder.generate_code(prompt)
    print("\n--- GENERATED FULL SCRIPT ---")
    print(code)

    # Run tests with valid input
    test_result = tester.run_code(code, input_data="1 2 3 4 5\n")
    
    # Run test with edge case: empty input
    empty_test = tester.run_code(code, input_data="\n")
    
    # Run test with invalid input
    invalid_test = tester.run_code(code, input_data="a b c\n")

    print("\n--- TEST RESULTS ---")
    print("\n[Test 1] Valid input (1 2 3 4 5):")
    print("Success:", test_result["success"])
    print("Exit Code:", test_result["exit_code"])
    if test_result["stdout"]:
        print("Output:", test_result["stdout"].strip())
    if test_result["stderr"]:
        print("Errors:", test_result["stderr"].strip())

    print("\n[Test 2] Empty input:")
    print("Success:", empty_test["success"])
    print("Exit Code:", empty_test["exit_code"])
    if empty_test["stdout"]:
        print("Output:", empty_test["stdout"].strip())
    if empty_test["stderr"]:
        print("Errors:", empty_test["stderr"].strip())

    print("\n[Test 3] Invalid input (a b c):")
    print("Success:", invalid_test["success"])
    print("Exit Code:", invalid_test["exit_code"])
    if invalid_test["stdout"]:
        print("Output:", invalid_test["stdout"].strip())
    if invalid_test["stderr"]:
        print("Errors:", invalid_test["stderr"].strip())

    # Overall success: all tests should pass
    all_pass = test_result["success"] and empty_test["success"] and invalid_test["success"]
    print("\n--- OVERALL RESULT ---")
    print("All Tests Passed:", all_pass)
    
    # Code review
    print("\n--- CODE REVIEW ---")
    review = critic.review(user_query, code)
    print(review)

if __name__ == "__main__":
    query = input("Enter your coding request: ").strip()
    run_simple_pipeline(query)