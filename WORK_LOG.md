# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide triage role.

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
