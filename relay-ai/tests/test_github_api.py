from fastapi.testclient import TestClient
import pytest

from github_adapter import GitHubAdapterError
import main
from schemas import (
    GitHubPullRequestResponse,
    PipelineStatus,
    PipelineTaskResponse,
    ReviewResult,
    SandboxExecutionResult,
    TriageResult,
)


BASE = "1" * 40
HEAD = "2" * 40


def _task(task_id: str, *, approved: bool) -> PipelineTaskResponse:
    return PipelineTaskResponse(
        task_id=task_id,
        status=PipelineStatus.COMMITTED,
        current_stage="COMMITTED",
        bug_report="Regression test covers the reported behavior.",
        created_at="2026-11-10T00:00:00Z",
        updated_at="2026-11-10T00:00:00Z",
        triage=TriageResult(title="Fix regression", severity="medium", acceptance_criteria=["Regression is fixed"]),
        sandbox_result=SandboxExecutionResult(
            test_command="pytest -q", exit_code=0, tests_passed=True, isolation_mode="docker",
            applied_patch_cleanly=True,
        ),
        reviewer=ReviewResult(
            security_assessment="PASS", recommendation="APPROVE", review_summary="Bounded patch reviewed.",
        ),
        is_approved=approved,
        is_applied=True,
        is_committed=True,
        commit_hash=HEAD,
        repository_id="relay",
        repository_base_revision=BASE,
    )


class _FakeAdapter:
    def __init__(self):
        self.calls = []
        self.closed = False

    def create_pull_request(self, repository_id, **kwargs):
        self.calls.append((repository_id, kwargs))
        return {"number": 5, "url": "https://github.com/acme/relay/pull/5", "state": "open", "already_open": False}

    def close(self):
        self.closed = True


class _InvalidBranchAdapter(_FakeAdapter):
    def create_pull_request(self, repository_id, **kwargs):
        self.calls.append((repository_id, kwargs))
        raise GitHubAdapterError("Git branch name is invalid.")


class _InvalidRefAdapter(_FakeAdapter):
    def get_contents(self, repository_id, file_path, *, ref=None):
        self.calls.append((repository_id, file_path, ref))
        raise GitHubAdapterError("Git reference is invalid.")


def test_task_pr_api_fails_closed_without_approval(monkeypatch):
    task_id = "github-pr-not-approved"
    main.tasks_db[task_id] = _task(task_id, approved=False)
    adapter = _FakeAdapter()
    monkeypatch.setattr(main, "_github_adapter", lambda: adapter)
    try:
        with TestClient(main.app) as client:
            response = client.post(f"/api/v1/tasks/{task_id}/pull-request", json={
                "head_branch": "codex/fix", "base_branch": "main", "title": "Fix", "body": "",
            })
        assert response.status_code == 409
        assert "human-approved" in response.json()["detail"]
        assert adapter.calls == []
    finally:
        del main.tasks_db[task_id]


def test_task_pr_api_requires_operator_approval_then_audits_and_replays(monkeypatch):
    task_id = "github-pr-approved"
    main.tasks_db[task_id] = _task(task_id, approved=True)
    adapter = _FakeAdapter()
    monkeypatch.setattr(main, "_github_adapter", lambda: adapter)
    headers = {"Idempotency-Key": "open-pr-001"}
    body = {"head_branch": "codex/fix", "base_branch": "main", "title": "Fix regression", "body": "Reviewed patch"}
    try:
        with TestClient(main.app) as client:
            response = client.post(f"/api/v1/tasks/{task_id}/pull-request", json=body, headers=headers)
            replay = client.post(f"/api/v1/tasks/{task_id}/pull-request", json=body, headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "repository": "relay", "number": 5, "url": "https://github.com/acme/relay/pull/5",
            "state": "open", "already_open": False,
        }
        assert replay.json() == response.json()
        assert len(adapter.calls) == 1
        repo_id, kwargs = adapter.calls[0]
        assert repo_id == "relay"
        assert kwargs["approved"] is True
        assert kwargs["expected_base_sha"] == BASE
        assert kwargs["expected_head_sha"] == HEAD
        assert adapter.closed is True
        assert main.tasks_db.get_action_by_idempotency_key(task_id, "open-pr-001")["action"] == "open_pull_request"
    finally:
        del main.tasks_db[task_id]


def test_task_pr_api_reports_invalid_branch_as_client_error(monkeypatch):
    task_id = "github-pr-invalid-branch"
    main.tasks_db[task_id] = _task(task_id, approved=True)
    adapter = _InvalidBranchAdapter()
    monkeypatch.setattr(main, "_github_adapter", lambda: adapter)
    body = {"head_branch": "bad./branch", "base_branch": "main", "title": "Fix", "body": ""}
    try:
        with TestClient(main.app) as client:
            response = client.post(f"/api/v1/tasks/{task_id}/pull-request", json=body)
        assert response.status_code == 400
        assert response.json()["detail"] == "Git branch name is invalid."
        assert adapter.closed is True
    finally:
        del main.tasks_db[task_id]


def test_github_contents_api_reports_invalid_ref_as_client_error(monkeypatch):
    adapter = _InvalidRefAdapter()
    monkeypatch.setattr(main, "_github_adapter", lambda: adapter)
    with TestClient(main.app) as client:
        response = client.get(
            "/api/v1/github/repositories/relay/contents",
            params={"path": "src/main.py", "ref": "../private"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Git reference is invalid."
    assert adapter.calls == [("relay", "src/main.py", "../private")]
    assert adapter.closed is True


def test_github_repository_read_rejects_viewer_before_loading_adapter(monkeypatch):
    monkeypatch.setattr(main, "AUTH_USERS", {"viewer": "viewer-token"})
    monkeypatch.setattr(main, "AUTH_ROLES", {"viewer": "viewer"})
    monkeypatch.setattr(main, "_auth_roles_configured", True)
    monkeypatch.setattr(main, "API_TOKEN", None)
    monkeypatch.setattr(
        main,
        "_github_adapter",
        lambda: pytest.fail("viewer request must be rejected before adapter configuration"),
    )

    with TestClient(main.app) as client:
        response = client.get(
            "/api/v1/github/repositories/relay",
            headers={"Authorization": "Bearer viewer-token"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Operator access is required."
