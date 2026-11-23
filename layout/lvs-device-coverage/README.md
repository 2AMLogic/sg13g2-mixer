# lvs-device-coverage

Which SG13G2 devices `klt` can extract and LVS-match **today**, measured before a mixer
topology is chosen (issue #31; the risk is recorded as item 4 of the T1 tracker #5) and
**re-measured 2026-11-20 at current `klt`** after the four upstream fixes landed (issue
#98; see the [2026-11-20 table](#coverage-table-2026-11-20-current-klt) below).

Every row below is a committed run, not an assertion. The probe cells are the IHP PDK's
own golden LVS testcases, copied unmodified — see each `<device>/PROVENANCE.md` for the
upstream path, the PDK commit and the Apache-2.0 attribution.

**Headline (2026-11-20)**: **`npn13G2` reaches `status: match`** — on the PDK-runset
engine (`klt lvs --engine klayout-runset` with the runset's own
`ignore_top_ports_mismatch` switch), and it now also reaches an extracted netlist
(`klt extract --engine klayout-runset`: 3 devices). **All five cells match on that
engine**, exit 0, no error categories. The curated `sg13g2` deck still models **no
bipolar device class** (`npn13G2` still extracts as zero devices there — the closed
decision #1232 stands), and its own LVS rows still mismatch, now for one reason only
(the `subckt-call` reference pairing defect, upstream #6960). One caveat carried into
topology work: `klt signoff` **refuses an item-4 citation from these runset reports
today** (`runset_unrecognised_device`, upstream #6902) — see
[Signoff finding](#signoff-finding-item-4-and-the-runset-reports).

> **Nothing here is a design claim.** These are vendor test cells, not mixer geometry. The
> directory answers "what does the toolchain recognise", nothing else.

## Environment identity

**Read these back before trusting any row below.** Every number in this file was measured
against exactly the environment its dated table names; a different `content_hash` means
the table is stale and the rows must be re-run, not trusted.

### 2026-11-20 (current `klt`; the `*.2026-11-20.*` reports)

| item | value | how to re-read it |
|---|---|---|
| `klt` version | `0.9.3.dev2575+g6bd18bbc8637` | `klt --version` |
| `klt` git commit | `6bd18bbc8637f6d767b3c24e77bd5db7a39e4bbe` | `provenance.klt_git_commit` in any report here |
| the four fixes are in | verified: `f8b75151` (#5481), `18f78c41` (#5664), `85c7af02` (#5665), `1d6b1ad0` (#5666) each pass `git merge-base --is-ancestor <merge> 6bd18bbc8637` | klayout-tools checkout |
| KLayout — **one version for both engines** | `0.30.12` | `provenance.klayout_version` and `environment.engine_version` in any report here; `klayout_version_mismatch: false` on the curated-deck reports |
| `sg13g2` deck `content_hash` | `sha256:eaaf298957eeced674e4030635c66ba6bdee98adde15fe36203ba047fd7b0669` | `klt deck info --deck sg13g2` |
| PDK runset `content_hash` | `sha256:e01bcb1ec5858e8069bade8f7fd7ec28c1026fc2fd0590e8f611d3398a5bbbd7` | `provenance.runset.content_hash` in any `*.lvs-pdk-runset.2026-11-20.json` — **unchanged from 2026-11-14** |
| PDK | IHP-Open-PDK `v0.3.0` @ `5cccb161f7492697cfa52eb14dc03beb00bdca9e` | `sim/pdk-artifact.json` → `upstream.commit` |

The curated deck's `content_hash` changed since 2026-11-14 (`cf6dfead…` → `eaaf2989…`):
the deck itself gained device classes in that window. The five probe cells' curated
extract counts are unchanged (0/36/16/72/82) — none of the new classes appears in them.
The curated-deck runs now use `klt`'s bundled module at `0.30.12`, the same version as
the system binary the runset engine shells out to, so the 2026-11-14 version confounder
(two KLayouts, § *Open observation* below) is **eliminated** for the 2026-11-20 rows.

### 2026-11-14 (baseline; the undated reports)

Measured on 2026-11-14 against exactly this environment:

| item | value | how to re-read it |
|---|---|---|
| `klt` version | `0.9.2.dev1022+g2a9c52b27ce7` | `klt --version` |
| `klt` git commit | `2a9c52b27ce7986b4372ae5d73129dac4773e02c` | `provenance.klt_git_commit` in any report here |
| KLayout — `klt`'s bundled module (produced the `extract` + curated-deck rows) | `0.30.13` | `provenance.klayout_version` in any report here |
| KLayout — system binary (produced the `LVS (PDK runset)` rows **and** the `run_lvs.py` cross-check) | `0.30.12` | `klayout -v`; `environment.klayout_binary` and `provenance.runset.klayout_application_version` in any `*.lvs-pdk-runset.json` |
| `sg13g2` deck `content_hash` | `sha256:cf6dfeadf75bd95bf89beb0a64e06ed43b65f6ff782df10ae200ea200a73d8e9` | `klt deck info --deck sg13g2` |
| PDK | IHP-Open-PDK `v0.3.0` @ `5cccb161f7492697cfa52eb14dc03beb00bdca9e` | `sim/pdk-artifact.json` → `upstream.commit` |

`klt` warns that it resolved KLayout `0.30.13` while this `klt` build was tested against
`0.30.12`, and that report **counts** may differ across that gap even where the verdict
does not (`klt` records this as `provenance.klayout_version_mismatch: true` on the
curated-deck reports). **Both KLayout versions on this host produced rows below**, and the
split is by engine, not by cell:

- **`klt extract` and `LVS (klt curated deck)` rows** ran inside `klt` on its own bundled
  Python `klayout` module, `0.30.13`. The curated-deck reports say so in
  `environment.engine: klayout` / `environment.engine_version: 0.30.13` with no
  `environment.klayout_binary`; the `extract` reports carry no `environment` block at all,
  so their evidence is `provenance.klayout_version: 0.30.13` and the absence of any
  `provenance.runset` block.
- **`LVS (PDK runset)` rows did not.** `engine: klayout-runset` shells out to the system
  KLayout application, so all five of those rows were produced by `/usr/bin/klayout`
  `0.30.12` — `environment.klayout_binary: /usr/bin/klayout`,
  `environment.engine_version: 0.30.12`, and
  `provenance.runset.klayout_application_version: 0.30.12` in every
  `*.lvs-pdk-runset.json`.
- **The `run_lvs.py` cross-check** (§ *…but `klt lvs` still scores those as errors*) ran on
  that **same** system binary at `0.30.12`: the PDK's script invokes `klayout -b -r <deck>`
  from `PATH` (`run_lvs.py:572`, and its own `check_klayout_version()` reads `klayout -b
  -v`), which on this host resolves to `/usr/bin/klayout`. The cross-check therefore
  compares `klt lvs` against the identical engine, deck and switch it wrapped — the version
  gap is **not** a candidate explanation for that disagreement, which is what makes
  `klayout-tools#5664` a wrapper-scoring defect rather than a version artefact.

## Deck device coverage

`klt deck devices --deck sg13g2` answers "is this class modelled?" with no layout at all.
As of 2026-11-14 at the baseline deck hash it reports **13 device classes**, and the
2026-11-20 re-read at `eaaf2989…` reports **the same 13 classes with the same per-kind
lists** — including **no bipolar entry**:

| kind | classes |
|---|---|
| mos | `nfet`, `pfet` |
| capacitor | `cap_cmim`, `rfcmim` |
| mom_capacitor | `cap_cmomi`, `cap_cmomf` |
| resistor | `rsil`, `rppd`, `rhigh`, `res_metal1`, `res_metal2` |
| diode | `dantenna`, `dpantenna` |
| **bipolar** | **none** |

`klt deck info --deck sg13g2` prints only 9 names for the same deck because it collapses
the resistor subtypes — the per-class list above is the one to cite.

## Coverage table

One row per probed device. "deck class" is what `klt deck devices` calls it; "recognised"
and "extracted devices" come from the committed `klt extract` report; "LVS (curated deck)"
and "LVS (PDK runset)" come from the two committed `klt lvs` reports. All paths and
commands are relative to this directory. The two tables are two measurements of the same
five rows at two dated `klt` builds; neither replaces the other.

### Coverage table (2026-11-20, current `klt`)

The `*.2026-11-20.*` reports. Every PDK-runset LVS row exits 0 and reads
`status: match` with **no error categories** — the baseline's sole remaining category
(`pin.unmatched`, the #5664 defect) is gone.

| device | deck class | extracted (curated deck) | extracted (runset engine) | LVS (curated deck) | LVS (PDK runset) | notes |
|---|---|---|---|---|---|---|
| `npn13G2` (SiGe HBT) | **not modelled** (#1232, closed declined) | **0** — unchanged | **3** (`npn13G2`: 3) — the new #5481 route | `mismatch` — 0/3 devices, 0/10 nets | **`match`** — 3/3 devices, 10/10 nets, exit 0 | the headline answer: the HBT matches on the runset engine |
| `sg13_lv_nmos` | `nfet` (mos) | 36 (`nfet: 36`) | 28 (census) | `mismatch` — 0/28 devices matched | **`match`** — 28/28 devices, 87/87 nets, exit 0 | curated row = `subckt-call` pairing (#6960) |
| `sg13_lv_pmos` | `pfet` (mos) | 16 (`pfet: 16`) | 15 (census) | `mismatch` — 0/15 devices matched | **`match`** — 15/15 devices, 47/47 nets, exit 0 | as above |
| `cap_cmim` (MIM cap) | `cap_cmim` (capacitor) | 72 (`cap_cmim: 72`) | 69 (census) | `mismatch` — 71/72 devices, 136/138 nets | **`match`** — 69/69 devices, 138/138 nets, exit 0 | 71/72 unchanged from baseline (#6960) |
| `rppd` (poly resistor) | `rppd` (resistor) | 82 (`rppd: 82`) | 84 (census) | `mismatch` — **1/84** devices, 3/170 nets — **the row now runs** (baseline: pre-report `error`) | **`match`** — 84/84 devices, 171/171 nets, exit 0 | #5665 fixed; the near-total pairing failure is #6960 |

`--format text` on the PDK-runset route no longer crashes (#5666): all five rows exit 0
and print `status: match`. The dated text outputs are committed beside the JSON reports.

### Coverage table (2026-11-14, baseline — dated history)

The undated reports (`*.extract.json`, `*.lvs-klt-deck.json`, `*.lvs-pdk-runset.json`,
`rppd.lvs-klt-deck.error.json`). Kept byte-identical as the baseline the 2026-11-20
comparison is made against.

| device | deck class | recognised | extracted devices | LVS (curated deck) | LVS (PDK runset) | notes |
|---|---|---|---|---|---|---|
| `npn13G2` (SiGe HBT) | **not modelled** | **no** | **0** | `mismatch` — 0/3 devices, 0/10 nets matched | `mismatch` — **3/3 devices, 10/10 nets matched**, sole category `pin.unmatched: 10` | the headline gap; `2AMLogic/klayout-tools#1232`, closed investigated-and-declined — see [npn13G2](#npn13g2-the-hbt-gap-1232) |
| `sg13_lv_nmos` | `nfet` (mos) | yes | 36 (`nfet: 36`) | `mismatch` — 0/28 devices matched | `mismatch` — **28/28 devices, 87/87 nets matched**, sole category `pin.unmatched: 87` | curated-deck count is a geometry census, not schematic-equivalent — see [count delta](#open-observation-curated-deck-device-count-vs-runset-device-count) |
| `sg13_lv_pmos` | `pfet` (mos) | yes | 16 (`pfet: 16`) | `mismatch` — 0/15 devices matched | `mismatch` — **15/15 devices, 47/47 nets matched**, sole category `pin.unmatched: 47` | as above |
| `cap_cmim` (MIM cap) | `cap_cmim` (capacitor) | yes | 72 (`cap_cmim: 72`) | `mismatch` — **71/72 devices, 136/138 nets matched** | `mismatch` — **69/69 devices, 138/138 nets matched**, sole category `pin.unmatched: 138` | the only class that nearly matches on the curated deck; needs `reference.form: "subckt-call"` |
| `rppd` (poly resistor) | `rppd` (resistor) | yes | 82 (`rppd: 82`) | **cannot run** — reference netlist unreadable (`error`, exit 1) | `mismatch` — **84/84 devices, 171/171 nets matched**, sole category `pin.unmatched: 171` | curated-deck reference path is broken for every `sg13g2` resistor class: `2AMLogic/klayout-tools#5665` |

Scope note: `cap_cmomi`/`cap_cmomf`, `res_metal*`, `dantenna`/`dpantenna`, HV MOS,
inductors, varactors and ESD devices were deliberately **not** probed — a mixer core and
bias would not plausibly use them, so they are out of scope for this issue.

### Reproducing a row

Every command below runs from this directory and needs only the files committed here (the
PDK install is **not** needed for the curated-deck rows). Substitute `<device>` with the
directory name.

```bash
# 1. Deck coverage — the "deck class" and "recognised" columns, no layout needed
klt deck devices --deck sg13g2
klt deck info --deck sg13g2          # content_hash; must match the table above

# 2. Extraction — the "extracted (curated deck)" columns. The 2026-11-20 re-run writes
#    a dated netlist beside the baseline one; counts are identical to the baseline.
klt extract <device>/<device>.gds --deck sg13g2 --format json \
    -o <device>/<device>.extracted.2026-11-20.spice
#   npn13G2      -> device_count 0,  device_counts {}
#   sg13_lv_nmos -> device_count 36, device_counts {"nfet": 36}
#   sg13_lv_pmos -> device_count 16, device_counts {"pfet": 16}
#   cap_cmim     -> device_count 72, device_counts {"cap_cmim": 72}
#   rppd         -> device_count 82, device_counts {"rppd": 82}

# 2b. Extraction on the PDK runset engine (the #5481 route) — HBT reaches a netlist here.
#     Measured for npn13G2 on 2026-11-20: device_count 3, device_counts {"npn13G2": 3}.
PDKLVS="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/lvs"
klt extract npn13G2/npn13G2.gds --engine klayout-runset \
    --deck-file "$PDKLVS/sg13g2.lvs" --format json \
    -o npn13G2/npn13G2.extracted.runset.2026-11-20.spice

# 3. LVS, curated sg13g2 deck — the "LVS (curated deck)" column. At the 2026-11-20 klt
#    the rppd row runs (#5665 fixed); the near-total pairing failure that remains is #6960.
klt lvs '{"layout":{"file":"<device>/<device>.gds","deck":"sg13g2"},
          "reference":{"netlist":"<device>/<device>.cdl"}}' --format json
#   cap_cmim and rppd additionally need the capacitor/resistor rewrite:
#     "reference":{"netlist":"…","form":"subckt-call","deck":"sg13g2"}
#   (2026-11-14 baseline only: rppd then failed with error
#    "reference netlist has no top circuit" — #5665, since fixed)

# 4. LVS, PDK's own runset — the "LVS (PDK runset)" column. Needs the PDK install.
#    At the 2026-11-20 klt every row exits 0 with status: match (#5664 fixed) and
#    --format text works too (#5666 fixed); the 2026-11-14 baseline needed json only.
klt lvs '{"layout":{"file":"<device>/<device>.gds"},
          "reference":{"netlist":"<device>/<device>.cdl"},
          "engine":"klayout-runset"}' \
    --deck-file "$PDKLVS/sg13g2.lvs" \
    --deck-var ignore_top_ports_mismatch=true --format json
```

### Re-verifying the committed reports without re-running the engines

Each committed report carries the hashes of its own inputs, so drift is detectable
cheaply. All 14 baseline reports re-check clean as of 2026-11-14, and all 16 dated
2026-11-20 reports re-check clean as of 2026-11-20 (five curated extracts, one runset
extract, five curated-deck LVS — the `rppd` one included, it emits a report now — and
five runset LVS):

```bash
# baseline (2026-11-14, undated files)
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt extract --check "$d/$d.extract.json"            # exit 0 = still consistent, 3 = drifted
done
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim; do
  klt lvs --check "$d/$d.lvs-klt-deck.json"
done
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt lvs --check "$d/$d.lvs-pdk-runset.json"
done

# dated (2026-11-20, current klt) — every emitted report, mismatches included
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt extract --check "$d/$d.extract.2026-11-20.json"
done
klt extract --check npn13G2/npn13G2.extract.runset.2026-11-20.json
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt lvs --check "$d/$d.lvs-klt-deck.2026-11-20.json"
  klt lvs --check "$d/$d.lvs-pdk-runset.2026-11-20.json"
done
```

**Which loops pass where (measured 2026-11-20).** The dated loop above exits clean for
all 16 reports at the 2026-11-20 `klt`. On the *baseline* files the picture splits by
engine: the five baseline runset reports re-check clean (the PDK runset file is
unchanged since v0.3.0), but the nine baseline curated-deck reports (five `extract`,
four `lvs-klt-deck`) now read `status: drifted` with the **sole** drifted field
`provenance.deck.content_hash` — expected `sha256:cf6dfead…` (the 2026-11-14 deck),
actual `sha256:eaaf2989…` (the deck at the 2026-11-20 `klt`). The curated deck itself
evolved between the two builds; every layout/reference input hash still re-checks OK.
That drift is exactly why the 2026-11-20 rows are dated siblings rather than in-place
updates: the baseline rows remain reproducible against their own deck revision, and the
drift message names the revision to install to replay them.

Two caveats on the committed reports' path fields, both upstream-known:

- The `lvs-pdk-runset` reports record `deck_file` as a **host-absolute path** into the PDK
  install, so `--check` on them only re-verifies the layout/reference hashes on a host
  whose PDK sits at the same path; a `--rerun` elsewhere needs `--deck-file` pointed at
  the local install.
- Every `extract.json` records `netlist_path` as a **host-absolute path naming the
  worktree it was produced in** (`.loom/worktrees/issue-31/…`), which will not exist after
  this lands. **Ignore that field**: the input path (`file`) *is* a portable
  `{path, scope: "repo"}` envelope, and the netlist it names is committed right beside the
  report as `<device>.extracted.spice`, whose sha256 equals the report's
  `netlist_sha256` — verified for all five on 2026-11-14:

  ```bash
  python3 -c 'import json,hashlib,sys
  d=sys.argv[1]; r=json.load(open(f"{d}/{d}.extract.json"))
  a=hashlib.sha256(open(f"{d}/{d}.extracted.spice","rb").read()).hexdigest()
  print(d, "ok" if a==r["netlist_sha256"] else "DRIFTED")' <device>
  ```

  This is a ratified upstream decision, not a new gap: `klayout-tools#2700` asked for
  `netlist_path` to move to the `{path, scope}` envelope and was closed `not_planned`,
  because the envelope has no way to say which root an *output* path is relative to.
  Nothing was filed for it here.

## `npn13G2`: the HBT gap (#1232)

`klt extract npn13G2/npn13G2.gds --deck sg13g2` reports `status: extracted` and
`device_count: 0`. The deck models no bipolar class, so the HBT's geometry is read as
ordinary wiring — and the run says so explicitly rather than silently:

> 7 candidate `dantenna` regions match every other drawn-layer predicate of that device
> class but are missing its device-recognition marker `Recog.diode (99/31)` … Note: this
> geometry also matches SiGe HBT (`npn13G2`/`npn13G2l`/`npn13G2v`), a device family this
> deck does not model, so it is probably not a diode at all — see the `sg13g2.py`
> docstring section "SiGe HBTs — investigated, declined (issue #1232)".

**This gap is already filed upstream and deliberately closed:
[`2AMLogic/klayout-tools#1232`](https://github.com/2AMLogic/klayout-tools/issues/1232)**,
*"SG13G2 extraction deck: no SiGe HBT (bipolar) device recognition"*, state `closed`
(`state_reason: completed`), re-read 2026-11-14. **No new issue is filed here for it.**

The declined rationale, from the deck source's own docstring: `klt`'s `BipolarDevice` model
is a *static* per-terminal set of drawn layers, while SG13G2's own `CustomBJTExtractor`
needs *size-filtered* (`with_bbox_min`/`with_bbox_max`) and dynamic per-instance geometric
relationships that the static model cannot express. The documented consequence is that a
SiGe HBT "continues to extract as ordinary unconnected geometry (a `klt lvs`
`device.unmatched`/short, never a wrong device)" — which is exactly what the committed
`npn13G2.lvs-klt-deck.json` shows (`device.unmatched: 3`, `net.unmatched: 11`,
`topology: 1`).

**The HBT is not unreachable, though — and at current `klt` it is fully reached.** The
PDK's own runset recognises it: via `engine: klayout-runset`, `npn13G2` matched
**3/3 devices and 10/10 nets** at the 2026-11-14 baseline
(`npn13G2.lvs-pdk-runset.json`) and at the 2026-11-20 re-run the same request reads
**`status: match`, exit 0** (`npn13G2.lvs-pdk-runset.2026-11-20.json`) — the #5664 fix
models the `ignore_top_ports_mismatch` deck-var the request carries. And since #5481
closed, `klt extract --engine klayout-runset` reaches an extracted netlist too
(`npn13G2.extract.runset.2026-11-20.json`: 3 devices, four-terminal `X` cards onto the
`npn13G2` subcircuit). The curated deck remains what cannot see it (#1232, unchanged).

**Consequence to carry into topology work, not to act on here**: an HBT mixer core
**can** reach `status: match` and an extracted netlist on the runset engine at current
`klt` — the 2026-11-14 "not achievable today" statement is superseded. The one blocker
left on that route is the signoff grader, not the engine: `klt signoff` refuses an
item-4 citation from these runset reports (`runset_unrecognised_device`, upstream
[`klayout-tools#6902`](https://github.com/2AMLogic/klayout-tools/issues/6902)) — see the
[Signoff finding](#signoff-finding-item-4-and-the-runset-reports) below. This is a
finding for the tracker; it is not a licence to change topology or relax the ratified
spec, and the curated deck's HBT gap (#1232) is not reopened by it.

## LVS status

The embedded question issue #31 had to settle was whether `klt lvs` can anchor a match on
vendor cells at all. **It can** — the 2026-11-14 answer was "yes, through the PDK runset,
and the remaining failure is a `klt` verdict defect (#5664), not a missing anchor"; the
2026-11-20 re-run confirms the fix: **all five runset rows read `status: match`, exit 0,
no error categories.**

### 1. The cells carry no pin labels anywhere — and that is legitimate

`klt extract` warns on every cell:

> found 0 pin-name label(s) on any of this deck's label layers (5/1, 8/25, 10/25, 30/25,
> 50/25, 67/25, 126/25, 134/25) … no net can be named, so 0 top-level pins will be promoted
> and `klt lvs` will have no net/device anchor to seed a match against a reference netlist.

`klt layers <cell>.gds` confirms this is not a case of labels sitting on the *wrong* layer:
none of the five cells carries **any** text/annotation shape on **any** layer. So
`--label-layer`, `--pins` and `--top-cell-pins` have nothing to redirect or promote, and
re-pointing them was not pursued.

This is how the vendor's device-recognition testcases are built, and the PDK's own harness
handles it with a documented switch rather than by labelling the cells: `run_regression.py`
passes `--ignore_top_ports_mismatch` for every unit testcase, which sets
`IGNORE_TOP_PORTS_MISMATCH` in `sg13g2.lvs`. **An unanchored LVS row here is therefore a
missing-pin-label property of a vendor test cell, not a device-recognition failure and not,
by itself, a tool gap.**

### 2. With the PDK runset, every cell matches topologically

Through `engine: klayout-runset` with that switch, all five cells match **100% of nets and
100% of devices**, including the HBT (tables above). At the 2026-11-14 baseline the only
category left in all five reports was `pin.unmatched` — reference pins with no layout
counterpart, i.e. exactly what the switch exists to suppress; at 2026-11-20 not even that
category remains.

### 3. Baseline only (2026-11-14): `klt lvs` scored those as errors — fixed by #5664

`klt lvs` forwarded the deck-var (it is echoed in the report's `deck_vars`) yet still
counted every suppressed pin as an error, returning `status: mismatch` / exit 3.
Cross-checked by running the **same runset with the same switch** through the PDK's own
`run_lvs.py`: all five pairs reported `Congratulations! Netlists match` / `Comparison
mode: PASS` / `Errors: 0`.

**Resolution:** filed as
[`klayout-tools#5664`](https://github.com/2AMLogic/klayout-tools/issues/5664), closed
completed 2026-11-17 (merge `18f78c41`, an ancestor of the 2026-11-20 `klt` commit). The
2026-11-20 re-run of the identical requests reads `status: match` / exit 0 on all five
cells — the defect is verified fixed, not assumed.

## Tool-gap issues filed from this probe

Per the friction protocol, each gap is filed generically against the tool, with the PDK's
own testcases as inputs and no design detail from this repository.

| gap | upstream issue | state | affects rows |
|---|---|---|---|
| SiGe HBT not modelled by the curated `sg13g2` deck → `devices: 0` | [`klayout-tools#1232`](https://github.com/2AMLogic/klayout-tools/issues/1232) | **pre-existing, closed** investigated-and-declined — **cited, not re-filed**; re-read 2026-11-20, the deck at `eaaf2989…` still models no bipolar class | `npn13G2` curated extract + curated LVS rows |
| HBT cannot reach an extracted netlist because `klt extract`/`klt pex` have no runset engine | [`klayout-tools#5481`](https://github.com/2AMLogic/klayout-tools/issues/5481) | closed completed 2026-11-17 (merge `f8b75151`) — **verified fixed 2026-11-20**: `klt extract --engine klayout-runset` extracts 3 `npn13G2` devices | the new `npn13G2.extract.runset.2026-11-20.json` |
| `klt lvs --engine klayout-runset` returns `mismatch` on compares the wrapped runset itself reports as `PASS` | [`klayout-tools#5664`](https://github.com/2AMLogic/klayout-tools/issues/5664) | closed completed 2026-11-17 (merge `18f78c41`) — **verified fixed 2026-11-20**: all five runset rows `status: match`, exit 0 | all five runset rows |
| `klt lvs`'s `subckt-call` + `deck` rewrite of a valueless `sg13g2` resistor card yields a reference with no top circuit | [`klayout-tools#5665`](https://github.com/2AMLogic/klayout-tools/issues/5665) | closed completed 2026-11-17 (merge `85c7af02`) — **verified fixed 2026-11-20**: the `rppd` curated-deck row emits a report (what it shows is #6960) | `rppd` curated-deck row |
| `klt lvs --format text` raises `AttributeError` on a `klayout-runset` report and still exits 0 | [`klayout-tools#5666`](https://github.com/2AMLogic/klayout-tools/issues/5666) | closed completed 2026-11-17 (merge `1d6b1ad0`) — **verified fixed 2026-11-20**: `--format text` exits 0 and prints `status: match` on all five rows | the runset command in every row |
| `klt signoff` refuses an item-4 citation from a matching runset report: zero-instance declared classes and case-different census keys both grade `runset_unrecognised_device` | [`klayout-tools#6902`](https://github.com/2AMLogic/klayout-tools/issues/6902) | **open** — the SG13G2 measurement was added to it 2026-11-20 (this probe: 42 zero-instance classes, `NPN13G2`/`npn13G2` census keys, runset pinned so the reason is exactly `runset_unrecognised_device`) | every runset row, for signoff only |
| `subckt-call` reference conversion emits upper-case placeholder classes so the curated compare pairs 1/84 (`rppd`) and 71/72 (`cap_cmim`) despite near-equal census | [`klayout-tools#6960`](https://github.com/2AMLogic/klayout-tools/issues/6960) | **open** — the 2026-11-20 `rppd`/`cap_cmim` curated-deck rows were added to it as data points | `rppd` + `cap_cmim` curated-deck rows |
| `klt extract`'s `netlist_path` is a host-absolute output path, so a committed report names a worktree that no longer exists | [`klayout-tools#2700`](https://github.com/2AMLogic/klayout-tools/issues/2700) | **pre-existing, closed `not_planned`** — ratified upstream, **cited, not re-filed**; worked around as described above (the dated 2026-11-20 reports carry the same caveat) | every `extract.json` |

No modelled device class failed to extract: all four of `nfet`, `pfet`, `cap_cmim` and
`rppd` produced non-zero `device_counts` from their vendor cell (re-confirmed 2026-11-20,
same counts), so there is no "declared but not recognised" gap to file.

## Signoff finding: item 4 and the runset reports

Would `klt signoff` accept an item-4 citation from the 2026-11-20 runset reports?
**No — not today.** Recorded here as a finding only; nothing was added to
`signoff/manifest.json` (these are vendor test cells, not a design claim).

The rule (item 4 of `docs/design-evidence-tiers.md` at `klt` commit `6bd18bbc8637`,
quoted):

> **PDK-runset path (issue #2870, operator ruling of 2026-10-08).** For device families
> the PDK's own open KLayout LVS runset recognises and the curated extraction deck does
> not, a `klt lvs` report with `"engine": "klayout-runset"` is accepted evidence for
> this item, on four conditions: (1) the runset is the PDK's own at a pinned revision —
> `klt signoff` checks `provenance.runset.content_hash` against a signoff-side allowlist
> (`signoff_runset.PINNED_RUNSETS`, hash → PDK revision), not against a field the block
> declares, and the runset file named by the report must still re-hash to that value;
> (2) the report is a `klt` envelope with the same `--check` re-hash guarantees as a
> curated-deck report (layout hash, reference netlist hash, plus the runset hash); (3)
> the report names its engine, and `klt signoff` carries `engine` and the runset hash
> distinctly in the check detail and the `met` citation; (4) every device is recognised
> — a non-empty `coverage.declared_not_recognized`, or a `device_census` whose per-class
> layout and reference counts differ, is a failure (`runset_unrecognised_device`), never
> a warning, even when `status` reads `match`.

Measured against each condition, on the five `*.lvs-pdk-runset.2026-11-20.json` reports:

| condition | holds? | evidence |
|---|---|---|
| (1) runset pinned | **yes** | `provenance.runset.content_hash` is `sha256:e01bcb1e…bbd7` in every report; `klt signoff --describe-grader` lists that digest under `pinned_runsets` as `ihp-sg13g2 @ 5cccb161f749` (v0.3.0), and the installed runset file re-hashes to it |
| (2) `--check` re-hash | **yes** | `klt lvs --check` exits 0 on all five dated runset reports (loop above) |
| (3) engine named | **yes** | `engine: "klayout-runset"` and `provenance.runset` present in every report |
| (4) every device recognised | **no** | every report carries `coverage.declared_not_recognized` with **42 zero-instance classes** (classes the runset declares but this cell does not instantiate: `inductor`, taps, the `diode*` families, `rhigh`, `res_metal*`, `rfcmim`, …), and on three of five the census keys differ in case (`npn13G2`/`NPN13G2`, `cap_cmim`/`CAP_CMIM`, `rppd`/`RPPD`) — each class then double-counts as a count gap |

End-to-end check (scratch manifest, not committed to `signoff/`): citing
`npn13G2/npn13G2.lvs-pdk-runset.2026-11-20.json` for item 4 grades the item
`unmet` with reason **`runset_unrecognised_device`** — `status: match`, exit 0 and a
pinned runset notwithstanding (`coverage_qualification.reason: "partial_coverage"`,
the 42 declared-not-recognised classes in `skipped[]`). This is upstream
[`klayout-tools#6902`](https://github.com/2AMLogic/klayout-tools/issues/6902), open; the
SG13G2 measurement was added there on 2026-11-20.

On the `ignore_top_ports_mismatch` deck-var specifically: the reports carry it in
`deck_vars` and the verdict-affecting fix (#5664) models it in the engine, but the
signoff-side refusal above fires on condition (4) independent of any deck-var, and the
grader at this commit has no deck-var-specific handling for runset citations at all
(no `deck_var` read in `signoff_runset.py`). So the deck-var question is **not yet
reachable**: until #6902 lands, no runset citation from this PDK gets far enough to test
it. Also recorded: `power_connectivity.status` is `"unchecked"` on all five reports (a
SPICE-reference form), which item 4 reads as "does not apply here", never as "verified".

## Open observation: curated-deck device count vs runset device count

Not resolved, and deliberately **not** filed upstream — recorded so the next reader does
not mistake it for agreement.

| device | `klt extract` (curated deck) | runset / reference | delta |
|---|---|---|---|
| `sg13_lv_nmos` | 36 | 28 | +8 |
| `sg13_lv_pmos` | 16 | 15 | +1 |
| `cap_cmim` | 72 | 69 | +3 |
| `rppd` | 82 | 84 | **−2** |

The positive deltas are the expected shape: `klt extract` reports a census of *recognised
geometry*, while the runset netlist is *schematic-equivalent* after its own `simplify` pass
and after folding `m`/`ng` multiplicity, so one schematic device can be several extracted
shapes. `rppd` goes the other way — the curated deck finds **fewer** resistors than both
the runset and the reference netlist — which that explanation does not cover.

**Version confounder: eliminated for the 2026-11-20 rows.** The baseline's two count
columns were produced by two different KLayouts (bundled `0.30.13` vs system `0.30.12`),
and `klt`'s own warning across that gap was specifically that report **counts** may
differ even where the verdict does not — so a version difference was a live candidate
explanation for every delta above. The 2026-11-20 re-run measured both engines on
**one** KLayout (`0.30.12`, `klayout_version_mismatch: false` on the curated-deck
reports) and reproduced **every delta unchanged** (36/28, 16/15, 72/69, 82/84). The
deltas are therefore properties of the two decks, not of the version split; the `rppd`
**−2** still has no traced explanation.

It is not filed because it has not been traced to a defect: a plausible benign cause is the
reference's two resistors with `b` (bend) parameters being split or merged differently by
the two decks, and filing a count delta without that trace would waste the tracker. It is
worth tracing before the curated deck is relied on for a resistor-bearing device count.
Reproduce with:

```bash
klt extract rppd/rppd.gds --deck sg13g2 --format json | python3 -c \
  'import json,sys; r=json.load(sys.stdin); print(r["device_count"], r["device_counts"])'
# vs counts.devices in rppd/rppd.lvs-pdk-runset.json (baseline)
#    and device_census.layout  in rppd/rppd.lvs-pdk-runset.2026-11-20.json (dated re-run)
```

## Files

```
lvs-device-coverage/
├── README.md                               this file
└── <device>/                               npn13G2, sg13_lv_nmos, sg13_lv_pmos, cap_cmim, rppd
    ├── PROVENANCE.md                       upstream path, PDK commit, Apache-2.0 attribution
    ├── <device>.gds                        vendor golden layout, unmodified
    ├── <device>.cdl                        vendor golden reference netlist, unmodified
    │
    │   # 2026-11-14 baseline (undated names) — byte-identical since issue #31
    ├── <device>.extracted.spice            netlist written by the baseline klt extract run
    ├── <device>.extract.json               klt extract report (curated sg13g2 deck)
    ├── <device>.lvs-klt-deck.json          klt lvs report (curated deck + native comparer)
    │   └── rppd only: .lvs-klt-deck.error.json — the baseline error envelope, kept as evidence
    ├── <device>.lvs-pdk-runset.json        klt lvs report (engine: klayout-runset)
    │
    │   # 2026-11-20 dated siblings (issue #98, klt 6bd18bbc8637)
    ├── <device>.extracted.2026-11-20.spice      netlist written by the dated klt extract run
    ├── <device>.extract.2026-11-20.json         klt extract report (curated sg13g2 deck)
    ├── <device>.lvs-klt-deck.2026-11-20.json    klt lvs report (curated deck) — rppd now emits one
    ├── <device>.lvs-pdk-runset.2026-11-20.json  klt lvs report (engine: klayout-runset): status: match
    └── <device>.lvs-pdk-runset.2026-11-20.txt   the --format text check (#5666) on the same request

npn13G2/ only, the #5481 route:
    npn13G2/npn13G2.extracted.runset.2026-11-20.spice   runset-engine extracted netlist (3 devices)
    npn13G2/npn13G2.extract.runset.2026-11-20.json      runset-engine extract report
```

The `.gds`/`.cdl` pairs are byte-identical to the upstream files; their sha256 values are
recorded in each `PROVENANCE.md` and are re-checked by `klt extract --check`.
