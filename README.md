# sg13g2-mixer

A SiGe HBT downconversion mixer on
[IHP SG13G2](https://github.com/IHP-GmbH/IHP-Open-PDK), IHP's open-source
130 nm SiGe BiCMOS PDK — the stage after
[sg13g2-lna](https://github.com/2AMLogic/sg13g2-lna) in a receive chain —
designed by AI agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools) and the
open-source xschem + ngspice flow.

**Status: just opened, specification phase.** Nothing is designed yet.

**Built agent-native.** Every specification, decision record, testbench, and
line of documentation here is produced by AI agents working from a ratified
spec and an append-only evidence trail — not human-authored work that agents
merely assisted with. Verification is the product: every claim traces to a
recorded result under PVT corners. Where the agents hit friction with the
open-source tooling — most often
[klayout-tools](https://github.com/2AMLogic/klayout-tools) — that friction is
filed as a public issue against the tool itself, so the fix benefits everyone
using SG13G2, not just this repo.

## Why this block, on this PDK

`sg13g2-lna` amplifies the 2.4 GHz ISM band (2400–2483.5 MHz, 50 Ω ports,
1.8 V supply, per its ratified spec). The next block in the chain translates
that band down to an intermediate frequency. A double-balanced HBT
(Gilbert-cell) mixer is the textbook choice on a SiGe process, and SG13G2's
HBTs have ample fT for a 2.4 GHz LO.

The canary's honest centerpiece is **measuring a frequency-translating
block with open tools**. Conversion gain, single-sideband noise figure,
IIP3 and LO-port isolation are all large-signal, periodically driven
quantities; ngspice has no periodic steady-state analysis, so every number
here comes from transient benches with stated windows, FFT settings and
convergence checks. Getting that methodology right, reproducibly, is as
much the deliverable as the circuit.

## Scope

- **In scope**: the mixer core, its bias, the RF input interface to the LNA,
  the LO input buffer interface, and the IF output stage into a stated load.
- **Not in scope**: the LNA (it comes from `sg13g2-lna`; this repo specifies
  the interface to it and stops), the LO source (an ideal source in every
  bench, with its required drive level and phase noise stated as a
  requirement on whatever supplies it), and anything after the IF output.
- **Related, not consumed**: `sg13g2-sat-rx` carries a Ka-band mixer
  topology study on the same HBTs. It is a different block at a different
  band; its bench methodology is prior art to read, and any shared,
  band-independent bench mechanics have one master.

## Target specification (DRAFT — engineering to ratify, see issue #2)

All rows are *targets*, not results.

| Parameter | Fallback | Target | Stretch |
|---|---|---|---|
| RF band | 2400–2483.5 MHz | 2400–2483.5 MHz (`sg13g2-lna`'s ratified band) | — |
| RF input | 50 Ω single-ended | 50 Ω, matched to the LNA output (S11 < −10 dB) | on-chip balun included |
| IF | single low IF | low IF (to be fixed by the spec, 1–50 MHz class) | zero-IF quadrature (I/Q) pair |
| Conversion gain | > 5 dB | > 10 dB | > 15 dB |
| SSB noise figure | < 15 dB | < 12 dB | < 9 dB |
| IIP3 | > −5 dBm | > 0 dBm | > +5 dBm |
| LO-to-RF isolation | > 30 dB | > 40 dB | > 50 dB |
| Supply / power | 1.8 V ±10%, < 20 mW | 1.8 V ±10%, < 10 mW | < 5 mW |
| Signoff | DRC + LVS clean | DRC + LVS clean, post-layout re-verified | — |

Maturity ladder: spec ratified → bench methodology validated on a known
reference → schematic simulated across PVT → layout DRC/LVS-clean →
post-layout re-verification → shuttle seat → measured silicon.
**Current position: pre-spec.**

## Tool flow

- **Design and simulation**: xschem + ngspice with the SG13G2 VBIC HBT and
  PSP MOS models; transient, FFT-based large-signal benches.
- **Layout, DRC, LVS**: klayout-tools (`klt`).

## Repo layout

```
spec/          ratified spec + decision records
design/        schematics / netlists (xschem)
sim/           testbenches + PVT corner results (ngspice)
layout/        GDS + DRC/LVS reports (klayout-tools driven)
scripts/       CI check scripts (also run locally via package.json) + negative-control fixtures
signoff/       block manifest and T1 attestation inventories/envelopes
measurements/  silicon characterization (empty until tape-out)
```

## Reproducing results

No bench has landed yet, so there are no simulated results to reproduce. Each
bench's cold-start command will be linked here as it lands (the harness and
bench documentation are tracked in issue #3; until it merges, see
[`sim/README.md`](sim/README.md)).

The repo-hygiene and evidence-format checks need no PDK or simulator and
reproduce today. They are the same commands CI runs
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):

```bash
npm run check:ci                      # every check below, via scripts/check-all.sh
BASE=origin/main npm run check:ci     # also the append-only gate against a base ref
scripts/test-checks.sh                # negative and positive controls for each gate
klt signoff --attest 10 --inventory signoff/repo-hygiene/inventory.json \
  --check signoff/repo-hygiene/envelope.json
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
