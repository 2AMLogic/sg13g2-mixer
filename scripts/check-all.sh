#!/usr/bin/env bash
# The single command list for every CI check that needs neither a PDK nor a
# simulator: .github/workflows/ci.yml jobs call this script with their group
# name, package.json runs it locally, and the commands are written here once.
# With no argument every group runs in CI job order. The append-only gate
# needs a base ref: set BASE (e.g. BASE=origin/main) to include it, otherwise
# it is skipped with a message (CI runs it on pull requests).
set -u
S="$(cd "$(dirname "$0")" && pwd)"
rc=0
run() { echo "== $*"; "$@" || rc=1; }

group_gate_self_test()      { run "$S/test-checks.sh"; }
group_python()              { run "$S/check-python.sh"; }
group_tb_json()             { run python3 -I "$S/check-tb-json.py"; }
group_reuse_lock()          { run "$S/check-reuse-lock.sh"; }
group_records_append_only() {
  if [ -n "${BASE:-}" ]; then run "$S/check-sim-append-only" --base "$BASE"
  else echo "== check-sim-append-only skipped (set BASE=<ref> to run it)"; fi
}

case "${1:-}" in
  "")                   group_gate_self_test
                        group_python
                        group_tb_json
                        group_reuse_lock
                        group_records_append_only ;;
  gate-self-test)       group_gate_self_test ;;
  python)               group_python ;;
  tb-json)              group_tb_json ;;
  reuse-lock)           group_reuse_lock ;;
  records-append-only)  group_records_append_only ;;
  *)
    echo "check-all.sh: unknown group '$1'" >&2
    echo "usage: check-all.sh [gate-self-test|python|tb-json|reuse-lock|records-append-only]" >&2
    exit 2 ;;
esac
exit $rc
