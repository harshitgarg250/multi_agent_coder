# test_planner_agent.py
from agents.planner import PlannerAgent

if __name__ == "__main__":
    agent = PlannerAgent()
    print("=== PlannerAgent Test ===")
    spec = "Build a Python function to check whether a string is a palindrome and write tests for it."
    tasks = agent.create_tasks(spec)
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task}")
