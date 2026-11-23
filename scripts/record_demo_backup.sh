#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Record a local macOS demo backup into demo-recordings/. No audio is captured."
  exit 0
fi
if [[ $# -ne 0 ]]; then
  echo "Usage: $0 [--help]" >&2
  exit 2
fi

if [[ "$(uname -s)" != "Darwin" ]] || ! command -v screencapture >/dev/null 2>&1; then
  echo "This recorder requires macOS screencapture. Record manually and save the file under demo-recordings/." >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
recording_dir="$repo_root/demo-recordings"
mkdir -p "$recording_dir"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$recording_dir/relay-ai-checkout-$timestamp.mov"

echo "Recording the screen to $output. Stop the capture to finalize the movie."
screencapture -v -k "$output"
if [[ ! -s "$output" ]]; then
  echo "The screen recording did not produce a non-empty movie." >&2
  exit 1
fi
echo "Saved demo backup recording: $output"
