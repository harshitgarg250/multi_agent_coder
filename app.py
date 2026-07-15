import streamlit as st
from main_pipeline import run_pipeline

st.set_page_config(page_title="Multi-Agent Coding Assistant", layout="wide")
st.title("Multi-Agent Coding Assistant")
st.caption("Planner -> Coder -> Tester -> Critic, with self-correction loop")

if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.text_area("Describe your coding task:")
user_input_data = st.text_input("Sample input for your script (optional):", "1 2 3 4 5")
max_iterations = st.slider("Max self-correction attempts", 1, 5, 3)

if st.button("Run"):
    with st.spinner("Planning, generating, running, and reviewing code..."):
        tasks, iterations = run_pipeline(
            user_query,
            input_data=user_input_data + "\n",
            max_iterations=max_iterations,
        )

    st.subheader("Planned Tasks")
    for i, t in enumerate(tasks, start=1):
        st.write(f"{i}. {t}")

    st.subheader(f"Agent Iterations ({len(iterations)})")
    for step in iterations:
        status = "APPROVED" if (step["approved"] and step["security_passed"]) else "NEEDS FIX"
        label = f"Iteration {step['iteration']} - {status}"
        with st.expander(label, expanded=(step is iterations[-1])):
            st.code(step["code"], language="python")

            if step["result"]["success"] and step["result"]["exit_code"] == 0:
                st.success("Execution passed")
            else:
                st.error("Execution failed")
            st.write("Exit code:", step["result"]["exit_code"])
            if step["result"]["stdout"]:
                st.text_area("STDOUT", step["result"]["stdout"], height=100, key=f"out_{step['iteration']}")
            if step["result"]["stderr"]:
                st.text_area("STDERR", step["result"]["stderr"], height=100, key=f"err_{step['iteration']}")

            st.markdown("**Critic Feedback**")
            st.write(step["critique"])

            st.markdown("**Security Scan**")
            if step["security_passed"]:
                st.success("No high-severity security issues found")
            else:
                st.error("Security issues detected — must be fixed")
            st.code(step["security_report"].summary(), language="text")

    final = iterations[-1]
    st.download_button(
        label="Download Final Code",
        data=final["code"],
        file_name="generated_code.py",
        mime="text/x-python",
    )

    st.session_state.history.append({
        "task": user_query,
        "final_approved": final["approved"],
        "iterations_used": len(iterations),
        "final_code": final["code"],
    })

if st.session_state.history:
    st.subheader("Run History")
    for i, item in enumerate(reversed(st.session_state.history), start=1):
        st.markdown(f"**{i}.** {item['task']}")
        st.write(f"Approved: {item['final_approved']} | Iterations used: {item['iterations_used']}")
        st.divider()
