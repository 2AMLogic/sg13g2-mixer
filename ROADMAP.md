# Roadmap

`sg13g2-mixer` is a SiGe HBT downconversion mixer for the 2.4 GHz ISM band on
IHP SG13G2, whose real deliverable is a reproducible way to measure a
frequency-translating block with transient-only open tools.

Status as of 2026-11-13, `main` @ `76a4a59`.

## Where it stands

README maturity ladder: spec ratified → bench methodology validated on a known
reference → schematic simulated across PVT → layout DRC/LVS-clean →
post-layout re-verification → shuttle seat → measured silicon.
**Position: first rung, ratified on the tracker but not yet recorded on `main`.**

- **Spec.** [`spec/target-spec.md`](spec/target-spec.md) (rows R1–R15, PVT
  corner box, measurement protocol, known-answer checks, validation plan
  V0–V6) and [decision record 0001](spec/decision-records/0001-target-spec-ratification.md)
  merged in PR #7. On `main` both still read PROPOSED. The operator ruling of
  2026-11-10 on [#2](https://github.com/2AMLogic/sg13g2-mixer/issues/2)
  ratifies R1–R15 as targets, with R4, the R9 load, R14 and the cascade values
  that depend on the LNA IIP3 left provisional; R1 and the R13 supply stay
  interface rows. PR [#23](https://github.com/2AMLogic/sg13g2-mixer/pull/23)
  records that ruling (status text only) and is approved but held.
- **Toolchain pins.** PDK v0.3.0 and ngspice 46 are pinned with an integrity
  gate and a negative control (`sim/pdk-artifact.json`, `sim/toolchain.json`,
  `sim/tools/verify_pdk.py`), plus one `npn13G2` smoke bench
  (`sim/smoke-hbt/`). PR #6, issue #3 closed.
- **CI.** Headless checks and gate self-tests (`scripts/`,
  `.github/workflows/ci.yml`) and the item-10 attestation
  (`signoff/repo-hygiene/`). PR #8, issue #4 closed.
- **No evidence yet.** `design/` and `layout/` hold only a README, `sim/`
  holds no bench result, and no row has simulation evidence.

T1 checklist (items as numbered in
[#5](https://github.com/2AMLogic/sg13g2-mixer/issues/5)), read against the tree today:

| Item | State |
|---|---|
| 1 Design sources | not started |
| 2 Layout | not started |
| 3 DRC clean | not started (no layout) |
| 4 LVS clean | not started; `npn13G2` extraction coverage is a known risk (#5) |
| 5 Corner verification vs ratified spec | waits on #23, then on benches and a schematic |
| 6 Monte Carlo for statistical rows | no statistical row exists yet (deferred D8) |
| 7 Post-layout verification | waits on items 1–4 |
| 8 Characterization report | waits on item 5 |
| 9 Testbenches shipped | groundwork only: pins and smoke bench; no spec-row bench |
| 10 Repo hygiene | attestation committed and checked in CI; its inventory says the item stays unmet until the spec table is ratified |
| 11 Power delivery (structural) | not started |

The body of #5 predates PRs #6 and #8; this table is the newer reading.

## Now

These do not depend on #23 and can start today. Each is filed: item 1 is
[#29](https://github.com/2AMLogic/sg13g2-mixer/issues/29), item 2 is
[#30](https://github.com/2AMLogic/sg13g2-mixer/issues/30), item 3 is
[#31](https://github.com/2AMLogic/sg13g2-mixer/issues/31).

1. **Re-check the pinned `sg13g2-lna` interface.** The spec copies the LNA's
   rows at `5532789`, notes that LNA `main` has moved, and says the difference
   has not been checked. *Done when:* a committed table under `spec/` compares
   every copied row (band, ports, supply, gain, NF, S22, IIP3 status, IIP3
   protocol, corner box, PDK pin) at the pin and at a named current LNA commit,
   and states "no interface change" or lists each change. Re-pinning itself is
   a separate decision record and is not part of this item.
2. **Settle deferred item D4: which bench mechanics are shared with
   `sg13g2-sat-rx`.** The spec requires one master for tone placement,
   coherent DFT, convergence and slope checks. *Done when:* a decision record
   under `spec/decision-records/` lists the candidate files in `sg13g2-sat-rx`
   at a named commit, marks each band-independent or not, and states whether
   this repo takes stamped copies through `reuse.lock.json` or writes its own,
   with the reason.
3. **LVS device-coverage probe.** #5 warns that `npn13G2` recognition has
   limited LVS on sibling SG13G2 blocks and asks for a coverage check before a
   topology is chosen. *Done when:* `layout/lvs-device-coverage/` holds
   single-device cells for `npn13G2` and the candidate resistor, capacitor and
   MOS devices, the `klt lvs` report for each, and a table of
   recognised / not recognised; each gap is filed generically on
   `klayout-tools` and linked.

## Next

Unblocked once #23 merges (the spec's validation plan, in its own order).

4. **V3: known-answer benches on behavioural elements.** Checks 1, 2 and 5 of
   the spec (ideal multiplier CG within 0.05 dB, hard-switched 2/π, window
   coherence within 0.05 dB), with a cold-start command and a
   `testbench/tb.json` per bench. Needs item 2's outcome for the shared code.
5. **V4: noise and IIP3 known-answer checks.** Check 3 (SSB NF 3.01 dB, DSB
   0 dB within stated statistical error) and check 4 (polynomial IIP3 within
   0.5 dB, slope 3 ± 0.3). *Done when:* both pass, or a decision record states
   the B-NF shortfall and stops that bench, as the spec requires. The measured
   runtime per cell is recorded either way.
6. **Topology selection and first schematic.** A decision record choosing the
   core and the active single-to-differential input stage (R2 target, no
   inductors), then `design/` sources and a derived netlist (T1 item 1). Needs
   items 3 and 4. If the topology uses MOS devices, pinning the OSDI build in
   `sim/toolchain.json` comes first.
7. **V5: first design cell.** B-CG at the typ corner with the per-HBT peak
   `vce`, `vbe`, `ic/Nx` report the spec's model-validity rule demands.

## Later

- **V6, the full PVT box** (T1 items 5 and 8). First question: what does one
  cell cost, measured in V5, and is the box affordable?
- **Mismatch row for R10–R12** (D8, T1 item 6). First question: sample count,
  percentile and confidence, set by a decision record; until then the
  isolation rows cannot be graded pass/fail.
- **Layout, DRC, LVS, power structure, post-layout** (T1 items 2–4, 7, 11).
  First question: does item 3's probe show the chosen devices extract?
- **R14 area re-baseline.** First question: what does the schematic imply?
- **On-chip balun (R2 stretch) and zero-IF I/Q (R9 stretch, D5).** Not before
  the single-IF target closes; the balun also waits on D3.

## Blocked and waiting

- **PR #23 / issue #2** — approved, CI green at review, parked under a
  ratification hold; it needs the operator's merge decision. Everything under
  *Next* waits on it.
- **D1** — LNA IIP3 is unratified in `sg13g2-lna`; the cascade IIP3 stays
  provisional until it is.
- **D2, D7** — R4 and the receive-chain budgets M1–M5 need an operator
  statement of target use; R4 stays a placeholder.
- **D3, D6** — consuming `sg13g2-vco` inductors is an operator decision (no
  `consumes` edge is assumed); image rejection is an open system question.

## Not planned

- The LNA, the LO source and anything after the IF output: this repo states
  requirements on them and stops.
- A noise figure from any method other than B-NF without a decision record;
  the spec forbids substituting a different quantity.
