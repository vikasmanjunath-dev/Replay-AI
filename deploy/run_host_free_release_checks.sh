#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${RELAY_RELEASE_PYTHON:-$ROOT/relay-ai/.venv/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
  echo "BLOCKED: create relay-ai/.venv and install relay-ai/requirements.txt, or set RELAY_RELEASE_PYTHON." >&2
  exit 2
fi

cd "$ROOT"
"$PYTHON" -m pytest -q relay-ai/tests
"$PYTHON" -m compileall -q relay-ai
npm test
npm run lint
npm run build
git diff --check
git diff --cached --check
"$PYTHON" relay-ai/preflight.py --json | "$PYTHON" -c 'import json,sys; checks=json.load(sys.stdin); counts={s:sum(c["status"]==s for c in checks) for s in ("PASS","ACTION REQUIRED","MANUAL","FAIL")}; print("Deployment preflight (not a host certification): " + ", ".join(f"{k}={v}" for k,v in counts.items()))'
echo "PASS: host-free release checks finished. Resolve every deployment preflight/blocker before release."
