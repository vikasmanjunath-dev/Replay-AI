# RELAY AI Build Tracker

Last updated: 2026-11-24 (Asia/Kolkata)

## Status key

- `DONE` — completed and recorded.
- `READY` — may start when its stated context applies; not complete until evidence is recorded.
- `IN PROGRESS` — actively being implemented.
- `BLOCKED` — requires a decision or external dependency.
- `TODO` — not started.
- `DEFERRED` — intentionally postponed until its dependency or a demonstrated need exists.

## Current milestone: Single-host release planning — implementation baseline complete; target-host and owner gates remain open

## Follow-on milestone: Controlled single-host pilot — host-free preparation complete; release remains blocked pending H6/H10 evidence

Planning source: [`PLAN.md`](./PLAN.md) defines sequence, dependencies, acceptance evidence, and deferred work. The rows below remain the status ledger; a plan or code artifact alone does not close a host/owner gate.

## Current repository and release position

| Check | State | Evidence |
|---|---|---|
| Source baseline | READY | At planning start, `main` and `origin/main` both pointed to `2449185` (`chore: verify commit and push setup`); `git status` was clean. Planning edits are the only intended changes in this work pass. |
| Local MVP implementation | DONE | P0, P1, P2, P3, P4, and P5 implementation rows below are complete for the documented single-host scope. |
| Host-free release preparation | DONE | Release scripts, CI, preflight, runbooks, backup/restore drills, and blocker/signoff artifacts are present; run them against the actual release candidate before a release. |
| Production/pilot authorization | BLOCKED | No target host/hostname or named owners/data/SLO approvals are recorded. H6 and H10 rows below enumerate required evidence. |
| Push status | DONE | The previous local `main` and `origin/main` divergence is resolved; both point to `2449185` at this planning baseline (`0` ahead, `0` behind). |

## Next execution plan

| Plan ID | Work | Status | Dependency / closure evidence |
|---|---|---|---|
| NEXT-01 | Freeze release commit and rerun CI plus host-free release checks | IN PROGRESS | Push succeeded; remote `main` is `6806022594b1587e7fb09ea87001fc99b20065b1`. CI run `45436918585`: Python 3.11 failed test collection because `test_preflight.py` used f-string syntax unsupported by 3.11; Python 3.12 and frontend jobs passed. Rewrote the test fixture without nested f-string expressions. Local host-free suite passes: backend 130 passed/3 skipped, frontend 20, compile/lint/build, preflight 3 PASS/5 ACTION REQUIRED/1 MANUAL/0 FAIL. Push the fix and verify the new CI run. Docker daemon is unavailable, preventing sandbox image identity inspection. |
| NEXT-02 | Select target, hostname, owners, change window, and rollback path | BLOCKED | Service owner supplies H10-OWNERS information and selects the staging/production host and hostname. |
| NEXT-03 | Approve provider data use, SLOs, load profile, backup/RPO/RTO, and integration scope | BLOCKED | Data owner, security owner, and SLO/service owner record approval references and numeric thresholds; decide whether Switch/GitHub live checks are in scope. |
| NEXT-04 | Prepare isolated staging and protected configuration | BLOCKED | Start after NEXT-02 and NEXT-03 close; deployment owner provisions secrets, TLS/proxy, data/workspace/backup paths, alerting, monitoring, and target-built digest-pinned sandbox image; production preflight/readiness pass. |
| NEXT-05 | Complete target-host security, lifecycle, load, recovery, and accessibility drills | BLOCKED | Start after NEXT-04 closes; close applicable H6/H10 rows with named-owner evidence; resolve and retest release-blocking findings. |
| NEXT-06 | Run bounded pilot and sign go/no-go | BLOCKED | Start after NEXT-05 closes; named service, security, operations, and data owners review pilot evidence, residual risks, rollback readiness, and sign the release record. |
| NEXT-07 | Select advanced capabilities from pilot evidence | DEFERRED | Choose only roadmap items A1–A8 in `PLAN.md` whose demand trigger is evidenced; approve owner, scope, threat review, migration/rollback, and measurable acceptance targets before implementation. |

The detailed procedure and pass/fail conditions are in [`PLAN.md`](./PLAN.md). Optional Switch delivery and GitHub live PR verification are required only when the corresponding integration is enabled for the release; never provision credentials in chat or commit them.

## Advanced feature backlog

These are deliberately deferred until their triggers are evidenced after the pilot. See the detailed scope and acceptance criteria in [`PLAN.md`](./PLAN.md#8-advanced-feature-roadmap-after-the-pilot).

| ID | Feature | Status | Start trigger |
|---|---|---|---|
| ADV-01 | Data governance and tenant lifecycle | DEFERRED | Approved broader source-data classes or contractual retention/deletion requirements |
| ADV-02 | Enterprise identity and repository policy | DEFERRED | Static token administration fails an evidenced federation, revocation, or access-review need |
| ADV-03 | Shared persistence and queue | DEFERRED | Pilot exceeds accepted single-host throughput or availability targets |
| ADV-04 | Stronger sandbox isolation tiers | DEFERRED | Security review or approved pilot scope requires isolation beyond current container controls |
| ADV-05 | Durable observability and SLO operations | DEFERRED | Owners need retained service-wide SLO reporting or actionable paging |
| ADV-06 | Pipeline policy and cost controls | DEFERRED | Pilot records repeated unsafe patches, provider failures, or material cost variance |
| ADV-07 | Team review and change workflow | DEFERRED | Named pilot users require shared ownership or separation of duties |
| ADV-08 | Additional source-control providers | DEFERRED | A named customer/pilot requires another provider |

## User-directed priority queue

| ID | Task | Status | Evidence / next step |
|---|---|---|---|
| P-A1 | Seed the deck's double-discount checkout bug and expose it as a dashboard scenario | DONE | `demo-store/src/checkout.py` and its regression test reproduce the `$100 - $10 - $10 = $80` defect. Re-ran `scripts/rehearse_checkout_fixture.sh`: the temporary-copy red/green fixture suite passed (2 tests); no demo source was modified by the rehearsal. |
| P-A2 | Run the checkout scenario end to end with fake provider and Gemini | BLOCKED | Fake-provider API/worker rehearsal re-ran successfully in this session: task reached `AWAITING_HUMAN_APPROVAL`, the exact one-file patch passed both fixture tests in a temporary `subprocess_dev` workspace, and no operator action occurred. This is local fixture evidence, not Docker isolation. Exact ask for live Gemini/Docker: configure `GEMINI_API_KEY` for the backend and provide an available Docker daemon with the prebuilt sandbox image. Neither is available here. |
| P-A3 | Add three demo rehearsal scripts and a backup recording path | DONE | Added fixture, fake-provider, and live-Gemini/Docker rehearsal commands with executable scripts and contract tests; live path checks for required key and strict Docker isolation before submitting work. Added timestamped macOS screen-recording command and retention/privacy notes. Recording capture itself was not run. |
| P-B1 | Add a replaceable Switch chat connector based on official docs | DONE | Optional outbound Switch notifier uses the documented agent message endpoint; posts content-minimal progress and final test/security/reviewer summary. Failed sends are not cached as delivered; URL/key bounds, port and whitespace/control checks fail closed; config representations omit the API key. Successful progress/final deduplication uses a bounded cache; delivery failures produce a safe task-ID warning. The mocked protocol/configuration suite currently passes 20 tests. No SDK is claimed and no inbound message subscription is implemented. |
| P-B1-LIVE | Verify delivery to a provisioned Switch room | BLOCKED | Exact ask: have the Switch agent owner provision an agent API key and provide the approved Switch bridge base URL, agent ID, and room ID through the protected service environment. The credential is not needed in chat. |
| P-B2 | Add a least-privilege GitHub read/PR adapter | DONE | Added operator-only allow-listed metadata/file reads, exact remote base/head comparison, approved-task PR creation, idempotency and audit. File paths and optional content refs are bounded/validated before network access; invalid branch input returns 400. Allow-list parsing rejects duplicate IDs; PR responses require a positive integer number and `open`/`closed` state. Viewer access is denied before adapter configuration is loaded. Fine-grained permissions documented. Branch must already be published; no push, merge, or deploy. Latest full backend suite: 128 passed/3 skipped. |
| P-B2-UI | Expose the guarded GitHub PR flow in task review | DONE | Operators can select from up to 100 validated branch name/SHA suggestions or enter a name; the UI previews whether selected remote SHAs match task provenance and can refresh that preview after publishing, while the API rechecks before PR creation. It also validates repository metadata, prefills bounded PR text, announces errors accessibly, copies exact task SHAs, submits idempotently, and restores the PR link from audit history. `npm run lint`, `npm run build`, and Python compilation pass. |
| P-B2-LIVE | Verify read and PR creation against GitHub | BLOCKED | Exact ask: configure `RELAY_GITHUB_TOKEN` in the protected backend environment with access limited to the selected test repository and `RELAY_GITHUB_REPOSITORIES_JSON`; provide a published test branch whose head SHA equals a passing, approved task commit and an unchanged expected base SHA. No credentials belong in chat. |
| P-B3 | Align pitch claims with implemented lifecycle states and actual agent count | DONE | Final 14-slide deck: `deliverables/RELAY_AI_Hackathon_Pitch_Deck_Aligned_v3.pptx`. Slide 7 and notes describe the optional GitHub adapter, existing published branch requirement, exact SHA check, human approval, and no push/merge/deploy. All 14 slides rendered; changed architecture slide visually inspected; package/layout/import validation passes with zero layout warnings. Regression test checks deck text/notes. |
| P-C1 | Prepare deployment-host and owner release drills | DONE | Added `deploy/RELEASE_RUNBOOK.md`, a nine-item `deploy/RELEASE_BLOCKERS.json` matrix, host-free and target-host scripts, and mocked target-smoke/checklist tests. Ran the host-free suite successfully. No target was accessed or modified. |
| P-D1 | Complete keyboard/screen-reader, mobile, contrast, empty/error-state, and queue-load reviews | BLOCKED | Local evidence: browser-tested skip link moves keyboard focus to main content with a visible 3px ring; automated focus/error/mobile/reduced-motion/empty-state checks pass; widths 320, 390, 768, and 1280 have no overflow; sampled light/dark text ratios meet 4.5:1. Exact remaining asks: assign a screen-reader reviewer and browser/AT pair (H10-ACCESSIBILITY-REVIEW), and select a host plus approved load profile (H10-LOAD-REVIEW). |
| P-D2 | Make API connection failures clear and actionable in the dashboard | DONE | Added shared network-error formatting across task refresh, submission, operator actions, deletion, and patch download. Browser-specific fetch failures now name the RELAY AI API and next step; API validation and request-ID details are preserved. Browser accessibility snapshot confirmed the updated offline message and retry/dismiss controls. Regression tests pass. |
| P-D3 | Guard sampled dark-theme text contrast against regressions | DONE | Added frontend contrast tests for muted/secondary text and offline readiness/detail text against the actual dark theme tokens and alpha-composited notice background. All sampled combinations meet the 4.5:1 normal-text threshold; this does not certify every UI color pairing. |
| P-D4 | Check responsive dashboard width boundaries | DONE | Inspected browser layout at 320×800, 390×844, 768×900, and 1280×900. Document/body widths matched the viewport at all four sizes; no horizontal overflow. The browser was returned to its default viewport afterward. |
| P-D5 | Extend sampled contrast regression coverage to light mode | DONE | The contrast test now checks muted and secondary text plus offline notice/detail colors in both light and dark themes, including the parent's translucent notice background. All sampled pairings pass 4.5:1; full color inventory still needs owner review. |
| P-D6 | Align session badge with offline and degraded readiness states | DONE | Added `getSessionBadgeLabel()` to show API offline, authentication required, or session unavailable when readiness determines that state. Unit tests cover authenticated and unavailable states; the browser accessibility snapshot now reports “API offline” when readiness is OFFLINE rather than “Connecting.” |
| P-D7 | Audit keyboard access for the offline viewer state | DONE | Browser Tab traversal reached the skip link, visible task filters, API token field, save/refresh/appearance controls, retry, and dismiss; each observed focus stop displayed a 3px outline. Task submission remains hidden because API failure leaves the viewer role unresolved; native screen-reader signoff remains blocked under H10-ACCESSIBILITY-REVIEW. |
| P-D8 | Exercise local queue claims under concurrent worker load | DONE | Expanded the temporary-SQLite drill to 64 queued jobs drained by 16 concurrent store instances. Three consecutive fresh-database runs passed (1 test each, 0.41s/0.43s/0.37s). Every job was claimed once at attempt 1, claim events preceded ingestion events, and no jobs remained. This is a short local correctness burst, not sustained throughput or target-host capacity. |
| P-D9 | Bound queued/running task admission per owner | DONE | `RELAY_MAX_ACTIVE_TASKS_PER_OWNER` defaults to 5 (range 1–1000); transactional SQLite admission protects JSON and ZIP submissions and returns HTTP 429 over cap. Focused tests cover API rejection for both submission forms and two concurrent store instances admitting exactly one task. This is single-host protection; H10 load review remains required. |
| CMT-01 | Commit the verified dashboard reliability increment | DONE | Explicit user authorization received for the reliability-only commit on `main`; committed as `87f4930` (`fix: harden dashboard state and preflight boundaries`). No push performed. |
| CMT-02 | Commit the seeded demo and rehearsal increment | DONE | User approved the exact commit on `main`, based on `87f4930`; committed as `fc0070b` (`feat: add repeatable seeded checkout demo`). No push performed. |
| CMT-03 | Commit the Switch adapter increment | DONE | Completed as `ac6a50a` (`feat: add Switch room status notifications`), including the hardening follow-up and worker integration. |
| CMT-04 | Commit pitch and lifecycle claim alignment | DONE | Completed as `39959e5` (`docs: align pitch deck with implemented workflow`); deck and claim regression are committed. |
| CMT-05 | Commit GitHub adapter and documentation | DONE | Adapter completed as `f77bf41`; integration/release docs completed as `a80c33a`. |
| CMT-06 | Commit release readiness pack | DONE | Completed as `3a7393f` (`feat: prepare host-free release readiness drills`). |
| CMT-07 | Commit dashboard PR and accessibility improvements | DONE | Completed as `326221f` (`feat: improve dashboard review and recovery flows`). |
| CMT-08 | Push feature chunks to origin/main | DONE | The previous divergence is resolved: `main` and `origin/main` both point to `2449185` at the 2026-11-24 planning baseline. The former approval-review block is closed; no push is pending. |

| ID | Task | Status | Evidence / next step |
|---|---|---|---|
| H1 | Enforce safe production startup configuration | DONE | `RELAY_ENV=production` requires authentication and explicit non-wildcard CORS origins, rejects unsafe host subprocess mode, and is enabled by the systemd template. Direct `python main.py` startup defaults to loopback and requires auth for non-loopback binds. |
| H2 | Pin and document sandbox image provenance | DONE | Dockerfile pins the official Python 3.11.18 slim Trixie multi-platform digest and pytest 8.3.5; production mode requires a full local image ID or registry digest. Runbook captures the image ID after build. |
| H3 | Define reverse-proxy deployment limits | DONE | Added Nginx TLS/proxy examples with body caps matching API routes, per-IP request/connection limits, timeouts, and overwritten forwarded headers. Uvicorn explicitly trusts only loopback. Multipart legacy `/tasks/submit` is now recognized by the backend body limiter. Host-specific Nginx syntax and real-IP configuration still require deployment-owner review. |
| H4 | Enforce production authentication and CORS configuration | DONE | Production mode already requires authentication and explicit CORS; it now validates every CORS entry as a bare HTTPS origin without credentials, wildcard, whitespace, path, query, or fragment. Host-side end-to-end auth/CORS verification remains in H10. |
| H5 | Harden patch boundaries against hostile diffs | DONE | Generated patches are capped at 1 MiB; scope validation rejects duplicate file sections, mode changes, renames/copies, binary patch sections, unsafe paths, undeclared paths, and non-snapshot targets. Request-level adversarial verification remains under H10. |
| H6 | Verify sandbox isolation on the deployment host | BLOCKED | The opt-in isolation probe passed on local Colima Docker 29.5.2, but this does not verify the deployment host. Exact ask: select a deployment host and authorized operator; build/use the pinned image there, run `deploy/run_target_host_drills.sh`, and record the sanitized result and image digest. |
| H7 | Verify worker concurrency and recovery | DONE | Added and passed durable-store drills for expired-lease recovery after reopening SQLite, cancellation winning a completion race, and retry exhaustion at the configured attempt bound. See `relay-ai/tests/test_recovery_drills.py`. |
| H8 | Rehearse configured Git target operations | DONE | Added and passed disposable-repository drills for stale-base rejection, snapshot matching, changed-file-only commit, recovery after staging, and idempotent recognition after a commit acknowledgement loss. See `relay-ai/tests/test_repository_drills.py`. |
| H9 | Complete backup restore and alerting drill | DONE | Created, verified, and restored an archive into isolation; task history, source snapshot, and applied workspace survived. A stale archive produced the failing monitoring result and the configured webhook POST reached a loopback drill receiver. Configure and rehearse the actual production destination under H10. See `relay-ai/tests/test_backup_drills.py` and `relay-ai/tests/test_backup_alert.py`. |
| H10 | Complete release verification and ownership review | BLOCKED | Host-free security/tests, preflight, CI checks, Nginx template validation, backup/restore drills, and a sign-off template are prepared. Exact asks are itemized as `H10-*` rows below and in `deploy/RELEASE_BLOCKERS.json`: select target/hostname, run target proxy/auth/CORS/load/accessibility/backup/restore checks, assign primary/backup/security/SLO owners, obtain Gemini data-use approval, and return sanitized evidence references. No deployment target has been selected. |
| H10-PROXY-AUTH-CORS | Verify production reverse proxy, auth, and CORS | BLOCKED | Exact ask: choose public hostname and target; configure production authentication and HTTPS CORS in protected service env; install Nginx with real cert paths; run `nginx -t` and `deploy/run_target_host_drills.sh`; record sanitized evidence. |
| H10-BACKUP-ALERT | Verify production backup alert delivery | BLOCKED | Exact ask: assign the alert receiver/owner, store its HTTPS webhook in the host secret manager, trigger one freshness-alert drill, and record confirmation without the URL. |
| H10-RESTORE-DRILL | Restore a production backup in isolation | BLOCKED | Exact ask: name the recovery operator and approve a maintenance window; restore a selected production archive to a new isolated path, verify SQLite/task/workspace integrity, and record archive reference/outcome. |
| H10-ACCESSIBILITY-REVIEW | Complete owner keyboard and screen-reader review | BLOCKED | Local evidence: keyboard activation of the skip link moved focus to `main#main-content` with a visible 3px ring; the browser accessibility snapshot announced API OFFLINE and the named retry/dismiss controls; widths 320, 390, 768, and 1280px have no horizontal overflow; sampled light/dark text ratios exceed 4.5:1. Exact remaining ask: assign a reviewer and browser/assistive-technology pair; complete full keyboard traversal and native screen-reader review (including focus order and announcements), record browser/AT versions, defects, and retests. |
| H10-LOAD-REVIEW | Complete target-host queue/load review | BLOCKED | Exact ask: choose target host and approve concurrency, ramp, duration, and latency/error thresholds; run the load drill and record resource/API results. |
| H10-OWNERS | Assign service and escalation owners | BLOCKED | Exact ask: name primary operator, backup operator, security contact, incident path, and change/rollback owner. |
| H10-GEMINI-DATA-APPROVAL | Approve provider source-data handling | BLOCKED | Exact ask: obtain the data owner's written approval for report/repository data sent to Gemini, including applicable handling and retention terms; record only the approval reference. |
| H10-SLO-ACCEPTANCE | Accept operational service objectives | BLOCKED | Exact ask: assign an SLO owner and obtain service-owner acceptance of availability, completion, queue-latency, recovery-point, and recovery-time objectives or revised thresholds. |

| ID | Task | Status | Evidence / next step |
|---|---|---|---|
| P0-01 | Write product and engineering blueprint | DONE | [`BLUEPRINT.md`](./BLUEPRINT.md) |
| P0-02 | Fix Python Gemini SDK method name | DONE | Changed orchestrator to call `models.generate_content`, matching the Python SDK. |
| P0-03 | Gate approval on sandbox/reviewer evidence | DONE | Approval requires clean patch application, passing tests, security `PASS`, and reviewer recommendation `APPROVE`; task status mutations now use the centralized allowed-transition graph. |
| P0-04 | Harden ZIP limits and normalized path checks | DONE | Implementation includes 25 MiB ZIP file/expanded caps, 500-entry cap, bounded streaming reads with declared-size consistency, 2 MiB/member cap, 1.5 MB aggregate model context cap, 10 MiB JSON/26 MiB multipart/1 MiB other-write ASGI body caps, NFC/case-fold path normalization, file/directory collision rejection, portable filename rules, regular-file/directory-only ZIP entry types, and canonical patch target checks. Request-level checks now cover traversal, aliases, entry types, malformed archives, and upload/member/expanded-size limits under H10. |
| P0-05 | Clarify/implement apply and commit behavior | DONE | Approval-gated apply and real commit operate in a durable task-owned repository copy; original upload is preserved and a patch download is available. |
| P0-06 | Add fake provider seam for deterministic local pipeline | DONE | `StructuredProvider`, Gemini adapter, and explicitly configured fake adapter are in `relay-ai/providers.py`. The fake provider now drives the durable-worker/API end-to-end journey in `relay-ai/tests/test_pipeline_e2e.py`. |
| P0-07 | Update docs to match implemented behavior | DONE | Root and API READMEs now describe the current prototype, setup, limitations, and routes. |

## Backlog

| ID | Task | Status | Milestone |
|---|---|---|---|
| P1-01 | Durable task and event persistence | DONE | Local MVP persists task, immutable source snapshot, initial events, and job atomically; task deletion rechecks queue inactivity transactionally; events/actions are append-only and paginated. Schema upgrades use a v9 compatibility baseline plus numbered v10 digest migration in a serialized transaction and reject newer schemas. Retention is implemented separately; migration rollback and recovery verification remain under P1-02/P4-02. |
| P1-02 | Background worker and queue | DONE | Local MVP worker claims SQLite jobs with attempt-number leases; progress writes, heartbeats, and final task/job completion are fenced and final state is committed atomically. Recovery reconciles persisted terminal state before replaying; expired leases recover and retries are bounded. Independent SQLite stores have a concurrency drill proving unique claims and ordered persisted events; injected worker failures persist a terminal job/task state, durable failure event, and redacted diagnostic. Multi-host queues are out of scope. |
| P1-03 | Progress polling/event stream, cancellation, retry, pagination | DONE | Local MVP includes dashboard polling, queue/stage lifecycle statuses with centralized transition validation, task/event/action pagination, stage-boundary cancellation, manual bounded retry, and replayable idempotency keys. SSE is unnecessary for current polling UI; fault/recovery verification remains in the P1-02 gate. |
| P1-04 | Structured logs, readiness, limits, and retry policy | DONE | Local MVP includes JSON application logs with best-effort credential redaction (configured credentials, common token formats, and exception tracebacks covered in `relay-ai/tests/test_redaction.py`), request IDs, per-process API request counts/latency histograms (label normalization and exposition covered in `relay-ai/tests/test_request_metrics.py`), readiness checks, request limits, worker exception logs, fenced leases, bounded provider retry/backoff (transient retry, non-retryable failure, and exhaustion covered in `relay-ai/tests/test_provider_resilience.py`), Prometheus queue/task/worker/provider usage gauges, optional operator-priced cost gauge, queue-wait/stage-duration histograms, rolling 30-day pipeline completion SLI, attempt/stage failure counts, and sandbox mode/outcome counts. API request metrics reset on process restart; retained service-wide history needs an external collector. `relay_pipeline_completion_sli_ratio` is regression-tested in `relay-ai/tests/test_pipeline_sli.py`; long-term reporting requires an external metrics store because owner deletions remove rows from its cohort. |
| P2-01 | Hardened sandbox adapter; fail closed without isolation | DONE | Local MVP has prebuilt image discovery with no runtime pulls, no-network/read-only/non-root container settings, OS-limited captured output files, core dump disabling, allow-listed fixed-argv `pytest` and `unittest` profiles, and fail-closed behavior. Deployment-host isolation verification remains under P4-02. |
| P2-02 | Immutable repository snapshot and patch scope validation | DONE | Source snapshots are digest-checked and immutable after first storage; normalized patch targets, diff/unified headers, declared files, and submitted paths must agree. Unsafe paths, duplicate declarations, and more than 25 files are rejected. Hostile-input verification remains under P0-04. |
| P2-03 | Authorized target worktree apply and real commit | DONE | Local MVP supports optional `RELAY_REPOSITORIES_JSON` allow-listed Git targets, dashboard selection, clean-base/revision checks, changed-file snapshot matching, separate apply/commit, changed-file-only staging, commit provenance, task-delete/retention protections, and persisted apply/commit recovery markers. Remote Git providers are a future extension; target apply/commit and interruption recovery still require execution-level verification under P4-02. |
| P3-01 | Task submission, list, detail, and event timeline UI | DONE | Local MVP dashboard supports JSON/ZIP submission, owner-scoped search/status filters, 50-item server pagination with total counts, task detail, independently paginated 50-event history with authoritative counts, owner-authorized deletion, and accessible codebase input selection. Cross-device visual/accessibility review remains under P3-03. |
| P3-02 | Diff/evidence review and approval UI | DONE | Local MVP displays diff, exact sandbox test command, separate stdout/stderr, reviewer evidence, per-call token and optional cost details, paginated operator action audit, approve/reject/apply/commit controls, optional decision notes, custom commit message, commit hash/message, and patch download. Cross-device visual/accessibility review remains under P3-03. |
| P3-03 | API integration and responsive/error states | DONE | Vite UI uses the `/api/v1` contract, polls in-flight tasks, handles loading/empty/error states, provides responsive task/token/action controls, and surfaces live API readiness as ready, degraded, offline, or authentication required. `relay-ai/tests/test_pipeline_e2e.py` verifies the API/worker journey from submission through review, human approval, task-copy apply, and a real Git commit with deterministic model output. Cross-device visual and assistive-technology review remains under P4-02. |
| P4-01 | Authentication and per-task authorization | DONE | Local MVP supports unique per-user bearer tokens, owner-scoped task access, optional viewer/operator roles, and shared-token/local development modes. Token rotation, external identity provider integration, and broader production access-control policy remain under P4-02. |
| P4-02 | Retention, observability, deployment, backup, runbooks | DONE | Local MVP includes owner-controlled deletion and dry-run-first retention, verified SQLite/workspace backups, non-destructive isolated restore tooling, backup-age CLI/systemd timers, service templates, restore/recovery runbook, threat model/SLOs, schema visibility, Prometheus metrics including the provisional completion SLI, local rate limits, and configured-repository audit protections. A deployment record template captures remaining host-specific ownership, socket policy, alert delivery, and restore-drill signoff; those operator-run steps are required before production exposure. |
| P5-01 | Automate backend and frontend verification in CI | DONE | `.github/workflows/ci.yml` runs the backend pytest suite on Python 3.11/3.12, compiles backend modules, checks frontend storage tests/TypeScript/build, and validates the deployment preflight JSON using an explicitly provisioned Python 3.12 runtime on pushes to `main`, pull requests, and manual dispatch; jobs use read-only repository permissions, bounded runtimes, and cancel superseded runs. Root README documents matching local commands. |
| P5-02 | Handle restricted browser storage gracefully | DONE | Dashboard reads/writes/removals for theme, API token, and action idempotency keys are guarded against storage access exceptions. Theme falls back to system mode; session values use an in-memory fallback for the current page, and token-save feedback explains whether the browser persisted the value or it is memory-only. Node built-in regression tests cover allowed, denied, quota, and stale-removal cases and run in CI. |

## Update log

### 2026-11-24 — Plan advanced post-pilot capabilities
- Added deferred roadmap items ADV-01–ADV-08 for data governance, enterprise identity, shared persistence/queue, sandbox tiers, durable observability, policy/cost controls, team review, and additional source-control providers.
- Each item has a demand trigger and acceptance evidence in `PLAN.md`; `TRACKER.md` links the backlog. No implementation starts before measured pilot demand and owner-approved scope.

### 2026-11-24 — Verify NEXT-01 against the configured remote
- Corrected the prior CI lookup target: the configured remote is `vikasmanjunath-dev/Replay-AI`. Its `main` remains at `2449185`; the exact candidate `ee827e4b3c72` has zero commit statuses and zero Actions runs. The connected GitHub account has read-only permission, so it cannot publish a candidate to trigger CI.
- Docker sandbox image identity remains unverified because the local Docker daemon is unavailable. NEXT-01 is BLOCKED; no candidate freeze is claimed.

### 2026-11-24 — Fix Python 3.11 CI test collection
- Push of `6806022` triggered workflow run `45436918585`: frontend and Python 3.12 passed, while Python 3.11 failed parsing nested f-string expressions in `relay-ai/tests/test_preflight.py`.
- Replaced those expressions with a shared plain-loop Nginx fixture helper. Focused Python 3.11 tests pass (9); the full local release check passes on Python 3.12 (130 backend passed/3 skipped, 20 frontend passed, compile/lint/build passed, preflight 3 PASS/5 ACTION REQUIRED/1 MANUAL/0 FAIL). CI rerun on the fix remains required.

### 2026-11-24 — Run host-free release checks for NEXT-01
- The first run found three ZIP test doubles that did not accept the new active-task-limit keyword; updated them to match the storage API.
- Rerun passed: backend 130 passed/3 skipped, frontend 20 passed, Python compilation, TypeScript lint, Vite production build, and `git diff --check`; deployment preflight returned 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. This is a dirty-tree diagnostic, not a frozen release-candidate result.
- Connected GitHub workflow-run lookup for baseline `2449185` returned 404; CI evidence remains unconfirmed.
- NEXT-01 remains IN PROGRESS until a clean release revision, CI evidence, and artifact/image identities are selected.

### 2026-11-24 — Re-run NEXT-01 on a clean candidate
- Committed the active-task limit (`4170515`), GitHub revision preview (`f5ca1f0`), and release-plan/docs updates (`564d8ba`) as separate chunks. No push performed.
- On clean candidate `564d8ba8cb865513dbc9715c92cca1eb281154bd`, host-free suite passed: backend 130 passed/3 skipped, frontend 20 passed, compile/lint/build passed; preflight 3 PASS/5 ACTION REQUIRED/1 MANUAL/0 FAIL. Frontend build artifact hashes are recorded in NEXT-01 above.
- GitHub CI/status calls for this repository returned 404. Docker image inspection was denied by the local Docker socket. NEXT-01 remains IN PROGRESS pending those identities; target host/owners remain release blockers.

### 2026-11-24 — Preview GitHub branch SHA matches before PR creation
- Branch suggestions now include validated remote commit SHAs. The dashboard shows whether the selected head/base currently match the task commit/base and can refresh the list after branch publication; this is advisory because the API still performs the authoritative comparison when creating a PR.
- No GitHub request was made; lint/build and Python compilation pass.

### 2026-11-23 — Add GitHub branch suggestions to PR creation
- Added an operator-only, allow-listed branch-list API backed by GitHub's List branches endpoint. Responses are capped to one 100-branch page and branch names/full commit SHAs are validated; the dashboard exposes names as suggestions while preserving free-text entry.
- Updated GitHub API documentation and token permission notes. No live GitHub call was made.

### 2026-11-23 — Record feature commits and push review block
- Updated CMT-03 through CMT-07 to DONE with commit references for Switch, GitHub, release readiness, pitch, and dashboard chunks. Recorded the automatic approval review's rejection of `git push origin main`, which cited exporting potentially nonpublic repository contents to an unverified remote and updating the shared default branch.
- Added separate backend and dashboard commits for validated GitHub branch suggestions, with API and permission details in both READMEs. At that time the local commits remained ahead of `origin/main`; see the 2026-11-24 synchronization entry for the current state.

### 2026-11-24 — Synchronize release plan and repository status
- Verified `main` and `origin/main` both point to `2449185` with zero ahead/behind commits and a clean checkout before documentation changes. Closed CMT-08; the earlier push-review block is historical and no push is pending at this baseline.
- Replaced the stale MVP build roadmap with the current single-host release sequence and created [`PLAN.md`](./PLAN.md) covering owners/decisions, staging, target-host drills, pilot, acceptance evidence, rollback triggers, and deferred scale work.
- No tests, deployment, host access, live integration calls, or external-state changes were performed in this planning pass. Release-host and named-owner gates remain BLOCKED.

### 2026-11-24 — Bound queued task admission per owner
- Added an owner-scoped maximum for queued/running tasks, configurable with `RELAY_MAX_ACTIVE_TASKS_PER_OWNER` (default 5, range 1–1000). SQLite checks the active count inside the same `BEGIN IMMEDIATE` transaction that stores the task, snapshot, events, and queue record, preventing concurrent API processes from racing past the cap. JSON and ZIP APIs return HTTP 429 when an owner is at capacity.
- Updated setup/security docs. Added focused coverage for JSON/ZIP HTTP 429 behavior and simultaneous submissions through separate SQLite store instances; exactly one request is admitted at a cap of one. Focused suite: 2 passed. The cap is local to one SQLite database and is not a multi-host quota.

### 2026-11-22 — Add dashboard controls for verified GitHub PR creation
- Added an operator-only PR form for committed repository tasks. It loads and validates allow-listed repository metadata/default branch, prefills an editable title and description from task evidence once commit evidence is ready, collects the already-published head branch and draft preference, shows the expected base revision with copy controls for the exact commit/base SHAs, explains the SHA verification requirement, sends an idempotent request to the guarded API, and displays the returned GitHub link. The link is recovered from action audit history after reload, and external URLs are constrained to `https://github.com`. A non-allow-listed local repository gets an inline configuration hint. Updated the root README to describe the dashboard flow.
- `npm run lint` and `npm run build` passed. No live GitHub request was made; the existing P-B2-LIVE requirement for a provisioned test repository and protected token still applies.

### 2026-11-10 — Review dashboard accessibility states and 390px layout
- Added `tests/frontend/accessibilityReview.test.mjs` checks for skip navigation and focus indicators, readiness and request-error announcements, mobile breakpoints, reduced-motion rules, and visible empty-state copy.
- Inspected the open dashboard at 320×800, 390×844, 768×900, and 1280×900. Document/body widths matched each viewport with no horizontal overflow; the browser viewport was reset afterward. At 390px, the API-offline alert/retry, fetch error/dismiss control, empty task list, and empty results state were visible. The browser accessibility tree exposed the skip link, named controls, alert, filters, retry, and empty content. The API remained offline, so no connected task workflow was exercised.
- Added `tests/frontend/themeContrast.test.mjs` for muted/secondary and offline notice/detail text in light and dark themes, with alpha compositing over the actual base canvas. All sampled combinations pass 4.5:1. The measured dark ratios were muted 7.64:1, secondary 12.92:1, offline notice 8.37:1, and offline detail 7.02:1; this sample is not a complete contrast audit. Hands-on keyboard traversal and native screen-reader review were not performed; exact owner/reviewer ask remains in H10-ACCESSIBILITY-REVIEW. Target-host load review remains blocked on an approved target and profile under H10-LOAD-REVIEW.
- Verification: latest `deploy/run_host_free_release_checks.sh` passed: backend 96 passed/3 skipped (one existing Starlette/httpx deprecation warning), frontend 20 passed/0 failed, compileall, TypeScript lint, Vite build, and `git diff --check`; release preflight reported 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. During iteration, initial selector/background test assertions failed; corrected both to match the actual markup and style inheritance and reran successfully. No host work, task mutation, push, or deployment was performed.
- P-D1 is now BLOCKED only for the named-owner screen-reader/keyboard signoff and target-host queue-load review. Continued with locally actionable P-D2 dashboard error copy.
- P-D2: browser network errors now produce a stable actionable RELAY AI API message across refresh and user actions; useful API errors remain unchanged. Verified the updated offline error in the browser accessibility snapshot.
- P-D3: added `tests/frontend/themeContrast.test.mjs`; the sampled dark theme text and offline notice combinations pass a WCAG AA 4.5:1 minimum. One initial contrast-test run found that the detail text inherits its background from its parent notice; updated the test to composite it against that actual parent background and reran successfully.
- P-D4: checked 320, 390, 768, and 1280px browser widths; no horizontal overflow at any size; reset the viewport.
- P-D5: extended contrast regression tests to light and dark themes; 18 frontend tests now pass.
- P-D6 plan: show API offline instead of Connecting when readiness has failed; touched `src/App.tsx`, `src/dashboardLabels.js`, its frontend test, and this tracker; verify unit and host-free suites plus the rendered accessibility snapshot.
- P-D6 verified: offline session badge shows `API offline` in the browser accessibility snapshot; keyboard Tab exposed the skip link with a 3px focus ring, and Enter moved focus to `main#main-content`. Full native screen-reader review remains blocked under H10-ACCESSIBILITY-REVIEW.
- P-D7: traversed every keyboard-operable control exposed in the offline viewer state. The sequence reached the skip link, task filters, token/save/refresh/appearance, readiness retry, and error dismissal with visible 3px focus rings. The submission form is not rendered for the viewer role; no API task operation was attempted. Native screen-reader review still requires the assigned owner.
- P-D8: ran `test_concurrent_worker_claims_are_unique_and_persist_ordered_events` (1 passed, 0.28s). Eight simultaneous SQLite store instances claimed eight temporary jobs exactly once. This does not establish sustained queue throughput; H10-LOAD-REVIEW remains blocked until a target and approved load profile are provided.

### 2026-11-10 — Bound GitHub content refs and harden branch validation
- Code review found the GitHub contents adapter validated paths but forwarded optional `ref` values without a length or Git-ref check. Added the same conservative 240-character ref validation used for branches before any network call, including rejection of trailing-dot ref components.
- Added regressions proving oversized/traversal refs and invalid PR branch names fail before GitHub access, and that the API reports invalid branch input as HTTP 400. Exact SHA checks and the human approval gate remain unchanged.
- Added a route-level regression confirming invalid contents refs are returned as HTTP 400 and the adapter closes. Focused GitHub adapter/API suite passed: 11 passed, 1 existing Starlette/httpx deprecation warning. Latest `deploy/run_host_free_release_checks.sh` passed: backend 99 passed/3 skipped, frontend 20 passed, compileall, TypeScript lint, Vite build, and `git diff --check`; preflight 3 PASS/5 ACTION REQUIRED/1 MANUAL/0 FAIL. No live GitHub request was made because no authorized repository/token is configured.

### 2026-11-10 — Prepare host-free release and exact host blockers
- Added `deploy/RELEASE_RUNBOOK.md`, nine explicit `BLOCKED` owner/host actions in `deploy/RELEASE_BLOCKERS.json`, `deploy/run_host_free_release_checks.sh`, and the read-only `deploy/run_target_host_drills.sh` plus `deploy/target_host_smoke.py` for authenticated health/readiness/metrics, headers, CORS, Nginx syntax, and the pinned Docker isolation probe. The target drill never reloads services or changes host configuration.
- Added ten tests covering the blocker matrix, HTTPS/loopback origin validation, auth/readiness/header/CORS smoke behavior, and script safety/coverage. Shell syntax checks passed. The host-free release script passed: backend 96 passed/3 skipped, frontend 7 passed, compileall, lint, build, diff check; preflight was 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL.
- Ran the target drill without protected host settings; it stopped immediately with `BLOCKED: set RELAY_NGINX_CONFIG...` before touching a host. Live H6/H10 actions remain blocked because no target or owners are selected; every precise ask is recorded. No service was restarted/reloaded and no deployment was performed.


### 2026-11-10 — Complete GitHub read/approved-PR adapter
- Added `relay-ai/github_adapter.py` with a repository-ID allow-list, protected-token loading, operator-only metadata and bounded UTF-8 content reads, exact base/head commit comparison, open-PR deduplication, and PR creation only when the caller confirms human approval. All network responses are size-bounded, redirects are disabled, and upstream error bodies/credentials are withheld.
- Added an operator-only, evidence-gated `POST /api/v1/tasks/{task_id}/pull-request` route. It requires a task in COMMITTED state with explicit approval, passing sandbox result, security PASS, reviewer APPROVE, and local repository/base/commit provenance. Remote branch publication is an operator step. The API does not push, merge, or deploy. PR creation is idempotency-key-aware and appears in the task action audit without changing pipeline states.
- Documented fine-grained GitHub permissions and official REST references in `.env.example`, `README.md`, `relay-ai/README.md`, and `BLUEPRINT.md`. Updated and re-finalized the pitch deck to v3 so the architecture and speaker notes match the implemented GitHub behavior. Finalizer passed integrity/layout/font/import checks (14 slides, 0 layout warnings); all slides rendered and changed architecture slide visually inspected.
- Verification: backend 86 passed, 3 skipped, 1 existing Starlette/httpx deprecation warning; frontend 7 passed; `compileall`, TypeScript lint, Vite build, pitch claim checks (3 passed), adapter/API checks (8 passed), and `git diff --check` passed. Release preflight reported 3/9 PASS, four ACTION REQUIRED environment/host items, and one MANUAL host-owner signoff. One full-suite run exposed a stale deck-test phrase; corrected the assertion to match the final speaker notes and reran focused plus full backend suites successfully.
- Live GitHub was not called because no authorized repository/token is provisioned. The precise blocker is recorded under P-B2-LIVE. No credentials used or printed. Commit remains blocked pending explicit authorization; no push performed.


### 2026-11-10 — GitHub adapter implementation underway
- Verified GitHub REST endpoint contracts from official docs. Implemented a fine-grained, repository-allow-listed adapter for metadata/content reads and PR creation from a branch already published by an operator. PR creation requires task approval and commit, passing sandbox evidence, security PASS, reviewer APPROVE, and exact remote base/head SHA matches; no remote push, merge, or deployment method exists.
- Added operator-only read routes, an audited/idempotency-key-aware PR route, bounded/validated GitHub content reads, safe API errors, and protected environment configuration guidance. Added mocked adapter and API tests; focused suite passed (8 passed, 1 existing Starlette/httpx deprecation warning).
- Live GitHub calls were not run: credentials and an authorized test repository are unavailable. P-B2 and deck alignment remain IN PROGRESS; exact live prerequisite is recorded in P-B2-LIVE. No secrets used or printed.


### 2026-11-10 — Align deck claims with the implemented product
- Reworked the pitch deck and product docs to accurately describe Stage A triage, Stage B investigation + patch, Stage C review, deterministic sandbox tests, human-controlled allow-listed apply/commit, and the optional outbound-only Switch notifier. Removed the unimplemented inbound-room and GitHub PR capabilities from current-build claims; documented exact API states and legacy compatibility status caveats in slide notes.
- Added `relay-ai/tests/test_pitch_claim_alignment.py` to catch future drift in pipeline roles, lifecycle states, approval boundaries, and unsupported PR claims.
- Rendered and inspected all 14 final slides. The first visual pass found the closing headline overlapped its subtitle; shortened the headline and re-rendered the corrected final deck. Artifact finalization passed package integrity, layout, reference-font policy, and first-party import checks with zero layout warnings.
- Verification: backend 78 passed, 3 skipped; frontend 7 passed; deck claims 3 passed; `compileall`, TypeScript lint, Vite production build, and `git diff --check` passed. Existing Starlette/httpx deprecation warning remains. A system-Python pytest collection failed due to missing `google.genai`; rerunning the full suite using the project virtualenv succeeded. Initial slide rendering lacked the required runtime environment and failed; rerunning with configured runtime paths succeeded. No credentials or external services were used.
- Commit remains blocked pending explicit authorization; no push performed.


### 2026-11-04 — Discovery and blueprint
- Inspected root React/Vite app, FastAPI API, orchestrator, Pydantic schemas, sandbox runner, and backend tests.
- Confirmed frontend currently renders an empty component and has no API integration.
- Confirmed task state is in-memory; apply and commit actions are simulations.
- Created the architecture, product journeys, data model direction, safety requirements, and phased delivery blueprint.
- Corrected the Python Gemini SDK method spelling in the orchestrator.
- Added an approval gate requiring passing sandbox evidence and an approving security review.

### 2026-11-05 — Phase 0 implementation and product foundation
- Hardened JSON/ZIP snapshots with file count, upload size, per-file size, expanded-size, path, duplicate, and symlink checks.
- Added Gemini and injectable structured-provider adapters plus an explicit fake adapter seam.
- Persisted tasks and source snapshots in SQLite; added an append-only event table and paginated event endpoint, task listing, and `/ready` health detail.
- Changed submissions to `202 Accepted` and in-process background execution; stage callbacks persist progress for UI polling.
- Implemented verified human approval, apply to a durable task-owned repository snapshot, actual Git commit creation, and patch download. The original upload is not changed.
- Added optional shared-token middleware and a session-only token entry in the dashboard for single-operator deployments.
- Added patch path validation against declared changed-file metadata and blocked `.git` paths in snapshots to prevent user-provided Git hooks/configuration from executing during task workspace initialization.
- Added explicit `APPLIED` and `COMMITTED` lifecycle states so UI and API state reflect real repository-copy operations.
- Removed simulated apply/commit success and implemented real apply/commit in a task-owned snapshot workspace.
- Built the React dashboard for JSON/ZIP submission, demo scenarios, task history, triage, diff, test evidence, reviewer findings, and approve/reject/apply/commit actions, with token-aware patch downloads.
- Added Docker sandbox image discovery and hardened runtime flags; runtime never pulls an image, and code execution fails closed unless the explicitly named unsafe development option is enabled.
- Rewrote setup and API documentation to match behavior.
- Resolved npm's Vite/esbuild peer conflict by aligning esbuild and removing unused server/model dependencies from the web package.
- Frontend production build, TypeScript type check, and Python `compileall` all pass. `npm install` reports zero vulnerabilities.
- Installed backend requirements in the ignored project virtual environment and confirmed the FastAPI app imports with its SQLite store.
- Updated existing lifecycle and sandbox test fixtures for evidence-gated approval, real task-copy commits, and explicitly trusted local sandbox tests. The test suite has not been run.
- Backend app import reports 15 routes. The configured isolated sandbox image was not detected in this environment, so `/ready` will remain unavailable until Docker and the image are present.

### 2026-11-05 — Durable worker and lifecycle continuation
- Replaced in-process FastAPI background execution with a lifespan-managed worker consuming SQLite job records.
- Made task creation atomic across task snapshot, initial event rows, and job queue insertion.
- Added transactional job claiming and leases, heartbeat renewal, stale lease recovery, failed-job reconciliation, cancellation requests at stage boundaries, and bounded manual retries.
- Exposed queue counts through `/health`; worker claim failures now log and recover instead of terminating the worker thread.
- Added JSON-line application logging with task/stage/attempt context fields and documented the output format.
- Updated dashboard queued-state messaging and stopped polling terminal cancelled tasks.
- Corrected root and backend setup documentation to describe the worker actually in use.
- Verification this continuation: Python syntax compilation and FastAPI import (15 routes; queue initially empty) passed after the JSON logging addition; Vite production build, TypeScript check, and `git diff --check` passed for the prior worker/UI chunk. No test suite was run. Docker sandbox image remains unavailable locally.

### 2026-11-05 — Input and patch scope hardening
- Changed ZIP member extraction to read at most the configured per-file bound plus one byte, reject declared/actual size mismatches, and enforce the aggregate bound against streamed bytes.
- Strengthened patch scope validation to require matching `diff --git` and unified file headers, exact declared-file agreement without duplicates, safe relative paths, existing files from the submitted snapshot, and a 25-file change maximum. New files, deletions, and renames are rejected until explicitly supported end to end.
- Moved temporary patch files outside the repository workspace so a submitted file cannot collide with or be overwritten by RELAY's patch plumbing.
- Replaced Docker `sh -c` test launching and caller-supplied command strings with a fixed pytest argv profile executed directly in the container or explicitly enabled trusted subprocess mode.
- Added a 1.5 MB UTF-8 aggregate model input cap across report text, file paths, and JSON/ZIP source content, plus 20,000-character report and path-depth/length limits; surfaced the cap in the dashboard and API setup docs.
- Added bounded retry with exponential delay and jitter for transient Gemini 408/429/5xx responses only; non-transient errors still fail immediately.
- Verification for this chunk: Python syntax compilation, FastAPI import (15 routes; queue initially empty), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run. Docker sandbox image is unavailable for runtime verification.

### 2026-11-05 — Operator action audit
- Added durable append-only `task_actions` records for successful approve, reject, apply, commit, cancel, and retry operations. Records include a non-secret local/shared-token actor label, outcome, notes, details, and timestamp.
- Added paginated `GET /tasks/{task_id}/actions` and documented that shared-token attribution is not an individual identity.
- Verification for this chunk: Python syntax compilation, FastAPI import, route inspection confirming both action endpoints, Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Operations visibility
- Added SQLite schema version history (current version 2, including audit and rate-limit tables) and exposed the current schema version through `/health`.
- Added a Prometheus-compatible `/metrics` endpoint for durable job status counts, task status counts, and local worker liveness; documented it for operators.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema version 1; health/readiness/metrics routes registered), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — API rate limiting
- Added atomic fixed-window SQLite rate limits of 10 submissions/minute and 60 actions/minute per client address digest. Raw client addresses are not stored; expired buckets are pruned opportunistically.
- Documented the local single-host scope and the need for a shared limiter in multi-instance deployments.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema version 2; action, health, readiness, and metrics routes registered), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Per-user ownership
- Added optional `RELAY_AUTH_USERS_JSON` username-to-unique-token authentication, taking precedence over the shared token when configured; malformed and duplicate credentials fail startup.
- Added task ownership at submission and enforced owner-scoped task lists, task detail, events, action history, patch download, and mutation actions. Non-owned tasks return 404 to avoid disclosing existence.
- Preserved local single-operator and shared-token modes; legacy ownerless tasks remain visible only when per-user auth is not configured.
- Kept actor labels non-secret and documented token storage and mode precedence.
- Moved owner filtering and task pagination into indexed SQLite queries instead of loading all task payloads into the API process.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema version 3; 17 routes), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Action idempotency
- Added optional `Idempotency-Key` support to actions with durable uniqueness scoped to task, actor, and action key; the stored request fingerprint prevents reusing the same key for a different body.
- Successful action responses are persisted and replayed for matching retries; the dashboard retains a key in session storage until a successful response arrives.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema version 4; 17 routes), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Task data deletion
- Added owner-authorized `DELETE /tasks/{task_id}` for stopped jobs; active queued/running work must be cancelled and stopped first.
- Task deletion cascades through task snapshots, stage events, queue state, and action audit, and removes the task-owned Git working copy using a rename-and-delete cleanup sequence.
- Added a confirmation flow in the dashboard task list and documented that task data does not automatically expire by default.
- Verification for this chunk: Python syntax compilation, FastAPI import (GET/DELETE task routes registered), Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Dependency readiness
- Extended `/ready` to check SQLite availability/schema version and live worker state alongside configured model and sandbox capabilities; `/health` now reports worker liveness.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema 4; worker correctly reports stopped before lifespan startup), and `git diff --check` passed. No test suite was run.

### 2026-11-05 — Pipeline usage telemetry
- Captured Gemini-reported prompt, candidate, and total token counts as task events and durable idempotent usage rows; task deletion cascades the usage data.
- Added elapsed milliseconds to successful and failed triage, investigation, sandbox, and review events and exposed aggregate Gemini token counters through `/metrics`.
- Did not estimate monetary cost because pricing depends on model, account, and time-varying rates.
- Verification for this chunk: Python syntax compilation, FastAPI import (schema version 5; token counters initially zero), Vite production build, TypeScript check, and `git diff --check` passed. Gemini usage reporting was not live-verified because no model request was made. No test suite was run.

### 2026-11-05 — Backup and recovery operations
- Added `relay-ai/backup.py` using SQLite's online backup API and a private timestamped archive containing the database, manifest, and task-owned repository workspaces.
- Added `OPERATIONS.md` with health/readiness interpretation, backup/restore steps, recovery actions, and the current single-host/retention limits.
- Documented that archives contain source code and must be kept encrypted/access-controlled; credentials remain outside backups.
- Verification for this chunk: Python syntax compilation, backup CLI help, FastAPI import (schema version 5; 18 routes), Vite production build, TypeScript check, and `git diff --check` passed. The backup archive itself and a restore drill were not run; no test suite was run.

### 2026-11-05 — Mobile dashboard controls
- Added a mobile recent-task selector because the desktop sidebar task list is hidden at narrow widths.
- Kept API token saving available on mobile with an icon button and accessible label; delete controls remain visible on touch devices.
- Visual review exposed that the default CORS list omitted the `127.0.0.1` origin used by Vite, so the browser could not fetch tasks or scenarios even though the API returned `200`. Added both localhost and loopback Vite origins to the default allowlist and `.env.example`.
- Connected browser review then showed the demo scenarios load without a fetch error. At a 390×844 viewport the task selector and token-save control remained available; the default viewport was restored afterward. Both temporary local servers were stopped.
- Verification for this chunk: Python syntax compilation, FastAPI import (18 routes; default CORS includes localhost and loopback Vite origins), connected browser scenario load, 390×844 mobile viewport inspection, Vite production build, TypeScript check, and `git diff --check` passed. No automated accessibility audit or submission-through-pipeline browser journey was run.

### 2026-11-05 — Versioned API contract
- Added `/api/v1` routes for task submit/upload/list/detail/events/actions/patch/delete and scenarios while preserving the unversioned routes as compatibility aliases.
- Migrated the dashboard to the versioned routes and updated rate limiting to cover versioned submissions and actions.
- Updated API documentation to identify `/api/v1` as the client contract.
- Verification for this chunk: Python syntax compilation, OpenAPI inspection confirming `/api/v1` resources and hidden legacy aliases, Vite production build, TypeScript check, and `git diff --check` passed. No test suite was run.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-11-04 | Treat repository apply/commit as unavailable until a target repository/worktree and authorization are explicit. | Current implementation does not mutate or commit any repository, despite its API description. |
| 2026-11-04 | Do not claim sandbox isolation when the local subprocess fallback is used. | Running untrusted repository code on the host is not a security boundary. |
| 2026-11-04 | Keep Gemini behind a provider seam and add a fake provider before expanding the pipeline. | Allows reproducible local operation and focused development without model credentials. |
| 2026-11-04 | Require test pass, clean patch application, reviewer security PASS, and recommendation APPROVE before human approval. | Prevents the API from authorizing patches the pipeline itself says failed or unsafe. |
| 2026-11-05 | Use a SQLite lease queue with a local lifespan-managed worker for the durable MVP (supersedes the earlier in-process background task decision). | Enables restart recovery and safe atomic claims on one host without an additional broker; production multi-host deployments should move to a server database and queue. |
| 2026-11-05 | Disable host subprocess execution by default and require an explicit opt-in for trusted local code only. | Repository tests execute arbitrary code, so the API must not silently run them on the host. |
| 2026-11-05 | Apply/commit against a durable task-owned copy of the uploaded snapshot. | Enables real Git operations without changing the user's original repository; patch file remains available for local application. |
| 2026-11-05 | Store event history separately with insert-only sequence records. | Preserves an auditable event trail even as the current task snapshot is updated. |
| 2026-11-05 | Limit generated patches to modifications of existing submitted files. | Prevents model-declared paths from expanding the patch's authority beyond the immutable task snapshot while add/delete/rename flows lack complete validation and review support. |
| 2026-11-05 | Launch the fixed pytest profile with argv directly, without a shell. | Keeps test execution policy server-controlled and avoids shell interpretation if configuration paths are expanded later. |
| 2026-11-05 | Cap aggregate submitted source context at 1.5 MB. | Keeps prompt input bounded independently from ZIP transport limits and avoids silently truncating repository content before model analysis. |
| 2026-11-05 | Add optional shared-token protection for single-operator deployments. | Protects local/controlled instances without implying per-user identity; full auth and task ownership remain required before shared deployment. |
| 2026-11-05 | Record `local-operator` or `shared-token` as action actor labels. | Audits must never imply that one shared bearer token identifies a particular human; per-user identity remains a separate authentication milestone. |
| 2026-11-05 | Use configured username-to-token mappings as the task owner identity, superseding the shared-token identity when present. | Enables per-task isolation without claiming support for an external identity provider; the simple mapping is appropriate for controlled local deployments. |
| 2026-11-05 | Keep task search substring-based and parameterized, with status stored/indexed separately in SQLite. | Provides predictable, injection-safe history filtering while retaining owner-scoped pagination. |
| 2026-11-05 | Never embed provider prices in the code; only estimate cost when operators supply both token rates and a pricing source label. | Model/account pricing can change; the estimate must be reproducible and clearly distinct from billed cost. |

## Verification log

Latest verification (2026-11-10): host-free release script backend suite passed (96 passed, 3 skipped, 1 existing Starlette/httpx deprecation warning) using `relay-ai/.venv/bin/pytest`; an initial system-Python `pytest` collection failed because `google.genai` was unavailable there, then reran successfully in the project venv. Pitch-claim regression tests passed (3 passed); GitHub adapter/API tests passed (8 passed); release checklist/smoke tests passed (10 passed). Final PPTX v3 package integrity, layout geometry, source-font policy, and Artifact Tool import checks passed (14 slides, 0 layout warnings); all slides rendered and changed architecture slide inspected. Closing-slide overlap fixed. Initial slide render omitted runtime env and failed, then succeeded with declared runtime paths. `python -m compileall -q relay-ai`, frontend tests (7 passed), `npm run lint`, `npm run build`, and `git diff --check` passed. Latest release preflight: 3/9 PASS, five ACTION REQUIRED production/auth/CORS/sandbox/proxy setup items, one MANUAL host-owner signoff. Host-free release script passed; target-host script stopped before host access because `RELAY_NGINX_CONFIG` is unset. Fixture rehearsal passed (2 tests); fake-provider API/worker rehearsal passed (1 test); rehearsal script contracts passed (5 tests); Switch adapter tests passed (7 tests, included in backend total). Live Gemini rehearsal was safely blocked with exit 2 because `GEMINI_API_KEY` is absent; no credentials were printed and no host fallback ran. Recording capture was not run. Preflight reports four host/configuration actions required and one manual owner signoff; the first ad hoc JSON-count wrapper expected an object, while the actual valid output is a nine-element array, and the corrected parser confirmed all nine checks. CI YAML parsing, opt-in Docker isolation drill, Nginx syntax validation, and local browser accessibility-tree review are recorded in earlier entries. Browser interaction/cross-device review, actual GitHub-hosted Python 3.11 execution, target-host validation, and operator signoff remain outstanding.

### 2026-11-05 — Task history search and status filters
- Added a migrated `status` column and owner/status/updated-time index to SQLite task snapshots; status is kept synchronized on creation, snapshot updates, worker lease failure, and retry.
- Added `q` substring search and enum-validated `status` filters to the versioned task list endpoint. Search and status are applied in SQLite before pagination and remain scoped to the actor, including legacy unowned task visibility where configured.
- Added matching desktop and mobile dashboard filters.
- Verification: Python syntax compilation, Vite production build, TypeScript check, and `git diff --check` passed. FastAPI import/route inspection could not run because the active Python environment lacks `google.genai` (`ModuleNotFoundError`); no tests run.

### 2026-11-05 — Bound sandbox capture files
- Added POSIX child-process file-size limits so stdout/stderr capture files stop at 1 MiB each, matching the response output cap; disabled core dumps for these children.
- This limits host temporary-file growth from verbose subprocess output. Docker still provides the actual code isolation boundary; container execution and hostile workload behavior remain to be verified in an environment with the configured image.
- Verification: Python syntax compilation, FastAPI import and route inspection (schema 6; versioned task GET/POST registered), and `git diff --check` passed using `relay-ai/.venv`. No tests run.

### 2026-11-05 — Event attribution and correlation
- Extended task evidence events with backward-compatible actor and correlation ID fields. New automated stage events are attributed to `system`; ingestion, retries, and operator decisions carry the authenticated actor, and task ID is used as the correlation ID.
- Displayed actor attribution in the task activity timeline. Existing persisted events deserialize with `system` attribution and remain readable.
- Verification: Python syntax compilation, FastAPI import (schema 6 and event route registered), legacy `EvidenceEvent` payload deserialization defaults (`actor=system`), Vite production build, TypeScript check, and `git diff --check` passed. No tests run.

### 2026-11-05 — Fence stale worker attempts
- Worker lease renewal, task progress persistence, and job completion now require the attempt number returned by the atomic queue claim.
- A worker that loses its lease discards further progress and failure writes, preventing a delayed process from overwriting state produced by a newer retry attempt.
- Verification: Python syntax compilation, FastAPI import/schema inspection (SQLite schema 6), Vite production build, TypeScript check, and `git diff --check` passed. Fault-injection and concurrency checks remain unrun; no tests run.

### 2026-11-05 — Persist stage metrics
- Added schema version 7 `stage_observations`, backfilled idempotently from prior event history and updated with each worker snapshot using task/sequence uniqueness.
- `/metrics` now emits stage duration histograms, stage failure counters, and sandbox execution counts by isolation mode and pass/fail outcome, alongside existing queue/task/provider metrics.
- Queue latency metrics and representative populated histogram scrape remain. Verification: Python syntax compilation, FastAPI import and schema migration inspection (version 7), `/metrics` route serialization/content type and metric-family presence, OpenAPI confirmation of task `q`/`status` filters, and `git diff --check` passed. The current store has no completed stage observations to verify populated buckets; no tests run.

### 2026-11-05 — Queue wait telemetry
- Added schema version 8 durable job-attempt rows with queue wait duration and terminal outcome. Each atomic claim records its wait, including manual retries and expired-lease recovery attempts; completion is recorded only by the current unexpired lease holder.
- Added queue-wait Prometheus histogram and attempt-state counts; updated API operations documentation to cover the expanded metric set.
- Verification: Python syntax compilation, FastAPI import and migration inspection (schema 8), `/metrics` serialization and zero-valued histogram/counter series across queue, stage, attempt, and sandbox families, OpenAPI task filter inspection, and `git diff --check` passed. No tests run. Existing attempts from before schema 8 cannot be assigned accurate queue-wait durations and are not backfilled.

### 2026-11-05 — Explicit active task statuses
- Added `QUEUED`, `RUNNING`, `TRIAGING`, `INVESTIGATING`, `SANDBOX_RUNNING`, and `REVIEWING` states. Submission and retry now report `QUEUED`; the atomic worker claim records `RUNNING` plus an activity event; stage starts persist their active status before provider/sandbox work begins.
- Updated status filters and setup documentation; kept legacy `RECEIVED` deserialization support.
- Updated the existing enum expectation. Verification: Python syntax compilation, FastAPI import and route/filter inspection (schema 8), status enum enumeration, queue metric serialization, Vite production build, TypeScript check, and `git diff --check` passed. No tests run; queue lifecycle behavior still needs concurrent worker verification.

### 2026-11-05 — Task history pagination UI
- Added owner/filter-scoped total task counts as the `X-Total-Count` response header and exposed it through CORS/OpenAPI.
- Added desktop and mobile previous/next page controls, matching status/search filters, page ranges, and selected-task detail refresh while navigating history.
- Verification: Python syntax compilation, FastAPI import and OpenAPI inspection (schema 8, list parameters and `X-Total-Count` response header), Vite production build, TypeScript check, and `git diff --check` passed. No tests run; pagination behavior in a connected browser still needs review.

### 2026-11-05 — Production threat model and provisional SLOs
- Added `THREAT_MODEL.md` covering assets, trust boundaries, abuse scenarios, implemented controls, residual risks, deployment requirements, pilot SLOs, ownership responsibilities, and incident response.
- Documented current limitations: optional/static-token authentication, privileged Docker daemon boundary, unsafe subprocess host execution, JSON body ingress limits, Gemini source disclosure, unencrypted-by-tool backups, and unverified concurrency/restore/security/load behavior.
- Linked the threat model from the root README and operations runbook. SLOs are explicitly provisional; named owners and on-call integration must be assigned per deployment.
- Verification: required threat-model sections and linked artifacts present, `git diff --check` passed. SLO numbers are proposed pilot targets rather than measured results; no security review or tests were run.

### 2026-11-05 — Viewer/operator authorization
- Added optional `RELAY_AUTH_ROLES_JSON` for configured per-user bearer accounts. `viewer` is restricted server-side to GET/HEAD/OPTIONS; `operator` may write while remaining scoped to owned tasks. If a role map is explicitly set, omitted users default to viewer; if unset, existing per-user deployments retain operator permissions.
- Added `/api/v1/session` for actor/role capabilities and updated the dashboard to hide submission, decision, retry, cancellation, and deletion controls from viewers while keeping full-width task/evidence browsing available.
- Updated environment/setup docs and the threat model. Verification: Python syntax compilation, FastAPI import/schema inspection (schema 8, session route registered, unset role map compatibility confirmed), Vite production build, TypeScript check, and `git diff --check` passed. No tests run; authorization behavior still needs request-level security verification.

### 2026-11-05 — Pre-parse request body limits
- Added ASGI receive middleware that caps JSON, multipart, and other write request bodies before FastAPI parses them; declared lengths are rejected early and streaming bodies are counted as received.
- Updated the threat model and setup docs to distinguish application caps from upstream proxy/server buffering and to require ingress limits too.
- Verification: Python syntax compilation, FastAPI import and middleware-order inspection (CORS outermost; request limiter before routing/body parsing), request-limit constants, route registration, and `git diff --check` passed. No tests run; actual chunked oversized-request behavior still needs request-level verification.

### 2026-11-05 — Centralized task status transitions
- Added `PipelineTaskResponse.transition_to()` and one allowed-transition graph covering queued execution, stage starts/completions, cancellation/failure, approval/rejection, task-copy apply/commit, and retry.
- Routed API, worker, SQLite recovery, and orchestrator status changes through the validator. Same-state updates remain idempotent; invalid jumps raise a clear `ValueError`.
- Atomically committed final task output and queue completion under the active lease; cancellation checks the persisted task state and terminal task outcomes are reconciled after worker crashes rather than rerun.
- Verification: Python syntax compilation, FastAPI import/schema inspection (schema 8; 29 routes), static search confirming no direct task-status assignments remain outside `transition_to()`, finalizer method presence, Vite production build, TypeScript check, and `git diff --check` passed. No tests run; existing lifecycle/recovery/API behavior still requires execution-level verification.

### 2026-11-05 — Operator-managed retention purge
- Added `relay-ai/retention.py` with dry-run as the default, explicit `--apply --confirm-delete`, a caller-specified age threshold, and eligibility limited to inactive FAILED/CANCELLED/REJECTED/COMMITTED tasks.
- Excluded open approvals and applied-but-uncommitted tasks. Workspace removal uses a private rename staging path with rollback if transactional database eligibility recheck fails; concurrent retries therefore prevent purge.
- Updated runbook, backend setup, and threat model. Verification: Python syntax compilation, CLI help, safe empty-database dry run using an isolated temporary SQLite path, and `git diff --check` passed. No tests or actual deletions run; populated-candidate and filesystem rollback behavior remain unverified.

### 2026-11-05 — Operator action audit in task review
- Added dashboard loading of the selected task's persisted `/actions` history and displayed actor, action, outcome, timestamp, notes, and structured details in a separate expandable audit section.
- Cleared stale audit rows on task selection; read-only viewers can inspect action history while write controls remain hidden.
- Verification: Vite production build, TypeScript check, and `git diff --check` passed. No tests run; connected-browser review remains outstanding.

### 2026-11-05 — Human decision notes and commit provenance
- Connected optional reviewer notes in the approval/rejection flow to the API's audited action notes, with bounded 2,000-character input and idempotency key reset when edited.
- Added an optional 200-character custom Git commit message and displayed the persisted commit hash/message after commit; blank input retains the backend generated-message behavior.
- Verification: Vite production build, TypeScript check, and `git diff --check` passed. No tests run; connected-browser review remains outstanding.

### 2026-11-05 — Paginated task activity timeline
- Connected task review to the persisted `/events` endpoint with 50-record pages, newest-first display within each page, and older/newer navigation. Refreshing an active task reloads the selected event page.
- This avoids rendering the full embedded timeline in the review panel and exposes the existing event-pagination contract to the dashboard.
- Verification: Vite production build, TypeScript check, and `git diff --check` passed. The connected browser preview loads the dashboard but the API is not running (no `google.genai` module in the active Python environment); no API journey or tests were run.

### 2026-11-05 — Event pagination counts
- Added SQLite event counts and exposed `X-Total-Count` on the versioned and compatibility event-history endpoints; documented the header in OpenAPI. CORS already exposes this header for browser clients.
- Dashboard now displays the total and current range and disables navigation at exact page boundaries without opening an empty page.
- Verification: Vite production build, TypeScript check, Python syntax compilation, `git diff --check`, FastAPI import, schema version 8 inspection, and OpenAPI header inspection passed using `relay-ai/.venv`. No tests run.

### 2026-11-05 — Paginated operator action audit
- Added SQLite action counts and `X-Total-Count` to both versioned and compatibility action-history endpoints; documented the count header in the API reference and OpenAPI.
- Dashboard now loads 50 audit records per page, shows the page range and total, and prevents navigation beyond the final page, including exact 50-record boundaries.
- Verification: Vite production build, TypeScript check, Python syntax compilation, `git diff --check`, FastAPI import, and OpenAPI total-count header inspection passed using `relay-ai/.venv`. No tests run.

### 2026-11-05 — Allow-listed sandbox test profiles
- Added `RELAY_TEST_PROFILE` with fixed `pytest` (default) and Python `unittest` argv profiles. Invalid profile names fail configuration; callers cannot provide commands or shell fragments.
- Documented the setting in `.env.example` and backend setup docs.
- Verification: Python syntax compilation, `git diff --check`, Vite production build, and TypeScript check passed. Sandbox container/runtime verification remains unavailable here; no tests run.

### 2026-11-05 — Sandbox evidence completeness and connected local review
- Dashboard now displays the exact executed test command and preserves stdout and stderr as separate output sections; previously stderr disappeared whenever stdout was non-empty.
- Started the API with an isolated temporary database and reviewed the dashboard in a connected browser. `/api/v1/tasks`, `/api/v1/session`, and `/api/v1/scenarios` returned `200`; the dashboard loaded the operator session and all demo scenarios. No task was submitted and no tests were run.
- Current `relay-ai/.venv` imports FastAPI and google-genai successfully; schema 8 and OpenAPI total-count headers for events/actions were confirmed. This supersedes earlier notes based on the global Python environment missing google.genai.
- Verification: Vite production build, TypeScript check, Python syntax compilation, and `git diff --check` passed. The local UI preview and read-only API load were inspected in the connected browser; no task execution or tests were run.

### 2026-11-05 — Best-effort diagnostic credential redaction
- Added a shared redactor for configured secret environment values and per-user bearer tokens, common Google/GitHub/OpenAI/Slack/AWS token forms, JSON/key-value credential fields, bearer credentials, and private-key blocks.
- Applied redaction to structured log messages and tracebacks, pipeline/worker task errors, and bounded sandbox stdout/stderr so diagnostics are less likely to persist or expose credentials.
- Updated the threat model and backend docs to describe the control and its limits: transformed or unrecognized secrets can still pass through, and Gemini source disclosure remains an operator data-use decision.
- Verification: Python syntax compilation, FastAPI import (29 routes; schema 8), Vite production build, TypeScript check, and `git diff --check` passed. Redaction behavior has not been exercised with fixtures; no tests run.

### 2026-11-05 — Recheck task deletion against active worker claims
- Task deletion now rechecks queue state and removes the task cascade under one SQLite `BEGIN IMMEDIATE` transaction after the workspace is staged. If the worker claimed the task during staging, the API restores the workspace and returns `409`.
- This closes the check-then-delete race between the initial API check and a concurrent queue claim.
- Verification: Python syntax compilation, FastAPI import (29 routes; schema 8), and `git diff --check` passed. No tests run; concurrent claim/delete behavior remains unexercised.

### 2026-11-05 — Open audit histories at the newest records
- Changed event and action SQL pagination to return newest records first. The first page now opens on recent task activity; `Older` pages advance through history and `Newer` returns toward the present.
- Updated dashboard range labels to show the correct oldest-based sequence ordinals for each newest-first page, and documented the endpoint order.
- Verification: Vite production build, TypeScript check, Python syntax compilation, FastAPI import (29 routes; schema 8), and `git diff --check` passed. No tests run; populated multi-page ordering remains unexercised.

### 2026-11-05 — Optional provider cost attribution
- Added optional operator-configured Gemini input/output USD rates per million tokens plus a required pricing source/model revision label. Invalid, partial, non-finite, negative, or excessive values fail configuration; no rates means token-only telemetry.
- Persisted the rates, label, and estimated per-call cost with provider usage in schema 9; existing usage rows migrate as unpriced. Added retained estimated USD and priced/unpriced usage gauges to `/metrics`.
- Updated setup docs and `.env.example` to require operators to use their current account/model pricing schedule. Estimates are explicitly not represented as billing records.
- Verification: Python syntax compilation, fresh app import, SQLite schema 9/pricing-column inspection, zero-usage cost totals, and a connected browser `/metrics` scrape showing valid zero-valued cost/coverage series passed; `git diff --check` passed. No actual provider call or tests were run, and populated priced-usage aggregation remains unverified.

### 2026-11-05 — Correct retained usage metric semantics
- Changed Gemini token, estimated-cost, and priced/unpriced usage metrics from counters to gauges because task deletion cascades usage records and therefore may reduce the reported totals.
- Updated operations and API docs to identify these as retained task-usage measurements that can decrease after deletion.
- Verification: fresh FastAPI import, connected-browser `/metrics` scrape showing the new gauge names/types with zero values, and `git diff --check` passed. No tests run; decreasing values after task deletion were verified from the storage cascade semantics, not a populated deletion scenario.

### 2026-11-05 — Show per-call model usage in task review
- Model-usage activity events now display provider/model, prompt/candidate/total tokens, and estimated USD with the configured pricing label when available. Token-only records remain clear when rates were not configured.
- Verification: Vite production build, TypeScript check, and `git diff --check` passed. No tests run; a populated model-usage event has not been displayed in the browser.

### 2026-11-05 — Complete portable archive path validation
- Added shared NFC path normalization and portable filename checks for JSON snapshots, ZIP members, workspace population, and generated patch targets. Rejects case-fold aliases, file/directory prefix collisions, drive/ADS syntax, Windows reserved names, trailing dots/spaces, invalid UTF-8, and `.git` paths.
- ZIP extraction now rejects special file types other than regular files/directories and detects normalized duplicate entries before extraction. Updated README and threat model to reflect these controls.
- Verification: Python syntax compilation, FastAPI app import with 29 routes, and `git diff --check` passed. No tests run; hostile ZIP request fixtures and patch-scope scenarios still require request-level verification.

### 2026-11-05 — Guard SQLite schema startup upgrades
- Serialized SQLite schema setup with `BEGIN IMMEDIATE` so concurrent API starts cannot interleave upgrades; schema DDL and legacy backfill now roll back together on startup errors.
- Added a future-schema guard that fails startup before mutation and documented backup/upgrade behavior and the lack of downgrade/per-release migration scripts.
- Verification: Python syntax compilation, FastAPI import with 29 routes, and `git diff --check` passed. No tests run; legacy database upgrade and rollback scenarios still need execution-level verification.

### 2026-11-05 — Make codebase input accessible
- Replaced the hidden ZIP input embedded inside its radio label with a named, keyboard-operable radio group and a visible, explicitly labeled native ZIP file picker. Added accessible labeling for the JSON file-map editor, visible focus indicators across controls, and live semantics plus an accessible dismiss label for notices.
- Selecting a source mode now controls which input is shown; ZIP submission stays disabled until a file is selected, and loading a demo returns to JSON mode.
- Verification: Vite production build, TypeScript check, and `git diff --check` passed. No tests run; assistive-technology review remains outstanding.

### 2026-11-05 — Detect stored source snapshot corruption
- Added numbered SQLite migration 10 with a SHA-256 digest of each serialized source snapshot. Startup upgrades legacy databases to the v9 compatibility baseline, applies registered migrations inside the schema transaction, backfills existing snapshot digests, and rejects databases marked newer than the application.
- Snapshot writes keep the digest in sync, and reads reject mismatches before source reaches the worker or API response. Documented the integrity behavior; future migration entries and downgrade support remain.
- Verification: Python syntax compilation, FastAPI import (29 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No tests run; migration backfill and corruption detection still need execution-level verification.

### 2026-11-05 — Close local MVP progress and observability implementation
- Marked P1-03 and P1-04 complete for the local MVP because their planned polling, cancellation/retry/pagination, structured logging, readiness, limits, retry, and metrics functionality is implemented. Remaining verification obligations are explicitly tracked under P1-02 and P4-02.

### 2026-11-05 — Enforce immutable source snapshots
- Changed the compatibility snapshot write API from update-on-conflict to insert-only/idempotent behavior. Repeated identical writes succeed; attempts to replace stored task source fail, and snapshot digests continue to detect out-of-band changes.
- Marked P2-01 and P2-02 complete for the local MVP implementation; deployment-host isolation and hostile-input verification remain explicit in the P4-02 and P0-04 gates.
- Verification: Python syntax compilation, FastAPI import (29 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No tests run; immutability and digest mismatch behavior still need execution-level verification.

### 2026-11-05 — Close local MVP task UI and access control
- Marked P3-01 complete for the implemented submission/list/detail/timeline journeys and P4-01 complete for static per-user ownership and viewer/operator authorization. Cross-device UI review remains under P3-03; token rotation and external identity remain production extensions under P4-02.

### 2026-11-05 — Close durable persistence and review UI implementation
- Marked P1-01 complete for local MVP persistence, immutable snapshots, append-only records, retention tooling, and numbered schema upgrades. Migration rollback/recovery checks remain in the P1-02/P4-02 verification gates.
- Marked P3-02 complete for the evidence, diff, action, and provenance review flow. Cross-device visual/accessibility review remains grouped under P3-03.

### 2026-11-05 — Close worker and API integration implementation
- Marked P1-02 complete for the single-host SQLite worker/lease/retry implementation; multi-host queueing remains out of scope and restart/fault-injection verification remains under P4-02.
- Marked P3-03 complete for the `/api/v1` integration, polling, loading/error handling, and responsive controls; cross-device QA remains under P4-02.

### 2026-11-05 — Close archive hardening implementation
- Marked P0-04 complete for the archive/path validation implementation across ingress, workspace writes, and patch targets. Request-level hostile archive verification remains an explicit P4-02 release gate.

### 2026-11-05 — Add configured local repository targets
- Added an operator allow-list mapping repository IDs to local Git roots; API callers cannot supply filesystem paths. The UI can bind a task to a clean configured target and records its base revision.
- Apply requires the target to remain at that clean base and verifies changed source files match the submitted snapshot. Commit separately stages only approved changed paths, verifies the applied diff has not changed, and records base/result revisions. Per-repository file locks serialize RELAY actions; apply/commit markers support interrupted-operation recovery; conditional task updates prevent deletion races from resurrecting tasks; and applied target audit records are protected from deletion/retention.
- Updated setup, operations, and threat-model docs. Verification: Python syntax compilation, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No tests run; real Git target apply/commit and crash-recovery scenarios remain unverified.

### 2026-11-05 — Add backup archive verification
- Added `backup.py --verify` to validate archive paths/types/size limits and manifest, then run SQLite quick-check and foreign-key integrity without extracting task workspaces.
- Backup creation now verifies its temporary archive before atomically publishing it. Documented that this check does not replace a restore drill.
- Verification: Python syntax compilation, CLI help, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No tests or real backup archives run.

### 2026-11-05 — Add single-host systemd templates
- Added a localhost-only API/worker service unit, daily backup timer, and setup notes for secrets, persistent paths, repository allow-lists, TLS proxying, and Docker socket risk.
- Backup archives are checked before publication; the timer still requires an assigned operator and external failure monitoring. Restore drills remain outstanding.
- Verification: Python syntax compilation, backup CLI help, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No service was installed or started, and no backup archive was created.

### 2026-11-05 — Add isolated backup restore workflow
- Added `backup.py --restore-archive ... --restore-to ...`, which verifies the archive, rejects existing/live destinations and unsafe paths, restores to a private staging directory, checks SQLite integrity, then atomically publishes the isolated restore tree.
- Updated the runbook for non-destructive restore drills. The restore workflow is implemented but has not been run against an archive; actual replacement of live data remains a manual operator step.
- Verification: Python syntax compilation, backup CLI help, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No backup archive was restored.

### 2026-11-05 — Complete local target repository integration
- Marked P2-03 complete for the configured local-Git implementation: explicit binding, expected-base checks, changed-file-only commit, audit provenance, retention/deletion protection, and interrupted-action recovery are present.
- Remote Git providers remain future scope; direct target apply/commit and crash-recovery scenarios are still required in the P4-02 verification gate.

### 2026-11-05 — Add backup freshness monitoring
- Added `backup.py --check-latest DIR --max-age-hours N` with JSON output and nonzero status for missing/stale archives, plus a daily systemd check timer.
- Documented that failed units need external alert delivery. Verification: Python syntax compilation, backup CLI help, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, and `git diff --check` passed. No archive-age scenarios or systemd units were executed.

### 2026-11-05 — Finish local MVP operations artifacts
- Added a deployment record template for named ownership, authentication references, Docker socket policy, repository targets, backup/alert setup, Gemini data approval, and restore-drill signoff.
- Marked P4-02 complete for the local MVP implementation; host-specific configuration, alert integration, and an executed restore drill remain explicit requirements before production exposure.
- Verification: Python syntax compilation, backup CLI help, FastAPI import (30 routes/schema 10), Vite production build, TypeScript check, `git diff --check`, and roadmap count (19/19) passed. No deployment was installed and no restore drill was performed.

### 2026-11-05 — Start single-host production readiness phase
- Added `RELAY_ENV=production` startup checks requiring authentication and explicit non-wildcard CORS origins, and rejecting unsafe host-subprocess mode. The systemd service template enables production mode; setup docs explain required configuration.
- Added a separate 10-task production-readiness phase so the completed 19-item local MVP and operator-dependent release gates are tracked independently. H1 is complete (1/10); H2–H10 require deployment-specific work or execution-level verification.
- No tests were added or run.

### 2026-11-05 — Pin sandbox image provenance
- Pinned the sandbox base to the official Python 3.11.18 slim Trixie multi-platform manifest digest and made the pytest install invocation explicit. Production mode now rejects mutable sandbox tags and requires an image ID or repository digest.
- Documented image ID capture and production configuration in the API setup guide, root README, and systemd runbook. H2 is complete; production-readiness progress is 2/10.
- No tests or image builds were run.

### 2026-11-06 — Add a bounded Nginx reverse-proxy template
- Added an Nginx TLS/upstream config and shared proxy-location snippet with 1 MiB general, 10 MiB JSON submit, and 27 MiB multipart caps, per-IP request/connection limits, and request/upstream timeouts. Forwarded address headers are overwritten at the edge; Uvicorn trusts only loopback. Docs call out trusted load-balancer CIDRs for deployments with another proxy hop.
- Fixed the multipart body-limit path matching for the legacy `/tasks/submit` route. H3 is complete; production-readiness progress is 3/10.
- `git diff --check` passed. No Nginx config validation or tests were run.

### 2026-11-06 — Validate production CORS origins
- Production startup now accepts only bare HTTPS CORS origins and rejects malformed URLs, wildcard characters, credentials, whitespace, and URL path/query/fragment components. Kept live browser-origin and auth-flow verification as a deployment-host release check under H10.
- H4 is complete; production-readiness progress is 4/10. No tests were added or run.

### 2026-11-06 — Canonicalize proxy redirects
- Changed the Nginx HTTP redirect to use the configured canonical host instead of reflecting the request `Host` header, and reject mismatched hosts on HTTP and HTTPS virtual hosts.
- `git diff --check` passed; Nginx configuration was not installed or validated on a host.

### 2026-11-06 — Bound generated patch size and metadata
- Capped generated patch text at 1 MB and added scope checks rejecting repeated file sections, mode changes, renames/copies, and binary-patch metadata before Git validation or application.
- H5 is complete for implementation; adversarial request-level verification remains under H10. Production-readiness progress is 5/10.
- No tests were added or run.

### 2026-11-05 — Default direct API startup to localhost
- Changed `python main.py` to bind to `127.0.0.1` by default, require an IP literal for `RELAY_HOST`, and refuse non-loopback binds unless shared-token or per-user authentication is configured. Disabled auto-reload in this entry point.
- Documented the bind and authentication behavior in both setup guides and `.env.example`.
- Verification: not run in this change; no tests were added or executed.

### 2026-11-06 — Exercise local production recovery and isolation drills
- Added worker recovery tests covering lease expiry across a store reopen, cancellation/finalization ordering, and the maximum retry count. Added disposable Git repository drills covering stale bases, changed-file-only commits, staged commit recovery, and commit replay after a lost acknowledgement. Added backup creation, isolated restore, data inspection, and stale archive detection drills.
- Ran the full project test suite and found a missing `normalize_snapshot_paths` import in `sandbox.py`; fixed the import. Final suite: 25 passed, 2 opt-in/environment-specific checks skipped, with 1 Starlette deprecation warning. The loopback alert receiver drill passed separately (5 tests), and the Docker isolation drill passed separately (1 test).
- Added an `OnFailure` systemd webhook notifier for backup freshness failures; HTTPS is required for configured destinations and plain HTTP is accepted only for loopback drill receivers. Verified a failure notice reached a temporary loopback receiver.
- Built `relay-ai-sandbox:python3.11` from the pinned base and ran the opt-in Docker isolation probe against image `sha256:cb82b18dd09452ee061d5630516cad8f3a4ffb73a941564e57dfe00e89636f44` on Docker 29.5.2 / Ubuntu 24.04.4 under Colima; the probe passed. Added `tests/test_sandbox_isolation_drill.py` for repeatable runs. Deployment-host repetition remains required.
- H7, H8, and H9 are complete for their implementation and local execution criteria. H6 remains in progress until repeated on the actual deployment host; H10 still requires production endpoint configuration, named ownership, and the combined release review. Production-readiness completion is 8/10 (80%).
- `git diff --check` and Python `compileall` passed.
- Added and passed adversarial patch metadata/path tests plus production startup validation for missing authentication, mutable sandbox images, and unsafe CORS origins. Verified per-user viewer/operator enforcement and browser-origin CORS behavior. Vite production build and TypeScript check passed. H10 is in progress; target-host, accessibility/load, and ownership gates remain open.
- Validated the checked-in Nginx configuration with `nginx -t` inside a disposable `nginx:alpine` container using a temporary self-signed certificate; syntax validation succeeded and the certificate directory was removed.
- Opened the local dashboard with its API and confirmed the empty-task state and labelled submission controls in the browser accessibility tree. Full keyboard/screen-reader and load reviews still require release QA.

### 2026-11-06 — Verify hostile ZIP uploads at the API boundary
- Added request-level release checks for traversal paths, case-fold duplicate names, file/directory collisions, symlink entries, archives without readable text, malformed ZIP bytes, and the 500-entry limit. Invalid requests are verified to return 400/413 before task persistence; a normal source ZIP is verified to return 202 and persist the expected code map.
- Verification: focused release checks passed (6 tests; one existing Starlette/httpx deprecation warning); the full suite passed (41 passed, 3 skipped, same warning). `git diff --check` passed.

### 2026-11-07 — Add continuous integration checks
- Added GitHub Actions CI for backend tests and frontend typecheck/build on `main` pushes, pull requests, and manual runs. Restricted workflow permissions to repository read access and added job timeouts plus cancellation for superseded runs. Documented the same local commands in the root README.
- Local verification: backend suite passed (41 passed, 3 skipped); frontend TypeScript check and production build passed; workflow formatting and `git diff --check` reviewed. GitHub-hosted execution will provide the first remote runner confirmation after push.

### 2026-11-07 — Improve keyboard access to the dashboard workspace
- Added a first-focusable skip link that moves keyboard users past the task sidebar and navigation controls to the main workspace. The target main landmark is programmatically focusable, and the link becomes visibly styled when focused.
- Verification: frontend TypeScript check, production build, and `git diff --check` passed. Manual keyboard and screen-reader review remains part of the H10 release gate.

### 2026-11-07 — Verify ZIP resource limits at the API boundary
- Expanded upload endpoint drills to cover the 25 MiB transport cap, 2 MiB per-member cap, and 25 MiB expanded archive cap. Tests bypass the per-IP rate limiter so results are deterministic and isolate ZIP validation behavior.
- Verification: focused release checks passed (7 tests); full backend suite passed (42 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Verify concurrent worker claims and event order
- Added an eight-worker drill using separate SQLite store instances against one database. All eight queued jobs are claimed once, each attempt starts at one, and claim events are persisted ahead of their ingestion events in reverse-chronological API order.
- Verification: focused recovery drills passed (4 tests); full backend suite passed (43 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Verify the complete local remediation journey
- Added an API/worker end-to-end test that submits a task, executes all pipeline stages using the fake provider and controlled sandbox result, verifies persisted evidence, then approves, applies, and commits the patch in its actual task-owned Git workspace.
- Updated the Phase 3 blueprint gate with the test artifact and separated the fake sandbox result from the production sandbox runtime gate.
- Verification: end-to-end drill passed; full backend suite passed (44 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Exercise provider retry and failure behavior
- Added provider adapter tests for transient 429 recovery, token usage capture, immediate failure on a non-retryable 400, and retry exhaustion on transient errors without network calls.
- Verification: focused provider checks passed (4 tests); full backend suite passed (48 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Verify credential redaction in diagnostics
- Added regression coverage for configured Gemini/shared/per-user credentials, common provider and cloud token formats, JSON key-value secrets, and private-key blocks. Verified the JSON log formatter redacts credentials from both messages and exception tracebacks.
- Verification: focused redaction checks passed (2 tests); full backend suite passed (50 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Verify durable worker failure reporting
- Injected a provider exception into a claimed worker attempt and verified the task and job reach FAILED, a failure event is persisted, and the diagnostic is redacted before storage.
- Verification: focused recovery drills passed (5 tests); full backend suite passed (51 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Expose the provisional pipeline completion SLI
- Added `/metrics` gauges for accepted jobs in a rolling 30-day cohort, reviewed, failed, cancelled, in-progress, eligible, late, completed-within-15-minutes, and the completion ratio for the provisional 90% objective. Outcomes use persisted job/task timestamps; the ratio excludes cancellations and jobs younger than 15 minutes, while overdue active jobs count as late.
- Documented that owner deletion removes observations from this local ratio, so operators need an external durable metrics store for long-term SLO reporting.
- Verification: storage/metrics SLI test passed; full backend suite passed (52 passed, 3 skipped, one existing Starlette/httpx deprecation warning). `git diff --check` passed.

### 2026-11-07 — Correct completion SLI maturity handling
- Changed the completion ratio denominator to mature jobs only, excluding cancellations and jobs still inside their initial 15-minute window. A job still in progress after the objective deadline now counts as late. Added coverage for both fresh and overdue active jobs so recent traffic does not depress the SLI prematurely.
- Verification: focused SLI test passed; full backend suite passed (52 passed, 3 skipped, one existing Starlette/httpx deprecation warning); `git diff --check` passed.

### 2026-11-07 — Add request-level correlation to API telemetry
- Added a server-generated request ID to API responses and structured request logs containing only route template, method, status, duration, and ID. Unexpected 500 responses return a generic detail and preserve the ID. Exposed the ID through configured browser CORS headers and stored it in operator action audit details, linking approvals, applies, commits, cancellations, and retries to their request logs without a schema change.
- Verification: `python3 -m py_compile relay-ai/main.py relay-ai/observability.py` and `git diff --check` passed; no request telemetry test was added or run in this increment.

### 2026-11-07 — Surface request IDs in dashboard API errors
- Updated the shared dashboard API client to append the response request ID to readable API errors, using the header first and the sanitized error body as a fallback. This gives users a useful identifier to send to an operator without showing internal exception text.
- Verification: `npm run lint`, `npm run build`, and `git diff --check` passed.

### 2026-11-07 — Add bounded API request metrics
- Added process-local Prometheus request counters by registered route, normalized method, and status class, plus cumulative duration histogram buckets. These telemetry series are bounded, thread-safe, reset on process restart, and intentionally exclude requests rejected before application middleware.
- Added unit and API exposition checks for label normalization, cumulative buckets, request ID responses, emitted counter/histogram series, and sanitized unexpected 500 correlation in `relay-ai/tests/test_request_metrics.py`.
- Verification: focused telemetry checks passed (3 tests); full backend suite passed (55 passed, 3 skipped, one existing Starlette/httpx deprecation warning); `npm run lint`, `npm run build`, Python syntax compilation, and `git diff --check` passed.

### 2026-11-07 — Surface service readiness in the dashboard
- Added a live readiness badge driven by `/ready`, checked at startup, after saving an API token, and every 30 seconds. The badge distinguishes ready, degraded dependencies, offline API, and authentication-required states; narrow mobile layouts retain the status and controls.
- Verification: `npm run lint` and `npm run build` passed; full backend suite passed (55 passed, 3 skipped, one existing Starlette/httpx deprecation warning); `git diff --check` passed. An initial parallel run caused one 15-second production-config subprocess timeout; the isolated check and serial full-suite rerun passed.

### 2026-11-07 — Explain degraded readiness in the dashboard
- Preserved structured API error payloads and added safe readiness detail extraction, so the degraded badge can name missing dependencies from `/ready`. Authentication and network failures now include actionable accessible labels and titles.
- Verification: `npm run lint`, `npm run build`, and `git diff --check` passed. Backend code was unchanged in this increment.

### 2026-11-08 — Make readiness failures visible and retryable
- Added an inline dashboard notice for degraded, offline, and authentication-required readiness states. The notice shows the current reason without requiring hover and offers a dedicated readiness retry action; periodic checks and post-token-save checks remain active.
- Verification: `npm run lint`, `npm run build`, full backend suite (55 passed, 3 skipped, one existing Starlette/httpx deprecation warning), and `git diff --check` passed. Started the Vite server at `http://127.0.0.1:3000/`; automated browser inspection was denied by the browser URL policy, so visual verification remains outstanding.

### 2026-11-08 — Make production dashboard deployment same-origin
- Changed production builds to use relative same-origin API requests by default; development still defaults to `http://localhost:8000`, and `VITE_API_URL` remains an explicit override. Updated `.env.example` so a copied blank setting preserves environment-aware defaults.
- Updated the Nginx template to serve the Vite SPA from `/opt/relay-ai/dist`, proxy versioned/legacy API and health routes to FastAPI, and use the SPA entry point for client-side routes. Updated deployment and root setup docs.
- Verification: `npm run lint`, `npm run build`, full backend suite (55 passed, 3 skipped, one existing Starlette/httpx deprecation warning), `git diff --check`, and a production-bundle scan confirming no `http://localhost:8000` reference passed. Nginx syntax validation was unavailable because Nginx is not installed and the local Docker socket is inaccessible.

### 2026-11-08 — Harden dashboard delivery headers and cache policy
- Added `nosniff`, frame denial, strict-origin referrer handling, disabled unused camera/microphone/location permissions, and one-year HSTS to the TLS Nginx server. Fingerprinted `/assets/` files receive one-year caching; `index.html` is revalidated to avoid stale release manifests.
- Verification: `npm run lint`, `npm run build`, the production-bundle scan for localhost API URLs, and `git diff --check` passed. Nginx syntax validation remains unavailable in this environment.

### 2026-11-08 — Bound dashboard readiness probes
- Added an eight-second timeout to `/ready` requests. A timed-out probe now changes the visible service state to offline with a clear timeout message, while task submissions and Git actions retain their existing request behavior. Manual retries are serialized and show a disabled checking state while the probe runs.
- Verification: `npm run lint`, `npm run build`, the production-bundle scan for localhost API URLs, and `git diff --check` passed.

### 2026-11-08 — Establish Apple-inspired dashboard design system
- Added a dedicated visual theme with a system-font stack, bright layered canvas, translucent sidebar and toolbar, elevated rounded panels, blue action hierarchy, readable status/evidence colors, and consistent field/button treatments. Added gentle entrance, hover, empty-state, and readiness animations with `prefers-reduced-motion` support, visible focus treatment, and responsive refinements. Added a matching scalable app mark and light browser theme color.
- Recorded the visual direction in `BLUEPRINT.md` as a product standard for future dashboard work.
- Verification: `npm run lint`, `npm run build`, and `git diff --check` passed. Automated browser inspection remains unavailable under the current browser URL policy, so rendered cross-device visual review is still outstanding.

### 2026-11-08 — Add adaptive appearance preferences
- Added a persistent System/Light/Dark appearance control. System mode follows live OS appearance changes; explicit choices update page and browser chrome colors. Added dark-mode styling across navigation, forms, evidence, statuses, code output, and actions, with compact responsive header behavior and improved secondary-text contrast.
- Updated the blueprint to require operating-system appearance support and a user override.
- Verification: `npm run lint`, `npm run build`, and `git diff --check` passed. Browser interaction and rendered visual checks remain outstanding due the browser URL policy.

### 2026-11-08 — Add a credential-safe deployment preflight
- Added `relay-ai/preflight.py` with human and JSON output for production mode, authentication, HTTPS CORS, immutable sandbox image, unsafe subprocess mode, frontend build assets, Nginx sample host, and manual owner/host gates. The report intentionally describes only whether credentials are configured and never prints their values.
- Resolved frontend assets and the app mark are constrained to the build directory, including symlinks and traversal segments, with regression coverage for references resolving outside `dist`.
- Added `deploy/RELEASE_SIGNOFF_TEMPLATE.json` and `--signoff-file` support so operators can record evidence references and complete strict checks without placing secrets in the record. The CLI continues to label absent host evidence as manual.
- Added regression cases for ready config, missing production artifacts, invalid/insecure configuration, unsafe subprocess mode, malformed auth maps/roles, credential non-disclosure, and complete sign-offs. Documented use in the backend README.
- Verification: focused preflight suite passed (6 tests); full backend suite passed (61 passed, 3 skipped, one existing Starlette/httpx deprecation warning); frontend TypeScript and production build passed; Python syntax compilation and `git diff --check` passed. The current workspace correctly remains short of strict release readiness because no target or sign-off evidence has been selected.

### 2026-11-08 — Bring deployment checks into continuous integration
- Extended the existing least-privilege GitHub Actions workflow to test Python 3.11 and 3.12, compile backend Python modules, and run the deployment preflight after the frontend build.
- Frontend CI also runs the dependency-free browser-storage resilience tests and explicitly provisions Python 3.12 for the deployment preflight rather than relying on the runner image.
- CI validates the preflight JSON contract and expected release-gate IDs, including delivery headers, while preserving the report in the job log; incomplete host-specific configuration remains visible without blocking ordinary CI builds.
- Verification: backend suite passed on the available Python 3.12 interpreter (61 passed, 3 skipped, one existing Starlette/httpx deprecation warning); Python compileall passed; `npm run lint` and `npm run build` passed; preflight emitted all nine expected checks and correctly marked unconfigured production/host inputs as action required or manual; CI YAML parsed and `git diff --check` passed. GitHub-hosted execution, including Python 3.11, has not yet run.

### 2026-11-08 — Clarify the appearance control
- The dashboard appearance button now displays its active System/Light/Dark mode and its accessible label and tooltip announce the next mode in the cycle.
- Verification: `npm run lint`, `npm run build`, and `git diff --check` passed.

### 2026-11-09 — Add a restrictive production Content Security Policy
- Added a production CSP to the Nginx template that blocks objects, framing, untrusted scripts/styles, and insecure upgrades while allowing same-origin API requests and explicit HTTPS API origins.
- The deployment preflight now checks CSP, HSTS, MIME, framing, referrer, and permissions headers; CI validates this additional gate. Documented the policy and dependency review requirement in the operations runbook.
- Verification: full backend suite passed (61 passed, 3 skipped, one existing deprecation warning); Python compileall, `npm run lint`, `npm run build`, nine-check preflight including a permissive-CSP rejection case, CI YAML parse, and `git diff --check` passed. Nginx runtime syntax validation and browser CSP behavior remain unverified on a deployment host.

### 2026-11-09 — Keep dashboard controls usable when storage is restricted
- Wrapped local/session storage access so browser security policies or quota/access errors do not crash dashboard initialization or user actions. The theme uses the operating-system default when local storage is unavailable; API tokens and pending idempotency keys fall back to page-memory values when session storage is unavailable.
- Token-save feedback now says whether the token was stored for the tab session, held only in memory, or removed.
- Added dependency-free Node regression checks for permitted storage, denied storage, write quota errors, and stale values when removal is denied; added the test step to frontend CI.
- Verification: `npm run lint`, frontend storage tests, `npm run build`, and `git diff --check` passed; backend behavior was unchanged.

### 2026-11-09 — Confine deployment preflight frontend artifacts
- Applied resolved `dist/` boundary checks to `index.html`, JavaScript/CSS assets, and `relay-mark.svg`, preventing symlinks from pointing outside the generated frontend bundle and ensuring the preflight does not read an external index file.
- Added regression tests for index and app-mark symlinks that resolve outside `dist/`; retained the existing traversal-path regression for bundled assets.
- Verification: focused preflight suite passed (8 tests), Python compileall, frontend storage tests (4), TypeScript check, production build, nine-check preflight JSON output, CI YAML parsing, and `git diff --check` passed. The system Python lacked `google.genai`; the project virtual environment supplied the dependency for full-suite verification in the next build update.

### 2026-11-10 — Prevent stale dashboard refresh results
- Dashboard refreshes now abort any older request set when a newer refresh starts, commit response totals only after the current request set succeeds, ignore abort errors, and cancel outstanding calls when the app unmounts.
- This prevents search/filter changes and task polling from allowing older list/detail responses to overwrite current dashboard state. `AbortableRequests` holds the request lifecycle policy and has regression tests for replacement, stale completion, and unmount cancellation.
- Verification at implementation: frontend storage tests (4), TypeScript check, production build, focused preflight suite (8), Python compileall, CI YAML parsing, and `git diff --check` passed.

### 2026-11-10 — Verify and package the dashboard reliability increment
- Rechecked the pending storage, stale-refresh, CI, and frontend artifact-boundary changes against the project's `.venv`; corrected the earlier verification note after finding the environment was available under `relay-ai/.venv`.
- Added focused tests for request replacement, stale completion, and cancellation to the dependency-free Node suite.
- Verification: full backend suite passed (63 passed, 3 skipped, one existing Starlette/httpx deprecation warning); compileall, frontend tests (7), TypeScript check, production build, nine-check preflight JSON, CI YAML parsing, and `git diff --check` passed.

### 2026-11-10 — Seed the pitch deck checkout regression
- Added `demo-store/src/checkout.py` with the intentional double-subtraction bug, a failing `$100`/`$10` regression, a zero-discount control, and the one-line example patch.
- Registered a dashboard/API scenario from a fixed allow-list of the checked-in demo source and test files. Added a repeatable fixture test that verifies the scenario source, observes the expected baseline failure, applies the checked patch in a temporary copy, and observes both tests pass.
- Verification: seeded baseline reproduced `1 failed, 1 passed` (`80.00` vs expected `90.00`); patched copy passed `2 passed`; fixture tests passed (2 tests). Full backend suite passed (66 passed, 3 skipped, one existing deprecation warning); compileall, frontend tests (7), TypeScript check, production build, preflight JSON, CI YAML parsing, and `git diff --check` passed.

### 2026-11-10 — Exercise the checkout scenario through the fake-provider pipeline
- Added an API/worker end-to-end regression for the dashboard checkout scenario. The deterministic fake provider emits the scoped fix, the sandbox policy checks scope and patch syntax, and the test runs the trusted fixture tests in a temporary `subprocess_dev` workspace.
- The task reaches `AWAITING_HUMAN_APPROVAL` only after the real fixture output reports `2 passed`; the test asserts that no operator action occurred automatically. This test harness uses a controlled trusted fixture subprocess and does not claim Docker isolation.
- Verification: dedicated e2e test passed (1 test); full backend suite passed (66 passed, 3 skipped, one existing warning); compileall, frontend tests (7), TypeScript check, production build, nine-check preflight JSON, CI YAML parse, and `git diff --check` passed. The environment has no `GEMINI_API_KEY`, Docker daemon, or sandbox image, so the live Gemini plus isolated sandbox rehearsal is `BLOCKED`; exact requirements are recorded in P-A2.

### 2026-11-10 — Add checkout rehearsal and backup recording paths
- Added executable commands for fixture red/green, fake-provider API/worker, and live Gemini plus Docker rehearsals. The live script refuses to run without `GEMINI_API_KEY` or strict Docker isolation and uses a temporary database/workspace; the operator token is selected according to configured auth mode and is never printed.
- Added contract tests for shell syntax/help and missing-key fail-closed behavior, plus README instructions and an ignored local recording directory with a timestamped macOS screen-capture script. Recording capture was not run.
- Verification: script contract tests passed (5); fixture rehearsal passed (2); fake-provider rehearsal passed (1); live rehearsal exited 2 with the expected missing-key message and no secret output; full backend suite passed (68 passed, 3 skipped, one existing warning); compileall, frontend tests (7), TypeScript check, production build, and `git diff --check` passed.

### 2026-11-10 — Commit dashboard reliability increment
- Committed the previously approved, verified reliability-only change set on `main` as `87f4930` (`fix: harden dashboard state and preflight boundaries`). The commit contains dashboard storage and refresh protections, frontend tests, preflight boundary checks, and CI wiring; no push was performed.
- The separate checkout demo and rehearsal changes remain uncommitted pending explicit commit authorization, as required by the human-approval gate.

### 2026-11-10 — Add outbound Switch room status adapter
- Verified the official Switch agent protocol and event model. Switch agents receive room events on a WebSocket; message posting is separately documented as `POST /agents/{agent_id}/message` with an agent API bearer key and `{room_id, content}` body. Relay uses only this documented outbound operation and does not guess at an SDK, registration flow, or event consumer.
- Added an optional replaceable notifier that publishes allow-listed task IDs, pipeline stages, and states, plus final test/security/reviewer verdicts and the human approval requirement. It does not include bug reports, source paths/content, model output, patch text, exception details, or credentials. Invalid/partial settings fail closed; untrusted stage/status strings are rejected; network errors are hidden from responses and logs.
- Added mock-transport tests for route/auth/body, deduplication, final approval wording, invalid configuration, unrecognized stages, and safe handling of HTTP failures. Added service environment documentation. No live room message was sent.
- Verification: full backend suite passed (75 passed, 3 skipped, one existing Starlette/httpx deprecation warning); Switch adapter suite passed (7 tests, included in total); frontend tests (7), TypeScript check, production build, compileall, preflight JSON (9 checks), and `git diff --check` passed.

### 2026-11-10 — Re-run the checkout fake-provider rehearsal
- Re-ran `scripts/rehearse_checkout_fake.sh` against its test-owned temporary SQLite database and temporary workspace. The API/worker flow reached `AWAITING_HUMAN_APPROVAL`; the scoped checkout patch passed both fixture tests, reported `subprocess_dev`, and created no operator action.
- Verification: rehearsal 1 passed with one existing Starlette/httpx deprecation warning; full backend suite 99 passed/3 skipped with the same warning; frontend tests 20 passed/0 failed; `compileall`, TypeScript lint, Vite production build, and `git diff --check` passed. Live Gemini/Docker remains BLOCKED because credentials, daemon, and sandbox image are unavailable; no external service was called.

### 2026-11-10 — Re-verify host-free release gate and target-host guard
- Re-ran `deploy/run_host_free_release_checks.sh`: backend 99 passed/3 skipped with one existing Starlette/httpx deprecation warning; frontend 20 passed/0 failed; compileall, TypeScript lint, production build, and whitespace validation passed. The nine-item preflight reported 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, and 0 FAIL; this is explicitly not host certification.
- Confirmed the target-host script's required protected variables are unset without printing any values, then ran `deploy/run_target_host_drills.sh`. It exited 2 with the expected BLOCKED message for missing `RELAY_NGINX_CONFIG`, before Nginx, HTTP, or Docker checks. No host or external service was contacted.
- Repeated the fake-provider checkout rehearsal three additional consecutive times; each invocation passed (1 test) and remained isolated to temporary test data.

### 2026-11-10 — Cover GitHub response-bound and error-redaction guarantees
- Added regressions proving the adapter stops an oversized response at its 1 MB cap, suppresses a secret-bearing upstream error body, and does not follow the returned redirect.
- Focused GitHub adapter suite: 9 passed. Full host-free release gate: backend 101 passed/3 skipped with one existing Starlette/httpx deprecation warning; frontend 20 passed/0 failed; compileall, TypeScript lint, Vite production build, and `git diff --check` passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL; no GitHub request was made.

### 2026-11-10 — Expand local queue-claim concurrency sample
- Expanded the temporary-SQLite worker-claim test from 8 jobs/workers to 64 queued jobs drained across 16 concurrent store instances. Asserted unique exactly-once claims, attempt 1, ordered claim/ingestion events, and an empty queue after the burst.
- Focused test passed (1 test, 0.41s). Full host-free gate passed: backend 101 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, TypeScript lint, production build, and `git diff --check` passed. Nine-item preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No target host was measured; H10-LOAD-REVIEW remains BLOCKED pending an approved host and workload profile.

### 2026-11-10 — Assert production startup rejects host subprocess mode
- Added a production configuration regression that sets `RELAY_ALLOW_UNSAFE_SUBPROCESS=true` with otherwise valid production settings and confirms application import fails closed with the explicit policy error. The sandbox image must remain digest-pinned; no fallback to host execution is permitted in production.
- Focused configuration test passed (1 test). Full host-free gate passed: backend 102 passed/3 skipped with one existing Starlette/httpx deprecation warning; frontend 20 passed/0 failed; compileall, TypeScript lint, production build, and `git diff --check` passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. The live Docker isolation drill remains skipped because no pinned image/daemon is available.

### 2026-11-10 — Enforce sandbox fallback policy inside the runner
- Hardened `SandboxRunner` so `RELAY_ALLOW_UNSAFE_SUBPROCESS=true` enables host execution only when `RELAY_ENV=development`. Any production or unrecognized runtime mode remains `unavailable` when Docker is missing; the runner returns exit code 125 without executing test code.
- Added a direct runner regression that makes host execution fail the test if invoked, plus retained the application-startup production configuration guard. Focused checks passed (2 tests). Full host-free gate passed: backend 103 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, TypeScript lint, production build, and `git diff --check` passed. Nine-item preflight: 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. Docker's actual isolation integration remains skipped because no daemon/image is configured.

### 2026-11-10 — Guard the live Gemini rehearsal path
- Added a script-contract regression that verifies the Gemini key check precedes backend import, unsafe subprocess mode is forced off, Docker and the configured image are verified before task submission, and the script contains no approval/action call.
- Rehearsal-script suite passed (3 tests). Full host-free gate passed: backend 104 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, TypeScript lint, production build, and `git diff --check` passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. The live rehearsal itself remains BLOCKED on a real Gemini key and available Docker image; no credentials or external services were used.

### 2026-11-10 — Check both staged and unstaged diffs in the release gate
- The host-free release script previously checked whitespace only in the unstaged worktree diff, so staged changes could bypass that check. Added `git diff --cached --check`, extended the release-script contract test to require both checks, and clarified the staged/unstaged coverage in the runbook.
- Full host-free gate passed with the staged Switch set present: backend 104 passed/3 skipped with one existing Starlette/httpx deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, unstaged diff check, staged diff check, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL.

### 2026-11-10 — Reject duplicate IDs in GitHub repository configuration
- GitHub allow-list parsing now rejects duplicate JSON object keys instead of silently keeping the final repository mapping. Added a duplicate-ID configuration regression.
- Focused GitHub adapter suite passed (10 tests). Full host-free gate passed: backend 105 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, production build, both staged/unstaged diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL; no GitHub requests were made.

### 2026-11-10 — Re-run the seeded checkout red/green fixture
- Inspected and ran `scripts/rehearse_checkout_fixture.sh`; its pytest fixture creates a temporary demo copy, observes the seeded baseline failure, applies the checked example patch only in that copy, and confirms the regression/control tests pass. Rehearsal completed with 2 passed tests and did not modify the checked-in demo source.

### 2026-11-10 — Link each release blocker to signoff evidence
- Added a release-package regression mapping all nine H6/H10 blockers to the required evidence fields in `RELEASE_SIGNOFF_TEMPLATE.json`, including the three named-owner fields. The blocker matrix and signoff file must stay aligned as release asks change.
- Focused release-package suite passed (11 tests). Full host-free gate passed: backend 106 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both staged/unstaged diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL.

### 2026-11-10 — Keep failed Switch status messages retryable
- Review found that the notifier recorded a failed HTTP send as if it had been delivered, so an identical later caller invocation was deduplicated instead of retried. Removed that cache write and added a fail-once/succeed-next test. Automatic background retries are not implemented; worker-driven future stage callbacks or an explicit repeated invocation can retry. Updated the Switch setup docs to distinguish minimal progress messages from final test/security/reviewer verdicts and list excluded content.
- Switch notifier suite passed (8 tests). Full host-free gate passed: backend 107 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No live Switch request was made. The pending staged commit index remains unchanged; the retry fix is an unstaged follow-on change.

### 2026-11-10 — Bound Switch bridge URL and credential configuration
- Added a 2,048-character URL cap, parsed-port validation (including port zero/out-of-range rejection), and a 512-character/no-whitespace agent API key rule. Invalid values fail during configuration rather than reaching the HTTP client.
- Switch suite passed (12 tests). Full host-free gate passed: backend 111 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, production build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No live Switch request was made; these Switch changes remain unstaged follow-up work outside the pending exact staged proposal.

### 2026-11-10 — Verify Switch API keys stay out of configuration representations
- Added a sentinel regression proving `SwitchRoomConfig.__repr__` never includes its API key, complementing the transport/header tests that verify the key is only sent as bearer auth.
- Switch suite passed (13 tests). Full host-free gate passed: backend 112 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No real Switch credential was read or used.

### 2026-11-10 — Keep release signoff fields aligned with preflight
- Added a regression requiring the checked-in `RELEASE_SIGNOFF_TEMPLATE.json` to contain exactly the `SIGNOFF_FIELDS` accepted by `preflight.py`, complementing the blocker-to-evidence mapping test.
- Focused schema test passed (1 test). Full host-free gate passed: backend 113 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL.

### 2026-11-10 — Require a digest-pinned image in target-host drills
- Added an early target-drill guard requiring `RELAY_SANDBOX_IMAGE` to be a SHA-256 image ID or repository digest, before Nginx validation or HTTP/Docker operations. Added a subprocess regression confirming a mutable `:latest` tag exits BLOCKED without leaking the fake smoke token or touching a host; documented this guard in the runbook.
- Focused guard test passed (1 test). Full host-free gate passed: backend 114 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No target host was accessed.
- Also verified both accepted immutable forms (local `sha256:<digest>` image ID and repository `@sha256:<digest>`) pass the image guard and stop at the deliberately missing Python runtime before any host operation.

### 2026-11-10 — Validate GitHub pull-request response types
- Tightened upstream PR response validation to reject boolean/non-positive numbers, non-string states, and states outside `open`/`closed`, instead of allowing Python's `bool`-is-an-`int` behavior or malformed response fields through.
- Focused GitHub adapter suite passed (14 tests). Full host-free gate passed: backend 120 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both diff checks, and preflight passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL; no GitHub requests were made.

### 2026-11-10 — Avoid buffering unused Switch response bodies
- Changed Switch posting to use streamed HTTP responses and inspect only the status code. Since RELAY AI does not use the Switch response body, the client now closes it without buffering arbitrary response content.
- Added a tracking-stream regression proving a successful response body is never consumed. Switch suite passed (14 tests); full host-free gate passed: backend 121 passed/3 skipped with one existing deprecation warning; frontend 20 passed, compileall/lint/build and both diff checks passed. Preflight remains 3 PASS, 5 ACTION REQUIRED, 1 MANUAL, 0 FAIL. No live Switch request was made.

### 2026-11-10 — Bound Switch deduplication and retain final-state dedupe
- Replaced the unbounded per-task status cache with a 10,000-entry LRU bound, retained successful final states for duplicate suppression, and kept failed sends uncached so they remain retryable.
- Added regressions for duplicate final reports, failed-send retries, and cache eviction. Switch suite passed (15 tests); full host-free gate passed: backend 122 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. No live Switch service was called.

### 2026-11-10 — Enforce operator-only GitHub metadata reads
- Added an API regression proving a viewer receives 403 before the GitHub adapter loads protected configuration; the test fails if adapter construction or network-facing code runs.
- Focused API test passed (1 test). Full host-free gate passed: backend 123 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both diff checks, and preflight passed. No GitHub credentials or network calls were used.

### 2026-11-10 — Reject malformed Switch bridge URL characters
- Extended the Switch bridge URL checks to reject embedded whitespace and control characters before parsing or posting; added a newline-injection configuration regression.
- Switch suite passed (16 tests). Full host-free gate passed: backend 124 passed/3 skipped with one existing deprecation warning; frontend 20 passed/0 failed; compileall, lint, build, both diff checks, and preflight passed. No live Switch request was made.

### 2026-11-10 — Restrict Switch API keys to valid header characters
- Restricted environment-loaded agent API keys to at most 512 visible ASCII characters, preventing Unicode/whitespace values from reaching HTTP header construction. Added non-ASCII, whitespace, and oversized-key regressions and documented the URL/key limits for operators.
- Switch suite passed (17 tests). Full host-free gate passed: backend 125 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. No live credential was used.

### 2026-11-10 — Repeat the local concurrent queue burst
- Ran the 64-job/16-store temporary-SQLite queue drill three consecutive times with a fresh database each run. Results: 1 passed at 0.41s, 1 passed at 0.43s, and 1 passed at 0.37s. Each run asserted unique attempt-1 claims, claim-before-ingestion event order, and an empty queue.
- This repeated local correctness sample does not measure sustained throughput or target-host capacity; H10-LOAD-REVIEW remains BLOCKED until a host and workload profile are approved.

### 2026-11-10 — Log best-effort Switch notification failures safely
- Refactored the worker notification call so a `False` delivery result and raised delivery exception both produce a warning containing only the task ID; neither response bodies nor credentials are logged, and remediation continues. Clarified this behavior in the operator docs.
- Added a worker-level regression for the false-return path. Switch suite passed (19 tests); full host-free gate passed: backend 127 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. No live Switch call was made.
- Extended the worker-level regression to cover an exception containing a fake credential; the sanitized warning remains generic and contains only the task ID. Latest full host-free gate: backend 128 passed/3 skipped; frontend 20 passed; compileall/lint/build and both diff checks passed.

### 2026-11-10 — Clarify skipped full-suite integrations
- The latest backend suite reported 3 skipped: two opt-in Docker isolation tests (`RELAY_RUN_ISOLATION_DRILL=true` is required), and one backup-alert integration test that cannot bind a loopback receiver in this execution environment. The backup alert's unsafe-destination unit cases did run. No skip is counted as a pass.

### 2026-11-10 — Re-run host-free backup and restore cases
- Inspected the backup drill and confirmed it creates its database, applied workspace, archive, and isolated restore under pytest's temporary directory. Re-ran the backup/restore/staleness drill plus backup-alert unsafe-destination cases: 4 passed; the loopback receiver integration was deselected because this runtime cannot bind loopback.
- Production backup paths and destinations were not read or modified. The previous H9 local backup/restore and receiver drill remains recorded; this focused run does not replace target-owner signoff.

### 2026-11-10 — Cover the Switch bridge URL length bound
- Added a fail-closed regression for a 2,049-character bridge URL, complementing the existing malformed port and whitespace/control cases.
- Switch suite passed (18 tests). Full host-free gate passed: backend 126 passed/3 skipped with one existing deprecation warning; frontend 20 passed; compileall, lint, build, both diff checks, and preflight passed. No network call was made.
