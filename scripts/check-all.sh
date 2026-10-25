#!/usr/bin/env bash
# Run every CI check that needs neither a PDK nor a simulator, locally, with the
# same commands as .github/workflows/ci.yml. The append-only gate needs a base
# ref: set BASE (e.g. BASE=origin/main) to include it, otherwise it is skipped
# with a message (CI runs it on pull requests).
set -u
S="$(cd "$(dirname "$0")" && pwd)"
rc=0
run() { echo "== $*"; "$@" || rc=1; }
run "$S/test-checks.sh"
run "$S/check-python.sh"
run python3 -I "$S/check-tb-json.py"
run "$S/check-reuse-lock.sh"
if [ -n "${BASE:-}" ]; then run "$S/check-sim-append-only" --base "$BASE"
else echo "== check-sim-append-only skipped (set BASE=<ref> to run it)"; fi
exit $rc
