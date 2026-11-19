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

1. Fetch #5's body **once** into the pass's own scratch directory — the
   ordered block below creates it — and take its survey stamp from "How
   this status was derived": the commit SHA and date the previous
   comparison started from. That one copy is both the step-3 comparison
   baseline and the base of the edit, so no peer write can slip between
   deciding a change is needed and preparing the edit from that decision.
2. Survey the current tip: `git fetch origin && git log -1 --format=%h
   origin/main`, then re-derive every checkable claim against it —
   directory listings (`git ls-tree -r --name-only origin/main -- <dir>`),
   file contents (`git show origin/main:<file>`), the decision records
   under `spec/decision-records/`, and the issues/PRs each item names as
   evidence.
3. Compare claim by claim — against the step-1 copy, never a second GET:
   the preamble, the gate note, and each of the 11 checklist items.

**When a claim has changed**, prepare the edit from the step-1 copy and
PATCH it back — never retype it. The block shows the whole sequence in
order; a successful uncached read and an equal comparison are both
prerequisites for the PATCH, which runs only inside the identical branch:

```bash
WORK="$(mktemp -d)"   # per-pass scratch directory — never a fixed /tmp path:
                      # every Guide targets #5, so a name keyed on the issue
                      # number is still shared by concurrent passes on this
                      # host, and a peer can clobber your files mid-procedure

# Step 1 — the single GET. This copy is the step-3 baseline AND the base of
# the edit; one fetch serves both, so a peer write after it cannot slip
# between the decision that a change is needed and the edit prepared from it.
gh api repos/2AMLogic/sg13g2-mixer/issues/5 --jq .body > "$WORK/baseline" || exit 1
[ -s "$WORK/baseline" ] || exit 1   # empty body: stop — never write on bad data

# Steps 2-3 — survey origin/main (`git fetch origin && git log -1
# --format=%h origin/main`, then re-derive every claim) and compare claim by
# claim against "$WORK/baseline". Every claim still holding ends the pass
# here: zero PATCHes, zero comments.

# When a claim has changed: copy the baseline and edit the copy.
cp "$WORK/baseline" "$WORK/prepared"
# edit "$WORK/prepared" — re-derive only the affected text; see below.

# Final gate, immediately before the PATCH: an uncached re-read, compared
# against the exact body the decision and the edit were made from.
gh api repos/2AMLogic/sg13g2-mixer/issues/5 --jq .body > "$WORK/final" || exit 1
[ -s "$WORK/final" ] || exit 1     # failed or empty read: stop the write

cmp -s "$WORK/baseline" "$WORK/final"; CMP=$?
if [ "$CMP" -eq 0 ]; then
    # Nothing landed in between: the only path that reaches the PATCH.
    gh api -X PATCH repos/2AMLogic/sg13g2-mixer/issues/5 -F "body=@$WORK/prepared"
elif [ "$CMP" -eq 1 ]; then
    echo "peer wrote first — discard the prepared edit, re-run the"
    echo "step-3 comparison against the fresh copy in $WORK/final"
else
    echo "comparison error — stop the write; never PATCH on unverifiable state"
fi
```

`-F body=@file` reads the file; `--body @file` posts the literal string
`@file`. The final-gate read is a literal `gh api` call — **not** routed
through `.loom/scripts/gh-cached` / `$GH_READ`, which caches `gh api`
GETs for 30 seconds and could serve a body up to that old, matching your
prepared copy and masking exactly the peer write this check exists to
detect. The read-edit-write sequence is not atomic, and nothing
serializes two Guides across hosts, so the PATCH runs only after that
uncached read succeeds and compares equal:

- **Identical** → nothing landed in between: the PATCH runs, inside this
  branch only.
- **Different** → a peer completed a write between the step-1 fetch and
  the final read. Discard the prepared edit and re-run the step-3
  comparison against the latest body (`$WORK/final`). If the peer's
  refresh already applied the change, end the pass silently — zero
  PATCHes, zero comments. If it was an unrelated edit and a claim still
  needs correction, re-apply your derivation on top of the latest body,
  preserving the unrelated edit, and PATCH that — applying the same
  final-read gate before that PATCH too.
- **A failed or empty final read, or a comparison error** → stop the
  write. Never PATCH on unverifiable state.
- **The PATCH itself fails** → post no comment. The body keeps whatever
  the last successful write left; the next pass re-derives from it.

When preparing the edit:

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

After a successful PATCH for a change this Guide still needed to make,
post a short comment on #5 recording what was refreshed and the commit
surveyed — a dated audit trail the body alone does not keep. A stand-down
and a failed PATCH post none.

**Residual race.** The final read and the PATCH are two separate calls, so
two Guides whose final reads both complete before either write proceeds
both see an unchanged body, both PATCH their own prepared edit, and both
post an audit comment. Last write wins; when the two surveys started from
different tips, the loser's stale text overwrites the winner's. The body
self-heals — the next pass re-derives every claim and corrects it — but
duplicate audit comments do not. The procedure guarantees only that a
Guide whose final read sees a peer's completed refresh writes nothing; it
does not serialize simultaneous final reads.

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
