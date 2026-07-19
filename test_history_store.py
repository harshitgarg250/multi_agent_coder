# test_history_store.py
# Tests for SQLite-based run history persistence. Each test points
# DB_PATH at a temporary file so tests never touch the real history.db.

import os
import importlib

import history_store


def _use_temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", str(db_file))
    history_store.init_db()
    return db_file


def test_init_db_creates_empty_table(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)
    runs = history_store.get_all_runs()
    assert runs == []


def test_save_and_retrieve_run(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    history_store.save_run(
        task="Reverse a string",
        approved=True,
        security_passed=True,
        iterations_used=1,
        final_code="def reverse(s): return s[::-1]",
    )

    runs = history_store.get_all_runs()
    assert len(runs) == 1
    assert runs[0]["task"] == "Reverse a string"
    assert runs[0]["approved"] == 1
    assert runs[0]["security_passed"] == 1
    assert runs[0]["iterations_used"] == 1
    assert "reverse" in runs[0]["final_code"]


def test_runs_returned_most_recent_first(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    history_store.save_run("First task", True, True, 1, "code1")
    history_store.save_run("Second task", False, True, 2, "code2")

    runs = history_store.get_all_runs()
    assert runs[0]["task"] == "Second task"
    assert runs[1]["task"] == "First task"


def test_get_all_runs_respects_limit(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    for i in range(5):
        history_store.save_run(f"Task {i}", True, True, 1, f"code{i}")

    runs = history_store.get_all_runs(limit=2)
    assert len(runs) == 2


def test_clear_history_removes_all_runs(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    history_store.save_run("Some task", True, True, 1, "code")
    assert len(history_store.get_all_runs()) == 1

    history_store.clear_history()
    assert history_store.get_all_runs() == []


def test_toggle_pin_sets_and_unsets(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    run_id = history_store.save_run("Some task", True, True, 1, "code")
    assert history_store.get_all_runs()[0]["pinned"] == 0

    history_store.toggle_pin(run_id)
    assert history_store.get_all_runs()[0]["pinned"] == 1

    history_store.toggle_pin(run_id)
    assert history_store.get_all_runs()[0]["pinned"] == 0


def test_pinned_runs_sort_before_unpinned(tmp_path, monkeypatch):
    _use_temp_db(tmp_path, monkeypatch)

    history_store.save_run("First task", True, True, 1, "code1")
    second_id = history_store.save_run("Second task", True, True, 1, "code2")
    history_store.toggle_pin(second_id)

    runs = history_store.get_all_runs()
    assert runs[0]["task"] == "Second task"
    assert runs[0]["pinned"] == 1