# cap_cmim — provenance

`cap_cmim.gds` and `cap_cmim.cdl` are **unmodified copies** of the IHP SG13G2 PDK's own
LVS unit testcase. Nothing here was drawn, generated or edited in this repository.

| field | value |
|---|---|
| upstream repo | `IHP-GmbH/IHP-Open-PDK` |
| upstream tag / commit | `v0.3.0` / `5cccb161f7492697cfa52eb14dc03beb00bdca9e` |
| upstream path (layout) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/cap_devices/layout/cap_cmim.gds` |
| upstream path (netlist) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/cap_devices/netlist/cap_cmim.cdl` |
| licence | Apache-2.0 (`SPDX-License-Identifier: Apache-2.0`, stated in the `.cdl` header) |
| copied | 2026-11-14 |
| `cap_cmim.gds` sha256 | `80cb907a35f1098d59864a1d227045ca020855f42af5f2af3a1ee84385c24749` |
| `cap_cmim.cdl` sha256 | `dfa634616522c278e6a923797a767249ec3304e287f85f8e1878d0d39dbcdeba` |

The commit above is the commit `sim/pdk-artifact.json` pins, so this cell is at the same
PDK revision as the simulation evidence in this repository.

The cell is a **multi-device array** (69 instances: `C0`…`C2` plus `C_pattern_*`, across a
spread of `w`/`l`/`m`), not a single device. That is fine for a device-coverage probe and
is why the recorded counts are in the tens rather than 1.

## Redistribution

Apache-2.0 permits redistribution of these files. The licence header inside
`cap_cmim.cdl` is preserved verbatim; `cap_cmim.gds` is a binary stream with no in-file
header, so this note carries its attribution. The repository's own `LICENSE` does not
apply to these two files.

## Derived artefacts in this directory

Produced locally from the two files above; see `../README.md` for the exact commands and
the environment identity.

| file | produced by |
|---|---|
| `cap_cmim.extract.json` | `klt extract … --deck sg13g2 --format json` |
| `cap_cmim.extracted.spice` | the same run's `-o` netlist output |
| `cap_cmim.lvs-klt-deck.json` | `klt lvs`, curated `sg13g2` deck + native comparer (needs `reference.form: "subckt-call"`) |
| `cap_cmim.lvs-pdk-runset.json` | `klt lvs`, `engine: klayout-runset` against the PDK's `sg13g2.lvs` |
