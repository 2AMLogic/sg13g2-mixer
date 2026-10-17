# sg13g2-mixer — agent instructions

Open-source canary block: a SiGe HBT downconversion mixer on IHP SG13G2, a
130 nm SiGe BiCMOS open PDK, the companion to `sg13g2-lna`, designed and
verified by AI agents.

- **PDK**: IHP SG13G2 (open PDK, IHP-GmbH/IHP-Open-PDK). Open-source flow:
  xschem + ngspice for design/sim, klayout-tools (`klt`) for layout, DRC and
  LVS. Pin the PDK release and build the OSDI models the way `sg13g2-lna`
  documents.
- **Measuring a mixer with open tools is the risk.** ngspice has no
  periodic steady-state analysis, so conversion gain, SSB noise figure,
  IIP3 and isolation all come from transient benches. Every number states
  its LO drive, the FFT length and window, the settling time discarded,
  SSB or DSB, and the port impedances. Validate the bench on a reference
  whose answer is known (an ideal multiplier, a textbook passive mixer)
  before trusting it on the design. Stay inside the HBT model card's
  validity window, and state when a corner leaves it.
- **Scope discipline.** The LNA comes from `sg13g2-lna`: take its ratified
  band, 50 Ω port convention, supply and output behaviour as the interface,
  cite it at a named commit, and do not redesign it. Findings that bear on
  the LNA (an output-match or linearity requirement it does not meet) are
  filed on `sg13g2-lna`. The LO source is not designed here; specify the
  drive level, waveform and phase noise this block requires of it and stop.
  `sg13g2-sat-rx`'s mixer topology study is a different block at Ka band;
  read its methodology, and if band-independent bench code is shared, it has
  one master and stamped copies (`reuse.lock.json`), not two designs.
- **Friction protocol (the canary's job)**: every time klayout-tools is
  awkward, missing a capability, or wrong for what you need, file an issue at
  `2AMLogic/klayout-tools` describing the tool gap generically — that tracker
  is scoped to the tool, so keep design-specific detail out of it and describe
  the gap, not the design.
- **Verification is the product**: no claim without a testbench. PVT corners
  on every recorded result; `sim/` results are append-only evidence. Every
  simulated figure is labelled as simulated, with its corner and testbench.
- Spec changes go through `spec/` with a decision record; agents do not relax
  the ratified spec to make results pass.
- **A single low IF is the target.** Zero-IF I/Q is a stretch; do not let it
  drive the core architecture before the single-IF target closes.
