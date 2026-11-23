"""Run the seeded checkout pipeline with live Gemini and Docker isolation."""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def main() -> int:
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        print("GEMINI_API_KEY is required for this rehearsal.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="relay-checkout-gemini-") as temporary:
        work_root = Path(temporary)
        os.environ["RELAY_DB_PATH"] = str(work_root / "rehearsal.sqlite3")
        os.environ["RELAY_APPLIED_ROOT"] = str(work_root / "applied")
        os.environ["RELAY_ALLOW_UNSAFE_SUBPROCESS"] = "false"

        import main as relay_api
        from fastapi.testclient import TestClient

        sandbox = relay_api.orchestrator.sandbox
        if not sandbox.docker_available or not sandbox.sandbox_image_available:
            print(
                "Docker isolation is unavailable. Start Docker and build/configure the sandbox image; no host fallback will run.",
                file=sys.stderr,
            )
            return 2
        if relay_api.orchestrator.provider is None:
            print("The Gemini provider did not initialize.", file=sys.stderr)
            return 2

        auth_headers: dict[str, str] = {}
        if relay_api.AUTH_USERS:
            operator = next(
                (
                    (name, token)
                    for name, token in relay_api.AUTH_USERS.items()
                    if relay_api.AUTH_ROLES.get(name, "operator") == "operator"
                ),
                None,
            )
            if operator is None:
                print("Configure an operator token for the rehearsal.", file=sys.stderr)
                return 2
            auth_headers["Authorization"] = f"Bearer {operator[1]}"
        elif relay_api.API_TOKEN:
            auth_headers["Authorization"] = f"Bearer {relay_api.API_TOKEN}"

        with TestClient(relay_api.app) as client:
            scenarios_response = client.get("/api/v1/scenarios", headers=auth_headers)
            if scenarios_response.status_code != 200:
                print("Could not load the seeded checkout scenario.", file=sys.stderr)
                return 1
            scenario = next(
                (
                    item
                    for item in scenarios_response.json()
                    if item["id"] == "scenario_checkout_discount_twice"
                ),
                None,
            )
            if scenario is None:
                print("The seeded checkout scenario is missing.", file=sys.stderr)
                return 1
            submitted = client.post(
                "/api/v1/tasks",
                json={"chat_message": scenario["bug_report"], "codebase": scenario["codebase"]},
                headers=auth_headers,
            )
            if submitted.status_code != 202:
                print(f"Scenario submission failed with HTTP {submitted.status_code}.", file=sys.stderr)
                return 1
            task_id = submitted.json()["task_id"]

            deadline = time.monotonic() + 180
            task = submitted.json()
            while time.monotonic() < deadline:
                response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
                if response.status_code != 200:
                    print("Could not retrieve the rehearsal task.", file=sys.stderr)
                    return 1
                task = response.json()
                if task["status"] in {"AWAITING_HUMAN_APPROVAL", "FAILED"}:
                    break
                time.sleep(0.5)

            sandbox_result = task.get("sandbox_result") or {}
            reviewer = task.get("reviewer") or {}
            passed = (
                task["status"] == "AWAITING_HUMAN_APPROVAL"
                and sandbox_result.get("tests_passed") is True
                and sandbox_result.get("isolation_mode") == "docker"
                and reviewer.get("security_assessment") == "PASS"
                and reviewer.get("recommendation") == "APPROVE"
            )
            print(
                "Checkout rehearsal: "
                f"status={task['status']} "
                f"isolation={sandbox_result.get('isolation_mode', 'none')} "
                f"tests_passed={str(sandbox_result.get('tests_passed', False)).lower()} "
                f"human_decision_required=true"
            )
            return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
