import streamlit as st
from main_pipeline import run_pipeline
from history_store import init_db, save_run, get_all_runs, clear_history

init_db()

st.set_page_config(page_title="Multi-Agent Coding Assistant", layout="wide")
st.title("Multi-Agent Coding Assistant")
st.caption("Planner -> Coder -> Tester -> Critic, with self-correction loop")

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

    save_run(
        task=user_query,
        approved=final["approved"],
        security_passed=final["security_passed"],
        iterations_used=len(iterations),
        final_code=final["code"],
    )

past_runs = get_all_runs()
if past_runs:
    st.subheader(f"Run History ({len(past_runs)})")
    for run in past_runs:
        status = "Approved" if run["approved"] and run["security_passed"] else "Needs fix"
        st.markdown(f"**{run['created_at']}** — {status}")
        st.write(run["task"])
        st.write(f"Iterations used: {run['iterations_used']} | Security clean: {bool(run['security_passed'])}")
        with st.expander("View generated code"):
            st.code(run["final_code"], language="python")
        st.divider()

    if st.button("Clear history"):
        clear_history()
        st.rerun()
