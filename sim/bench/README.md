# sim/bench — known-answer bench library (V3)

The shared, band-independent parts of this repo's measurement bench, per
[record 0002](../../spec/decision-records/0002-shared-bench-mechanics.md).
Each mechanic has exactly one master; there is no second implementation of
a stamped mechanic anywhere in this repo.

| Mechanic | Master | Where |
|---|---|---|
| M1 coherent single-bin DFT (both halves) | written here | [`lib/coherent.py`](lib/coherent.py) |
| M2 tone placement / coherence pre-flight | stamped copy | [`lib/coherence.py`](lib/coherence.py) |
| M3 window / PSD normalisation + cross-checks | stamped copy | [`lib/psd.py`](lib/psd.py) |
| shared preamble (constants, exceptions) for M3/M6 | stamped copy | [`lib/nfcommon.py`](lib/nfcommon.py) |
| M4 settling / convergence gate | written here | [`lib/convergence.py`](lib/convergence.py) |

M5 (IIP3 slope fit) and M6/M7 (noise factors, statistical interval) are
V4 mechanics (record 0002 decides their masters; they land with the V4
benches and are named here only so the table stays complete).

Stamped copies (`coherence.py`, `psd.py`, `nfcommon.py`) are **verbatim**:
never edit them in place. An improvement belongs upstream
(`2AMLogic/sg13g2-sat-rx`), or in a local wrapper; `reuse.lock.json`
(schema 2) records each copy's commit, symbols and hashes, and a local edit
shows up as a hash mismatch. M1 and M4 are written here *because* their
load-bearing content is this repo's convention and protocol numbers.

## Dependencies

`lib/psd.py` needs numpy (record 0002, M3 consequence) — the repo's only
third-party Python dependency, declared in
[`requirements.txt`](requirements.txt). CI installs it into a venv; the
bench cold start does the same via `sim/bench/mkenv.sh` (worktree-local
`.tools/`, never a host-wide install). Everything else — `coherent.py`,
`convergence.py`, `lib/coherence.py`, `lib/nfcommon.py`, `runner.py` — is
standard library only.

## Benches (V3: known-answer checks 1, 2, 5)

| Bench | Spec check | What it proves |
|---|---|---|
| [`../ka1-ideal-multiplier/`](../ka1-ideal-multiplier/) | 1 | ideal behavioural multiplier: IF amplitude = k·A/2 × RF amplitude, B-CG within 0.05 dB |
| [`../ka2-switch-mixer/`](../ka2-switch-mixer/) | 2 | double-balanced ideal-switch mixer: IF voltage = 2/π × RF voltage within 0.1 dB |
| [`../ka5-window-coherence/`](../ka5-window-coherence/) | 5 | one coherent tone reads the same power on rectangular FFT, Hann FFT and independent DFT within 0.05 dB |

Each bench README documents its cold-start command; results land
append-only in `sim/<bench>/records/`. The benches are behavioural
(no HBT models, no PDK), single corner per run, per the V3 row of the
validation plan.
