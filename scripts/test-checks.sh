#!/usr/bin/env bash
# Self-test of the CI gates: each must fail on its negative control and pass on
# its positive one, so a gate that cannot fail is caught. Also asserts that
# every scripts/ entry point is run by .github/workflows/ci.yml and by
# scripts/check-all.sh (the local wrapper package.json delegates to), so the
# two wirings cannot drift apart.
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
E="$(mktemp -d)"; trap 'rm -rf "$T" "$E" "$N" "$V"' EXIT
git -C "$E" init -q
expect 0 "check-python passes with nothing to check" -- "$S/check-python.sh" --root "$E"
expect 0 "reuse-lock passes when absent"             -- "$S/check-reuse-lock.sh" "$E"
printf 'syntax error here(\n' > "$E/bad.py"; git -C "$E" add bad.py
expect 1 "check-python fails on a syntax error"      -- "$S/check-python.sh" --root "$E"
printf '[1,2]\n' > "$E/reuse.lock.json"
expect 1 "reuse-lock rejects a non-object"           -- "$S/check-reuse-lock.sh" "$E"

# wiring assertions: every tracked, executable scripts/ entry point must be
# invoked by each wiring target, or a gate added under scripts/ later could be
# wired into one copy and silently left out of the other. The entry-point set
# is always derived from the tracked tree (git ls-files), never hardcoded;
# taking the root as a parameter lets the negative controls below drive the
# same assertion against a fixture root.
# assert_invoked <root> <target-file> <match-prefix>
# The needle is <match-prefix><basename>. "scripts/" reproduces the tracked
# path as written in ci.yml; '$S/' reproduces the invocation form check-all.sh
# actually uses ("$S/<basename>") — the tracked path never appears there, so
# greping for it would report FAIL on every gate. The assertion is presence of
# the invocation, not unconditional execution: check-all.sh may run a gate
# conditionally (it runs check-sim-append-only only when BASE is set).
assert_invoked() {
  local root="$1" target="$2" prefix="$3" s rc=0
  local -a ents
  mapfile -t ents < <(git -C "$root" ls-files scripts/ | grep -v '^scripts/fixtures/')
  if [ "${#ents[@]}" -eq 0 ]; then
    echo "FAIL no tracked scripts/ entry points under $root; $(basename "$target") coverage assertion would be vacuous"
    rc=1
  fi
  for s in "${ents[@]}"; do
    [ -x "$root/$s" ] || continue
    if [ "$s" = "scripts/check-all.sh" ]; then
      # check-all.sh is the local-only convenience wrapper that runs the other
      # gates (see its header); ci.yml documents it as the local counterpart,
      # not a CI job, and it does not invoke itself. Exempted as a named single
      # case, never a second list. (Load-bearing for ci.yml: its header comment
      # names scripts/check-all.sh in prose, so a path grep alone would pass on
      # the comment.)
      continue
    fi
    if grep -qF "$prefix$(basename "$s")" "$target"; then echo "ok   $(basename "$target") runs $s"
    else echo "FAIL $(basename "$target") does not run $s"; rc=1; fi
  done
  return $rc
}
assert_invoked "$ROOT" "$ROOT/.github/workflows/ci.yml" "scripts/" || fail=1
assert_invoked "$ROOT" "$ROOT/scripts/check-all.sh" '$S/' || fail=1

# negative controls for the wiring assertions themselves — same standard as
# every gate above: a check that cannot fail is indistinguishable from no
# check. N: a tracked, executable gate absent from check-all.sh must fail the
# assertion and name the gate. V: an empty derived set must fail loudly, not
# pass vacuously.
N="$(mktemp -d)"
git -C "$N" init -q
mkdir -p "$N/scripts"
cp "$ROOT/scripts/check-all.sh" "$N/scripts/check-all.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$N/scripts/check-new-gate.sh"
chmod +x "$N/scripts/check-new-gate.sh" "$N/scripts/check-all.sh"
git -C "$N" add scripts/
expect 1 "coverage fails when a gate is missing from check-all.sh" \
  -- assert_invoked "$N" "$N/scripts/check-all.sh" '$S/'
if assert_invoked "$N" "$N/scripts/check-all.sh" '$S/' 2>&1 | grep -qF 'check-new-gate.sh'; then
  echo "ok   coverage failure names the missing gate"
else
  echo "FAIL coverage failure does not name the missing gate"; fail=1
fi
V="$(mktemp -d)"
git -C "$V" init -q
expect 1 "coverage fails loudly when the derived set is empty" \
  -- assert_invoked "$V" "$V/scripts/check-all.sh" '$S/'

exit $fail
