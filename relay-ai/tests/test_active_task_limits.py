"""Focused coverage for per-owner active task admission."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from io import BytesIO
from threading import Barrier
from zipfile import ZIP_DEFLATED, ZipFile
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import main
from schemas import PipelineStatus, PipelineTaskResponse
from storage import ActiveTaskLimitExceeded, SQLiteTaskStore


def _queued_task(owner_id: str) -> PipelineTaskResponse:
    now = datetime.now(timezone.utc).isoformat()
    return PipelineTaskResponse(
        task_id=str(uuid4()), owner_id=owner_id, status=PipelineStatus.QUEUED,
        current_stage="QUEUED", bug_report="test task", created_at=now, updated_at=now,
    )


def test_active_task_admission_serializes_concurrent_store_instances(tmp_path):
    database = tmp_path / "active-limit.sqlite3"
    stores = [SQLiteTaskStore(database), SQLiteTaskStore(database)]
    gate = Barrier(2)

    def submit(index: int) -> str:
        task = _queued_task("owner-a")
        gate.wait()
        try:
            stores[index].create_task(task, {"app.py": "pass\n"}, max_active_tasks_per_owner=1)
            return "accepted"
        except ActiveTaskLimitExceeded:
            return "limited"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(submit, range(2)))

    assert sorted(outcomes) == ["accepted", "limited"]
    assert len(stores[0]) == 1


def test_json_submission_returns_429_when_owner_limit_is_reached(tmp_path, monkeypatch):
    store = SQLiteTaskStore(tmp_path / "api-active-limit.sqlite3")
    monkeypatch.setattr(main, "tasks_db", store)
    monkeypatch.setattr(main.pipeline_worker, "store", store)
    monkeypatch.setattr(main.pipeline_worker, "start", lambda: None)
    monkeypatch.setattr(main.pipeline_worker, "stop", lambda: None)
    monkeypatch.setattr(main, "MAX_ACTIVE_TASKS_PER_OWNER", 1)
    monkeypatch.setattr(main, "API_TOKEN", None)
    monkeypatch.setattr(main, "AUTH_USERS", {})
    monkeypatch.setattr(main, "AUTH_ROLES", {})
    monkeypatch.setattr(main, "_auth_roles_configured", False)

    payload = {"chat_message": "Please inspect this function.", "codebase": {"app.py": "pass\n"}}
    archive = BytesIO()
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        bundle.writestr("app.py", "pass\n")
    with TestClient(main.app) as client:
        accepted = client.post("/api/v1/tasks", json=payload)
        limited = client.post("/api/v1/tasks", json=payload)
        zip_limited = client.post(
            "/api/v1/tasks/upload",
            data={"bug_report": payload["chat_message"]},
            files={"file": ("snapshot.zip", archive.getvalue(), "application/zip")},
        )

    assert accepted.status_code == 202
    assert limited.status_code == 429
    assert "queued or running tasks" in limited.json()["detail"]
    assert zip_limited.status_code == 429
    assert len(store) == 1
