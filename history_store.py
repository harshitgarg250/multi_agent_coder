# history_store.py
# Lightweight SQLite persistence for past pipeline runs, so history
# survives a Streamlit app restart/refresh instead of living only in
# in-memory session state.

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = "history.db"


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                task TEXT NOT NULL,
                approved INTEGER NOT NULL,
                security_passed INTEGER NOT NULL,
                iterations_used INTEGER NOT NULL,
                final_code TEXT NOT NULL
            )
        """)


def save_run(task: str, approved: bool, security_passed: bool, iterations_used: int, final_code: str) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO runs (created_at, task, approved, security_passed, iterations_used, final_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                task,
                int(approved),
                int(security_passed),
                iterations_used,
                final_code,
            ),
        )
        return cursor.lastrowid


def get_all_runs(limit: int = 50):
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def clear_history():
    with _connect() as conn:
        conn.execute("DELETE FROM runs")
