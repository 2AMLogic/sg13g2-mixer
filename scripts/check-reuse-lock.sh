#!/usr/bin/env bash
# Validate reuse.lock.json when present (stamped copies of shared bench code).
# No org reuse checker is installed in CI yet, so this applies only the
# structural JSON contract of check-tb-json.py (UTF-8 JSON, non-empty object,
# no repeated keys). Absent file: passes trivially; the job still exists.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HERE/..}"
if [ ! -f "$ROOT/reuse.lock.json" ]; then
  echo "check-reuse-lock: no reuse.lock.json yet; nothing to check."
  exit 0
fi
exec python3 -I "$HERE/check-tb-json.py" "$ROOT/reuse.lock.json"
