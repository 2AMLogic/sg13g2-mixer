#!/usr/bin/env bash
# Self-test of the CI gates: each must fail on its negative control and pass on
# its positive one, so a gate that cannot fail is caught. Also tests the group
# dispatch of scripts/check-all.sh — the single command list the ci.yml jobs
# and package.json both call — by observing which gates each group invokes.
# Needs bash, git, python3.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
S="$ROOT/scripts"
fail=0
expect() { # expect <want-rc> <label> -- cmd...
  local want="$1" label="$2"; shift 3
  "$@" >/dev/null 2>&1; local rc=$?
  if [ "$rc" -eq "$want" ]; then echo "ok   $label (rc=$rc)"; else echo "FAIL $label: rc=$rc, want $want"; fail=1; fi
}

# tb.json validation
expect 0 "tb-json accepts a good file"        -- python3 -I "$S/check-tb-json.py" "$S/fixtures/tb-good.json"
expect 1 "tb-json rejects truncated JSON"     -- python3 -I "$S/check-tb-json.py" "$S/fixtures/tb-bad-truncated.json"
expect 1 "tb-json rejects a duplicate key"    -- python3 -I "$S/check-tb-json.py" "$S/fixtures/tb-bad-duplicate-key.json"

# append-only, against a throwaway git repo
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
g() { git -C "$T" -c user.email=t@example.com -c user.name=t -c commit.gpgsign=false "$@"; }
g init -q -b main
mkdir -p "$T/sim/b1/records"
echo one > "$T/sim/b1/records/r1.md"; echo two > "$T/sim/b1/records/r2.md"
g add -A; g commit -q -m base
g checkout -q -b work
AO() { "$S/check-sim-append-only" --root "$T" --base main; }
expect 0 "append-only passes with no change"  -- AO
echo three > "$T/sim/b1/records/r3.md"; g add -A; g commit -q -m add
expect 0 "append-only passes on an added record" -- AO
# Merge-group shape: the merge queue checks the trial-merge commit against a
# base given as a raw sha (merge_group.base_sha), not an origin/ ref. The
# gate takes any ref git can resolve, so a sha must behave like a ref name.
expect 0 "append-only passes with the base as a sha (merge-group shape)" \
  -- "$S/check-sim-append-only" --root "$T" --base "$(g rev-parse main)"
echo edited >> "$T/sim/b1/records/r1.md"; g commit -q -am edit
expect 1 "append-only fails on an edited record vs a sha base" \
  -- "$S/check-sim-append-only" --root "$T" --base "$(g rev-parse main)"
g reset -q --hard HEAD~1
g rm -q sim/b1/records/r2.md; g commit -q -m delete
expect 1 "append-only fails on a deleted record" -- AO
g reset -q --hard HEAD~1
g mv sim/b1/records/r1.md sim/b1/records/r1-renamed.md; g commit -q -m rename
expect 1 "append-only fails on a renamed record" -- AO
expect 2 "append-only fails closed on an unknown base" -- "$S/check-sim-append-only" --root "$T" --base nosuchref
expect 2 "append-only fails closed on an empty base" -- "$S/check-sim-append-only" --root "$T" --base ""

# empty tree: every gate passes trivially
E="$(mktemp -d)"
cleanup() {
  local d
  for d in "$T" "$E" "${G:-}"; do
    [ -n "$d" ] && rm -rf "$d"
  done
}
trap cleanup EXIT
git -C "$E" init -q
expect 0 "check-python passes with nothing to check" -- "$S/check-python.sh" --root "$E"
expect 0 "reuse-lock passes when absent"             -- "$S/check-reuse-lock.sh" "$E"
printf 'syntax error here(\n' > "$E/bad.py"; git -C "$E" add bad.py
expect 1 "check-python fails on a syntax error"      -- "$S/check-python.sh" --root "$E"
printf '[1,2]\n' > "$E/reuse.lock.json"
expect 1 "reuse-lock rejects a non-object"           -- "$S/check-reuse-lock.sh" "$E"

# check-all.sh group dispatch — the script's own behaviour, not a copy of any
# wiring: each group must invoke exactly its own gate and nothing else, the
# append-only group must respect BASE, and an unknown group must fail. The
# script is copied into a fixture tree of stub gates that append their name to
# $CALL_LOG, so what actually ran is observed, not assumed.
G="$(mktemp -d)"
mkdir -p "$G/scripts"
cp "$S/check-all.sh" "$G/scripts/check-all.sh"
CALL_LOG="$G/called.log"; export CALL_LOG
for gate in test-checks.sh check-python.sh check-reuse-lock.sh check-sim-append-only; do
  printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$(basename "$0")" >> "$CALL_LOG"\nexit 0\n' > "$G/scripts/$gate"
  chmod +x "$G/scripts/$gate"
done
# check-all.sh invokes this one through python3 -I, so the stub must be Python
cat > "$G/scripts/check-tb-json.py" <<'EOF'
import os
with open(os.environ["CALL_LOG"], "a") as f:
    f.write("check-tb-json.py\n")
EOF
chmod +x "$G/scripts/check-tb-json.py"
expect_group() { # expect_group <group> <expected gate basenames...>
  local group="$1"; shift; : > "$CALL_LOG"
  "$G/scripts/check-all.sh" "$group" >/dev/null 2>&1 || { echo "FAIL group $group exits nonzero"; fail=1; return; }
  if [ "$(sort "$CALL_LOG" | tr '\n' ' ' | sed 's/ $//')" = "$(printf '%s\n' "$@" | sort | tr '\n' ' ' | sed 's/ $//')" ]; then
    echo "ok   group $group runs only: $*"
  else
    echo "FAIL group $group ran: $(tr '\n' ' ' < "$CALL_LOG")— want: $*"; fail=1
  fi
}
expect_group python              "check-python.sh"
expect_group tb-json             "check-tb-json.py"
expect_group reuse-lock          "check-reuse-lock.sh"
expect_group gate-self-test      "test-checks.sh"
BASE="$G"; export BASE
expect_group records-append-only "check-sim-append-only"
: > "$CALL_LOG"
"$G/scripts/check-all.sh" >/dev/null 2>&1 && \
  [ "$(tr '\n' ' ' < "$CALL_LOG" | sed 's/ $//')" = \
    "$(printf '%s ' test-checks.sh check-python.sh check-tb-json.py check-reuse-lock.sh check-sim-append-only | sed 's/ $//')" ] && \
  echo "ok   no argument runs every gate in check-all.sh's order" || { echo "FAIL no-argument run: rc or gate order wrong: $(tr '\n' ' ' < "$CALL_LOG")"; fail=1; }
BASE=""
: > "$CALL_LOG"
"$G/scripts/check-all.sh" records-append-only >/dev/null 2>&1 && [ ! -s "$CALL_LOG" ] && \
  echo "ok   records-append-only without BASE skips and passes" || \
  { echo "FAIL records-append-only without BASE: $(tr '\n' ' ' < "$CALL_LOG")"; fail=1; }
# CI's fail-closed mode: RECORDS_BASE_REQUIRED=1 turns the no-BASE skip into
# a failure (a merge-queue run with no base must not pass as skipped), and
# must not run the gate either.
: > "$CALL_LOG"
RECORDS_BASE_REQUIRED=1 "$G/scripts/check-all.sh" records-append-only >/dev/null 2>&1
rc=$?
[ "$rc" -ne 0 ] && [ ! -s "$CALL_LOG" ] && \
  echo "ok   records-append-only with RECORDS_BASE_REQUIRED=1 and no BASE fails closed, gate not run" || \
  { echo "FAIL fail-closed no-BASE: rc=$rc, log: $(tr '\n' ' ' < "$CALL_LOG")"; fail=1; }
expect 2 "check-all.sh rejects an unknown group" -- "$G/scripts/check-all.sh" nonsense

# A failing gate must propagate: after the gate list moved here, every ci.yml
# job reaches its gate through check-all.sh, so run()'s `|| rc=1` and the
# final `exit $rc` are load-bearing. Every stub gate is made to exit 1, and
# each group — which the dispatch tests above prove invokes only its own gate
# — and the no-argument run must then exit nonzero.
BASE="$G"; export BASE
for gate in test-checks.sh check-python.sh check-reuse-lock.sh check-sim-append-only; do
  printf '#!/usr/bin/env bash\nexit 1\n' > "$G/scripts/$gate"
done
printf 'import sys\nsys.exit(1)\n' > "$G/scripts/check-tb-json.py"
for group in python tb-json reuse-lock gate-self-test records-append-only; do
  expect 1 "failing gate makes group $group exit nonzero" -- "$G/scripts/check-all.sh" "$group"
done
expect 1 "failing gates make the no-argument run exit nonzero" -- "$G/scripts/check-all.sh"

exit $fail
