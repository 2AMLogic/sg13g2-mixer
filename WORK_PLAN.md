# Work Plan

Generated from GitHub label state by the Guide triage role. Everything between the markers is overwritten.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#23**: docs(spec): record operator ratification of target spec, mark provisional rows

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

_None._

## Important

`loom:important`; taken before unlabelled work.

- **#2**: Draft and ratify the target spec

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#46**: File record 0002's three sg13g2-sat-rx findings on that repo
- **#54**: Refresh tracker #5's body: its T1 checklist predates PRs #6/#8 and now reads false

## In Progress

Issues currently being built (`loom:building`).

- **#2**: Draft and ratify the target spec
- **#39**: Gate the item-10 manifest hash binding in CI, and label what it anchors
- **#42**: Derive the ci.yml wiring assertion in scripts/test-checks.sh instead of hardcoding a five-name list
- **#47**: spec/target-spec.md still defers D4 to closed issue #3; record 0002 decided it
- **#50**: verify_pdk CI control cannot catch a hash-algorithm swap or two _target() parser branches

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#58**: test: close the three mutation gaps in the verify_pdk fixture control

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#23**: docs(spec): record operator ratification of target spec, mark provisional rows
- **#48**: test: derive ci.yml wiring assertion from tracked entry points
- **#57**: ci: gate the item-10 manifest hash binding, label the pin, document signoff regeneration

## Proposed

Issues carrying `loom:curated`.

- **#2**: Draft and ratify the target spec *(curated)*
- **#39**: Gate the item-10 manifest hash binding in CI, and label what it anchors *(curated)*
- **#46**: File record 0002's three sg13g2-sat-rx findings on that repo *(curated)*
- **#47**: spec/target-spec.md still defers D4 to closed issue #3; record 0002 decided it *(curated)*
- **#50**: verify_pdk CI control cannot catch a hash-algorithm swap or two _target() parser branches *(curated)*
- **#54**: Refresh tracker #5's body: its T1 checklist predates PRs #6/#8 and now reads false *(curated)*

## Proposed (Architect / Hermit)

- **#37**: Remove the duplicated R1–R15 spec table and status prose from README.md: a second, ungated copy of the ratified spec *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 0 |
| Important | 1 |
| Ready (`loom:issue`) | 2 |
| In Progress (`loom:building`) | 5 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 3 |
| Curated | 6 |
| Architect / Hermit proposals | 1 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
