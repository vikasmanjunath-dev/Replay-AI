# RELAY AI End-to-End Delivery Plan

**Planning date:** 2026-11-24 (Asia/Kolkata)  
**Planning baseline:** release candidate `8be75181f3b996da25fea27bca99c3f18e7a877c` passed exact-SHA host-free checks and CI. Its pinned local sandbox image digest and local isolation probe are recorded below; target-host evidence remains open.
**Release posture:** local MVP implemented; single-host production/pilot gate remains closed pending named-owner and target-host evidence.

This plan sequences the remaining work from the current repository baseline to a controlled pilot. `TRACKER.md` is the status ledger, `BLUEPRINT.md` is the product/architecture contract, `deploy/RELEASE_BLOCKERS.json` is the exact external-action list, and `deploy/RELEASE_SIGNOFF_TEMPLATE.json` is the evidence record. Update all four when a gate changes. Do not put secrets, source code, private URLs, or personal data in those files.

## 1. What is complete

The local single-host MVP includes the React/Vite dashboard, versioned FastAPI API, Gemini and fake provider adapters, SQLite persistence and lease-based worker, task/event/action history, bounded retries and recovery, per-owner active-task admission limits, immutable snapshots, fail-closed Docker test execution, patch/evidence review, human approval, allow-listed Git apply/commit, per-user token authorization, retention and backup/restore tooling, metrics/logging, optional Switch and GitHub integrations, CI, and host-free release checks. The current dashboard also supports the guarded GitHub PR workflow and branch suggestions.

Implementation status does not certify production operation. The selected host, hostname, owners, protected production secrets, data-use approval, and target-host test evidence are not present in the repository. No public launch is approved by this plan.

## 2. Execution sequence

Run these stages in order. A blocked prerequisite stops dependent work; it does not get converted to a pass by a local mock or a documentation update.

| Stage | Work | Status | Depends on | Owner | Exit evidence |
|---|---|---|---|---|---|
| 0. Freeze release candidate | Confirm intended commit, clean tree, CI status, host-free release result, and build/image identities. | DONE; clean candidate `8be75181f3b996da25fea27bca99c3f18e7a877c` passed the full host-free release script; GitHub Actions run `45438208521` passed on Python 3.11, Python 3.12, and frontend jobs. Local image built from the pinned Dockerfile has ID/digest `sha256:cb82b18dd09452ee061d5630516cad8f3a4ffb73a941564e57dfe00e89636f44`; the local Docker isolation probe passed (2 tests) on Docker 29.5.2. Build outputs: JS `a2cc585bbc7882fc34911b110d8134d787a60182d7009cde53b777a1aee53200`, CSS `4ec779d4bf46cff44eaea6d9eb618d02742c22d2943a30433ced8fe296421982`. Target-host image provenance remains required before staging. | None | Release owner | Commit SHA, CI run, sanitized host-free report, artifact identities |
| 1. Establish service ownership and target | Select host, hostname, environment boundary, change window, rollback owner, primary/backup operator, and security/escalation contact. | BLOCKED | Owner decisions | Service owner | Named roles, target and hostname, approved change/rollback window |
| 2. Approve data and service objectives | Approve Gemini source-data use/retention; decide enabled optional integrations; set queue/load profile, availability/completion objectives, backup age, RPO, and RTO. | BLOCKED | Stage 1 | Data owner, security owner, SLO owner | Approval reference, integration scope, accepted numeric thresholds |
| 3. Prepare staging | Provision host identity, protected secrets, TLS, Nginx, persistent SQLite/workspace paths, encrypted backup destination, alert receiver, monitoring, and digest-pinned sandbox image. | TODO; blocked by Stages 1–2 | Stages 1–2 | Deployment operator | Sanitized config/preflight evidence, readiness, image digest, secret-store confirmation |
| 4. Verify target and recovery | Run target-host drills, controlled task lifecycle, load profile, backup alert/restore, accessibility review, and only the live integrations selected in Stage 2. | BLOCKED; blocked by Stage 3 | Stage 3 | Security, operations, accessibility, integration owners | All applicable H6/H10 evidence references; failures and retests resolved |
| 5. Approve and run controlled pilot | Restrict access to named operators and allow-listed test repositories; operate at agreed low volume and review task/audit/backup/alert outcomes. | TODO; blocked by Stage 4 | Stage 4 | Service, security, operations owners | Signed go/no-go, pilot window/results, rollback readiness, remaining-risk disposition |
| 6. Decide on broader release | Decide whether evidence supports broader single-host use or whether access/workload requires more controls. | DEFERRED | Stage 5 | Product and service owners | Explicit release decision and scope |
| 7. Select advanced capabilities | Use the post-pilot backlog below; commission only the capabilities triggered by measured demand or a control gap. | DEFERRED | Stage 5 pilot evidence | Product, service, security, architecture owners | Approved capability brief with trigger evidence, scope, owner, risks, and acceptance thresholds |

## 3. Stage 1–2 decision checklist

These are inputs for the service owners; no values are assumed by this plan.

- **Target:** host/provider, operating system, hostname, network boundary, staging versus production, and who can access it.
- **People:** primary operator, backup operator, security/escalation contact, accessibility reviewer, SLO owner, data owner, and rollback/change owner.
- **Data:** whether repository/report data may be sent to the selected Gemini account; applicable retention and data handling terms; approved source classes for the pilot.
- **Identity:** whether per-user bearer-token administration is sufficient for the pilot; who provisions, rotates, revokes, and audits credentials. Do not expose the service publicly with a shared token as a substitute for owner-scoped identities.
- **Integrations:** explicitly enable or leave disabled Switch notifications and GitHub PR creation. Live checks are required before enabling them; they are not required to prove the core local pipeline when disabled.
- **Service targets:** accepted availability, task completion deadline, queue latency, max concurrency, request/error thresholds, backup maximum age, RPO, and RTO.
- **Operations:** backup destination and encryption, alert receiver, maintenance window, log/metrics retention, incident contact path, and rollback trigger.

Record references and decisions only; never record actual credential values, webhook URLs, source snapshots, or unredacted logs.

## 4. Stage 3 staging preparation checklist

1. Select and freeze the release commit; confirm CI status and run `deploy/run_host_free_release_checks.sh` from the release checkout.
2. Build the sandbox image from the pinned Dockerfile on the target host. Record the immutable image ID/digest and configure `RELAY_SANDBOX_IMAGE`; runtime image pulls remain prohibited.
3. Create a dedicated service account and restrict file access to the application, database, applied workspace, and backup paths. Keep `RELAY_APPLIED_ROOT` separate from backups.
4. Put Gemini, API/user tokens, optional Switch/GitHub credentials, and backup webhook only in the host secret manager or protected environment file. Use least privilege and confirm redaction in sanitized logs.
5. Configure production mode, explicit HTTPS CORS origins, allowed users/roles, loopback-only upstream trust, Nginx TLS/body/rate/timeout limits, and local Git repository allow-lists.
6. Configure persistent data directories, backup schedule, retention policy, freshness alert receiver, service restart policy, and log/metrics collection. Confirm disk capacity and file permissions.
7. Deploy first to an isolated staging boundary; verify startup, `/health`, `/ready`, `/metrics`, authentication, and expected denial behavior before task submission.

**Stage 3 pass:** production settings load without unsafe defaults, readiness is truthful, unauthenticated access is denied, an authorized operator is owner-scoped, and no secret appears in command output/logs/evidence.

## 5. Stage 4 verification matrix

Use the exact asks in `TRACKER.md` and `deploy/RELEASE_BLOCKERS.json`; capture evidence in the sign-off template.

| Area | Required check | Pass condition |
|---|---|---|
| Proxy/auth/CORS (H10-PROXY-AUTH-CORS) | `nginx -t`; unauthenticated and authenticated health/readiness/metrics; HTTPS origin and disallowed-origin behavior; delivery headers. | All expected allow/deny outcomes match policy; no permissive wildcard or trusted-forwarded-header gap. |
| Sandbox isolation (H6-TARGET-ISOLATION) | Target drill with the pinned image, no network, read-only mounts/root, non-root user, dropped capabilities, and resource/output limits. | Drill passes on the actual deployment host and recorded digest equals configured image. |
| Pipeline lifecycle | Use a designated test repo and deterministic/approved provider; trace submit through review, approve, apply, and commit. Confirm the target base is checked and only authorized changed files are committed. | Correct evidence and owner audit are persisted; stale base and unsafe patch are rejected; original source remains untouched. |
| Load/concurrency (H10-LOAD-REVIEW) | Run only the owner-approved concurrency, ramp, duration, and traffic profile. Inspect queue delay, latency, failures, CPU/memory, and lease recovery. | All measured values meet accepted thresholds; no duplicate claims, lost tasks, or unbounded backlog. |
| Backup/alert/restore (H10-BACKUP-ALERT, H10-RESTORE-DRILL) | Verify a current archive, fire one controlled stale/missing backup alert, restore an identified archive into a new isolated directory, and inspect DB/task/event/source/workspace integrity. | Named receiver confirms delivery; restore is non-destructive and meets accepted RPO/RTO. |
| Accessibility (H10-ACCESSIBILITY-REVIEW) | Keyboard-only walkthrough and supported native screen reader/browser pair; inspect focus order, names, announcements, errors, empty/offline state, zoom/mobile, light/dark contrast. | Reviewer records versions/results; release-blocking defects are fixed and retested. |
| Owners/SLO/data (H10-OWNERS, H10-SLO-ACCEPTANCE, H10-GEMINI-DATA-APPROVAL) | Confirm role assignments, incident route, accepted targets, and written provider data approval. | References and numeric targets are recorded; no secret or source is included. |
| Optional Switch/GitHub | If enabled, test only a provisioned room or dedicated GitHub repository/branch with minimum permissions. Verify status-only notification or exact SHA-gated PR behavior. | Live behavior is confirmed without granting push/merge/deploy or unrelated repository permission. |

**Stage 4 fail handling:** stop the release, preserve sanitized logs and task IDs, classify the failure, assign an owner, fix on a new release candidate, rerun the failed check and relevant regression suite, then rerun the full host-free gate. Never repair production state manually without an audited change/rollback plan.

## 6. Stage 5 pilot and release decision

- Limit the pilot to named users, approved source classes, and explicitly allow-listed repositories.
- Set a fixed pilot duration and task-volume ceiling from the accepted load profile. Review daily queue, failure, provider, sandbox, audit, backup, and alert outcomes.
- Keep human approval mandatory. Relay's GitHub integration does not push a branch, merge a PR, or deploy; branch publication remains an operator action.
- Roll back or pause intake for auth/ownership failure, sandbox escape or isolation uncertainty, unapproved data flow, unexpected repository mutation, lost/corrupt task data, missed critical alert, or any accepted SLO/security threshold breach.
- At pilot end, the service, security, operations, and data owners review the evidence and sign one of: proceed at the same scope; extend pilot with named corrective actions; or stop/rollback.
- A go decision must list residual risks, their owners, due dates, compensating controls, and expiry. If policy disallows residual blockers, the release remains blocked.

## 7. Deferred engineering decisions

Do not implement these without an observed requirement and an owner-approved design:

- **Multi-host durability:** replace SQLite queue/lease assumptions with a shared transactional database and queue; define migration, idempotency, disaster recovery, and rollback.
- **Global limits and telemetry:** move per-process/per-client rate limits and rolling DB-derived metrics to shared services when multi-instance use or durable SLO reporting is required.
- **Enterprise identity:** select an identity provider only if bearer-token administration cannot meet the pilot's lifecycle, revocation, audit, or federation needs.
- **Provider portability:** add another model adapter only for a stated availability, cost, or policy need; preserve structured schemas, redaction, retry bounds, and deterministic tests.
- **Additional repository operations:** any push, merge, branch creation, or deployment endpoint requires a separate threat model, narrowly scoped permission model, explicit user confirmation UX, audit semantics, rollback plan, and adversarial tests. These are out of current product scope.
- **Data lifecycle:** before broader use, set source snapshot and event retention periods, backup retention, deletion guarantees, legal/data owner requirements, encryption-at-rest policy, and restore access controls.

## 8. Advanced feature roadmap after the pilot

These are planning candidates, not release commitments. Keep them deferred until the named trigger is observed and an owner approves a feature brief. Do not build scale, identity, or policy machinery solely for hypothetical demand.

| Order | Feature area | Start when | Scope to plan | Acceptance evidence |
|---|---|---|---|---|
| A1 | Data governance and tenant lifecycle | Broader source-data classes or contractual retention/deletion requirements are approved | Per-tenant retention, deletion/export policy, encrypted backups, key rotation, model/data routing rules, and audited administrative access | Data-owner approval; deletion/restore drills; encryption/key-rotation evidence; no cross-tenant reads in negative tests |
| A2 | Enterprise identity and repository policy | Static bearer-token administration cannot meet operator lifecycle, federation, or access review requirements | OIDC first; map groups to viewer/operator roles; per-repository task access; token revocation and break-glass procedure; keep repository IDs allow-listed | Login/revocation tests; cross-user and cross-repository denial tests; audit trail for role and policy changes |
| A3 | Shared persistence and queue | Pilot measurements exceed the accepted single-host capacity or availability target | Select a transactional database and queue through an ADR; define migrations, idempotent delivery, fenced leases, global quotas, transactional outbox, backup consistency, and rollback | Approved workload target; crash/duplicate/partition drills; migration rollback; measured recovery and throughput against SLOs |
| A4 | Sandbox isolation tiers | Security review or pilot scope requires stronger isolation for untrusted or public submissions | Compare hardened containers with microVM/runtime isolation; define network egress, resource budgets, image provenance, secret boundary, and cleanup | Independent threat review; adversarial escape tests; egress/resource verification; reproducible image provenance |
| A5 | Durable observability and SLO operations | Pilot owners need retained service-wide SLOs or actionable paging beyond process-local metrics | OpenTelemetry-compatible traces/metrics, durable aggregation, queue and stage alerts, error budgets, and redacted audit export | Alert delivery drill; metric correctness across restart; SLO dashboard reconciles with task evidence and deletion policy |
| A6 | Pipeline policy and cost controls | Pilot data shows repeated unsafe patches, provider failures, or material model cost variance | Versioned policy profiles, per-owner budgets/quotas, provider fallback rules, deterministic prompt/schema versions, and reviewer escalation; preserve human approval | Replayable policy decision records; budget boundary tests; failure/fallback drills; no automatic approval or merge |
| A7 | Team review and change workflow | Pilot users need shared ownership or separation of duties | Reviewer assignment, optional second approval for selected repositories, review deadlines, escalation, and auditable handoff | Role matrix; self-approval and missing-approver denial tests; complete action/evidence audit |
| A8 | Additional source-control providers | A named pilot/customer requires another provider | Provider-neutral repository interface, provider-specific least-privilege adapter, immutable revision checks, PR/MR semantics, and capability matrix | Contract suite per provider; permission review; stale revision and duplicate-request drills; provider failure does not alter task evidence |

### Advanced-feature sequencing rules

1. Close the controlled pilot and retain its workload, cost, failure, identity, and operator findings before selecting A1–A8.
2. Resolve data governance and identity requirements before broadening users, repositories, or source-data classes.
3. Start shared infrastructure only from measured capacity or availability gaps; carry out migration and rollback design before code.
4. Preserve current safety boundaries: human approval stays mandatory; no push, merge, or deployment endpoint is implied by this roadmap.
5. Give every selected feature an owner, baseline metric, target, migration/rollback plan, threat review, and evidence-backed `DONE` gate in `TRACKER.md`.

## 9. Definition of done and change control

For each implementation slice: define a single behavior; add/update focused tests; run the relevant suite; update `TRACKER.md`; update `BLUEPRINT.md` or `README.md` only when product/API behavior changes; preserve API compatibility or document migration; and review the diff for secrets, generated files, and unrelated artifacts. A task is `DONE` only with evidence, not because code exists. A host-dependent task is `BLOCKED` until its named owner supplies the missing resource and evidence. Do not store credentials in Git.

For a release candidate, require a clean checkout, CI success for the exact commit, successful host-free release checks, a pinned sandbox image, all applicable Stage 4 passes, completed owner/data/SLO approvals, backup/restore evidence, and a signed go/no-go. The current plan stops before deployment because those owner/host inputs have not been selected.

## 10. Current next actions

1. Service owner selects the target/hostname and names primary, backup, security, rollback, accessibility, data, and SLO owners.
2. Data owner records Gemini data-use approval; service/SLO owners set numeric service and load targets.
3. Owners decide whether live Switch/GitHub checks are in release scope and provision least-privilege test resources through protected channels.
4. Once Stages 1–2 are approved, schedule staging and target-host window; complete the Stage 3–4 checklists.
5. Review all evidence together and make a signed pilot go/no-go decision. Until then, keep deployment and public exposure blocked.
