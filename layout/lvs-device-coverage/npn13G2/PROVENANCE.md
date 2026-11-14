# npn13G2 — provenance

`npn13G2.gds` and `npn13G2.cdl` are **unmodified copies** of the IHP SG13G2 PDK's own
LVS unit testcase. Nothing here was drawn, generated or edited in this repository.

| field | value |
|---|---|
| upstream repo | `IHP-GmbH/IHP-Open-PDK` |
| upstream tag / commit | `v0.3.0` / `5cccb161f7492697cfa52eb14dc03beb00bdca9e` |
| upstream path (layout) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/bjt_devices/layout/npn13G2.gds` |
| upstream path (netlist) | `ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/bjt_devices/netlist/npn13G2.cdl` |
| licence | Apache-2.0 (`SPDX-License-Identifier: Apache-2.0`, stated in the `.cdl` header) |
| copied | 2026-11-14 |
| `npn13G2.gds` sha256 | `cb381d067c1862b0df2a0d7a9303423cf0a3737cddf4dc98d39e32ede8c5853d` |
| `npn13G2.cdl` sha256 | `c0fe68ca5277621084e2051244e2b562188df7155257c75739c280ade77f9f90` |

The commit above is the commit `sim/pdk-artifact.json` pins, so this cell is at the same
PDK revision as the simulation evidence in this repository.

The cell is a **three-device array** (`Q1`/`Q2`/`Q3`, `m=1`/`2`/`4`, `le=900n we=70n`), not
a single device. That is fine for a device-coverage probe and is why the recorded counts
are 3 rather than 1.

## Redistribution

Apache-2.0 permits redistribution of these files. The licence header inside `npn13G2.cdl`
is preserved verbatim; `npn13G2.gds` is a binary stream with no in-file header, so this
note carries its attribution. The repository's own `LICENSE` does not apply to these two
files.

## Derived artefacts in this directory

Produced locally from the two files above; see `../README.md` for the exact commands and
the environment identity.

| file | produced by |
|---|---|
| `npn13G2.extract.json` | `klt extract … --deck sg13g2 --format json` |
| `npn13G2.extracted.spice` | the same run's `-o` netlist output |
| `npn13G2.lvs-klt-deck.json` | `klt lvs`, curated `sg13g2` deck + native comparer |
| `npn13G2.lvs-pdk-runset.json` | `klt lvs`, `engine: klayout-runset` against the PDK's `sg13g2.lvs` |
