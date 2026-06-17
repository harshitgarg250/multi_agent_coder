import streamlit as st
from agents.coder import CoderAgent
from agents.tester import TesterAgent

def run_pipeline(user_query: str, input_data: str):
    coder = CoderAgent()
    tester = TesterAgent()

    code = coder.generate_code(user_query)
    result = tester.run_code(code, input_data=input_data)

    return code, result

st.title("Multi-Agent Coding Assistant")

user_query = st.text_area("Describe your coding task:")
user_input_data = st.text_input("Sample input for your script (optional):", "1 2 3 4 5")

if st.button("Run"):
    with st.spinner("Generating and running code..."):
        code, result = run_pipeline(user_query, input_data=user_input_data + "\n")

    st.subheader("Generated Code")
    st.code(code, language="python")

    st.subheader("Execution Result")
    st.write("Success:", result["success"])
    st.write("Exit code:", result["exit_code"])
    if result["stdout"]:
        st.text_area("STDOUT", result["stdout"], height=150)
    if result["stderr"]:
        st.text_area("STDERR", result["stderr"], height=150)