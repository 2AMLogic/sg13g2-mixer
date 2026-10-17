#!/usr/bin/env bash
# Byte-compile every tracked Python file and run the harness unit tests.
# Needs only python3 and git. With no Python files and no test_*.py yet it
# passes trivially (the harness lands with the first bench), but the job exists.
#
# Usage: scripts/check-python.sh [--root DIR]
# Exit: 0 clean (or nothing to check), 1 compile or test failure, 2 usage error.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ "${1:-}" = "--root" ]; then [ $# -eq 2 ] || { echo "usage: $0 [--root DIR]" >&2; exit 2; }; ROOT="$(cd "$2" && pwd)" || exit 2
elif [ $# -gt 0 ]; then echo "usage: $0 [--root DIR]" >&2; exit 2; fi
cd "$ROOT" || exit 2

mapfile -d '' PY < <(git ls-files -z -- '*.py')
if [ ${#PY[@]} -eq 0 ]; then
  echo "check-python: no tracked Python files; nothing to check."
  exit 0
fi

PYCACHE="$(mktemp -d)" || exit 2
trap 'rm -rf "$PYCACHE"' EXIT
export PYTHONPYCACHEPREFIX="$PYCACHE"
python3 -I -m py_compile "${PY[@]}" || { echo "check-python: byte-compile failed" >&2; exit 1; }
echo "check-python: byte-compiled ${#PY[@]} file(s)."

mapfile -d '' TESTS < <(git ls-files -z -- '*test_*.py')
rc=0
declare -A DIRS=()
for t in "${TESTS[@]}"; do DIRS["$(dirname "$t")"]=1; done
for d in "${!DIRS[@]}"; do
  echo "check-python: unittest discover in $d"
  python3 -m unittest discover -s "$d" -p 'test_*.py' || rc=1
done
[ ${#TESTS[@]} -eq 0 ] && echo "check-python: no test_*.py yet; no unit tests to run."
[ $rc -eq 0 ] || echo "check-python: unit tests failed" >&2
exit $rc
