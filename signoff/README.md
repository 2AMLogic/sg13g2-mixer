# signoff/

Block-level attestation evidence for the T1 checklist
(`docs/design-evidence-tiers.md`), produced and graded by `klt signoff` at the
klt commit pinned for its job in `.github/workflows/ci.yml` (`--attest` is newer
than the newest release wheel, so each pin is a commit, not a release). Items
9 and 10 are pinned to different commits; see "Item 9: a separate producer
pin" below.

## Files and what binds to what

- `repo-hygiene/inventory.json` — the item-10 attestation inventory: the files
  that must be present and the headless checks that must pass.
- `repo-hygiene/envelope.json` — the item-10 evidence envelope produced from
  that inventory. Its `provenance.input.content_hash` pins the inventory's
  raw-byte sha256.
- `testbenches/inventory.json` — the item-9 attestation inventory: the three
  `sim/*/testbench/tb.json` manifests, each bench's `depends_on` closure and
  the pins.
- `testbenches/envelope.json` — the item-9 evidence envelope produced from
  that inventory. It binds each manifest and each dependency by raw-byte
  sha256, and its `provenance.input.content_hash` pins the inventory's raw-byte
  sha256.
- `manifest.json` — the block-level evidence index. Its
  `evidence."10".content_hash` is klt's **binding anchor**: it must equal the
  envelope's `provenance.input.content_hash` (i.e. the *inventory's* hash,
  `sha256sum repo-hygiene/inventory.json`). It is **not** the hash of the
  `file` named beside it — klt gates `manifest.content_hash ==
  envelope.provenance.input.content_hash`, so editing or deleting the pin
  renders item 10 UNMET (`stale_evidence` / `unanchored_evidence`).
  `evidence."9".content_hash` anchors item 9 the same way: it must equal the
  raw-byte sha256 of `testbenches/inventory.json`
  (`sha256sum signoff/testbenches/inventory.json`), which is the item-9
  envelope's `provenance.input.content_hash` — again **not** the hash of the
  `testbenches/envelope.json` file named beside it — and editing or deleting
  it renders item 9 UNMET (`stale_evidence` / `unanchored_evidence`).

## Which checks `repo-hygiene/inventory.json` lists

`checks` is a deliberate subset of the headless CI job set, not a second copy
of it: it lists exactly the gates that are reproducible and context-free —
the identical command passes locally and in CI, with no PR-specific argument
and no network. Three CI jobs are deliberately excluded:

- `records-append-only` — it requires `--base REF` (it exits 2 without one),
  and any base ref baked into the inventory would be PR-context dependent,
  i.e. not reproducible, which is exactly what the envelope's `exit_status`
  claims to be.
- `signoff-item10` — it attests the attestation itself (circular) and needs
  the network plus the pinned external `klt` tool.
- `signoff-item9` — it needs the network plus the pinned external `klt` tool
  as well (it is not circular: item 9 attests the testbenches, not this
  inventory).

A new gate joins `checks` only once it is in `scripts/check-all.sh` — the
single command list that the `ci.yml` jobs call with their group name and that
`package.json` runs locally — and then the regeneration order below is re-run
in the same change.

## Regeneration order (envelope first, manifest pin second)

When the inventory changes (checks or hygiene files added/changed), regenerate
in this order so the manifest cannot lag the envelope by one commit:

1. Edit `repo-hygiene/inventory.json`.
2. Regenerate the envelope from it (`klt signoff --attest` writes the envelope
   only when it passes and its bytes changed):

   ```
   uvx --from "git+https://github.com/2AMLogic/klayout-tools@<pinned commit>" \
     klt signoff --attest 10 \
     --inventory signoff/repo-hygiene/inventory.json \
     -o signoff/repo-hygiene/envelope.json
   ```

3. Update `manifest.json`'s `evidence."10".content_hash` to the inventory's
   raw-byte sha256 (`sha256:<hex>` from
   `sha256sum signoff/repo-hygiene/inventory.json`).

The same order applies when a file the envelope attests changes (currently
`README.md`, `LICENSE`, `.github/workflows/ci.yml`): re-attest the envelope in
the same change, or CI's drift gate fails.

## Item 9: a separate producer pin

`testbenches/envelope.json` has its own CI gate, `signoff-item9` — a drift
step and a manifest-binding step — and its own klt pin, used by both steps: the
build that produced it, not item 10's.

```
uvx --from "git+https://github.com/2AMLogic/klayout-tools@6bd18bbc8637f6d767b3c24e77bd5db7a39e4bbe" \
  klt signoff --attest 9 --inventory signoff/testbenches/inventory.json \
  --check signoff/testbenches/envelope.json
```

That commit reports `0.9.3.dev2575+g6bd18bbc8637`, the `provenance.klt_version`
recorded in the envelope. Item 10's pin cannot check this envelope: that older
build rejects the item-9 inventory outright (`'testbenches' entries must be
non-empty path strings`) because its `testbenches` entries are objects, not
paths. So the two signoff jobs stay on separate pins, and a re-attested item-9
envelope is produced with the item-9 pin: the same command with `--check …`
replaced by `-o signoff/testbenches/envelope.json`, which, unlike `--check`,
runs the three cold starts and needs the pinned ngspice.

When the item-9 inventory itself is edited, finish in the same change or the
binding step fails: re-attest the envelope with the item-9 pin (the `-o` form
of the command above), then update `manifest.json`'s
`evidence."9".content_hash` to the new inventory's raw-byte sha256. The drift
step alone cannot catch a pin left behind, because a re-attested envelope
reproduces; the stale pin then reads `stale_evidence`.

## What CI gates

- `klt signoff --attest 9 --inventory testbenches/inventory.json --check
  testbenches/envelope.json` (job `signoff-item9`, drift step) — the committed
  item-9 envelope still reproduces: every file the item-9 inventory names still
  hashes to the `content_hash` recorded for it. Drift only: a re-attested
  envelope reproduces, so this step cannot see a stale manifest pin.
- The item-9 manifest-binding step (same job, same pin) asserts item 9 renders
  `met` with `input_verified: true` under `klt signoff --manifest` (manifest
  pin vs the envelope's `provenance.input`). One assertion grades the
  committed manifest and three scratch copies of it: the unmodified copy
  passes, a deleted `content_hash` fails with `unanchored_evidence`, and the
  envelope file's own hash fails with `stale_evidence`. Anything else fails
  the step instead of grading: a `klt` exit other than 0 (all met) or 3 (unmet
  overall), or a report without exactly one item 9.
- `klt signoff --attest 10 --inventory … --check repo-hygiene/envelope.json` —
  the committed envelope still reproduces against the inventory (envelope pin
  vs actual inventory bytes).
- The item-10 manifest-binding step asserts item 10 renders `met` with
  `input_verified: true` under `klt signoff --manifest` (manifest pin vs
  envelope's `provenance.input`).
