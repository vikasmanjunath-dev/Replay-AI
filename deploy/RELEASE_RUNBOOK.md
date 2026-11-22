# RELAY AI release verification runbook

Status: host-free preparation is complete; deployment-host and named-owner work is blocked because no target host or owners have been selected. See [`RELEASE_BLOCKERS.json`](./RELEASE_BLOCKERS.json) for the exact ask and state for each action. Store evidence references in [`RELEASE_SIGNOFF_TEMPLATE.json`](./RELEASE_SIGNOFF_TEMPLATE.json). Never put secrets or source code in the evidence file.

## 1. Before scheduling a host window

- [ ] Review the current [`BLUEPRINT.md`](../BLUEPRINT.md), [`THREAT_MODEL.md`](../THREAT_MODEL.md), [`OPERATIONS.md`](../OPERATIONS.md), and [`deploy/systemd/README.md`](./systemd/README.md).
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
