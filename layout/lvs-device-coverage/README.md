# lvs-device-coverage

Which SG13G2 devices `klt` can extract and LVS-match **today**, measured before a mixer
topology is chosen (issue #31; the risk is recorded as item 4 of the T1 tracker #5).

Every row below is a committed run, not an assertion. The probe cells are the IHP PDK's
own golden LVS testcases, copied unmodified — see each `<device>/PROVENANCE.md` for the
upstream path, the PDK commit and the Apache-2.0 attribution.

**Headline**: the curated `sg13g2` extraction deck models **no bipolar device class at
all**, so `npn13G2` extracts as zero devices. The four passive/MOS classes a mixer core
and bias would use are all recognised. No `klt lvs` run in this directory reaches
`status: match`, for two different reasons — one of them a vendor-cell property, the other
a `klt` defect — both detailed under [LVS status](#lvs-status-why-nothing-reaches-match).

> **Nothing here is a design claim.** These are vendor test cells, not mixer geometry. The
> directory answers "what does the toolchain recognise", nothing else.

## Environment identity

**Read these back before trusting any row below.** Every number in this file was measured
on 2026-11-14 against exactly this environment; a different `content_hash` means the table
is stale and the rows must be re-run, not trusted.

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
As of 2026-11-14 at the deck hash above it reports **13 device classes**:

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
commands are relative to this directory.

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

# 2. Extraction — the "extracted devices" column
klt extract <device>/<device>.gds --deck sg13g2 --format json \
    -o <device>/<device>.extracted.spice
#   npn13G2      -> device_count 0,  device_counts {}
#   sg13_lv_nmos -> device_count 36, device_counts {"nfet": 36}
#   sg13_lv_pmos -> device_count 16, device_counts {"pfet": 16}
#   cap_cmim     -> device_count 72, device_counts {"cap_cmim": 72}
#   rppd         -> device_count 82, device_counts {"rppd": 82}

# 3. LVS, curated sg13g2 deck — the "LVS (curated deck)" column
klt lvs '{"layout":{"file":"<device>/<device>.gds","deck":"sg13g2"},
          "reference":{"netlist":"<device>/<device>.cdl"}}' --format json
#   cap_cmim and rppd additionally need the capacitor/resistor rewrite:
#     "reference":{"netlist":"…","form":"subckt-call","deck":"sg13g2"}
#   rppd then fails with: error "reference netlist has no top circuit" (#5665)

# 4. LVS, PDK's own runset — the "LVS (PDK runset)" column. Needs the PDK install;
#    --format json is required (--format text crashes: #5666)
PDKLVS="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/lvs"
klt lvs '{"layout":{"file":"<device>/<device>.gds"},
          "reference":{"netlist":"<device>/<device>.cdl"},
          "engine":"klayout-runset"}' \
    --deck-file "$PDKLVS/sg13g2.lvs" \
    --deck-var ignore_top_ports_mismatch=true --format json
```

### Re-verifying the committed reports without re-running the engines

Each committed report carries the hashes of its own inputs, so drift is detectable
cheaply. All 14 reports in this directory re-check clean as of 2026-11-14:

```bash
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt extract --check "$d/$d.extract.json"            # exit 0 = still consistent, 3 = drifted
done
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim; do
  klt lvs --check "$d/$d.lvs-klt-deck.json"
done
for d in npn13G2 sg13_lv_nmos sg13_lv_pmos cap_cmim rppd; do
  klt lvs --check "$d/$d.lvs-pdk-runset.json"
done
```

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

**The HBT is not unreachable, though.** The PDK's own runset *does* recognise it: via
`engine: klayout-runset`, `npn13G2` matches **3/3 devices and 10/10 nets**
(`npn13G2.lvs-pdk-runset.json`). The curated deck is what cannot see it. Making that path
available to `klt extract`/`klt pex` — needed for any extracted-netlist or parasitic
evidence on an HBT core — is open upstream as
[`klayout-tools#5481`](https://github.com/2AMLogic/klayout-tools/issues/5481), which
explicitly does not reopen #1232.

**Consequence to carry into topology work, not to act on here**: with the curated deck as
it stands, an HBT mixer core cannot reach a `status: match` `klt lvs` result, so T1 item 4
is not achievable for the HBT devices today. The runset path above is the candidate route.
This is a finding for the tracker; it is not a licence to change topology or relax the
ratified spec.

## LVS status: why nothing reaches `match`

The embedded question this issue had to settle was whether `klt lvs` can anchor a match on
vendor cells at all. **It can** — the answer is "yes, through the PDK runset, and the
remaining failure is a `klt` verdict defect, not a missing anchor."

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
100% of devices**, including the HBT (table above). The only category left in all five
reports is `pin.unmatched` — reference pins with no layout counterpart, i.e. exactly what
the switch exists to suppress.

### 3. …but `klt lvs` still scores those as errors, so its verdict is `mismatch`

`klt lvs` forwards the deck-var (it is echoed in the report's `deck_vars`) yet still counts
every suppressed pin as an error, returning `status: mismatch` / exit 3. Cross-checked by
running the **same runset with the same switch** through the PDK's own `run_lvs.py`: all
five pairs report `Congratulations! Netlists match` / `Comparison mode: PASS` / `Errors: 0`.

A wrapper disagreeing with the engine it wraps is a tool defect, and it is **filed**:
[`klayout-tools#5664`](https://github.com/2AMLogic/klayout-tools/issues/5664).

## Tool-gap issues filed from this probe

Per the friction protocol, each gap is filed generically against the tool, with the PDK's
own testcases as inputs and no design detail from this repository.

| gap | upstream issue | state at filing | affects rows |
|---|---|---|---|
| SiGe HBT not modelled by the curated `sg13g2` deck → `devices: 0` | [`klayout-tools#1232`](https://github.com/2AMLogic/klayout-tools/issues/1232) | **pre-existing, closed** investigated-and-declined — **cited, not re-filed** | `npn13G2` |
| HBT cannot reach an extracted netlist because `klt extract`/`klt pex` have no runset engine | [`klayout-tools#5481`](https://github.com/2AMLogic/klayout-tools/issues/5481) | **pre-existing, open** — cited, not re-filed | `npn13G2` |
| `klt lvs --engine klayout-runset` returns `mismatch` on compares the wrapped runset itself reports as `PASS`: verdict-affecting deck-vars are forwarded but not modelled | [`klayout-tools#5664`](https://github.com/2AMLogic/klayout-tools/issues/5664) | **filed 2026-11-14 by this probe** | all five runset rows |
| `klt lvs`'s `subckt-call` + `deck` rewrite of a valueless `sg13g2` resistor card yields a reference with no top circuit — the remedy `klt`'s own error hint prescribes | [`klayout-tools#5665`](https://github.com/2AMLogic/klayout-tools/issues/5665) | **filed 2026-11-14 by this probe** | `rppd` curated-deck row |
| `klt lvs --format text` raises `AttributeError` on a `klayout-runset` report and still exits 0 | [`klayout-tools#5666`](https://github.com/2AMLogic/klayout-tools/issues/5666) | **filed 2026-11-14 by this probe** | the runset command in every row |
| `klt extract`'s `netlist_path` is a host-absolute output path, so a committed report names a worktree that no longer exists | [`klayout-tools#2700`](https://github.com/2AMLogic/klayout-tools/issues/2700) | **pre-existing, closed `not_planned`** — ratified upstream, **cited, not re-filed**; worked around as described above | every `extract.json` |

No modelled device class failed to extract: all four of `nfet`, `pfet`, `cap_cmim` and
`rppd` produced non-zero `device_counts` from their vendor cell, so there is no
"declared but not recognised" gap to file.

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

**Version confounder, not eliminated:** the two count columns were not produced by the same
KLayout. The curated-deck column ran on `klt`'s bundled module `0.30.13` and the runset
column on the system binary `0.30.12` (§ *Environment identity*), and `klt`'s own warning
across that gap is specifically that report **counts** may differ even where the verdict
does not. A version difference is therefore a live candidate explanation for every delta in
this table — including the `rppd` **−2** that the census-vs-schematic-equivalent reasoning
above does not cover. Before reading these deltas as a curated-deck defect, re-run both
sides on one KLayout version; that is cheaper than the geometry trace below and may remove
the question entirely.

It is not filed because it has not been traced to a defect: a plausible benign cause is the
reference's two resistors with `b` (bend) parameters being split or merged differently by
the two decks, and filing a count delta without that trace would waste the tracker. It is
worth tracing before the curated deck is relied on for a resistor-bearing device count.
Reproduce with:

```bash
klt extract rppd/rppd.gds --deck sg13g2 --format json | python3 -c \
  'import json,sys; r=json.load(sys.stdin); print(r["device_count"], r["device_counts"])'
# vs counts.devices in rppd/rppd.lvs-pdk-runset.json
```

## Files

```
lvs-device-coverage/
├── README.md                          this file
└── <device>/
    ├── PROVENANCE.md                  upstream path, PDK commit, Apache-2.0 attribution
    ├── <device>.gds                   vendor golden layout, unmodified
    ├── <device>.cdl                   vendor golden reference netlist, unmodified
    ├── <device>.extracted.spice       netlist written by the klt extract run
    ├── <device>.extract.json          klt extract report (curated sg13g2 deck)
    ├── <device>.lvs-klt-deck.json     klt lvs report (curated deck + native comparer)
    │   └── rppd only: .lvs-klt-deck.error.json — the error envelope, kept as evidence
    └── <device>.lvs-pdk-runset.json   klt lvs report (engine: klayout-runset)
```

The `.gds`/`.cdl` pairs are byte-identical to the upstream files; their sha256 values are
recorded in each `PROVENANCE.md` and are re-checked by `klt extract --check`.
