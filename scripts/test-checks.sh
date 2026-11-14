#!/usr/bin/env bash
# Self-test of the CI gates: each must fail on its negative control and pass on
# its positive one, so a gate that cannot fail is caught. Also asserts that
# every scripts/ entry point is run by .github/workflows/ci.yml.
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
echo edited >> "$T/sim/b1/records/r1.md"; g commit -q -am edit
expect 1 "append-only fails on an edited record" -- AO
g reset -q --hard HEAD~1
g rm -q sim/b1/records/r2.md; g commit -q -m delete
expect 1 "append-only fails on a deleted record" -- AO
g reset -q --hard HEAD~1
g mv sim/b1/records/r1.md sim/b1/records/r1-renamed.md; g commit -q -m rename
expect 1 "append-only fails on a renamed record" -- AO
expect 2 "append-only fails closed on an unknown base" -- "$S/check-sim-append-only" --root "$T" --base nosuchref

# empty tree: every gate passes trivially
E="$(mktemp -d)"; trap 'rm -rf "$T" "$E"' EXIT
git -C "$E" init -q
expect 0 "check-python passes with nothing to check" -- "$S/check-python.sh" --root "$E"
expect 0 "reuse-lock passes when absent"             -- "$S/check-reuse-lock.sh" "$E"
printf 'syntax error here(\n' > "$E/bad.py"; git -C "$E" add bad.py
expect 1 "check-python fails on a syntax error"      -- "$S/check-python.sh" --root "$E"
printf '[1,2]\n' > "$E/reuse.lock.json"
expect 1 "reuse-lock rejects a non-object"           -- "$S/check-reuse-lock.sh" "$E"

# workflow wiring: derive the entry-point set from the tracked tree instead of
# hardcoding names, so a gate added under scripts/ later cannot silently skip
# this check. Entry points are tracked scripts/ files excluding scripts/fixtures/
# that are executable.
mapfile -t entries < <(git -C "$ROOT" ls-files scripts/ | grep -v '^scripts/fixtures/')
if [ "${#entries[@]}" -eq 0 ]; then
  echo "FAIL no tracked scripts/ entry points found; wiring assertion would be vacuous"; fail=1
fi
for s in "${entries[@]}"; do
  [ -x "$ROOT/$s" ] || continue
  if [ "$s" = "scripts/check-all.sh" ]; then
    # check-all.sh is the local-only convenience wrapper that runs the other
    # gates (see its header); ci.yml documents it as the local counterpart,
    # not a CI job. Exempted as a named single case, never a second list.
    continue
  fi
  if grep -qF "$s" "$ROOT/.github/workflows/ci.yml"; then echo "ok   ci.yml runs $s"
  else echo "FAIL ci.yml does not run $s"; fail=1; fi
done
exit $fail
