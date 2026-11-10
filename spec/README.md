# spec

- [`target-spec.md`](target-spec.md) — the target specification (rows R1–R15),
  the `sg13g2-lna` interface at a pinned commit, the cascade arithmetic, the requirements
  trace, validation plan, PVT corner box, and the measurement protocol with
  its known-answer validation.
  Status: RATIFIED by operator on issue #2 (2026-11-10), ratifying PR #7, as
  targets; R4, R9 load, R14 and the LNA-IIP3-dependent cascade values are
  provisional.
- [`decision-records/`](decision-records/) — numbered decision records.
  - [0001 — target spec ratification](decision-records/0001-target-spec-ratification.md)

Spec changes go through a decision record. Agents do not relax a ratified row to
make a result pass.
