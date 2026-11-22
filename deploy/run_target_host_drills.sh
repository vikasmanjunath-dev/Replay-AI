#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${RELAY_RELEASE_PYTHON:-$ROOT/relay-ai/.venv/bin/python}"

for name in RELAY_NGINX_CONFIG RELAY_SMOKE_URL RELAY_SMOKE_TOKEN RELAY_SANDBOX_IMAGE; do
  if [[ -z "${!name:-}" ]]; then
    echo "BLOCKED: set $name in the protected target-host environment." >&2
    exit 2
  fi
done
if [[ ! "$RELAY_SANDBOX_IMAGE" =~ ^sha256:[0-9a-f]{64}$ && ! "$RELAY_SANDBOX_IMAGE" =~ ^[^@[:space:]]+@sha256:[0-9a-f]{64}$ ]]; then
  echo "BLOCKED: RELAY_SANDBOX_IMAGE must be pinned by a SHA-256 image ID or repository digest." >&2
  exit 2
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "BLOCKED: configured release Python is missing or not executable." >&2
  exit 2
fi

cd "$ROOT"
nginx -t -c "$RELAY_NGINX_CONFIG"
"$PYTHON" deploy/target_host_smoke.py
RELAY_RUN_ISOLATION_DRILL=true "$PYTHON" -m pytest -q relay-ai/tests/test_sandbox_isolation_drill.py
echo "PASS: target-host drills passed. Save sanitized output references in deploy/RELEASE_SIGNOFF_TEMPLATE.json."
