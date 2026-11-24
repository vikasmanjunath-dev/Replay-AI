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
| 0. Freeze release candidate | Confirm intended commit, clean tree, CI status, host-free release result, and build/image identities. | DONE; the original candidate `8be75181f3b996da25fea27bca99c3f18e7a877c` passed its gate, and current clean main `a2aa1f5fc17c2d93ec6c292c73b1745db918f0e4` was reverified with host-free checks and exact-SHA CI run `45445667363` (Python 3.11/3.12, frontend, Docker rehearsal). Current host-free result: backend 132 passed/3 skipped, frontend 20 passed, compile/lint/build, preflight 3 PASS/5 ACTION REQUIRED/1 MANUAL/0 FAIL. JS/CSS hashes: `a2cc585bbc7882fc34911b110d8134d787a60182d7009cde53b777a1aee53200` / `7672a114d5dd02924da789b56a05cbd871874ad7e8a3a7eabe4440ce20104559`. Pinned local sandbox image digest remains `sha256:cb82b18dd09452ee061d5630516cad8f3a4ffb73a941564e57dfe00e89636f44`; opt-in local isolation drill passed 2 tests. Target-host image provenance and isolation remain required before staging. | None | Release owner | Commit SHA, CI run, sanitized host-free report, artifact identities |
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

### Advanced-feature execution playbooks (planning only)

These playbooks make A1–A8 ready for estimation after a trigger is observed. They do not satisfy a trigger or authorize implementation. At feature start, open a scoped tracker task and an ADR with the evidence, owner, success metric, threat review, data classification, compatibility impact, migration/backfill, rollback, and operational support plan. If the trigger is absent, keep the feature `DEFERRED`.

#### A1 — Data governance and tenant lifecycle

- **Entry evidence:** approved broader data classes or a contractual retention, export, deletion, or residency requirement; named data owner and retention/legal interpretation.
- **Design sequence:** define tenant identity and trusted assignment at authentication; map every task, snapshot, event, action, usage, workspace, backup, and repository reference to that boundary; choose tenant key and backup-encryption ownership; specify retention, export, deletion, restore, and audit semantics before schema changes.
- **Implementation slices:** add a versioned migration with an explicit legacy single-tenant mapping; enforce tenant scope in storage queries and all API/worker/retention/backup paths; add idempotent export and deletion workflows with audit evidence; add key rotation and encrypted-backup operations; update operator tooling and data-handling docs.
- **Exit checks:** negative cross-tenant tests for list/detail/events/actions/search/usage/workspaces/backups; migration and rollback on copied production-shaped data; deletion/export/restore and key-rotation drills; data-owner signoff. Do not claim deletion until primary, derived, log, and backup copies have documented expiry behavior.

#### A2 — Enterprise identity and repository policy

- **Entry evidence:** recorded failure of static bearer-token issuance, revocation, access review, or federation requirements; named identity and repository-policy owners.
- **Design sequence:** choose issuer and supported OIDC flows, stable subject mapping, group-to-role policy, session/token lifetime, outage behavior, provisioning/deprovisioning, break-glass path, and audit events. Define repository authorization separately from broad operator role.
- **Implementation slices:** add OIDC discovery/JWKS validation and login/callback or API token exchange; map verified subjects/groups to explicit roles with deny-by-default behavior; add per-repository grants and revocation; preserve a narrowly controlled break-glass account and record policy changes; migrate existing token users with a reversible overlap window.
- **Exit checks:** issuer/audience/signature/nonce and key-rotation tests; expired, revoked, disabled-user, and IdP-outage cases; cross-user, cross-role, and cross-repository denial tests on every resource endpoint; audit completeness and rollback of the migration. Never grant operator access from an unverified claim or missing group mapping.

#### A3 — Shared persistence and queue

- **Entry evidence:** pilot measurements breach an owner-accepted single-host throughput or availability objective; measured bottleneck and target workload are recorded.
- **Design sequence:** ADR compares transactional database/queue options against SQLite's transaction, lease, fencing, backup, and recovery semantics; choose global quota ownership, outbox delivery guarantees, migration method, and the supported single-/multi-region topology before code.
- **Implementation slices:** define provider-neutral storage/queue contracts; implement schema migrations and idempotent job/outbox dispatch; preserve attempt fencing, cancellation, bounded retry, and atomic terminal state; move quotas and rate limits to shared transactional state; add backup/restore and operational telemetry; cut over with a bounded canary and documented rollback to the frozen single-host release.
- **Exit checks:** duplicate delivery, worker crash, lease expiry, cancellation race, DB/queue partition, failover, restore, and migration rollback drills; load tests at the approved profile with measured recovery/throughput against SLOs. No dual-write or queue “exactly once” claim without a tested reconciliation protocol.

#### A4 — Sandbox isolation tiers

- **Entry evidence:** independent security review or approved workload requires stronger isolation than the current Docker boundary; threat model names attacker capability and protected host assets.
- **Design sequence:** compare hardened containers and microVM/runtime options against supported hosts, startup cost, image provenance, patching, egress control, resource accounting, cleanup, and operations. Specify tier-selection policy and prohibit caller-controlled privilege or tier escalation.
- **Implementation slices:** build a sandbox adapter contract; implement the selected runtime with immutable image identity, no secret injection, read-only inputs, explicit egress policy, resource/output/time limits, lifecycle cleanup, and structured failure evidence; add deployment preflight and operator runbooks.
- **Exit checks:** independent threat review; adversarial escape, filesystem, network/DNS, metadata/credential, resource exhaustion, timeout, and cleanup tests; reproducible image provenance and target-host drills. A second tier is not enabled until failure defaults to the stricter tier or denies execution.

#### A5 — Durable observability and SLO operations

- **Entry evidence:** owners require retained service-wide SLO reporting, cross-restart history, or actionable paging beyond current process-local metrics.
- **Design sequence:** agree SLI definitions, event-time windows, retention/deletion coupling, cardinality limits, alert ownership, redaction, sampling, and telemetry backend before choosing instrumentation/exporters.
- **Implementation slices:** instrument request/task/worker/provider/sandbox spans with correlation IDs and bounded attributes; export metrics/logs/traces to the approved backend; implement queue/stage/failure/backup alerts and error-budget views; document access, retention, outage buffering, and deletion behavior.
- **Exit checks:** metric reconciliation against persisted task evidence across restart; alert delivery and deduplication drills; no source text, tokens, or high-cardinality IDs in metric labels; dashboard and SLO calculations agree with documented cohort and deletion rules.

#### A6 — Pipeline policy and cost controls

- **Entry evidence:** pilot evidence shows repeated unsafe patches, provider failures, or material cost variance, with an owner-defined baseline and acceptable budget/error limits.
- **Design sequence:** define versioned policy schema, evaluation order, authority, budget source, estimation uncertainty, provider fallback boundaries, and human escalation. Policies may narrow permissions or halt work; they must never auto-approve, apply, commit, merge, or deploy.
- **Implementation slices:** store immutable policy version and decision evidence per task; add deterministic preflight checks for repository/file scope and provider choice; enforce per-owner/task budgets atomically before calls; implement bounded, schema-compatible fallback only for approved failure classes; surface rejection, uncertainty, and remaining budget in review UI.
- **Exit checks:** replayable decisions; budget boundary/concurrency tests; stale/invalid policy rejection; provider timeout, quota, malformed output, fallback exhaustion, and cost-estimate error drills; tests prove human approval remains mandatory and no policy can expand allow-lists.

#### A7 — Team review and change workflow

- **Entry evidence:** named pilot users demonstrate shared ownership or separation-of-duties need; approved role matrix and escalation deadlines.
- **Design sequence:** define reviewer assignment, eligible roles, repository-specific requirements, self-approval rule, reassignment/escalation, expiry, and how approval binds to an immutable diff/base/evidence revision.
- **Implementation slices:** persist reviewer assignments and workflow deadlines; add assignment/reassignment/escalation actions with idempotency and append-only audit; implement optional second approval for selected repositories; invalidate approvals when diff, base, tests, or policy evidence changes; expose queue and notification states accessibly.
- **Exit checks:** role-matrix tests; self-approval, missing reviewer, revoked reviewer, stale evidence, reassignment race, duplicate action, and timeout drills; full audit reconstruction. A timeout never implies approval.

#### A8 — Additional source-control providers

- **Entry evidence:** named pilot/customer requires a specific provider and operation absent from the existing local/GitHub adapters; owner identifies required permissions and branch/MR semantics.
- **Design sequence:** document a capability matrix and immutable revision model; define credential custody, webhook signature rules if used, rate-limit/retry behavior, provider-specific branch protection, and failure mapping. Keep branch publication, merge, and deployment out of scope unless separately authorized and threat-modeled.
- **Implementation slices:** extract only the common repository contract proven by current adapters; implement one provider with least-privilege reads and approval-gated change-request creation; verify base/head SHA and idempotency; preserve provider-neutral task evidence and failure states; add configuration/preflight and operator recovery docs.
- **Exit checks:** shared adapter contract suite; permission review; stale revision, duplicate request, rate limit, timeout, malformed response, and provider outage tests; provider failure leaves task/source evidence unchanged. No provider receives unrelated repository or write permissions.

#### Shared release gate for every selected feature

Before implementation, the tracker must name the trigger evidence, accountable owner, measurable baseline/target, dependencies, threat/data review, schema/API compatibility, migration and rollback steps, and operational owner. Close with focused tests, relevant full suites, CI on the exact commit, updated blueprint/docs where behavior changes, and an evidence-backed tracker status. Keep all unselected A-items `DEFERRED`; complete planning is not feature authorization.

## 9. Definition of done and change control

For each implementation slice: define a single behavior; add/update focused tests; run the relevant suite; update `TRACKER.md`; update `BLUEPRINT.md` or `README.md` only when product/API behavior changes; preserve API compatibility or document migration; and review the diff for secrets, generated files, and unrelated artifacts. A task is `DONE` only with evidence, not because code exists. A host-dependent task is `BLOCKED` until its named owner supplies the missing resource and evidence. Do not store credentials in Git.

For a release candidate, require a clean checkout, CI success for the exact commit, successful host-free release checks, a pinned sandbox image, all applicable Stage 4 passes, completed owner/data/SLO approvals, backup/restore evidence, and a signed go/no-go. The current plan stops before deployment because those owner/host inputs have not been selected.

## 10. Current next actions

1. Service owner selects the target/hostname and names primary, backup, security, rollback, accessibility, data, and SLO owners.
2. Data owner records Gemini data-use approval; service/SLO owners set numeric service and load targets.
3. Owners decide whether live Switch/GitHub checks are in release scope and provision least-privilege test resources through protected channels.
4. Once Stages 1–2 are approved, schedule staging and target-host window; complete the Stage 3–4 checklists.
5. Review all evidence together and make a signed pilot go/no-go decision. Until then, keep deployment and public exposure blocked.
