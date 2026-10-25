#!/usr/bin/env bash
# Smoke bench: integrity gate, then one single-corner ngspice -b run.
# Writes nothing into the repo (scratch dir under $TMPDIR, removed on exit).
#   PDK_ROOT  directory containing ihp-sg13g2/   (required)
#   NGSPICE   ngspice binary                      (default: ngspice)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
sim="$(dirname "$here")"
: "${PDK_ROOT:?set PDK_ROOT to the directory containing ihp-sg13g2/}"
NGSPICE="${NGSPICE:-ngspice}"

# Gate first: on any mismatch this exits non-zero and ngspice is never started.
python3 -I "$sim/tools/verify_pdk.py" --pdk-root "$PDK_ROOT" --ngspice "$NGSPICE"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
sed "s|@PDK_MODELS@|$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice/models|g" "$here/smoke.cir" > "$work/smoke.cir"
"$NGSPICE" -b -o "$work/smoke.log" "$work/smoke.cir"
grep -E 'v\(c\)|vcmin|vcmax' "$work/smoke.log" || true
if grep -qiE 'fatal|error' "$work/smoke.log"; then
  echo "smoke bench: ngspice reported errors" >&2; sed -n 1,40p "$work/smoke.log" >&2; exit 1
fi
echo "smoke-hbt OK (simulated, hbt_typ, 27 C, 1.80 V; no evidence written)"
