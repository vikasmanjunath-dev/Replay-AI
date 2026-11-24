#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Run the seeded checkout scenario through the API and worker with the deterministic fake provider."
  echo "Use --docker with a digest-pinned RELAY_SANDBOX_IMAGE to test the real Docker isolation path."
  exit 0
fi
use_docker=false
if [[ "${1:-}" == "--docker" && $# -eq 1 ]]; then
  use_docker=true
elif [[ $# -ne 0 ]]; then
  echo "Usage: $0 [--help|--docker]" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$repo_root/relay-ai/.venv/bin/python"
shared_tmp=""
cleanup() {
  if [[ -n "$shared_tmp" ]]; then
    rm -rf -- "$shared_tmp"
  fi
}
trap cleanup EXIT

if [[ ! -x "$python" ]]; then
  echo "Create relay-ai/.venv and install relay-ai/requirements.txt first." >&2
  exit 2
fi

if [[ "$use_docker" == "true" ]]; then
  if [[ ! "${RELAY_SANDBOX_IMAGE:-}" =~ ^sha256:[0-9a-f]{64}$ && ! "${RELAY_SANDBOX_IMAGE:-}" =~ ^[^@[:space:]]+@sha256:[0-9a-f]{64}$ ]]; then
    echo "Set RELAY_SANDBOX_IMAGE to the built image ID or repository digest before using --docker." >&2
    exit 2
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "Docker daemon is unavailable; no subprocess fallback will run." >&2
    exit 2
  fi
  if ! docker image inspect "$RELAY_SANDBOX_IMAGE" >/dev/null 2>&1; then
    echo "The configured digest-pinned sandbox image is unavailable locally; runtime pulls are disabled." >&2
    exit 2
  fi
  export RELAY_CHECKOUT_USE_DOCKER=true
  export RELAY_ALLOW_UNSAFE_SUBPROCESS=false
  # Colima commonly shares the project path with its VM, not macOS /var/folders.
  shared_parent="${RELAY_CHECKOUT_TMPDIR:-$repo_root}"
  mkdir -p "$shared_parent"
  shared_tmp="$(mktemp -d "$shared_parent/.relay-checkout-tmp.XXXXXX")"
  export TMPDIR="$shared_tmp"
fi

cd "$repo_root/relay-ai"
"$python" -m pytest -q tests/test_checkout_demo_e2e.py
