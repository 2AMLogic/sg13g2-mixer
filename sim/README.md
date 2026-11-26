# sim

Simulation tooling and benches. Nothing here states a spec-row result; the
spec is owned by `spec/` (issue #2).

| Path | What |
|---|---|
| `pdk.json` | What this block uses from the PDK: fetch method, install layout, devices exercised so far. Carries no pin — it is mutable and no gate reads it |
| `pdk-artifact.json` | The enforced pin, and the only copy of it: upstream release tag + commit, install subtree, per-file sha256 of the `cornerHBT.lib` closure |
| `toolchain.json` | ngspice 46 source tarball + sha256, Python floor (3.10) |
| `tools/verify_pdk.py` | Integrity gate: refuses on any mismatch before a simulator starts |
| `tools/tests/` | Negative control: tampered / missing / unlisted model files are rejected |
| `smoke-hbt/` | One `npn13G2` DC op + short transient; cold-start steps in its README |
| `bench/` | Shared known-answer bench mechanics (M1–M4 of [record 0002](../spec/decision-records/0002-shared-bench-mechanics.md)): `lib/coherent.py` and `lib/convergence.py` written here, `lib/coherence.py`, `lib/psd.py`, `lib/nfcommon.py` stamped copies tracked in `reuse.lock.json`; plus the shared runner and the numpy venv helper |
| `ka1-ideal-multiplier/` | V3 check 1: ideal behavioural multiplier, B-CG within 0.05 dB; record + cold start in its README |
| `ka2-switch-mixer/` | V3 check 2: hard-switched ideal mixer, IF = 2/π × RF within 0.1 dB |
| `ka5-window-coherence/` | V3 check 5: one coherent tone, rectangular FFT / Hann FFT / independent DFT within 0.05 dB |

Pins are the reproducibility contract: any recorded result must trace to
`pdk-artifact.json` and `toolchain.json` at the commit it was produced from.
