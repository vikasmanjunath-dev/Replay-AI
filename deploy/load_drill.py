"""Bounded, opt-in load drill for the seeded checkout scenario on a Relay API."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import statistics
import sys
import time
from collections import Counter
from urllib.parse import urlsplit

import httpx

SCENARIO_ID = "scenario_checkout_discount_twice"
MAX_TASKS = 5
TERMINAL_STATES = {"AWAITING_HUMAN_APPROVAL", "FAILED", "REJECTED", "CANCELLED"}
METRIC_NAMES = (
    "relay_pipeline_jobs",
    "relay_tasks",
    "relay_worker_running",
    "relay_job_attempts",
    "relay_pipeline_stage_failures_total",
    "relay_gemini_usage_tokens",
)


def validate_origin(raw: str) -> str:
    parsed = urlsplit(raw)
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("Load target has an invalid port.") from error
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        parsed.scheme != ("http" if local else "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use a bare HTTPS origin (HTTP is allowed only for loopback development).")
    return raw.rstrip("/")


def read_metrics(client: httpx.Client, origin: str, headers: dict[str, str]) -> dict[str, list[str]]:
    response = client.get(f"{origin}/metrics", headers=headers)
    response.raise_for_status()
    values: dict[str, list[str]] = {}
    for line in response.text.splitlines():
        if line.startswith("#"):
            continue
        name = line.split("{", 1)[0].split(None, 1)[0] if line.strip() else ""
        if name in METRIC_NAMES:
            values.setdefault(name, []).append(line)
    return values


def submit_one(origin: str, token: str, timeout: float) -> tuple[str | None, float, int | None, str | None]:
    started = time.monotonic()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        with httpx.Client(
            timeout=httpx.Timeout(timeout, connect=min(timeout, 5.0)),
            follow_redirects=False,
            trust_env=False,
        ) as client:
            scenarios = client.get(f"{origin}/api/v1/scenarios", headers=headers)
            scenarios.raise_for_status()
            scenario = next((item for item in scenarios.json() if item.get("id") == SCENARIO_ID), None)
            if not isinstance(scenario, dict):
                return None, time.monotonic() - started, scenarios.status_code, "seeded checkout scenario is unavailable"
            submission_started = time.monotonic()
            submitted = client.post(
                f"{origin}/api/v1/tasks",
                json={"chat_message": scenario["bug_report"], "codebase": scenario["codebase"]},
                headers=headers,
            )
            if submitted.status_code != 202:
                return None, time.monotonic() - submission_started, submitted.status_code, f"submission returned HTTP {submitted.status_code}"
            payload = submitted.json()
            task_id = payload.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                return None, time.monotonic() - submission_started, submitted.status_code, "submission response omitted task ID"
            return task_id, time.monotonic() - submission_started, submitted.status_code, None
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return None, time.monotonic() - started, None, "request failed; response details suppressed"


def poll_tasks(origin: str, token: str, task_ids: list[str], timeout: float, poll_seconds: float) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    deadline = time.monotonic() + timeout
    states = {task_id: "PENDING" for task_id in task_ids}
    with httpx.Client(
        timeout=httpx.Timeout(min(10.0, timeout), connect=5.0),
        follow_redirects=False,
        trust_env=False,
    ) as client:
        while time.monotonic() < deadline:
            for task_id, state in list(states.items()):
                if state in TERMINAL_STATES:
                    continue
                try:
                    response = client.get(f"{origin}/api/v1/tasks/{task_id}", headers=headers)
                    response.raise_for_status()
                    task = response.json()
                    next_state = task.get("status")
                    if isinstance(next_state, str):
                        states[task_id] = next_state
                except (httpx.HTTPError, ValueError, TypeError):
                    states[task_id] = "POLL_ERROR"
            if all(state in TERMINAL_STATES or state == "POLL_ERROR" for state in states.values()):
                break
            time.sleep(poll_seconds)
    return states


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default=os.environ.get("RELAY_LOAD_URL", ""), help="bare API origin; defaults to RELAY_LOAD_URL")
    parser.add_argument("--token-env", default="RELAY_LOAD_TOKEN", help="environment variable containing the operator bearer token")
    parser.add_argument("--tasks", type=int, default=2, help=f"number of seeded tasks, 1-{MAX_TASKS} (default: 2)")
    parser.add_argument("--concurrency", type=int, default=2, help="maximum simultaneous submissions, 1-5 (default: 2)")
    parser.add_argument("--ramp-seconds", type=float, default=0, help="spread submissions across this many seconds (default: 0, immediate bounded burst)")
    parser.add_argument("--task-timeout", type=float, default=900, help="maximum seconds to await terminal task states (default: 900)")
    parser.add_argument("--poll-seconds", type=float, default=2, help="seconds between task status polls (default: 2)")
    parser.add_argument("--execute", action="store_true", help="send requests and create persistent tasks; without this flag only validate and print the plan")
    args = parser.parse_args()

    try:
        origin = validate_origin(args.origin)
    except ValueError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    if not 1 <= args.tasks <= MAX_TASKS or not 1 <= args.concurrency <= min(MAX_TASKS, args.tasks):
        print(f"BLOCKED: tasks must be 1-{MAX_TASKS}, and concurrency must be 1-{min(MAX_TASKS, max(args.tasks, 1))}.", file=sys.stderr)
        return 2
    if not 1 <= args.task_timeout <= 3600 or not 0.25 <= args.poll_seconds <= 30 or not 0 <= args.ramp_seconds <= 3600:
        print("BLOCKED: timeout/ramp must be 1-3600/0-3600 seconds and poll interval 0.25-30 seconds.", file=sys.stderr)
        return 2
    token = os.environ.get(args.token_env, "")
    if len(token) > 4096 or any(char in token for char in "\r\n"):
        print(f"BLOCKED: {args.token_env} must contain a valid bearer token.", file=sys.stderr)
        return 2
    print(f"Target: {origin}; scenario: {SCENARIO_ID}; tasks: {args.tasks}; submission concurrency: {args.concurrency}; ramp: {args.ramp_seconds}s.")
    if not args.execute:
        print("DRY RUN: no HTTP requests were sent. Review the profile, then add --execute to create persistent tasks and trigger provider/sandbox work.")
        return 0
    if not token:
        print(f"BLOCKED: set {args.token_env} in the protected environment before execution.", file=sys.stderr)
        return 2

    headers = {"Authorization": f"Bearer {token}"}
    try:
        with httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0), follow_redirects=False, trust_env=False) as client:
            before_metrics = read_metrics(client, origin, headers)
    except httpx.HTTPError:
        print("FAIL: could not read authenticated target metrics; response details suppressed.", file=sys.stderr)
        return 1

    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = []
        interval = args.ramp_seconds / max(args.tasks - 1, 1)
        for index in range(args.tasks):
            if index and interval:
                time.sleep(interval)
            futures.append(executor.submit(submit_one, origin, token, 10.0))
        results = [future.result() for future in futures]
    elapsed = time.monotonic() - started
    task_ids = [task_id for task_id, _, _, _ in results if task_id]
    latencies = [duration for _, duration, _, _ in results]
    errors = [error for _, _, _, error in results if error]
    states = poll_tasks(origin, token, task_ids, args.task_timeout, args.poll_seconds) if task_ids else {}
    metrics_after_error = False
    try:
        with httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0), follow_redirects=False, trust_env=False) as client:
            after_metrics = read_metrics(client, origin, headers)
    except httpx.HTTPError:
        after_metrics = {}
        metrics_after_error = True

    state_counts = Counter(states.values())
    submitted_count = len(task_ids)
    latency_sorted = sorted(latencies)
    p95_index = max(0, min(len(latency_sorted) - 1, int(0.95 * len(latency_sorted)))) if latency_sorted else 0
    report = {
        "target": origin,
        "scenario": SCENARIO_ID,
        "requested_tasks": args.tasks,
        "accepted_tasks": submitted_count,
        "submission_concurrency": args.concurrency,
        "submission_ramp_seconds": args.ramp_seconds,
        "submission_elapsed_seconds": round(elapsed, 3),
        "submission_latency_seconds": {
            "min": round(min(latencies), 3) if latencies else None,
            "median": round(statistics.median(latencies), 3) if latencies else None,
            "p95": round(latency_sorted[p95_index], 3) if latency_sorted else None,
            "max": round(max(latencies), 3) if latencies else None,
        },
        "final_task_states": dict(state_counts),
        "task_ids": task_ids,
        "metrics_before": before_metrics,
        "metrics_after": after_metrics,
        "metrics_after_error": metrics_after_error,
        "submission_errors": len(errors),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        print(f"{len(errors)} submission(s) failed; details suppressed.", file=sys.stderr)
    print("Tasks remain in the target database for normal operator review and retention handling.")
    all_terminal = all(state in TERMINAL_STATES for state in states.values())
    review_states = sum(count for state, count in state_counts.items() if state == "AWAITING_HUMAN_APPROVAL")
    return 0 if submitted_count == args.tasks and not errors and not metrics_after_error and all_terminal and review_states == args.tasks else 1


if __name__ == "__main__":
    raise SystemExit(main())
