# Work Plan

Generated from GitHub label state by the Guide triage role. Everything between the markers is overwritten.

<!-- guide:plan-body:start -->
_Generated: 2026-11-21T00:16:00Z (snapshot; compare against live labels)_
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#23**: docs(spec): record operator ratification of target spec, mark provisional rows
- **#56**: spec: repair two stale citations in target-spec.md under record 0003

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

_None._

## Important

`loom:important`; taken before unlabelled work.

- **#2**: Draft and ratify the target spec

## Ready

Human-approved issues (`loom:issue`) ready for implementation — excluding held (`loom:blocked`/`loom:operator`/`loom:frozen`), `loom:building`, and issues closed by an open `loom:pr` PR (listed under Approved).

_None._

## In Progress

Issues currently being built (`loom:building`).

- **#97**: V3: known-answer benches 1, 2 and 5 on behavioural elements, with tb.json and a cold-start command per bench (T1 item 9)
- **#98**: Re-run the lvs-device-coverage probe at current klt: does npn13G2 reach status: match on the PDK-runset route?

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#99**: layout: npn13G2 reaches status: match on the PDK-runset engine at current klt

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#23**: docs(spec): record operator ratification of target spec, mark provisional rows — closes #2
- **#56**: spec: repair two stale citations in target-spec.md under record 0003 — closes #47

## Proposed

Issues carrying `loom:curated`.

- **#2**: Draft and ratify the target spec *(curated)*
- **#47**: spec/target-spec.md still defers D4 to closed issue #3; record 0002 decided it *(curated)*
- **#97**: V3: known-answer benches 1, 2 and 5 on behavioural elements, with tb.json and a cold-start command per bench (T1 item 9) *(curated)*
- **#98**: Re-run the lvs-device-coverage probe at current klt: does npn13G2 reach status: match on the PDK-runset route? *(curated)*

## Proposed (Architect / Hermit)

- **#37**: Remove the duplicated R1–R15 spec table and status prose from README.md: a second, ungated copy of the ratified spec *(hermit)* *(held)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Very important | 0 |
| Important | 1 |
| Ready (`loom:issue`, net of holds/building/merge-pending) | 0 |
| In Progress (`loom:building`) | 2 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 2 |
| Curated | 4 |
| Architect / Hermit proposals | 1 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
