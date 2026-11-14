# layout

No mixer geometry has been drawn yet. See the repo README for scope.

What is here is toolchain evidence, gathered before a topology is chosen:

- [`lvs-device-coverage/`](lvs-device-coverage/) — which SG13G2 devices `klt` can extract
  and LVS-match today, measured on the IHP PDK's own golden test cells (issue #31). The
  headline: the curated `sg13g2` extraction deck models **no bipolar class**, so `npn13G2`
  extracts as zero devices (`2AMLogic/klayout-tools#1232`, closed
  investigated-and-declined); the MOS, MIM-cap and poly-resistor classes a mixer core and
  bias would use are all recognised. Committed `klt extract` / `klt lvs` reports per
  device, with the `klt`, deck and PDK identities each row was read against.
