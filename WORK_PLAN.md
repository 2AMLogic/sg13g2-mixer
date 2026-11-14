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

_None._

## In Progress

Issues currently being built (`loom:building`).

- **#2**: Draft and ratify the target spec
- **#38**: Trim package.json scripts: a dead worktree:return entry and lint's diverged copy of the gate list
- **#42**: Derive the ci.yml wiring assertion in scripts/test-checks.sh instead of hardcoding a five-name list
- **#43**: PDK integrity gate has no CI-executed negative control: all 5 tests in sim/tools/tests skip without PDK_ROOT

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#44**: fix: point lint at scripts/check-all.sh, drop dead worktree:return entry
- **#45**: test: add PDK-independent fixture control for the verify_pdk gate
- **#48**: test: derive ci.yml wiring assertion from tracked entry points

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#23**: docs(spec): record operator ratification of target spec, mark provisional rows

## Proposed

Issues carrying `loom:curated`.

- **#2**: Draft and ratify the target spec *(curated)*
- **#46**: File record 0002's three sg13g2-sat-rx findings on that repo *(curated)*

## Proposed (Architect / Hermit)

- **#37**: Remove the duplicated R1–R15 spec table and status prose from README.md: a second, ungated copy of the ratified spec *(hermit)*
- **#39**: Remove the ungated content_hash in signoff/manifest.json: a wrong second copy of a hash the envelope already carries *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 0 |
| Important | 1 |
| Ready (`loom:issue`) | 0 |
| In Progress (`loom:building`) | 4 |
| PRs awaiting review | 3 |
| Approved PRs awaiting merge | 1 |
| Curated | 2 |
| Architect / Hermit proposals | 2 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
