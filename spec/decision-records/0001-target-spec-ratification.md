# 0001 — Target specification ratification

- **Status**: PROPOSED, **not ratified**. Revised 2026-10-25 under the
  operator's requirements-review ruling of 2026-10-19. Approving the PR that
  carries this record is not ratification. Ratification needs an independent
  review of the requirements trace, then a later explicit operator
  ratification. Until then no row of [`../target-spec.md`](../target-spec.md)
  is ratified.
- **Issue**: [#2](https://github.com/2AMLogic/sg13g2-mixer/issues/2)
- **Date drafted**: 2026-10-17

## Decision

Adopt [`spec/target-spec.md`](../target-spec.md) as the fixed target every later
design and verification issue (#3 onward) verifies against, and make the README
target table a copy of its rows.

## Evidence and inputs

- `sg13g2-lna` at `5532789887c6c10abbaba541fb9294ce72b8cf5e`
  (`spec/target-spec.md`, `spec/ratified-rows.json`), read 2026-10-17. Band,
  50 Ω ports, supply, gain, NF and the S11/S22 rows are RATIFIED there. Its
  **IIP3 numeric target is not ratified**; its two-tone protocol is.
- Local PDK install v0.3.0 (`.fetched-version` = 0.3.0): section names in
  `cornerHBT.lib`, `cornerMOSlv.lib`, `cornerMOShv.lib`, `cornerRES.lib`,
  `cornerCAP.lib` listed from the files on 2026-10-17. The HBT validity window and
  1.6 V maximum VCE were read from the `sg13g2_hbt_mod.lib` header in that
  install.
- Cascade arithmetic: spec §"Cascade arithmetic" (computed in this PR, no
  simulation).
- No simulation was run for this record.

## What is ratified, row by row

- **Unchanged from the former README draft** (carried unchanged, **proposed
  assumptions with no receiver-requirement derivation**; nothing is ratified
  by this record):
  RF band, RF input impedance, CG, SSB NF, IIP3, LO-to-RF isolation,
  supply/power, signoff — all three columns. No value was relaxed.
- **Interface rows** (R1 band, the supply in R13): copied from `sg13g2-lna`;
  owned upstream.
- **New rows proposed by this record** (the former README had no number, so
  these are the agent's proposals and the operator should read them first):
  R3 LO level and low-side plan, R4 LO phase noise (provisional), R8 P1dB,
  R9 IF value, bandwidth and load, R11 LO-to-IF and R12 RF-to-IF isolation,
  R14 area (provisional). Rationale: each is the minimum a bench needs in order
  to state its conditions; none has measured support yet, and R4 and R14 are
  explicitly placeholders.

## Revision under the operator ruling (2026-10-19)

- Added the spec's *Requirements trace*: approved requirements are only the
  upstream INTERFACE rows; every other row is a proposed assumption, with its
  support and missing budgets (M1–M6) named. R4 and R14 stay placeholders; R9's
  IF load has no agreed downstream allocation; B-NF is unproven.
- Alternatives and intended-use framing are recorded, undecided. Standards
  receiver clauses (Bluetooth RF PHY, IEEE 802.15.4 2450 MHz PHY) are named as
  primary sources to read; their figures were **not** retrieved and none is
  quoted.
- Added a finite validation plan (V0–V6) with executor prerequisites,
  known-answer checks, cost or named unknowns, and stop conditions. **No
  simulation is authorized.**
- Pinned LNA interface and cascade assumptions reviewed: bounds used as values,
  pin has not been compared with LNA `main`, LNA IIP3 still unratified.
- Preserved: single-low-IF target scope, upstream LNA/LO ownership,
  append-only `sim/` evidence. No numeric limit changed, no `consumes` edge,
  no design, simulation, spending, merge or closure.
- The earlier Judge approval covered documents and arithmetic only. The
  operator keeps final ratification of PR #7; issue #2 stays open.

## Open questions — resolution or deferral

| Question (from the issue) | Resolution |
|---|---|
| RF input / balun location | **Resolved (proposed)**: target is an active single-to-differential stage, no inductors; fallback is an ideal balun at the bench boundary, declared on every figure; on-chip balun is the stretch. Basis: `sg13g2-lna` records that the PDK has no inductor SPICE/EM model. |
| LO frequency plan | **Resolved (proposed)**: low-side, f_LO = f_RF − f_IF. Not performance-driven; it keeps the bench tone plan coherent (spec §Measurement protocol). Revisit only with evidence. |
| Bench methodology, SSB NF extraction without periodic noise analysis | **Resolved as a protocol, unproven as a method.** B-NF injects per-device transient noise and measures the IF PSD; the first work item is to validate it on the known-answer cases. If ngspice cannot do this, the spec must be amended by a new record, not worked around. |
| Known-answer reference | **Resolved**: ideal multiplier (CG = k·A/2), hard-switched ideal mixer (2/π), ideal-multiplier SSB NF = 3.01 dB, polynomial IIP3. |
| `sg13g2-sat-rx` band-independent bench code | **Deferred (D4)**: decided when #3 builds the bench. If shared, one master and stamped copies in `reuse.lock.json`. |
| Inductor / balun models for 2.4 GHz; `sg13g2-vco` spiral inductors | **Deferred (D3), operator decision**: using `sg13g2-vco`'s inductor model needs a `consumes` edge. **No `consumes` edge is assumed anywhere in the spec.** This record neither requests nor presumes it. |
| Cascade vs standalone NF/IIP3 | **Resolved**: mixer NF and IIP3 rows are standalone. The cascade arithmetic is in the spec so the system effect is visible. |

## Deferred

- **D1 — LNA IIP3.** The upstream number is unratified. The cascade IIP3 table
  assumes the draft 0 dBm and is labelled provisional; re-derive it when
  `sg13g2-lna` ratifies IIP3. Owner: re-open this record then.
- **D2 — LO phase noise.** R4 is a placeholder with no system reciprocal-mixing
  budget behind it. Owner: the issue that defines the receive-chain blocker
  level, or an operator ruling.
- **D3 — Inductor source (operator decision).** Whether to consume
  `sg13g2-vco` inductors. The single low-IF target does not depend on it.
- **D4 — Shared bench code with `sg13g2-sat-rx`.**
- **D5 — Zero-IF I/Q.** Stays a stretch (R9); not allowed to drive the core
  architecture before the single-IF target closes.
- **D7 — Receive-chain requirements (M1–M5).** Target use, sensitivity/blocker
  profile, IF filtering/ADC allocation and LO capability. Owner: operator
  statement, then an independent reviewer. Blocks derivation of R4–R12.
- **D6 — Image rejection.** The cascade NF has two readings (spec table)
  depending on whether the image is rejected. This is a system question, not
  fixed here.

## Findings for other repositories

- **`sg13g2-lna`**: no new finding filed by this PR. The mixer states its
  RF-input requirement (50 Ω single-ended, S11 < −10 dB). The LNA's own output
  match and IIP3 ratification are tracked in that repo; this block's
  cascade views are conditional on them.
- **`klayout-tools`**: no tool gap hit while writing this specification.
  Gaps found during #3 and later benches are filed there, described
  generically.

## Consequences

- #3 pins the PDK and builds the models the spec's corner box refers to.
- Once rows are ratified, later issues verify against R1–R15 and the protocol;
  none may relax a ratified row to pass. A change to a ratified row is a new numbered record.
- The README target table is a copy of the spec's rows R1–R15 at Fallback /
  Target / Stretch.
