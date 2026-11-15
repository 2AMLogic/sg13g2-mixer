# signoff/

Block-level attestation evidence for the T1 checklist
(`docs/design-evidence-tiers.md`), produced and graded by `klt signoff` at the
klt commit pinned in `.github/workflows/ci.yml` (`--attest` is newer than the
newest release wheel, so the pin is a commit, not a release).

## Files and what binds to what

- `repo-hygiene/inventory.json` — the item-10 attestation inventory: the files
  that must be present and the headless checks that must pass.
- `repo-hygiene/envelope.json` — the item-10 evidence envelope produced from
  that inventory. Its `provenance.input.content_hash` pins the inventory's
  raw-byte sha256.
- `manifest.json` — the block-level evidence index. Its
  `evidence."10".content_hash` is klt's **binding anchor**: it must equal the
  envelope's `provenance.input.content_hash` (i.e. the *inventory's* hash,
  `sha256sum repo-hygiene/inventory.json`). It is **not** the hash of the
  `file` named beside it — klt gates `manifest.content_hash ==
  envelope.provenance.input.content_hash`, so editing or deleting the pin
  renders item 10 UNMET (`stale_evidence` / `unanchored_evidence`).

## Which checks `repo-hygiene/inventory.json` lists

`checks` is a deliberate subset of the headless CI job set, not a second copy
of it: it lists exactly the gates that are reproducible and context-free —
the identical command passes locally and in CI, with no PR-specific argument
and no network. Two CI jobs are deliberately excluded:

- `records-append-only` — it requires `--base REF` (it exits 2 without one),
  and any base ref baked into the inventory would be PR-context dependent,
  i.e. not reproducible, which is exactly what the envelope's `exit_status`
  claims to be.
- `signoff-item10` — it attests the attestation itself (circular) and needs
  the network plus the pinned external `klt` tool.

A new gate joins `checks` only after it is wired into both `ci.yml` and
`scripts/check-all.sh` (`scripts/test-checks.sh` asserts both wirings), and
then the regeneration order below is re-run in the same change.

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

## What CI gates

- `klt signoff --attest 10 --inventory … --check repo-hygiene/envelope.json` —
  the committed envelope still reproduces against the inventory (envelope pin
  vs actual inventory bytes).
- The item-10 manifest-binding step asserts item 10 renders `met` with
  `input_verified: true` under `klt signoff --manifest` (manifest pin vs
  envelope's `provenance.input`).
