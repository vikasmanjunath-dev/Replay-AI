#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Run the seeded checkout regression before and after the checked example patch."
  exit 0
fi
if [[ $# -ne 0 ]]; then
  echo "Usage: $0 [--help]" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$repo_root/relay-ai/.venv/bin/python"
if [[ ! -x "$python" ]]; then
  echo "Create relay-ai/.venv and install relay-ai/requirements.txt first." >&2
  exit 2
fi

cd "$repo_root/relay-ai"
exec "$python" -m pytest -q tests/test_demo_store_fixture.py
