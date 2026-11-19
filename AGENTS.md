<!-- BEGIN LOOM ORCHESTRATION (AGENTS) -->
This repository uses [Loom](https://github.com/rjwalters/loom) for AI-powered development orchestration (dual-runtime: Claude Code reads `CLAUDE.md`; OpenAI Codex CLI and other AGENTS.md-aware runtimes read this file). See the Loom repository for the full guide (roles, labels, worktrees, configuration). When installed, Loom also writes a locally-substituted copy of the runtime-neutral guide to `.loom/AGENTS.md`.

Work is coordinated through `loom:` labels on issues and pull requests, and the same roles run either under `loom-daemon` or by hand in an attended session — daemon mode is optional. Create the labels once with `.loom/scripts/sync-labels.sh` (an install ships `.github/labels.yml` but does not create the labels on the forge). A pull request ready for review carries `loom:review-requested`; Judge reviews it and applies `loom:pr` (approved) or `loom:changes-requested`; Doctor fixes a `loom:changes-requested` pull request and returns it to `loom:review-requested`. Only a `loom:pr` pull request gets merged, and always via this repo's merge script (`.loom/scripts/merge-pr.sh`) — never a raw forge merge command such as `gh pr merge`. Full state machine: `.loom/docs/label-state-machine.md`.
<!-- END LOOM ORCHESTRATION (AGENTS) -->

## Keeping the T1 tracker current (Guide duty)

Issue #5 ("Track the gap to T1") is this repository's sole owner of T1
status: `ROADMAP.md`'s "Current status" pointer names it, and no tracked
file carries a second copy. Its body drifts as the tree moves, so it has a
standing owner and a check that runs on a schedule the role already has.
This section lives outside the Loom-managed block on purpose: a Loom resync
must not delete it, and both runtimes (Claude via `CLAUDE.md`'s pointer,
Codex via this file) read this one copy.

**Owner:** Guide.

**Trigger:** at the end of each Guide triage cycle, alongside the Document
Maintenance phase. The tracker check is unconditional — run it even when
the document-maintenance flow opens no documentation PR. It edits a forge
issue body, not repository files, so it needs no docs worktree, and the
documents phase's early return (nothing to commit) never skips it.

**Procedure** — the deliverable is a forge mutation; no repository file
changes:

1. Read #5's body and take its survey stamp from "How this status was
   derived": the commit SHA and date the previous comparison started from.
2. Survey the current tip: `git fetch origin && git log -1 --format=%h
   origin/main`, then re-derive every checkable claim against it —
   directory listings (`git ls-tree -r --name-only origin/main -- <dir>`),
   file contents (`git show origin/main:<file>`), the decision records
   under `spec/decision-records/`, and the issues/PRs each item names as
   evidence.
3. Compare claim by claim: the preamble, the gate note, and each of the 11
   checklist items.

**When a claim has changed**, fetch the body, edit it, PATCH it back —
never retype it:

```bash
gh api repos/2AMLogic/sg13g2-mixer/issues/5 --jq .body > /tmp/issue-5-body.md
# edit /tmp/issue-5-body.md
gh api -X PATCH repos/2AMLogic/sg13g2-mixer/issues/5 -F body=@/tmp/issue-5-body.md
```

`-F body=@file` reads the file; `--body @file` posts the literal string
`@file`. Then:

- Re-derive only the affected text, clause by clause — no blanket rewrite.
  A claim that is still true stays word-for-word.
- Record the newly surveyed SHA and date in "How this status was derived";
  when item states are carried over unchanged from an older survey, keep
  naming that survey and its date alongside the new one.
- Cite the supporting artifact, decision record, issue or PR next to each
  changed claim.
- Tick a box only when the artifact exists AND passes. A partial item
  states what is done and what is still missing, and stays unticked until
  its stated requirements pass.
- Post a short comment on #5 recording what was refreshed and the commit
  surveyed — a dated audit trail the body alone does not keep.

Always preserve: unrelated edits, the 11-item structure and numbering, the
block-kind line, the gate note, the "Work that can start now" section, the
`<!-- loom:tracker -->` marker on a line by itself, #5's labels, and its
open state. Never relocate T1 status into a tracked file and never add a
second copy in `ROADMAP.md`, `WORK_PLAN.md` or `README.md`. The check only
records where the repo stands — it does not ratify the spec (#2) or advance
a T1 item.

**When every claim still holds** at the newer tip: change nothing — not the
body, not the survey stamp, and no comment. An older survey SHA by itself
never justifies an edit; it only tells the next comparison where to start.
A second pass over the same evidence must produce no write.
