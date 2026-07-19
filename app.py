import streamlit as st
from main_pipeline import run_pipeline, continue_pipeline
from history_store import init_db, save_run, update_run, get_all_runs, clear_history, toggle_pin

st.set_page_config(
    page_title="Multi-Agent Coding Assistant",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "current_run_id" not in st.session_state:
    st.session_state.current_run_id = None
if "iterations_cache" not in st.session_state:
    st.session_state.iterations_cache = {}
if "planned_tasks_cache" not in st.session_state:
    st.session_state.planned_tasks_cache = {}
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ---------------------------------------------------------------------------
# Theming: we deliberately do NOT run our own dark/light logic. Streamlit's
# native theme engine (☰ menu -> Settings -> App theme: Light / Dark / Use
# system setting) already handles this correctly, including following the
# OS preference. We just style our custom elements using Streamlit's own
# CSS variables (--background-color, --text-color, etc.), which update
# automatically whenever the user changes the native theme setting.
# ---------------------------------------------------------------------------
ACCENT = "#7C6BFF"
ACCENT_GRADIENT = f"linear-gradient(135deg, {ACCENT} 0%, #9F7BFF 100%)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
code, pre, [data-testid="stCodeBlock"] * {{ font-family: 'JetBrains Mono', monospace !important; }}

[data-testid="stSidebar"] {{
    background: color-mix(in srgb, var(--background-color) 88%, var(--text-color) 12%);
    border-right: 1px solid color-mix(in srgb, var(--text-color) 15%, transparent);
    box-shadow: 2px 0 12px rgba(0,0,0,0.08);
}}
[data-testid="stSidebar"] .stButton button {{
    width: 100%; text-align: left; background: transparent;
    border: 1px solid transparent; color: var(--text-color);
    border-radius: 10px; padding: 0.5rem 0.8rem; font-size: 0.85rem;
    margin-bottom: 0.2rem; transition: all 0.15s ease;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: color-mix(in srgb, var(--background-color) 78%, var(--text-color) 22%);
    transform: translateX(2px);
}}

.sidebar-brand {{
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 1.15rem; font-weight: 800; color: var(--text-color);
    padding: 0.2rem 0 1rem 0;
}}
.sidebar-brand .dot {{
    width: 26px; height: 26px; border-radius: 50%;
    background: {ACCENT_GRADIENT};
    box-shadow: 0 0 12px {ACCENT}66;
    display: inline-block;
}}

.new-task-btn button {{
    background: {ACCENT_GRADIENT} !important; color: white !important;
    border: none !important; font-weight: 700 !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 10px {ACCENT}40;
}}
.new-task-btn button:hover {{ filter: brightness(1.08); box-shadow: 0 4px 16px {ACCENT}55; }}

.active-run button {{
    background: color-mix(in srgb, var(--background-color) 75%, var(--text-color) 25%) !important;
    border-left: 3px solid {ACCENT} !important;
    font-weight: 600 !important;
}}

.pin-btn button {{
    background: transparent !important; border: none !important;
    padding: 0.2rem !important; min-height: unset !important;
}}

.hero-title {{
    font-size: 2.3rem; font-weight: 800; margin-bottom: 0.15rem;
    background: {ACCENT_GRADIENT};
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
}}
.hero-sub {{ color: color-mix(in srgb, var(--text-color) 65%, transparent); font-size: 0.97rem; margin-bottom: 1.8rem; }}

.status-pill {{
    display: inline-block; padding: 0.2rem 0.8rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.03em;
}}
.pill-approved {{ background: #113325; color: #4ADE80; border: 1px solid #1F5C3D; }}
.pill-needsfix {{ background: #3A1F1F; color: #F87171; border: 1px solid #6B2C2C; }}

.sidebar-label {{
    display: flex; align-items: center; gap: 0.35rem;
    color: color-mix(in srgb, var(--text-color) 60%, transparent);
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; margin: 1.2rem 0 0.5rem 0.2rem;
}}

[data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT}22 !important;
}}

.stButton button[kind="primary"] {{
    background: {ACCENT_GRADIENT}; border: none; border-radius: 10px; font-weight: 700;
    box-shadow: 0 2px 10px {ACCENT}40;
    transition: all 0.15s ease;
}}
.stButton button[kind="primary"]:hover {{
    filter: brightness(1.08); box-shadow: 0 4px 18px {ACCENT}55; transform: translateY(-1px);
}}

[data-testid="stExpander"] {{
    border-radius: 12px;
}}

@media (max-width: 640px) {{
    .hero-title {{ font-size: 1.6rem; }}
    .hero-sub {{ font-size: 0.85rem; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><span class="dot"></span> Multi-Agent Coder</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="new-task-btn">', unsafe_allow_html=True)
    if st.button("+ New Task", use_container_width=True):
        st.session_state.current_run_id = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.text_input("Search chats", key="search_query", placeholder="🔍 Search chats",
                  label_visibility="collapsed")

    all_runs = get_all_runs()
    q = st.session_state.search_query.strip().lower()
    filtered_runs = [r for r in all_runs if q in r["task"].lower()] if q else all_runs

    pinned_runs = [r for r in filtered_runs if r["pinned"]]
    recent_runs = [r for r in filtered_runs if not r["pinned"]]

    def render_history_row(run):
        icon = "✅" if (run["approved"] and run["security_passed"]) else "⚠️"
        short_task = run["task"][:32] + ("…" if len(run["task"]) > 32 else "")
        is_active = run["id"] == st.session_state.current_run_id
        row_l, row_r = st.columns([5, 1])
        with row_l:
            wrapper_class = "active-run" if is_active else ""
            st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
            if st.button(f"{icon} {short_task}", key=f"hist_{run['id']}", use_container_width=True):
                st.session_state.current_run_id = run["id"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with row_r:
            st.markdown('<div class="pin-btn">', unsafe_allow_html=True)
            pin_icon = "📍" if run["pinned"] else "📌"
            if st.button(pin_icon, key=f"pin_{run['id']}"):
                toggle_pin(run["id"])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if pinned_runs:
        st.markdown('<div class="sidebar-label">📍 Pinned</div>', unsafe_allow_html=True)
        for run in pinned_runs:
            render_history_row(run)

    if recent_runs:
        st.markdown('<div class="sidebar-label">🕒 Recent</div>', unsafe_allow_html=True)
        for run in recent_runs:
            render_history_row(run)

    if not pinned_runs and not recent_runs:
        if q:
            st.caption("No chats match your search.")
        else:
            st.caption("No past runs yet. Your history will show up here.")

    if all_runs:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear all history", use_container_width=True):
            clear_history()
            st.session_state.current_run_id = None
            st.session_state.iterations_cache = {}
            st.rerun()


def render_iteration_trail(iterations):
    st.markdown(f"**Agent Iterations ({len(iterations)})**")
    for step in iterations:
        status = "APPROVED" if (step["approved"] and step["security_passed"]) else "NEEDS FIX"
        label = f"Iteration {step['iteration']} — {status}"
        with st.expander(label, expanded=(step is iterations[-1])):
            st.code(step["code"], language="python")

            if step["result"]["success"] and step["result"]["exit_code"] == 0:
                st.success("Execution passed")
            else:
                st.error("Execution failed")
            st.write("Exit code:", step["result"]["exit_code"])
            if step["result"]["stdout"]:
                st.text_area("STDOUT", step["result"]["stdout"], height=100, key=f"out_{step['iteration']}_{id(step)}")
            if step["result"]["stderr"]:
                st.text_area("STDERR", step["result"]["stderr"], height=100, key=f"err_{step['iteration']}_{id(step)}")

            st.markdown("**Critic Feedback**")
            st.write(step["critique"])

            st.markdown("**Security Scan**")
            if step["security_passed"]:
                st.success("No high-severity security issues found")
            else:
                st.error("Security issues detected — must be fixed")
            st.code(step["security_report"].summary(), language="text")


def run_and_persist(user_query, input_data, max_iterations, existing_run_id=None):
    with st.spinner("Planning, generating, running, and reviewing code..."):
        tasks, iterations = run_pipeline(user_query, input_data=input_data + "\n", max_iterations=max_iterations)

    final = iterations[-1]
    if existing_run_id is None:
        run_id = save_run(
            task=user_query, approved=final["approved"], security_passed=final["security_passed"],
            iterations_used=len(iterations), final_code=final["code"], critique=final["critique"],
            security_summary=final["security_report"].summary(), input_data=input_data,
        )
    else:
        run_id = existing_run_id
        update_run(
            run_id, task=user_query, approved=final["approved"], security_passed=final["security_passed"],
            iterations_used=len(iterations), final_code=final["code"], critique=final["critique"],
            security_summary=final["security_report"].summary(), input_data=input_data,
        )

    st.session_state.iterations_cache[run_id] = iterations
    st.session_state.planned_tasks_cache[run_id] = tasks
    return run_id


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
current_id = st.session_state.current_run_id

if current_id is not None:
    match = next((r for r in all_runs if r["id"] == current_id), None)
    if match is None:
        st.session_state.current_run_id = None
        st.rerun()

    status_ok = match["approved"] and match["security_passed"]
    pill_class = "pill-approved" if status_ok else "pill-needsfix"
    pill_text = "APPROVED" if status_ok else "NEEDS FIX"
    st.markdown(f'<span class="status-pill {pill_class}">{pill_text}</span>', unsafe_allow_html=True)
    st.markdown(f"#### {match['task']}")
    st.caption(f"Iterations used: {match['iterations_used']}  |  Security clean: {bool(match['security_passed'])}")

    if current_id in st.session_state.iterations_cache:
        tasks = st.session_state.planned_tasks_cache.get(current_id, [])
        if tasks:
            st.markdown("**Planned Tasks**")
            for i, t in enumerate(tasks, start=1):
                st.write(f"{i}. {t}")
        render_iteration_trail(st.session_state.iterations_cache[current_id])
    else:
        st.markdown("**Generated Code**")
        st.code(match["final_code"], language="python")
        if match.get("critique"):
            with st.expander("Critic Feedback"):
                st.write(match["critique"])
        if match.get("security_summary"):
            with st.expander("Security Scan"):
                st.code(match["security_summary"], language="text")

    st.download_button("Download code", data=match["final_code"], file_name="generated_code.py",
                        mime="text/x-python", key=f"dl_{current_id}")

    st.markdown("---")
    st.markdown("**Edit this task**")
    st.caption("Describe what you'd like changed — the same code will be refined, not replaced with a new task.")
    refinement = st.text_area("What should change?", key=f"refine_{current_id}", label_visibility="collapsed",
                               placeholder="e.g. Also handle negative numbers, or add input validation")
    if st.button("Update Task", type="primary"):
        if not refinement.strip():
            st.warning("Describe what you'd like changed first.")
        else:
            with st.spinner("Refining based on your feedback..."):
                iterations = continue_pipeline(
                    match["task"], match["final_code"], refinement,
                    input_data=match.get("input_data", ""), max_iterations=3,
                )
            final = iterations[-1]
            update_run(
                current_id, task=match["task"], approved=final["approved"],
                security_passed=final["security_passed"], iterations_used=len(iterations),
                final_code=final["code"], critique=final["critique"],
                security_summary=final["security_report"].summary(), input_data=match.get("input_data", ""),
            )
            st.session_state.iterations_cache[current_id] = iterations
            st.rerun()

else:
    st.markdown('<div class="hero-title">Multi-Agent Coding Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Planner → Coder → Tester → Critic → Security Critic, '
        'with an automatic self-correction loop.</div>',
        unsafe_allow_html=True,
    )

    user_query = st.text_area("Describe your coding task", placeholder="e.g. Write a function that checks if a number is prime")
    user_input_data = st.text_input("Sample input for your script (optional)", "1 2 3 4 5")
    max_iterations = st.slider("Max self-correction attempts", 1, 5, 3)

    if st.button("Run", type="primary"):
        if not user_query.strip():
            st.warning("Please describe a coding task first.")
        else:
            run_id = run_and_persist(user_query, user_input_data, max_iterations)
            st.session_state.current_run_id = run_id
            st.rerun()