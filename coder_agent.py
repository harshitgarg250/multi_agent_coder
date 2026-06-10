# coder_agent.py
# Ollama-based Coder Agent (local, free, no quota)

import ollama

# Model name
MODEL_NAME = "llama3.2"

def generate_code(user_request: str) -> str:
    """
    user_request: 'Write a Python function to reverse a string'
    return: generated code string (from Ollama)
    """
    prompt = f"""
You are a coding assistant. Your task is to generate clean, working code based on the user's request.

User request:
{user_request}

Rules:
- Only generate code.
- Use Python by default unless user specifies another language.
- Add short comments in code to explain logic.
- Do not add extra explanation text before or after the code.

Generate code:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    code = response["message"]["content"].strip()
    return code


if __name__ == "__main__":
    print("=== Basic Coder Agent (Ollama Local) ===")
    print("Type your coding request (e.g., 'Write a Python function to reverse a string'):")
    user_input = input("> ")

    code = generate_code(user_input)

    print("\n=== Generated Code ===")
    print(code)
    print("\n=== End of Code ===\n")