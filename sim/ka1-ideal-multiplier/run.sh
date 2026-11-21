#!/usr/bin/env bash
# Cold start for the ka1-ideal-multiplier bench (V3 check 1). Runs two
# sequential ngspice -b legs (12.5 ps, 6.25 ps), gates the result, and
# writes records/<UTC-timestamp>-v3.json (append-only). Standard library only --
# no numpy needed for this bench.
#   NGSPICE   ngspice 46 binary (default: ngspice on PATH; the pinned
#             major is checked before anything runs -- sim/toolchain.json)
# Scratch (decks, samples, logs) lands in .tools/ka1-work/ (gitignored).
# See README.md for the from-scratch clone recipe.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
python3 "$here/bench.py" "$@"
