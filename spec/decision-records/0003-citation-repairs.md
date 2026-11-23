# 0003 — Value-preserving citation repairs in `target-spec.md`

- **Status**: PROPOSED. This record states one rule — what a
  value-preserving citation repair is — and applies it to two citation
  repairs in [`../target-spec.md`](../target-spec.md) (one stale pointer,
  one ambiguous cross-repo citation). It ratifies no row
  of `target-spec.md`, changes no protocol number, no row R1–R15, no
  tolerance and no PVT corner. Approving the PR that carries this record is
  not ratification of the spec.
- **Issue**: [#47](https://github.com/2AMLogic/sg13g2-mixer/issues/47)
  (consolidating [#40](https://github.com/2AMLogic/sg13g2-mixer/issues/40))
- **Date**: 2026-11-15
- **Decided by**: Builder agent, issue #47
- **Supersedes**: two sentences in `../target-spec.md`, quoted with their
  replacements under "The repairs" below. It does not edit record
  [`0001`](0001-target-spec-ratification.md) (a decision record is a dated
  artifact; supersession is recorded here) and does not change record
  [`0002`](0002-shared-bench-mechanics.md) (it applies what 0002 already
  decided).

## The rule

A correction that changes **only a pointer** — where a decision or a value
already lives — and no row value, no protocol number, no tolerance and no
PVT corner is recorded here and applied. It is not a relaxation of a
ratified row: `CLAUDE.md`'s rule that "agents do not relax the ratified
spec to make results pass" is about values and tolerances, not about which
file a citation names. The spec's history still shows why the citation
moved, because this record is that history.

## Why now

- **The D4 deferral lost its owner.** `../target-spec.md` §"Measurement
  protocol" said the band-independence question "is decided when #3 builds
  the bench". [#3](https://github.com/2AMLogic/sg13g2-mixer/issues/3)
  closed on 2026-10-17T21:59:22Z having pinned the PDK and committed a
  smoke simulation — it built no bench. Meanwhile record
  [`0002`](0002-shared-bench-mechanics.md) (PR #35, merged 2026-11-14)
  decided D4 ahead of the bench issue, enumerating mechanics M1–M8 with an
  owner each. Its §Consequences flagged the sentence as "slightly stale"
  and left the correction "to be folded into the next record that touches
  the measurement protocol". No such record is pending; waiting was the
  ownerless state this record ends.
- **The PDK-pin row's bare filename was ambiguous.** The ratified PDK-pin
  row cites `sim/pdk.json` "there" — the LNA repo at the pinned commit,
  where that file carries the release tag `v0.3.0` (its blob is unchanged
  between the two LNA commits, per
  [`lna-interface-recheck.md`](../lna-interface-recheck.md), §"Evidence").
  The commit SHA is not in that file; it is recorded in
  `lna-interface-recheck.md` and this repo's `sim/pdk-artifact.json`.
  [#40](https://github.com/2AMLogic/sg13g2-mixer/issues/40) read the bare
  filename as a path in this repo, where — after
  [#33](https://github.com/2AMLogic/sg13g2-mixer/issues/33) — `sim/pdk.json`
  indeed carries no pin fields at all (the enforced local pin lives in
  `sim/pdk-artifact.json`, the only file `sim/tools/verify_pdk.py` reads,
  whose `upstream.tag` / `upstream.commit` equal the values the row
  quotes). The defect is the terseness of "there", not a stale pointer;
  the repair is a disambiguation, not a file swap. Filed as #40 and
  consolidated into #47: same row, same question — does a citation repair
  need its own record? This record answers once for both.

## The repairs

Both applied to `../target-spec.md` in the PR carrying this record.

1. **PDK-pin row** — the file citation only; the pinned tag and commit are
   untouched. The table's source line (under "Interface to
   `sg13g2-lna`") reads files in the LNA repo at commit `5532789…`, so
   bare filenames in that column are LNA-repo-relative; the
   disambiguation makes that explicit and stays consistent with
   [`lna-interface-recheck.md`](../lna-interface-recheck.md) ("recorded in
   `sim/pdk.json` (LNA repo)"). The LNA file carries the tag (`v0.3.0`)
   only, not the commit SHA (`5cccb161…`, the `v0.3.0` tag commit), which
   `lna-interface-recheck.md` records; this repo's
   `sim/pdk-artifact.json` `upstream.tag` / `upstream.commit` equal those
   values — one fact, several copies; each citation now names the file
   that holds the part it points at.

   - Before: `` (`sim/pdk.json` there) ``
   - After: `` (tag `v0.3.0` recorded in `sim/pdk.json` in the LNA repo at the pinned commit; tag commit SHA recorded in `lna-interface-recheck.md` and this repo's `sim/pdk-artifact.json`) ``

2. **D4 sentence, §"Measurement protocol"** — the paragraph's preceding
   three sentences (one master; stamped copy tracked in `reuse.lock.json`;
   reading methodology is not copying code) are unchanged.

   - Before: "Which of its mechanics are band-independent is decided when
     #3 builds the bench (decision record, Deferred D4)."
   - After: "Which of its mechanics are band-independent is decided in
     decision record [0002](0002-shared-bench-mechanics.md) (was Deferred
     D4)."

## Consequences

- **A rule exists for the next stale citation.** A future value-preserving
  pointer repair applies it under the next numbered record; it does not
  need a fresh ruling on whether the repair is allowed.
- **The four past-tense `#3` provenance references stay.** References that
  record what #3 already did (it committed the pin; its working document;
  its closed status) are accurate history, not deferrals, and are not
  touched by this rule.
- **Record 0001's stale D4 deferral stays.** Supersession belongs in the
  superseding record — 0002's own `Supersedes` bullet already names 0001's
  D4 deferral — not in a rewrite of a dated artifact.
