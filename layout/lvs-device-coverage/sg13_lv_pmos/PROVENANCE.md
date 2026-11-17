# sg13_lv_pmos — provenance

`sg13_lv_pmos.gds` and `sg13_lv_pmos.cdl` are **unmodified copies** of the IHP SG13G2
PDK's own LVS unit testcase. Nothing here was drawn, generated or edited in this
repository.

| field | value |
|---|---|
| upstream repo | `IHP-GmbH/IHP-Open-PDK` |
| upstream tag / commit | `v0.3.0` / `5cccb161f7492697cfa52eb14dc03beb00bdca9e` |
| upstream path (layout) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/mos_devices/layout/sg13_lv_pmos.gds` |
| upstream path (netlist) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/mos_devices/netlist/sg13_lv_pmos.cdl` |
| licence | Apache-2.0 (`SPDX-License-Identifier: Apache-2.0`, stated in the `.cdl` header) |
| copied | 2026-11-14 |
| `sg13_lv_pmos.gds` sha256 | `1c19e3f423e0efc5f2ed9ff0090525b9fb9dbe05c1aa41c6dacf069b5440ac9c` |
| `sg13_lv_pmos.cdl` sha256 | `e69efbd7352ef2957124f97a447fb8f6277534087601ecd61e9fdbc35cb067aa` |

The commit above is the commit `sim/pdk-artifact.json` pins, so this cell is at the same
PDK revision as the simulation evidence in this repository.

The cell is a **multi-device array** (15 instances: `MP1`…`MP8` plus `M_pattern_*`, across
a spread of `w`/`l`/`ng`), not a single device. That is fine for a device-coverage probe
and is why the recorded counts are in the tens rather than 1.

## Redistribution

Apache-2.0 permits redistribution of these files. The licence header inside
`sg13_lv_pmos.cdl` is preserved verbatim; `sg13_lv_pmos.gds` is a binary stream with no
in-file header, so this note carries its attribution. The repository's own `LICENSE` does
not apply to these two files.
