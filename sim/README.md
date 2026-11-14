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

Pins are the reproducibility contract: any recorded result must trace to
`pdk-artifact.json` and `toolchain.json` at the commit it was produced from.
