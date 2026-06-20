import streamlit as st
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.planner import PlannerAgent
from agents.critic import CriticAgent


def run_pipeline(user_query: str, input_data: str):
    planner = PlannerAgent()
    coder = CoderAgent()
    tester = TesterAgent()
    critic = CriticAgent()

    tasks = planner.create_tasks(user_query)
    code = coder.generate_code(user_query)
    result = tester.run_code(code, input_data=input_data)
    critique = critic.review(user_query, code, result)

    return tasks, code, result, critique


st.title("Multi-Agent Coding Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.text_area("Describe your coding task:")
user_input_data = st.text_input("Sample input for your script (optional):", "1 2 3 4 5")

if st.button("Run"):
    with st.spinner("Planning, generating, running, and reviewing code..."):
        tasks, code, result, critique = run_pipeline(
            user_query,
            input_data=user_input_data + "\n"
        )

    st.subheader("Planned Tasks")
    for i, t in enumerate(tasks, start=1):
        st.write(f"{i}. {t}")

    st.subheader("Generated Code")
    st.code(code, language="python")

    st.download_button(
        label="Download Generated Code",
        data=code,
        file_name="generated_code.py",
        mime="text/x-python"
    )

    st.subheader("Execution Result")
    if result["success"] and result["exit_code"] == 0:
        st.success("Execution passed")
    else:
        st.error("Execution failed")

    st.write("Exit code:", result["exit_code"])

    if result["stdout"]:
        st.text_area("STDOUT", result["stdout"], height=150)
    if result["stderr"]:
        st.text_area("STDERR", result["stderr"], height=150)

    st.subheader("Critic Feedback")
    st.write(critique)

    st.session_state.history.append({
        "task": user_query,
        "input": user_input_data,
        "code": code,
        "success": result["success"],
        "exit_code": result["exit_code"],
        "critique": critique,
    })

st.subheader("Run History")
for i, item in enumerate(reversed(st.session_state.history), start=1):
    st.markdown(f"**{i}.** {item['task']}")
    st.write(f"Success: {item['success']} | Exit code: {item['exit_code']}")
    st.write(item["critique"])
    st.divider()