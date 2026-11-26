#!/usr/bin/env bash
# Cold start for the ka5-window-coherence bench (V3 check 5). Runs two
# sequential ngspice -b legs (12.5 ps, 6.25 ps), gates the result, and
# writes records/<UTC-timestamp>-v3.json (append-only). This bench needs numpy for
# the Hann-window PSD leg (stamped mechanic M3); the venv is created
# worktree-locally by sim/bench/mkenv.sh, never a host-wide install.
#   NGSPICE   ngspice 46 binary (default: ngspice on PATH; the pinned
#             major is checked before anything runs -- sim/toolchain.json)
# Scratch lands in .tools/ka5-work/ (gitignored). See README.md.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
"$root/sim/bench/mkenv.sh"
"$root/.tools/bench-venv/bin/python" "$here/bench.py" "$@"
