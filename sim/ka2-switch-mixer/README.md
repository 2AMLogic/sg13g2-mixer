# ka2-switch-mixer

Known-answer bench, spec check 2 (validation step V3): a double-balanced
ideal-switch mixer (switch resistance → 0) driven by a ±1 square-wave LO
(1 ps edges) delivers an IF voltage of exactly 2/π times the RF voltage.
The voltage ratio is graded **within the 0.1 dB convergence tolerance**; a
power-gain diagnostic (same 50 Ω source / 1 kΩ load convention) is recorded
for context only, before any comparison with row R5.

**Simulated**, behavioural elements only (B-source, pulse source, resistors,
capacitor; no semiconductor models, no PDK), single corner. Protocol: 12.5 ps
step (6.25 ps halved leg), 2^19-point rectangular window with coherent tones,
≥ 2 µs settling discarded, following-window and step-halving agreement
< 0.1 dB (mechanic M4). RF: −40 dBm available from 50 Ω; load: 1 kΩ ‖ 2 pF.
LO edges are not on the sample grid; edge-time quantisation is second order
on the fundamental and is what the step-halving leg bounds.

## Cold start (from a clean checkout)

No PDK needed (behavioural deck). Build the pinned ngspice 46
(`sim/toolchain.json`) exactly as `sim/smoke-hbt/README.md` step 2 documents,
worktree-locally (that step runs on its own, without step 1), then:

```bash
NGSPICE="$PWD/.tools/ngspice-46/bin/ngspice" sim/ka2-switch-mixer/run.sh
```

Two sequential `ngspice -b` legs (12.5 ps, 6.25 ps) — standard library only,
no numpy. The gate (M2 pre-flight, M1 two-half agreement, M4 convergence,
2/π delta) runs before the record is written; exit 0 is a pass. The pinned
ngspice major is checked before anything runs. Scratch lands in
`.tools/ka2-work/` (gitignored).

To inspect the deck without running anything:
`python3 sim/ka2-switch-mixer/bench.py --dump-deck`.
