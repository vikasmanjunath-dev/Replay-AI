# RELAY AI

RELAY AI is a local engineering workflow prototype that accepts a bug report and repository snapshot, runs an AI-assisted remediation pipeline, executes tests in an isolated sandbox when available, and presents evidence for human review.

The current build includes a React/Vite dashboard and a FastAPI backend. Task snapshots, source files, events, and jobs are stored in SQLite. A lifespan-managed worker claims queued jobs with leases, recovers abandoned work, supports stage-boundary cancellation, and allows bounded manual retries. By default, approve/apply/commit operate on a durable task-owned repository copy. Operators can optionally configure local Git targets for an explicit, base-checked apply and separate commit.

The implemented pipeline uses three model calls: triage; combined investigation and patch generation; and review. A deterministic sandbox runner executes tests, then a human operator decides whether to approve. The current status path is `QUEUED → RUNNING → TRIAGING → TRIAGED → INVESTIGATING → PATCHED → SANDBOX_RUNNING → SANDBOX_TESTED → REVIEWING → AWAITING_HUMAN_APPROVAL → APPROVED → APPLIED → COMMITTED`; terminal outcomes are `REJECTED`, `FAILED`, and `CANCELLED`. Stage labels and API states are distinct. The optional GitHub REST adapter reads configured repositories and opens a PR only for a human-approved, committed task after exact remote base/head SHA verification. The matching commit must already be published on the head branch; Relay does not push, merge, or deploy. An optional Switch connector posts outbound status and final review/test summaries after an owner provisions its agent and room.

## Run locally

Requirements: Node.js, Python 3.11+, Git, and (for isolated code execution) Docker.

1. Install frontend dependencies with `npm install`.
2. Create a Python environment in `relay-ai/` and install `pip install -r requirements.txt`.
3. Configure `GEMINI_API_KEY` in the backend environment. The provider defaults to `gemini-2.5-flash` and can be changed with `GEMINI_MODEL`.
4. Build the sandbox image: `docker build -t relay-ai-sandbox:python3.11 relay-ai/sandbox`. For production, capture its immutable ID with `docker image inspect --format '{{.Id}}' relay-ai-sandbox:python3.11` and set `RELAY_SANDBOX_IMAGE` to that `sha256:...` value.
5. Start the API from `relay-ai/`: `uvicorn main:app --host 127.0.0.1 --port 8000`. Running `python main.py` also binds to localhost by default; set `RELAY_HOST` to an IP address for another interface and configure `RELAY_API_TOKEN` or `RELAY_AUTH_USERS_JSON` before doing so.
6. Start the dashboard from the repository root: `npm run dev`.

## Development checks

Run the backend suite from `relay-ai/` after activating its Python environment:

```bash
python -m pytest tests -q
```

Run the dashboard storage regression tests, type check, and production build from the repository root:

```bash
npm test
npm run lint
npm run build
```

GitHub Actions runs these backend and frontend checks for pushes to `main`, pull requests, and manual dispatch. The default backend suite skips opt-in or environment-specific drills; follow the relevant instructions in `TRACKER.md` to run those separately.

For deployment, set `RELAY_ENV=production`; the backend then requires authentication and an explicit non-wildcard CORS origin allow-list and rejects unsafe host-subprocess mode. The systemd service template enables production mode.

The dashboard uses `VITE_API_URL` when set. Development defaults to `http://localhost:8000`; production builds use the current origin so the UI can sit behind the same reverse proxy as the API. Backend options include `RELAY_DB_PATH`, `RELAY_APPLIED_ROOT`, `RELAY_MAX_ACTIVE_TASKS_PER_OWNER`, `RELAY_CORS_ORIGINS`, `RELAY_API_TOKEN`, `RELAY_AUTH_USERS_JSON`, `RELAY_AUTH_ROLES_JSON`, `RELAY_SANDBOX_IMAGE`, and `RELAY_ALLOW_UNSAFE_SUBPROCESS`. `RELAY_MAX_ACTIVE_TASKS_PER_OWNER` defaults to 5 queued/running jobs per owner and accepts values from 1 to 1000; submissions over the cap receive HTTP 429. The cap is enforced transactionally in SQLite, so concurrent submissions cannot exceed it. `RELAY_API_TOKEN` provides one shared credential. For per-user ownership, configure `RELAY_AUTH_USERS_JSON` with username-to-unique-token mappings; it takes precedence over the shared token. Optionally assign `viewer` or `operator` roles with `RELAY_AUTH_ROLES_JSON`; when the role map is set, users omitted from it are viewers. Operators can submit, cancel, retry, approve, reject, apply, commit, and delete their own tasks. Viewers can inspect only their own task data. Enter the active token in the dashboard header; it stays in the browser tab session. Keep the subprocess option disabled when handling untrusted uploads: it runs uploaded code on the API host and is provided only for trusted local development.

## What is implemented

- JSON and ZIP repository submission with file/path/size limits.
- ASGI-level request-body caps before FastAPI parses JSON or multipart uploads.
- Background task execution with persisted task state and stage evidence.
- SQLite-backed worker queue with leases, stage-boundary cancellation, and bounded retry.
- Gemini structured-output triage, patch generation, and review.
- Patch check/application in a temporary workspace, followed by sandbox test execution.
- Task list/detail review UI, scenario loading, diff/evidence display, and human approve/reject/apply/commit actions.
- A seeded checkout scenario where a `$10` discount is subtracted twice from a `$100` cart. The expected baseline is one failing regression and one passing zero-discount test; the example fix makes both pass. See [`demo-store/README.md`](./demo-store/README.md).
- Three repeatable rehearsal commands are available: `scripts/rehearse_checkout_fixture.sh`, `scripts/rehearse_checkout_fake.sh`, and `scripts/rehearse_checkout_gemini.sh`. Run the fake-provider rehearsal with `--docker` and a digest-pinned `RELAY_SANDBOX_IMAGE` to exercise real isolation; the standard unit test remains deterministic, while a dedicated CI job builds the image and runs the Docker rehearsal. The live Gemini rehearsal requires credentials and Docker isolation and fails closed without either. Use `scripts/record_demo_backup.sh` to capture a local macOS backup recording; see [`demo-recordings/README.md`](./demo-recordings/README.md).
- Optional Switch room notifications post status-only updates through the official agent message endpoint; they do not read room events or start tasks. See the [backend README](./relay-ai/README.md) and tracker for setup and live-verification status.
- Optional local Git targets can be explicitly allow-listed, base-checked, applied to, and committed separately.
- Optional GitHub routes are `GET /api/v1/github/repositories/{id}`, `GET /api/v1/github/repositories/{id}/branches`, `GET /api/v1/github/repositories/{id}/contents?path=...`, and `POST /api/v1/tasks/{task_id}/pull-request`. Set `RELAY_GITHUB_TOKEN` and `RELAY_GITHUB_REPOSITORIES_JSON` only in the protected backend environment. Use a fine-grained token restricted to named repositories with Metadata read, Contents read, and Pull requests write permissions. The adapter validates approval evidence and exact base/head revisions before PR creation; it never pushes or merges.
- The task review dashboard exposes this PR flow for committed repository tasks, loads the configured repository's default branch, prepares an editable title/description from task evidence, provides copy controls for the exact commit/base SHAs, and restores created PR links from the task audit. The operator must publish the verified commit to the head branch first.
- Approval policy requiring a clean patch, passing tests, security `PASS`, and reviewer `APPROVE`.

## Current limits

- SQLite queueing and fixed-window rate limits suit a single host, not multi-instance production deployment.
- If Docker is unavailable, tests are not run unless `RELAY_ALLOW_UNSAFE_SUBPROCESS=true` is explicitly enabled.
- Apply and commit create a real Git commit in the task-owned copy; they do not change the original uploaded repository or a user's local checkout.
- The static token maps provide task ownership and optional viewer/operator roles for controlled deployments but do not include token rotation or external identity-provider integration. Multi-instance production queue/rate-limit operations and deployment hardening remain roadmap items.

Before exposing a deployment beyond localhost, review [THREAT_MODEL.md](./THREAT_MODEL.md) for assets, trust boundaries, residual risks, provisional service objectives, and required ownership assignments.

See [BLUEPRINT.md](./BLUEPRINT.md) for the product and target architecture, [PLAN.md](./PLAN.md) for the sequenced end-to-end release plan, [TRACKER.md](./TRACKER.md) for live implementation/blocker status, and [OPERATIONS.md](./OPERATIONS.md) for backup, restore, health, and recovery procedures.

Release verification steps and currently blocked host/owner actions are tracked in [`deploy/RELEASE_RUNBOOK.md`](./deploy/RELEASE_RUNBOOK.md) and [`deploy/RELEASE_BLOCKERS.json`](./deploy/RELEASE_BLOCKERS.json). Run `deploy/run_host_free_release_checks.sh` for local checks; run the target-host drill only after selecting a host and provisioning its protected environment. For H10 queue/load review, [`deploy/load_drill.py`](./deploy/load_drill.py) previews a bounded seeded-checkout profile without network access by default and can save execution evidence as JSON with `--report-file`. Execute it only after the service, data, and SLO owners approve the target and workload profile; `--execute` creates persistent tasks and invokes the configured model and sandbox. See the runbook for setup, evidence, and limitations.
