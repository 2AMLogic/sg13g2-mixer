# spec

- [`target-spec.md`](target-spec.md) — the target specification (rows R1–R15),
  the `sg13g2-lna` interface at a pinned commit, the cascade arithmetic, the requirements
  trace, validation plan, PVT corner box, and the measurement protocol with
  its known-answer validation.
  Status: PROPOSED, not ratified; under requirements review. Approving the PR
  is not ratification.
- [`lna-interface-recheck.md`](lna-interface-recheck.md) — re-check of the pinned
  `sg13g2-lna` interface rows against a later LNA `main` commit, with the git
  object evidence, the "no interface row changed" result, and the answer to
  deferred item D1 (the LNA IIP3 row is still unratified). A record of a
  comparison; it makes no re-pin decision.
- [`decision-records/`](decision-records/) — numbered decision records.
  - [0001 — target spec ratification](decision-records/0001-target-spec-ratification.md)

Spec changes go through a decision record. Agents do not relax a ratified row to
make a result pass.
