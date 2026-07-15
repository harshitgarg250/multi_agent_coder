# agents/llm_client.py
# Unified LLM client - all agents talk through this.
# Uses Groq (cloud, fast, free-tier) instead of local Ollama so the
# app can be deployed and demoed live (e.g. Streamlit Community Cloud).

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
_client = Groq(api_key=_api_key) if _api_key else None

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def chat(prompt: str, system: str = None, temperature: float = 0.3) -> str:
    """Send a single-turn chat request to Groq and return the text response."""
    if _client is None:
        raise RuntimeError(
            "GROQ_API_KEY not set. Add it to your .env file "
            "(get a free key at https://console.groq.com/keys)"
        )

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
