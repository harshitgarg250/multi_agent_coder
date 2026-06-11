from agents.planner import PlannerAgent

if __name__ == "__main__":
    agent = PlannerAgent()

    print("=== PlannerAgent Test ===")
    spec = "Build a Python function to check whether a string is a palindrome and write tests for it."
    tasks = agent.plan_tasks(spec)

    print("\n--- Planned Tasks ---")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task}")

    print("\n=== End ===")