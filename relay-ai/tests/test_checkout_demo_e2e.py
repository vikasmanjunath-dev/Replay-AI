"""Run the seeded checkout scenario through the API and worker with a fake provider."""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

import main
from providers import FakeStructuredProvider
from schemas import (
    InvestigationAndPatchResult,
    PipelineStatus,
    ReviewResult,
    SandboxExecutionResult,
    TriageResult,
)
from storage import SQLiteTaskStore


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_STORE = REPOSITORY_ROOT / "demo-store"


def test_seeded_checkout_scenario_reaches_evidence_gated_human_review(tmp_path, monkeypatch):
    store = SQLiteTaskStore(tmp_path / "checkout-e2e.sqlite3")
    monkeypatch.setattr(main, "tasks_db", store)
    monkeypatch.setattr(main.pipeline_worker, "store", store)
    monkeypatch.setattr(main, "API_TOKEN", None)
    monkeypatch.setattr(main, "AUTH_USERS", {})
    monkeypatch.setattr(main, "AUTH_ROLES", {})
    monkeypatch.setattr(main, "_auth_roles_configured", False)

    patch = (DEMO_STORE / "patches" / "discount-once.patch").read_text(encoding="utf-8")
    source = (DEMO_STORE / "src" / "checkout.py").read_text(encoding="utf-8")
    monkeypatch.setattr(main.orchestrator, "provider", FakeStructuredProvider({
        TriageResult: TriageResult(
            title="Checkout subtracts a discount twice",
            severity="medium",
            acceptance_criteria=[
                "A $10 discount on a $100 subtotal produces $90.00.",
                "A zero discount leaves the subtotal unchanged.",
            ],
            rationale="The implementation applies the same discount amount twice.",
        ),
        InvestigationAndPatchResult: InvestigationAndPatchResult(
            buggy_file="src/checkout.py",
            affected_function="calculate_total",
            root_cause="The total expression subtracts the discount amount twice.",
            confidence_score=1.0,
            files_changed=["src/checkout.py"],
            unified_diff=patch,
            summary_of_changes="Subtract the fixed discount once.",
        ),
        ReviewResult: ReviewResult(
            security_assessment="PASS",
            recommendation="APPROVE",
            review_summary="The one-file patch is scoped and the checkout regression passes.",
        ),
    }))

    def run_trusted_checkout_fixture(**kwargs):
        codebase = kwargs["codebase"]
        unified_diff = kwargs["unified_diff"]
        expected_files = kwargs["expected_files"]
        test_command = f"{sys.executable} -m pytest -q tests/test_checkout.py"
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="relay-checkout-e2e-") as temporary:
            workspace = Path(temporary)
            sandbox = main.orchestrator.sandbox
            in_scope, scope_error = sandbox.validate_patch_scope(
                unified_diff, expected_files, set(codebase)
            )
            if not in_scope:
                return SandboxExecutionResult(
                    test_command=test_command,
                    exit_code=1,
                    tests_passed=False,
                    stdout="",
                    stderr=f"Patch rejected by scope validation: {scope_error}",
                    execution_time_ms=(time.perf_counter() - started) * 1000,
                    isolation_mode="subprocess_dev",
                    applied_patch_cleanly=False,
                    patch_error=scope_error,
                )
            sandbox._populate_workspace(workspace, codebase)
            syntax_valid, syntax_error = sandbox.validate_patch_syntax(workspace, unified_diff)
            if not syntax_valid:
                return SandboxExecutionResult(
                    test_command=test_command,
                    exit_code=1,
                    tests_passed=False,
                    stdout="",
                    stderr=f"Patch rejected by syntax validation: {syntax_error}",
                    execution_time_ms=(time.perf_counter() - started) * 1000,
                    isolation_mode="subprocess_dev",
                    applied_patch_cleanly=False,
                    patch_error=syntax_error,
                )
            applied, apply_error = sandbox.apply_patch(workspace, unified_diff)
            if not applied:
                return SandboxExecutionResult(
                    test_command=test_command,
                    exit_code=1,
                    tests_passed=False,
                    stdout="",
                    stderr=f"Patch application failed: {apply_error}",
                    execution_time_ms=(time.perf_counter() - started) * 1000,
                    isolation_mode="subprocess_dev",
                    applied_patch_cleanly=False,
                    patch_error=apply_error,
                )
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "tests/test_checkout.py"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            return SandboxExecutionResult(
                test_command=test_command,
                exit_code=result.returncode,
                tests_passed=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_ms=(time.perf_counter() - started) * 1000,
                isolation_mode="subprocess_dev",
                applied_patch_cleanly=True,
            )

    monkeypatch.setattr(main.orchestrator.sandbox, "run_tests", run_trusted_checkout_fixture)

    with TestClient(main.app) as client:
        scenarios = client.get("/api/v1/scenarios")
        assert scenarios.status_code == 200, scenarios.text
        scenario = next(
            item for item in scenarios.json()
            if item["id"] == "scenario_checkout_discount_twice"
        )
        assert scenario["codebase"]["src/checkout.py"] == source

        submitted = client.post(
            "/api/v1/tasks",
            json={"chat_message": scenario["bug_report"], "codebase": scenario["codebase"]},
        )
        assert submitted.status_code == 202, submitted.text
        task_id = submitted.json()["task_id"]

        deadline = time.monotonic() + 8
        task = submitted.json()
        while time.monotonic() < deadline:
            response = client.get(f"/api/v1/tasks/{task_id}")
            assert response.status_code == 200, response.text
            task = response.json()
            if task["status"] in {
                PipelineStatus.AWAITING_HUMAN_APPROVAL.value,
                PipelineStatus.FAILED.value,
            }:
                break
            time.sleep(0.05)

        assert task["status"] == PipelineStatus.AWAITING_HUMAN_APPROVAL.value, task
        assert task["sandbox_result"]["tests_passed"] is True
        assert task["sandbox_result"]["exit_code"] == 0
        assert task["sandbox_result"]["isolation_mode"] == "subprocess_dev"
        assert "2 passed" in task["sandbox_result"]["stdout"]
        assert task["investigation_patch"]["files_changed"] == ["src/checkout.py"]
        assert task["reviewer"]["security_assessment"] == "PASS"
        assert task["reviewer"]["recommendation"] == "APPROVE"
        assert store.count_actions(task_id) == 0
