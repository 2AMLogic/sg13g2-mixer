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
E="$(mktemp -d)"
cleanup() {
  local d
  for d in "$T" "$E" "${N:-}" "${V:-}" "${C:-}" "${W:-}"; do
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

# wiring assertions: every tracked, executable scripts/ entry point must be
# invoked by each wiring target, or a gate added under scripts/ later could be
# wired into one copy and silently left out of the other. The entry-point set
# is always derived from the tracked tree (git ls-files), never hardcoded;
# taking the root as a parameter lets the negative controls below drive the
# same assertion against a fixture root.
# assert_invoked <root> <target-file> <path-form>
# <path-form> selects the needle: "tracked-path" is the full tracked path ($s),
# the form ci.yml invokes gates in; "basename" is "$S/<basename>", the form
# check-all.sh actually uses — the tracked path never appears there, so
# greping for it would report FAIL on every gate. ci.yml needs the full path:
# a basename needle collapses two gates sharing a name at different depths
# (scripts/x.sh vs scripts/sub/x.sh) onto one match — a false pass when only
# the top-level gate is wired, a false FAIL when only the nested one is. The
# assertion is presence of the invocation, not unconditional execution:
# check-all.sh may run a gate conditionally (it runs check-sim-append-only
# only when BASE is set).
assert_invoked() {
  local root="$1" target="$2" form="$3" s rc=0 needle
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
    case "$form" in
      tracked-path) needle="$s" ;;
      basename)     needle="\$S/$(basename "$s")" ;;
      *) echo "FAIL unknown path form '$form'"; rc=1; continue ;;
    esac
    if grep -qF "$needle" "$target"; then echo "ok   $(basename "$target") runs $s"
    else echo "FAIL $(basename "$target") does not run $s"; rc=1; fi
  done
  return $rc
}
assert_invoked "$ROOT" "$ROOT/.github/workflows/ci.yml" tracked-path || fail=1
assert_invoked "$ROOT" "$ROOT/scripts/check-all.sh" basename || fail=1

# negative controls for the wiring assertions themselves — same standard as
# every gate above: a check that cannot fail is indistinguishable from no
# check. N: a tracked, executable gate absent from check-all.sh must fail the
# assertion and name the gate. V: an empty derived set must fail loudly, not
# pass vacuously. C/W: the ci.yml needle must be the full tracked path —
# C: a nested gate sharing a basename with a wired top-level gate must fail
# and name the nested path (a basename needle matches the top-level wiring
# and passes falsely); W: a nested gate wired into ci.yml by its full tracked
# path must pass (a basename needle cannot match it — a false FAIL). W also
# carries a tracked, non-executable scripts/ file, which must be skipped.
N="$(mktemp -d)"
git -C "$N" init -q
mkdir -p "$N/scripts"
cp "$ROOT/scripts/check-all.sh" "$N/scripts/check-all.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$N/scripts/check-new-gate.sh"
chmod +x "$N/scripts/check-new-gate.sh" "$N/scripts/check-all.sh"
git -C "$N" add scripts/
expect 1 "coverage fails when a gate is missing from check-all.sh" \
  -- assert_invoked "$N" "$N/scripts/check-all.sh" basename
if assert_invoked "$N" "$N/scripts/check-all.sh" basename 2>&1 | grep -qF 'check-new-gate.sh'; then
  echo "ok   coverage failure names the missing gate"
else
  echo "FAIL coverage failure does not name the missing gate"; fail=1
fi
V="$(mktemp -d)"
git -C "$V" init -q
expect 1 "coverage fails loudly when the derived set is empty" \
  -- assert_invoked "$V" "$V/scripts/check-all.sh" basename

C="$(mktemp -d)"
git -C "$C" init -q
mkdir -p "$C/scripts/sub"
printf '#!/usr/bin/env bash\nexit 0\n' > "$C/scripts/check-python.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$C/scripts/sub/check-python.sh"
chmod +x "$C/scripts/check-python.sh" "$C/scripts/sub/check-python.sh"
printf 'run: scripts/check-python.sh\n' > "$C/ci.yml"
git -C "$C" add scripts/ ci.yml
expect 1 "coverage fails when a same-basename nested gate is unwired" \
  -- assert_invoked "$C" "$C/ci.yml" tracked-path
if assert_invoked "$C" "$C/ci.yml" tracked-path 2>&1 | grep -qF 'scripts/sub/check-python.sh'; then
  echo "ok   collision failure names the nested path"
else
  echo "FAIL collision failure does not name the nested path"; fail=1
fi
W="$(mktemp -d)"
git -C "$W" init -q
mkdir -p "$W/scripts/sub"
printf '#!/usr/bin/env bash\nexit 0\n' > "$W/scripts/sub/check-python.sh"
printf 'notes, not a gate\n' > "$W/scripts/sub/not-a-gate.txt"
chmod +x "$W/scripts/sub/check-python.sh"
printf 'run: scripts/sub/check-python.sh\n' > "$W/ci.yml"
git -C "$W" add scripts/ ci.yml
expect 0 "coverage passes when a nested gate is wired by its full tracked path" \
  -- assert_invoked "$W" "$W/ci.yml" tracked-path

exit $fail
