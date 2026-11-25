# RELAY AI release verification runbook

Status as of 2026-11-25: host-free preparation is complete; deployment-host and named-owner work is blocked because no target host or owners have been selected. The end-to-end sequence is in [`PLAN.md`](../PLAN.md); see [`RELEASE_BLOCKERS.json`](./RELEASE_BLOCKERS.json) for the exact ask and state for each action. Store evidence references in [`RELEASE_SIGNOFF_TEMPLATE.json`](./RELEASE_SIGNOFF_TEMPLATE.json). Never put secrets or source code in the evidence file. A planning update does not close a blocker or authorize deployment.

## 1. Before scheduling a host window

- [ ] Review the current [`BLUEPRINT.md`](../BLUEPRINT.md), [`THREAT_MODEL.md`](../THREAT_MODEL.md), [`OPERATIONS.md`](../OPERATIONS.md), and [`deploy/systemd/README.md`](./systemd/README.md).
- [ ] Follow the stage order and dependencies in [`PLAN.md`](../PLAN.md); do not start target-host work before the target, owners, data approval, SLOs, and change window are recorded.
- [ ] Select a single-host target, public HTTPS hostname, primary and backup operators, security contact, and change/rollback owner.
- [ ] Approve the Gemini source-data use and retention basis; store the approval reference only.
- [ ] Agree on SLO thresholds, load profile, backup destination/age limit, and recovery point/time objectives.
- [ ] Provision secrets in the host secret manager. Do not paste tokens, API keys, webhook URLs, or user bearer tokens into this tracker or sign-off record.
- [ ] Build the pinned sandbox image on the target and record the image digest. Do not pull images during service runtime.

## 2. Host-free checks

From the repository root, run:

```sh
deploy/run_host_free_release_checks.sh
```

This runs backend pytest, Python compilation, frontend unit tests, TypeScript lint, the production frontend build, whitespace checks for both staged and unstaged Git changes, and the nine-item deployment preflight. A green host-free run does not certify host configuration. Preflight's `ACTION REQUIRED` and `MANUAL` results remain release blockers until the corresponding evidence is supplied.

## 3. Target-host drills

After the host owner has installed the release and configured protected environment files:

1. Set `RELAY_NGINX_CONFIG` to the installed Nginx config; confirm the template hostname and TLS certificate paths are real.
2. Set `RELAY_SMOKE_URL` to the public HTTPS origin and `RELAY_SMOKE_TOKEN` to an operator credential from the secret manager. These values are read by the drill and never printed. Do not put credentials in URL arguments.
3. Confirm `RELAY_SANDBOX_IMAGE` names the digest-pinned image built on that host. The drill rejects mutable tags before Nginx or HTTP checks.
4. From the installed release root, run:

   ```sh
   deploy/run_target_host_drills.sh
   ```

The script runs `nginx -t`, verifies unauthenticated rejection and authenticated `/health`, `/ready`, and `/metrics`, checks delivery headers and CORS behavior, then enables the opt-in Docker isolation probe. It fails on any missing prerequisite or failed check. It does not reload Nginx, restart services, change firewall rules, or deploy a release.

### Approved queue/load profile

`deploy/load_drill.py` prepares and runs a bounded queue sample against the seeded checkout scenario. Agree on the target, task count, concurrency, duration, error/latency thresholds, and provider-data approval before running it. Each submitted task invokes the configured model and sandbox, consumes provider/host resources, and remains in the target database for normal review and retention handling. Use an idle test deployment and an operator token from its secret manager; do not run against production without explicit owner approval.

The default is a no-network dry run. Set `RELAY_LOAD_URL` to the bare HTTPS API origin and `RELAY_LOAD_TOKEN` in the protected environment, then preview the bounded profile:

```sh
relay-ai/.venv/bin/python deploy/load_drill.py --tasks 2 --concurrency 2 --report-file /secure/evidence/load-drill.json
```

The dry run does not create the report file. Only after the service, data, and SLO owners approve that exact profile, add `--execute` to submit and save the JSON evidence. The report path's parent directory must already exist, and existing files are never overwritten. `--ramp-seconds` spreads submissions across the approved ramp (zero is an immediate bounded burst); `--task-timeout` bounds the time spent waiting for the resulting tasks. The runner caps a sample at five tasks, records submission latency, final task states, and selected before/after Prometheus samples, and never prints the token or API error body. Redact task IDs before recording a reference in the sign-off file. The result does not include host CPU/memory or prove sustained capacity, so pair it with host monitoring and the accepted profile's duration and thresholds. A timeout or failed task is a failed drill, not a pass.

## 4. Backup, alert, restore, and recovery

- [ ] Confirm the assigned encrypted backup destination is outside `RELAY_APPLIED_ROOT`; run the configured backup job and `relay-ai/.venv/bin/python relay-ai/backup.py --verify <archive>`.
- [ ] Run the freshness check with the configured age limit; trigger one controlled stale/missing-archive alert and obtain confirmation from the named receiver.
- [ ] Restore an identified archive into a new, isolated path with `--restore-archive ... --restore-to ...`. Do not overwrite live state. Check SQLite integrity, task/source/workspace presence, and a representative event/action history.
- [ ] Have the recovery owner review the recovery point/time and rollback steps, then record the archive reference and sanitized outcome.

## 5. Owner reviews

- [ ] Security owner confirms production authentication, task ownership, CORS, TLS/proxy trust, sandbox isolation, secret handling, and Gemini data approval.
- [ ] Accessibility reviewer completes keyboard-only, screen-reader, 390 px mobile, focus/contrast, and error/empty-state checks; log browser/AT versions and defects.
- [ ] Service owner runs the approved queue/load profile and reviews latency, errors, memory, worker concurrency, and recovery behavior.
- [ ] SLO owner accepts thresholds; primary and backup operators confirm alerts and incident contacts.
- [ ] Copy the completed evidence references into the sign-off template. Leave all unresolved checks explicitly BLOCKED and keep the release gate closed.

## 6. Release decision

The owner may consider a release only when every applicable sign-off field has a verifiable evidence reference and every blocker has been closed by its named owner. The current repository contains no deployment target, production secret, named service owner, or approval record, so this runbook does not authorize deployment.
