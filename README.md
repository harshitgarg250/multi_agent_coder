# Multi-Agent Coding Assistant

A self-correcting multi-agent system that plans, writes, tests, and reviews
Python code — automatically fixing its own bugs across iterations.

## Architecture

```
User task
   |
   v
[Planner Agent]  --> breaks task into sub-tasks
   |
   v
[Coder Agent]    --> generates Python code
   |
   v
[Tester Agent]   --> executes code in a sandboxed subprocess
   |
   v
[Critic Agent]   --> reviews code + test result -> APPROVED / NEEDS_FIX
   |
   v
[Security Critic Agent] --> static analysis (AST + regex) for hardcoded
   |                          secrets, eval/exec, shell injection, SQL
   |                          injection, unsafe deserialization
   |
   +--(NEEDS_FIX or security issue)--> back to [Coder Agent] with combined
   |                                    feedback (up to N iterations)
   |
   +--(APPROVED + security clean)---> final code returned
```

This loop is what makes it "multi-agent" rather than a single LLM call:
each agent has a narrow responsibility, and the Critic's feedback is fed
back to the Coder so the system self-corrects without human intervention.

## Why a separate Security Critic Agent?
LLM-generated code can compile and pass functional tests while still
containing security anti-patterns (hardcoded secrets, `eval()`, SQL built
via string formatting, `shell=True` subprocess calls). The Security Critic
is a **deterministic, rule-based static analyzer** (Python `ast` + regex) —
not another LLM call — so it's fast, free, and repeatable, similar to a
lightweight SAST tool you'd run in a CI pipeline. This is directly relevant
for code review in regulated domains like fintech/banking.

## Tech Stack
- **LLM:** Groq API (`llama-3.3-70b-versatile`) — fast cloud inference
- **UI:** Streamlit
- **Execution sandbox:** Python `subprocess` with timeout isolation

## Setup

```bash
pip install -r requirements.txt
```

Add your Groq API key to `.env` (get a free key at https://console.groq.com/keys):
```
GROQ_API_KEY=your_key_here
```

## Run

Web UI:
```bash
streamlit run app.py
```

CLI:
```bash
python main_pipeline.py
```

## Example
Task: "Write a function to check if a string is a palindrome, handling
spaces and case-insensitivity."

The system plans the task, generates code, executes it against sample
input, and if the Critic finds an edge-case bug (e.g. spaces not
stripped), it automatically regenerates a fixed version — without any
human writing corrective code.

## Possible Extensions
- Multi-language support (currently Python-only)
- Persist run history to SQLite/MongoDB instead of in-memory session state
- CI pipeline (GitHub Actions) running `pytest` + security scan on every push
