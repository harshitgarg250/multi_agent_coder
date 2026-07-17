# main_pipeline.py
# Multi-agent self-correcting pipeline (CLI version):
# Planner -> Coder -> Tester -> Critic -> (loop back to Coder if not approved)

from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.critic import CriticAgent
from agents.security_critic import SecurityCriticAgent


def run_pipeline(user_query: str, input_data: str = "", max_iterations: int = 3):
    planner = PlannerAgent()
    coder = CoderAgent()
    tester = TesterAgent()
    critic = CriticAgent()
    security_critic = SecurityCriticAgent()

    tasks = planner.create_tasks(user_query)

    code = coder.generate_code(user_query)
    iterations = []

    for i in range(1, max_iterations + 1):
        clean_code = tester.clean_code(code)
        result = tester.run_code(code, input_data=input_data)
        critique = critic.review(user_query, clean_code, result)
        approved = critic.is_approved(critique)

        security_report = security_critic.scan(clean_code)
        security_passed = security_report.passed

        iterations.append({
            "iteration": i,
            "code": clean_code,
            "result": result,
            "critique": critique,
            "approved": approved,
            "security_report": security_report,
            "security_passed": security_passed,
        })

        if approved and result["success"] and security_passed:
            break

        if i < max_iterations:
            combined_feedback = critique
            if not security_passed:
                combined_feedback += (
                    "\n\nSECURITY ISSUES (must fix):\n" + security_report.summary()
                )
            code = coder.generate_code(user_query, previous_code=clean_code, critique=combined_feedback)

    return tasks, iterations


if __name__ == "__main__":
    query = input("Enter your coding request: ").strip()
    sample_input = input("Sample stdin input (optional): ").strip() + "\n"

    tasks, iterations = run_pipeline(query, input_data=sample_input)

    print("\n--- PLANNED TASKS ---")
    for i, t in enumerate(tasks, start=1):
        print(f"{i}. {t}")

    for step in iterations:
        print(f"\n=== ITERATION {step['iteration']} ===")
        print("\n--- CODE ---")
        print(step["code"])
        print("\n--- EXECUTION ---")
        print("Success:", step["result"]["success"], "| Exit code:", step["result"]["exit_code"])
        if step["result"]["stdout"]:
            print("stdout:", step["result"]["stdout"].strip())
        if step["result"]["stderr"]:
            print("stderr:", step["result"]["stderr"].strip())
        print("\n--- CRITIC ---")
        print(step["critique"])
        print("Approved:", step["approved"])
        print("\n--- SECURITY SCAN ---")
        print(step["security_report"].summary())
        print("Security passed:", step["security_passed"])

    final = iterations[-1]
    print("\n--- FINAL RESULT ---")
    print("Approved after", len(iterations), "iteration(s):", final["approved"])
    print("Security clean:", final["security_passed"])
