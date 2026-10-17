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

<!-- BEGIN LOOM ORCHESTRATION -->
This repository uses [Loom](https://github.com/rjwalters/loom) for AI-powered development orchestration — see the Loom repository for the full guide (roles, labels, worktrees, configuration). When installed, Loom also writes a locally-substituted copy of that guide to `.loom/CLAUDE.md`.

Work is coordinated through `loom:` labels on issues and pull requests, and the same roles run either under `loom-daemon` or by hand in an attended session — daemon mode is optional. Create the labels once with `.loom/scripts/sync-labels.sh` (an install ships `.github/labels.yml` but does not create the labels on the forge). A pull request ready for review carries `loom:review-requested`; Judge reviews it and applies `loom:pr` (approved) or `loom:changes-requested`; Doctor fixes a `loom:changes-requested` pull request and returns it to `loom:review-requested`. Only a `loom:pr` pull request gets merged, and always via this repo's merge script (`.loom/scripts/merge-pr.sh`) — never a raw forge merge command such as `gh pr merge`. Full state machine: `.loom/docs/label-state-machine.md`.
<!-- END LOOM ORCHESTRATION -->
