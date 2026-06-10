# app.py
# Streamlit web UI for Coder Agent

import streamlit as st
import ollama

MODEL_NAME = "llama3.2"

def generate_code(user_request: str) -> str:
    prompt = f"""
You are a coding assistant. Generate clean, working code.

User request:
{user_request}

Rules:
- Only generate code.
- Use Python by default unless user specifies another language.
- Add short comments in code.
- No extra explanation text.

Generate code:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    code = response["message"]["content"].strip()
    return code


st.set_page_config(page_title="Coder Agent", page_icon="💻")

st.title("🤖 Multi-Agent Coding Assistant (Day 1: Coder Agent)")
st.markdown("### Local Ollama (llama3.2)")

st.markdown("Enter your coding request:")

user_input = st.text_input(
    "Your request:",
    placeholder="e.g., Write a Python function to reverse a string"
)

if st.button("Generate Code"):
    if not user_input:
        st.warning("Please enter a coding request.")
    else:
        with st.spinner("Generating code..."):
            code = generate_code(user_input)

        st.markdown("### Generated Code")
        st.code(code, language="python")

st.markdown("---")
st.caption("Built with Ollama (local LLM) + Streamlit")