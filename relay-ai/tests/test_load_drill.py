from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deploy import load_drill


def test_report_file_contains_complete_json_and_does_not_overwrite(tmp_path: Path) -> None:
    report_path = load_drill.validate_report_path(str(tmp_path / "run.json"))
    report = {"accepted_tasks": 2, "final_task_states": {"AWAITING_HUMAN_APPROVAL": 2}}

    load_drill.write_report(report_path, report)

    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    with pytest.raises(FileExistsError):
        load_drill.write_report(report_path, {"accepted_tasks": 0})
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_report_path_must_use_an_existing_parent(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / "run.json"

    with pytest.raises(ValueError, match="parent directory must already exist"):
        load_drill.validate_report_path(str(missing))


def test_dry_run_can_preview_report_path_without_httpx_or_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report_path = tmp_path / "preview.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "load_drill.py",
            "--origin",
            "http://localhost:8000",
            "--report-file",
            str(report_path),
        ],
    )

    assert load_drill.main() == 0
    assert "DRY RUN: no HTTP requests were sent" in capsys.readouterr().out
    assert not report_path.exists()


def test_execution_saves_completed_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report_path = tmp_path / "completed.json"

    class FakeClient:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    monkeypatch.setitem(
        sys.modules,
        "httpx",
        SimpleNamespace(Client=FakeClient, Timeout=lambda *_args, **_kwargs: object()),
    )
    monkeypatch.setattr(load_drill, "read_metrics", lambda *_args: {"relay_worker_running": ["relay_worker_running 1"]})
    monkeypatch.setattr(load_drill, "submit_one", lambda *_args: ("task-1", 0.125, 202, None))
    monkeypatch.setattr(
        load_drill,
        "poll_tasks",
        lambda *_args: {"task-1": "AWAITING_HUMAN_APPROVAL"},
    )
    monkeypatch.setenv("RELAY_LOAD_TOKEN", "test-operator-token")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "load_drill.py",
            "--origin",
            "http://localhost:8000",
            "--tasks",
            "1",
            "--concurrency",
            "1",
            "--report-file",
            str(report_path),
            "--execute",
        ],
    )

    assert load_drill.main() == 0
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["accepted_tasks"] == 1
    assert saved["final_task_states"] == {"AWAITING_HUMAN_APPROVAL": 1}
    assert "Report saved to:" in capsys.readouterr().out
