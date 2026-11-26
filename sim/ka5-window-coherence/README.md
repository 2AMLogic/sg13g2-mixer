# ka5-window-coherence

Known-answer bench, spec check 5 (validation step V3): one coherent tone at
f_IF (bin 64) must read the same power on the **rectangular FFT**
(ngspice's own `fft`, the deck half of mechanic M1), the **Hann FFT**
(the stamped PSD stack, mechanic M3: one-sided periodogram with the
window-power correction, integrated over a band around the tone with
`band_power`) and the **independent DFT** (the Python half of M1) —
**within 0.05 dB**. This bench is where M1's two halves are shown to agree;
every other bench inherits that agreement.

**Simulated**, behavioural elements only (ideal source, resistors, capacitor;
no semiconductor models, no PDK), single corner. Protocol: 12.5 ps step
(6.25 ps halved leg), 2^19-point window, ≥ 2 µs settling discarded,
following-window and step-halving agreement < 0.1 dB (mechanic M4).

## Cold start (from a clean checkout)

No PDK needed (behavioural deck). Build the pinned ngspice 46
(`sim/toolchain.json`) exactly as `sim/smoke-hbt/README.md` step 2 documents,
worktree-locally (that step runs on its own, without step 1); this bench also
needs numpy (mechanic M3), installed into a worktree-local venv by
`sim/bench/mkenv.sh` — never a host-wide install:

```bash
NGSPICE="$PWD/.tools/ngspice-46/bin/ngspice" sim/ka5-window-coherence/run.sh
```

Two sequential `ngspice -b` legs (12.5 ps, 6.25 ps), then the Hann/PSD
post-processing in the venv. The gate (M2 pre-flight, three-reading spread,
M1 two-half agreement, M4 convergence) runs before the record is written;
exit 0 is a pass. The pinned ngspice major is checked before anything runs.
Scratch lands in `.tools/ka5-work/` (gitignored).

To inspect the deck without running anything:
`python3 sim/ka5-window-coherence/bench.py --dump-deck`.
