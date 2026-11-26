# Work Plan

Generated from GitHub label state by the Guide triage role. Everything between the markers is overwritten.

<!-- guide:plan-body:start -->
_Generated: 2026-11-26T18:09:09Z (snapshot; compare against live labels)_
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#56**: spec: repair two stale citations in target-spec.md under record 0003

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

_None._

## Important

`loom:important`; taken before unlabelled work.

_None._

## Ready

Human-approved issues (`loom:issue`) ready for implementation — excluding held (`loom:blocked`/`loom:operator`/`loom:frozen`), `loom:building`, and issues closed by an open `loom:pr` PR (listed under Approved).

- **#130**: CI does not assert item 9's manifest binding (signoff-item9 is drift-only)

## In Progress

Issues currently being built (`loom:building`).

- **#120**: Trim unchecked toolchain, protocol and mechanics duplicates from sim/*/testbench/tb.json
- **#127**: Derive V3 stimulus frequencies and FFT bins from one tone plan

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#56**: spec: repair two stale citations in target-spec.md under record 0003 — closes #47
- **#126**: refactor(sim): trim the V3 tb.json to identity and entry points — closes #120

## Proposed

Issues carrying `loom:curated`.

- **#47**: spec/target-spec.md still defers D4 to closed issue #3; record 0002 decided it *(curated)*
- **#130**: CI does not assert item 9's manifest binding (signoff-item9 is drift-only) *(curated)*

## Proposed (Architect / Hermit)

- **#37**: Remove the duplicated R1–R15 spec table and status prose from README.md: a second, ungated copy of the ratified spec *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 0 |
| Important | 0 |
| Ready (`loom:issue`, net of holds/building/merge-pending) | 1 |
| In Progress (`loom:building`) | 2 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 2 |
| Curated | 2 |
| Architect / Hermit proposals | 1 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
