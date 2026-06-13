# main_pipeline.py
# Orchestrates Planner -> Coder -> Tester -> Critic

from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.critic import CriticAgent

def run_pipeline(user_spec: str):
    planner = PlannerAgent()
    coder = CoderAgent()
    tester = TesterAgent()
    critic = CriticAgent()

    print("=== USER SPEC ===")
    print(user_spec)
    print()

    tasks = planner.plan_tasks(user_spec)

    print("=== PLANNED TASKS ===")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task}")
    print()

    for i, task in enumerate(tasks, start=1):
        print(f"=== TASK {i}: {task} ===")

        code = coder.generate_code(task)
        print("\n--- Generated Code ---")
        print(code)

        success, test_output = tester.run_code(code)
        print("\n--- Tester Result ---")
        print("Success:", success)
        print(test_output)

        review = critic.review_code(task, code)
        print("\n--- Critic Review ---")
        print(review)
        print("\n========================\n")

if __name__ == "__main__":
    spec = input("Enter your high-level coding request:\n> ")
    run_pipeline(spec)