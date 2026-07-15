import os
from dotenv import load_dotenv

load_dotenv()

# Groq API key - get a free key at https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
