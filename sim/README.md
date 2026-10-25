# sim

Simulation tooling and benches. Nothing here states a spec-row result; the
spec is owned by `spec/` (issue #2).

| Path | What |
|---|---|
| `pdk.json` | Greppable fact sheet for the pinned PDK (IHP-Open-PDK v0.3.0, commit `5cccb161f7492697cfa52eb14dc03beb00bdca9e`) |
| `pdk-artifact.json` | The enforced pin: per-file sha256 of the `cornerHBT.lib` closure |
| `toolchain.json` | ngspice 46 source tarball + sha256, Python floor (3.10) |
| `tools/verify_pdk.py` | Integrity gate: refuses on any mismatch before a simulator starts |
| `tools/tests/` | Negative control: tampered / missing / unlisted model files are rejected |
| `smoke-hbt/` | One `npn13G2` DC op + short transient; cold-start steps in its README |

Pins are the reproducibility contract: any recorded result must trace to
`pdk-artifact.json` and `toolchain.json` at the commit it was produced from.
