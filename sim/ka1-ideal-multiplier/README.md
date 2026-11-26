# ka1-ideal-multiplier

Known-answer bench, spec check 1 (validation step V3): an ideal behavioural
multiplier `v(if) = k·V(rf)·V(lo)` with a sinusoidal LO of peak amplitude A
has an IF amplitude of exactly k·A/2 times the RF amplitude. Graded as B-CG
(IF-tone power in the stated load over RF available power from the 50 Ω
source, SSB): **within 0.05 dB** of the closed form.

**Simulated**, behavioural elements only (B-source, resistors, capacitor; no
semiconductor models, no PDK), single corner. Protocol: 12.5 ps step
(6.25 ps halved leg), 2^19-point rectangular window with coherent tones,
≥ 2 µs settling discarded, following-window and step-halving agreement
< 0.1 dB (mechanic M4). LO drive: sinusoid, 0.2236 V peak; RF: −40 dBm
available from 50 Ω; load: 1 kΩ ‖ 2 pF. The record under `records/` states
every number with its tolerance and wall-clock.

## Cold start (from a clean checkout)

No PDK needed (behavioural deck). Build the pinned ngspice 46
(`sim/toolchain.json`) exactly as `sim/smoke-hbt/README.md` step 2 documents,
worktree-locally:

```bash
mkdir -p .tools/dl .tools/src
curl -L -o .tools/dl/ngspice-46.tar.gz "$(python3 -c "import json;print(json.load(open('sim/toolchain.json'))['ngspice']['source_url'])")"
echo "a0d1699af1940b06649276dcd6ff5a566c8c0cad01b2f7b5e99dedbb4d64c19b  .tools/dl/ngspice-46.tar.gz" | sha256sum -c
tar -xzf .tools/dl/ngspice-46.tar.gz -C .tools/src
(cd .tools/src/ngspice-46 && ./configure --prefix="$PWD/../../ngspice-46" --with-x=no --with-ngshared=no \
   && make -j2 && make install)

NGSPICE="$PWD/.tools/ngspice-46/bin/ngspice" sim/ka1-ideal-multiplier/run.sh
```

Two sequential `ngspice -b` legs (12.5 ps, 6.25 ps) — standard library only,
no numpy. The gate (M2 pre-flight, M1 two-half agreement, M4 convergence,
0.05 dB closed-form delta) runs before the record is written; exit 0 is a
pass. The pinned ngspice major is checked before anything runs. Scratch
(decks, samples, logs) lands in `.tools/ka1-work/` (gitignored).

To inspect the deck without running anything:
`python3 sim/ka1-ideal-multiplier/bench.py --dump-deck`.
