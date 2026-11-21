# Roadmap

`sg13g2-mixer` is a SiGe HBT downconversion mixer for the 2.4 GHz ISM band on
IHP SG13G2, whose real deliverable is a reproducible way to measure a
frequency-translating block with transient-only open tools.

Current status: [`WORK_PLAN.md`](WORK_PLAN.md) (generated from label state)
and tracker item [#5](https://github.com/2AMLogic/sg13g2-mixer/issues/5).

## Next

Unblocked once #23 merges (the spec's validation plan, in its own order).

V3 is done (#97): the known-answer benches on behavioural elements shipped —
`sim/ka1-ideal-multiplier/` (check 1), `sim/ka2-switch-mixer/` (check 2),
`sim/ka5-window-coherence/` (check 5), with the shared mechanics in
`sim/bench/` per [record 0002](spec/decision-records/0002-shared-bench-mechanics.md)
and their evidence under `sim/<bench>/records/`.

1. **V4: noise and IIP3 known-answer checks.** Check 3 (SSB NF 3.01 dB, DSB
   0 dB within stated statistical error) and check 4 (polynomial IIP3 within
   0.5 dB, slope 3 ± 0.3). *Done when:* both pass, or a decision record states
   the B-NF shortfall and stops that bench, as the spec requires. The measured
   runtime per cell is recorded either way. Mechanics M5–M7 (record 0002:
   `iip3.py`, `noisefactor.py` stamps and their lock entries) land here.
2. **Topology selection and first schematic.** A decision record choosing the
   core and the active single-to-differential input stage (R2 target, no
   inductors), then `design/` sources and a derived netlist (T1 item 1). The
   LVS device-coverage probe it depends on is done
   (`layout/lvs-device-coverage/`); the benches are item 1. If the topology
   uses MOS devices, pinning the OSDI build in `sim/toolchain.json` comes
   first.
3. **V5: first design cell.** B-CG at the typ corner with the per-HBT peak
   `vce`, `vbe`, `ic/Nx` report the spec's model-validity rule demands.

## Later

- **V6, the full PVT box** (T1 items 5 and 8). First question: what does one
  cell cost, measured in V5, and is the box affordable?
- **Mismatch row for R10–R12** (D8, T1 item 6). First question: sample count,
  percentile and confidence, set by a decision record; until then the
  isolation rows cannot be graded pass/fail.
- **Layout, DRC, LVS, power structure, post-layout** (T1 items 2–4, 7, 11).
  First question — answered 2026-11-20 (issue #98): yes on the runset engine, where
  every probed class including the HBT both extracts and reaches `status: match`
  (`layout/lvs-device-coverage/`); the curated deck still extracts no HBT (#1232,
  declined). Next question: does `klt signoff` accept the runset citation for item 4
  (measured refusal `runset_unrecognised_device`, blocked upstream on
  `2AMLogic/klayout-tools#6902`)?
- **R14 area re-baseline.** First question: what does the schematic imply?
- **On-chip balun (R2 stretch) and zero-IF I/Q (R9 stretch, D5).** Not before
  the single-IF target closes; the balun also waits on D3.

## Not planned

- The LNA, the LO source and anything after the IF output: this repo states
  requirements on them and stops.
- A noise figure from any method other than B-NF without a decision record;
  the spec forbids substituting a different quantity.
