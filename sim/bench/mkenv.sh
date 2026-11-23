#!/usr/bin/env bash
# Create/refresh the bench venv (.tools/bench-venv, gitignored) with the
# pinned third-party Python deps (sim/bench/requirements.txt). Idempotent.
# No host-wide install (record 0002, M3 numpy consequence; host rules).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
venv="$root/.tools/bench-venv"
if [ ! -x "$venv/bin/python" ]; then
  mkdir -p "$root/.tools"
  python3 -m venv "$venv"
fi
"$venv/bin/pip" --quiet install -r "$here/requirements.txt"
echo "bench venv ready: $venv"
