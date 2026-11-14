# rppd — provenance

`rppd.gds` and `rppd.cdl` are **unmodified copies** of the IHP SG13G2 PDK's own LVS unit
testcase. Nothing here was drawn, generated or edited in this repository.

| field | value |
|---|---|
| upstream repo | `IHP-GmbH/IHP-Open-PDK` |
| upstream tag / commit | `v0.3.0` / `5cccb161f7492697cfa52eb14dc03beb00bdca9e` |
| upstream path (layout) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/res_devices/layout/rppd.gds` |
| upstream path (netlist) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/res_devices/netlist/rppd.cdl` |
| licence | Apache-2.0 (`SPDX-License-Identifier: Apache-2.0`, stated in the `.cdl` header) |
| copied | 2026-11-14 |
| `rppd.gds` sha256 | `6202e9ee7192238b0bed74bfa94d7d04fbeddddf41a85518d7bcb6aabe6e177b` |
| `rppd.cdl` sha256 | `d3932f9ffaba1fac5a745f2a1b25dd9e1f4f405c4092a53fedeb85e3fffbc02c` |

The commit above is the commit `sim/pdk-artifact.json` pins, so this cell is at the same
PDK revision as the simulation evidence in this repository.

The cell is a **multi-device array** (84 instances: `Rp1`…`Rp5` plus `R_pattern_*`, across
a spread of `w`/`l`/`b`/`ps`), not a single device. That is fine for a device-coverage
probe and is why the recorded counts are in the tens rather than 1. Note the reference
netlist deliberately mixes two spellings of the same device — a valued card with
`$SUB=`/`$[rppd]` and a valueless `n1 n2 sub rppd w= l=` card.

## Redistribution

Apache-2.0 permits redistribution of these files. The licence header inside `rppd.cdl` is
preserved verbatim; `rppd.gds` is a binary stream with no in-file header, so this note
carries its attribution. The repository's own `LICENSE` does not apply to these two files.

## Derived artefacts in this directory

Produced locally from the two files above; see `../README.md` for the exact commands and
the environment identity.

| file | produced by |
|---|---|
| `rppd.extract.json` | `klt extract … --deck sg13g2 --format json` |
| `rppd.extracted.spice` | the same run's `-o` netlist output |
| `rppd.lvs-klt-deck.error.json` | `klt lvs` with the curated `sg13g2` deck — the **error envelope**, kept as evidence; the reference cannot be read at all (`2AMLogic/klayout-tools#5665`) |
| `rppd.lvs-pdk-runset.json` | `klt lvs`, `engine: klayout-runset` against the PDK's `sg13g2.lvs` |
