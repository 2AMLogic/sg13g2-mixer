# Re-check of the pinned `sg13g2-lna` interface against current LNA `main`

**This file records a comparison. It makes no re-pin decision and changes no
row.** `spec/target-spec.md` §"Interface to `sg13g2-lna`" copies the LNA's
rows at a pinned commit and states that whether the newer LNA changes any
interface row "has **not** been checked in this revision and needs a
deliberate re-pin decision". This file performs that check and reports the
answer. Re-pinning — or leaving the pin where it is — remains its own
numbered decision record under `spec/decision-records/`.

Nothing here is a simulated figure: no bench was run and no number below is a
measurement. These are specification rows and git object identities.

## What was compared

| | Repository | Commit (full sha) | Commit date (UTC) | Read on |
|---|---|---|---|---|
| **The pin** | `2AMLogic/sg13g2-lna` | `5532789887c6c10abbaba541fb9294ce72b8cf5e` | 2026-10-16T20:01:09Z | 2026-10-17 (by `spec/target-spec.md`) |
| **The newer commit** | `2AMLogic/sg13g2-lna` | `979d5cf6d1780dbf80788124c43dd873e7fad4d8` | 2026-11-14T02:42:54Z | **2026-11-14** (this file) |

`979d5cf` was the `main` HEAD of `2AMLogic/sg13g2-lna` when this comparison
was run, read directly from the forge on 2026-11-14. It is named as a sha,
not as "latest": LNA `main` moves, and this file stays true as a record of
what `979d5cf` contained rather than as a claim about whatever `main` holds
when you read it. The two commits are **119 commits apart**.

Both source files the interface cites — `spec/target-spec.md` and
`spec/ratified-rows.json` — are in the **`2AMLogic/sg13g2-lna`** repository.
Neither exists in `sg13g2-mixer`; in particular there is no
`spec/ratified-rows.json` in *this* repository. Every path below names the
repository it belongs to.

## Row-by-row comparison

One row per row of `spec/target-spec.md` §"Interface to `sg13g2-lna`" (10
rows). "Value at the pin" is the value that section copied, re-read from the
LNA source at the pin rather than from this repository's copy.

| LNA row | Value at the pin `5532789` | Value at `979d5cf` | Same / difference |
|---|---|---|---|
| **Band** | 2400–2483.5 MHz (2.4 GHz ISM), primary band — RATIFIED | 2400–2483.5 MHz (2.4 GHz ISM), primary band — RATIFIED | **Same** |
| **Port convention** | All S-parameters, gain and match figures at a 50 Ω reference impedance at both ports; NF reference temperature T0 = 290 K — RATIFIED (Gain/NF/S11/S22 rows) | 50 Ω both ports; T0 = 290 K — RATIFIED (Gain/NF/S11/S22 rows) | **Same** |
| **Supply** | 1.80 V ± 10 % (1.62–1.98 V), single rail — RATIFIED | 1.80 V ± 10 % (1.62–1.98 V), single rail — RATIFIED | **Same** |
| **Gain (S21)** | > 15 dB (\|S21\|, 50 Ω ports) across the ratified band — RATIFIED | > 15 dB across the ratified band — RATIFIED | **Same** |
| **Noise figure** | < 1.5 dB across the ratified band at T0 = 290 K, 50 Ω ports both ends — RATIFIED | < 1.5 dB across band, T0 = 290 K — RATIFIED | **Same** |
| **Output match (S22)** | < −10 dB across the ratified band, 50 Ω reference — RATIFIED | < −10 dB across band, 50 Ω reference — RATIFIED | **Same** |
| **IIP3 numeric** | Former DRAFT > 0 dBm **remains DRAFT** — `status: not-ratified` in `spec/ratified-rows.json` (LNA repo) | Former DRAFT > 0 dBm **remains DRAFT** — `status: not-ratified`, `comparator: ">"`, `limit: "0"`, `unit: "dBm"`, `classification: not-ratified` | **Same** — still not ratified (see D1 below) |
| **IIP3 protocol** | Two-tone transient bench: f1 = 2.44140625 GHz, f2 = 2.44903564453125 GHz, Δ = 7.62939453125 MHz, FFT N = 65536 at 4 ps, rectangular window, coherent bin-centred products, 1 µs discarded before the window, double drive levels per cell with the 3:1 IM3 slope check mandatory — protocol RATIFIED | Identical protocol, identical parameters — protocol RATIFIED | **Same** |
| **Corner box** | Process {`typ`→`hbt_typ`, `bcs`→`hbt_bcs`, `wcs`→`hbt_wcs`; `sf`/`fs` fall back to `hbt_typ`} × temperature {−40, 27, 125} °C × supply {1.62, 1.80, 1.98} V — RATIFIED | Identical 45-cell grid, including the same `sf`/`fs`→`hbt_typ` fallback note — RATIFIED | **Same** |
| **PDK pin** | IHP-Open-PDK release `v0.3.0`, tag commit `5cccb161f7492697cfa52eb14dc03beb00bdca9e` (2026-03-11), recorded in `sim/pdk.json` (LNA repo) | Same release and same tag commit; `sim/pdk.json` blob unchanged | **Same** |

## Evidence

The comparison is made on **git object identities**, not on rendered prose.
Two commits sharing a tree SHA share every byte of every file under that
tree, recursively — so an identical `spec/` tree SHA is a complete proof that
no row of any file under `spec/` changed, and it needs one read per commit.

Reading the compare API's `files` list instead would have been unsound here:
`5532789...979d5cf` reports 119 commits and its `files` array comes back with
**exactly 300 entries**, i.e. truncated at GitHub's cap. A "nothing changed"
conclusion drawn from that list could not be trusted.

**Trees at the two commits** (`repos/2AMLogic/sg13g2-lna/git/trees/<ref>`,
read 2026-11-14):

| Path | At `5532789` | At `979d5cf` | |
|---|---|---|---|
| `spec/` | `56bf2b154995dc1bb335d9618db05da1e8c3395c` | `56bf2b154995dc1bb335d9618db05da1e8c3395c` | **identical** |
| `design/` | `a514146d559bd1cabcec9a3a9d7a217db737fed2` | `42be4d9f7482e963884f50d6d119a11ac6c49bd6` | changed |
| `sim/` | `0a43a8656fc03112955dbe27cd079e644383ef3c` | `caecaa452d3e35940fbcf67a601af37c1080c389` | changed |

**Blobs under the (identical) `spec/` tree `56bf2b15…`**, which therefore hold
at both commits:

| File (LNA repo) | Blob SHA |
|---|---|
| `spec/target-spec.md` | `153f83c0df9614f92e3ff523d6c5b55abe8a1e75` |
| `spec/ratified-rows.json` | `4fd346b8ea75a073504b1e0e5b19a2c47974d745` |
| `spec/README.md` | `433543cbeaebc3eab8cf1b18ce1bd81e7b342b5b` |
| `spec/porting-plan.md` | `b53c6fd9c1afded14dedc361add23d4c309a2f4c` |
| `spec/decision-records/` (tree) | `1f3b0871c3578c94f4498cf0578f3fd7252c7c4c` |

**Independent cross-check of the tree-identity argument.** The contents of
`spec/target-spec.md` were fetched at `979d5cf` and hashed locally with
`git hash-object`, giving `153f83c0df9614f92e3ff523d6c5b55abe8a1e75` — the
same blob SHA listed under the pinned `spec/` tree above. The file the newer
commit serves is byte-identical to the file the pin serves, confirmed without
relying on the tree SHA alone. The ten row values in the table above were
read from that fetched copy.

**The PDK pin row cites `sim/pdk.json`, which is outside `spec/`**, so it was
checked separately: blob `2a6762c0956a2ed3fdb6a66ee3d9c3eccb7cbd67` at both
`5532789` and `979d5cf`. The PDK pin row's cited source has not moved.

**One line on the trees that did change**, for completeness and deliberately
not tabulated: the LNA's `design/` and `sim/` trees both advanced between the
two commits, i.e. the LNA's design and simulation evidence has moved on. That
is the LNA's own standing against its own rows, which
`spec/target-spec.md` explicitly declines to restate here, and it is **not**
an interface-row change.

## Result

**No interface row changed.**

Every one of the ten rows of `spec/target-spec.md` §"Interface to
`sg13g2-lna`" holds the same value, with the same ratification status, at
`979d5cf6d1780dbf80788124c43dd873e7fad4d8` as at the pinned
`5532789887c6c10abbaba541fb9294ce72b8cf5e`. No mixer row R1–R15 and no
cascade value is affected by the LNA's movement between these two commits.

Consequently the pin is not *stale* in the sense of hiding a changed
interface. Whether to advance it anyway — so that later readers follow a
citation to a commit nearer the LNA's current evidence — is a judgement this
file does not make, and would be its own decision record.

## Deferred item D1: is the LNA IIP3 row still unratified?

**Yes — still `not-ratified` at `979d5cf`.** Read from
`spec/ratified-rows.json` in the **`2AMLogic/sg13g2-lna`** repository at that
commit, the row `id: "iip3"` carries:

```json
{
  "id": "iip3",
  "selector": "IIP3",
  "column": "value",
  "status": "not-ratified",
  "comparator": ">",
  "limit": "0",
  "unit": "dBm",
  "template": "Numeric: former DRAFT {comparator} {limit} {unit} remains DRAFT",
  "anchor": "start",
  "classification": "not-ratified"
}
```

Every other row in that file (`gain`, `nf`, `s11`, `s22`, `mu`, `negres`,
`supply`, `power`, `ic1`) is `"ratified"` — `iip3` is the single exception,
as it was at the pin.

**Deferred item D1 therefore stands.** `spec/target-spec.md` records that the
cascade IIP3 requirement "must be re-derived when the LNA IIP3 is ratified
(decision record, Deferred D1)"; the LNA IIP3 numeric is still DRAFT, so the
cascade IIP3 figure in this repository stays provisional and D1 stays open.
Nothing in this comparison closes it.

---

*Comparison run 2026-11-14 against `2AMLogic/sg13g2-lna` `main` HEAD
`979d5cf6d1780dbf80788124c43dd873e7fad4d8` using read-only forge API calls
(`git/trees`, `contents`, `compare`) and local `git hash-object`. No
simulation was run and no `sim/` path in this repository was touched.*
