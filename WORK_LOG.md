# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide triage role.

### 2026-11-26

- **Issue #134** (closed): Use the calculated RF drive amplitude in the KA1 and KA2 sine sources
- **PR #135**: fix(sim): drive both mixer RF sources from the calculated peak voltage
- **Issue #120** (closed): Trim unchecked toolchain, protocol and mechanics duplicates from sim/*/testbench/tb.json
- **PR #126**: refactor(sim): trim the V3 tb.json to identity and entry points
- **Issue #130** (closed): CI does not assert item 9's manifest binding (signoff-item9 is drift-only)
- **PR #133**: ci: assert item 9's manifest binding in signoff-item9
- **Issue #127** (closed): Derive V3 stimulus frequencies and FFT bins from one tone plan
- **PR #132**: refactor(sim): derive V3 deck tones and FFT bins from one runner plan
- **PR #129**: ci: gate the item-9 signoff envelope for drift
- **PR #123**: refactor(sim): read V3 deck source and load values from the shared runner constants
- **Issue #125** (closed): CI has no drift check for the item 9 envelope: a stale signoff/testbenches/envelope.json stays green
- **Issue #122** (closed): Use shared source and load values in the V3 ngspice decks
- **PR #121**: refactor(sim): read V3 record M4 limits from the convergence grader
- **PR #119**: docs(sim): single ngspice build recipe, pin read from toolchain.json
- **Issue #112** (closed): Read V3 record tolerances from the M4 convergence grader
- **Issue #118** (closed): Deduplicate the ngspice build recipe and hardcoded SHA-256 across the sim READMEs
- **PR #115**: test: share the synthetic bench fixture and isolate its ngspice pin
- **Issue #114** (closed): Share the V3 bench test fixture so measurement tests survive an ngspice pin bump

### 2026-11-24

- **PR #106**: fix: check the gate self-test fixture root before any fixture git command
- **Issue #102** (closed): Use one checked temporary directory for gate self-test fixtures

### 2026-11-23

- **PR #109**: refactor(sim): fold the shared V3 bench scaffold into runner.py
- **PR #107**: refactor(sim): read the ngspice major pin from sim/toolchain.json in the shared runner
- **PR #23**: docs(spec): record operator ratification of target spec, mark provisional rows
- **Issue #108** (closed): Fold the repeated V3 bench main() scaffold into runner.py
- **Issue #104** (closed): Read the ngspice major from the toolchain pin in all three V3 benches
- **Issue #2** (closed): Draft and ratify the target spec

### 2026-11-21

- **PR #105**: fix(sim): write bench samples by basename so spaced scratch paths work
- **PR #100**: feat(sim): add V3 known-answer benches with stamped bench mechanics
- **PR #99**: layout: npn13G2 reaches status: match on the PDK-runset engine at current klt
- **Issue #103** (closed): Allow V3 bench scratch directories with spaces
- **Issue #98** (closed): Re-run the lvs-device-coverage probe at current klt: does npn13G2 reach status: match on the PDK-runset route?
- **Issue #97** (closed): V3: known-answer benches 1, 2 and 5 on behavioural elements, with tb.json and a cold-start command per bench (T1 item 9)

### 2026-11-19

- **PR #95**: docs: gate the tracker refresh on a final read before its PATCH
- **Issue #94** (closed): Tracker #5 refresh has no cross-host mutual exclusion (duplicate audit comment)
- **PR #93**: docs: give Guide a standing procedure for keeping tracker #5 current
- **Issue #91** (closed): Assign Guide responsibility for keeping T1 tracker #5 current
- **Issue #54** (closed): Refresh tracker #5's body: its T1 checklist predates PRs #6/#8 and now reads false

### 2026-11-18

- **PR #89**: ci: run the required checks on merge_group and fail the records gate closed without a base
- **Issue #87** (closed): Merge queue: add the merge_group trigger and adapt the PR-metadata gates
- **PR #85**: test: assert gate failure propagates through check-all.sh; fix the CI-job-order wording
- **Issue #83** (closed): check-all.sh: add a control that a failing gate exits nonzero, and fix the "CI job order" wording
- **PR #82**: ci: single-source the gate list in check-all.sh, drop the wiring-drift test
- **Issue #81** (closed): Single-source the CI gate: ci.yml jobs call scripts/check-all.sh, drop the wiring-drift assertion

### 2026-11-17

- **PR #77**: chore(loom): resync installed Loom to v0.19.1306
- **Issue #46** (closed): File record 0002's three sg13g2-sat-rx findings on that repo

### 2026-11-16

- **PR #73**: chore(loom): resync installed Loom to v0.19.1302

### 2026-11-15

- **PR #69**: docs: drop duplicated derived-artefacts tables from lvs-device-coverage PROVENANCE.md
- **Issue #67** (closed): Trim the five duplicated 'Derived artefacts' tables from lvs-device-coverage PROVENANCE.md files
- **PR #68**: ci: item-10 conjunct-equivalence tripwire for klt pin bumps
- **Issue #65** (closed): item-10 control harness does not pin which conjunct of the assertion does the rejecting
- **PR #66**: fix: select assert_invoked wiring needles by path form, not basename prefix
- **Issue #63** (closed): assert_invoked matches a basename, so a nested scripts/ gate can pass on a sibling's wiring
- **PR #62**: ci: negative and positive controls for the item-10 manifest-binding gate
- **Issue #59** (closed): The new item-10 manifest-binding CI gate has no re-runnable negative control
- **PR #61**: test: assert check-all.sh covers every derived scripts/ entry point
- **Issue #55** (closed): Two unchecked copies of the gate list remain after #42: check-all.sh and signoff inventory.json
- **PR #58**: test: close the three mutation gaps in the verify_pdk fixture control
- **Issue #50** (closed): verify_pdk CI control cannot catch a hash-algorithm swap or two _target() parser branches
- **PR #57**: ci: gate the item-10 manifest hash binding, label the pin, document signoff regeneration
- **Issue #39** (closed): Gate the item-10 manifest hash binding in CI, and label what it anchors
- **PR #48**: test: derive ci.yml wiring assertion from tracked entry points
- **Issue #42** (closed): Derive the ci.yml wiring assertion in scripts/test-checks.sh instead of hardcoding a five-name list
- **PR #52**: docs(roadmap): drop hand-synced status sections duplicated by WORK_PLAN.md and tracker #5
- **Issue #51** (closed): Trim ROADMAP.md: drop stale hand-synced status sections that WORK_PLAN.md and #5 already own
- **PR #45**: test: add PDK-independent fixture control for the verify_pdk gate
- **Issue #43** (closed): PDK integrity gate has no CI-executed negative control: all 5 tests in sim/tools/tests skip without PDK_ROOT

### 2026-11-14

- **PR #44**: fix: point lint at scripts/check-all.sh, drop dead worktree:return entry
- **PR #41**: refactor: drop the unenforced PDK-pin copy from sim/pdk.json
- **PR #36**: feat(layout): add klt LVS device-coverage evidence for five SG13G2 golden cells
- **PR #35**: docs: decide D4 — classify sg13g2-sat-rx bench mechanics and specify the reuse-lock entry shape
- **PR #34**: docs(spec): record the pinned-LNA-interface re-check against LNA main
- **PR #28**: docs: roadmap as of 2026-11-13
- **Issue #40** (closed): spec/target-spec.md PDK-pin row cites sim/pdk.json, which no longer carries a pin
- **Issue #38** (closed): Trim package.json scripts: a dead worktree:return entry and lint's diverged copy of the gate list
- **Issue #33** (closed): Remove the duplicated PDK-pin fields in sim/pdk.json: an unchecked second copy of the enforced pin
- **Issue #31** (closed): LVS device-coverage probe for npn13G2 and candidate passives before topology selection
- **Issue #30** (closed): Decide deferred item D4: which bench mechanics are shared with sg13g2-sat-rx
- **Issue #29** (closed): Compare the pinned sg13g2-lna interface with current LNA main and record the result

### 2026-11-12

- **PR #25**: Bump Repo Skills 0.25.10 -> 0.26.1

### 2026-11-07

- **PR #21**: Bump Repo Skills 0.25.1 -> 0.25.10

### 2026-11-04

- **PR #7**: docs(spec): propose target spec, cascade arithmetic and ratification record

### 2026-11-01

- **PR #16**: Bump Repo Skills 0.24.7 -> 0.25.1

### 2026-10-22

- **PR #8**: ci: add headless check workflow and item-10 attestation
- **Issue #4** (closed): Repo hygiene and CI (T1 item 10): add a CI workflow and reproduction steps

### 2026-10-21

- **PR #11**: Bump Repo Skills 0.24.3 -> 0.24.7

### 2026-10-17

- **PR #6**: feat(sim): pin PDK and ngspice, add integrity gate and HBT smoke bench
- **Issue #3** (closed): Pin the SG13G2 PDK and ngspice, and commit a smoke simulation
- **PR #1**: chore(loom): Install Loom 0.19.1181
