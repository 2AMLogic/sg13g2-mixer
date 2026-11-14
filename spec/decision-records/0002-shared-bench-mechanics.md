# 0002 — Shared bench mechanics with `sg13g2-sat-rx` (resolves D4)

- **Status**: PROPOSED. This record resolves **D4** of
  [`0001-target-spec-ratification.md`](0001-target-spec-ratification.md)
  ("Shared bench code with `sg13g2-sat-rx`") by deciding it; it does not
  ratify any row of [`../target-spec.md`](../target-spec.md) and changes no
  protocol number. Approving the PR that carries this record is not
  ratification of the spec.
- **Issue**: [#30](https://github.com/2AMLogic/sg13g2-mixer/issues/30)
- **Date**: 2026-11-14
- **Decided by**: Builder agent, issue #30
- **Supersedes**: the D4 deferral in record 0001 and the sentence in
  `../target-spec.md` §"Measurement protocol" that says D4 "is decided when
  #3 builds the bench". **#3 is closed** (`gh issue view 3`, 2026-11-14:
  "Pin the SG13G2 PDK and ngspice, and commit a smoke simulation", closed
  2026-10-17T21:59:22Z) and built no bench, so that owner is stale. No bench
  issue is open. This record therefore decides D4 *ahead of* the bench issue
  rather than inheriting a closed owner. It does not edit `0001` or
  `../target-spec.md`.
- **No code lands with this record.** It adds no `reuse.lock.json`, no bench
  code and no simulation. It is a contract the bench PR must satisfy.

## Context

`../target-spec.md` §"Measurement protocol" requires that the shared,
band-independent parts of this bench — tone placement, coherent DFT,
convergence and slope checks — **have one master**, and that if
`sg13g2-sat-rx`'s bench code is taken it arrives "by a stamped copy tracked
in `reuse.lock.json`, not a second implementation". `CLAUDE.md` says the same
in its scope-discipline bullet. Record 0001 deferred which mechanics are
band-independent (D4).

Two facts make deciding now cheap and deferring expensive:

- **This repo has no bench code at all.** Verified on `main` @ `9f2e9be`,
  2026-11-14: `sim/` holds `pdk.json`, `pdk-artifact.json`, `toolchain.json`,
  `README.md`, `smoke-hbt/{smoke.cir,run.sh,README.md}`,
  `tools/verify_pdk.py` and `tools/tests/test_verify_pdk.py` — nine tracked
  files, no bench. There is no local second implementation to reconcile, so
  the decision is purely forward-looking.
- **The deferral has no owner left.** See Status above.

## The read

- **Repository**: `2AMLogic/sg13g2-sat-rx`
- **Commit read**:
  **`6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947`** (`main` HEAD at
  2026-11-14T03:56:48Z, "Merge pull request #248 from
  2AMLogic/docs/guide-update-20261114-024005").
- **Method**: shallow clone into a throwaway `/tmp` directory, then
  `grep`/`sed` over the working tree. Nothing was executed, nothing was
  simulated, and the upstream repo was not modified. Every line number,
  path, function name, file count and hash below was read at that commit and
  is stated as of it; **these drift quickly — re-resolve before relying on a
  line number.**
- **Licence**: upstream is Apache-2.0 (`LICENSE`, read at that commit); this
  repo is Apache-2.0. A stamped copy carrying its upstream attribution is
  licence-compatible.
- **This commit is not the one curation cited.** Issue #30's
  "Verified corrections" were read at `1f7f7c3130ee2b28a2ca78c5973aa9fa608fd847`
  (2026-11-12). Re-running the search at `6e5ebaf` found **more** sites than
  that inventory listed, and corrected one of its classifications — see
  "Corrections to the curated inventory" below. The inventory in this record,
  not the issue's, is the decided one.

## Inventory and classification

"Band-independent" means the code contains no band, frequency-plan, device or
PDK constant and no coupling to a block-specific data structure. Every item
below was read line by line at `6e5ebaf`.

### Band-independent

| # | Mechanic | Upstream site(s) at `6e5ebaf` | Why band-independent |
|---|---|---|---|
| M1 | Coherent single-bin DFT | `sim/mixer-topology-feasibility/mixfeas.py:90-106` `dft_bin`; `sim/lna-linearity/linearity.py:167-176` `window_dft`; `sim/mixer-pumped-rf-admittance/pumped.py:170-171` `phasor_from_integrals` | All three are pure arithmetic over samples (or integrals) and a frequency in Hz. No band constant in any of them. |
| M2 | Tone placement / coherence check | `sim/lna-linearity/linearity.py:118-139` `coherence_problems`; `sim/mixer-topology-feasibility/mixfeas.py:464-482` `coherence_problems` | Both are pure arithmetic on window, step and a frequency set: integer cycles in the window, integer samples in the window, and a Nyquist/samples-per-period bound. No band constant. |
| M3 | Window / PSD normalisation and cross-check | `sim/mixer-nf-method/nfmethod.py:97` `window`, `:106` `enbw_bins`, `:111` `one_sided_psd`, `:143` `check_parseval`, `:164-186` `band_power` (+ `MethodError` `:81`, `NormalizationError` `:85`) | Rectangular/Hann window generation, ENBW in bins, one-sided periodogram with the window-power correction, a Parseval rejection test, and band integration gated on ≥ N×ENBW. Frequencies are arguments; no constant other than the window definitions. |
| M4 | Settling / convergence check | `sim/mixer-nf-method/nfmethod.py:328` `Convergence`, `:337-355` `convergence_failures` | The *mechanism* — compare duration-doubling and timestep-halving deltas and a confidence half-width against thresholds — carries no band constant. But see "Policy-coupled" below: the thresholds are not ours. |
| M5 | IM3 / IIP3 slope fit | `sim/mixer-topology-feasibility/mixfeas.py:935-1013` `fit_iip3` (+ `_linfit` `:924-932`, `_finite` `:915-916`); `sim/lna-linearity/linearity.py:582-677` `fit_iip3` (+ `linfit` `:533-546`, `_baseline` `:548-558`, `_gain_rows` `:560-563`, `point_status` `:565-579`) | Both operate on `(pin_dbm, P_fund, P_im3, floor)` rows in dBm and fit slopes. No band constant in either. |
| M6 | SSB/DSB noise-factor definitions and closed-form known answers | `sim/mixer-nf-method/nfmethod.py:192` `NoiseBudget`, `:214` `_validate_budget`, `:237` `n_out_at_t0`, `:246` `ssb_noise_factor`, `:251` `dsb_noise_factor`, `:257` `db`, `:261` `attenuator_ideal_mixer_f_ssb`, `:274-289` `y_factor_f_ssb` | IEEE SSB/DSB factor definitions with explicit wanted/image gains and source temperatures, plus two closed-form known answers. Only physical constants (`K_B = 1.380649e-23`, `T0_K`). No band. |
| M7 | Statistical interval on a noise figure | `sim/mixer-nf-method/nfmethod.py:300` `t975`, `:306-326` `nf_interval` | Student-*t* 95 % interval on per-seed linear noise factor. Pure statistics. |
| M8 | Harness / `tb.json` manifest layer | `sim/harness/` — **29 tracked files** at `6e5ebaf` (`git ls-files sim/harness \| wc -l`) | Nine of its modules open their docstring with a `GENERIC CORE` paragraph; `sim/harness/testbench.py:1-4` states "**GENERIC CORE.** This module has no block-specific content". The only Ka-band strings in the package are in docstrings describing *callers* (`pdkartifact.py:6`, `klt_driver.py:3`, `sim/harness/tests/test_smoke_verdict.py:128`), never in logic. Band-independent — and nevertheless **out of the shared set**, for the reason under "Decision" M8. |

### Policy-coupled, not band-coupled (a distinct category)

M4's `convergence_failures` reads six **module-level policy constants**
(`nfmethod.py:62-68`, under the comment "Methodology qualification limits
(issue #27 step 4/5). Not row-10 limits."): `CONTROL_TOL_DB = 0.25`,
`CI_HALFWIDTH_MAX_DB = 0.25`, `DELTA_DURATION_MAX_DB = 0.25`,
`DELTA_TIMESTEP_MAX_DB = 0.25`, `MIN_SEEDS = 8`,
`MAX_DURATION_DOUBLINGS = 3`.

These are not band constants, but they are **not this repo's numbers**.
`../target-spec.md` §"Measurement protocol" fixes different ones: the
convergence check is "reproduce every reported figure to < 0.1 dB" on the
following window, time-step convergence is "< 0.1 dB on halving the step",
and B-NF requires "≥ 256 independent averages" with statistical error
"≤ 0.3 dB 1-σ". A stamped copy of `convergence_failures` would import
tolerances the spec does not authorise, and the bench contract forbids
loosening a protocol number without a decision record. This is why M4 is
decided differently from M3 and M6, which live in the same upstream file.

### Band-specific or block-specific (named for contrast, not candidates)

| Site at `6e5ebaf` | Why excluded |
|---|---|
| `mixfeas.py:39` `LO_RDIFF_OHM = 100.0` (used at `:396`) | A port-impedance constant of the Ka-band study. |
| `mixfeas.py:140` `class Band`, `:149` `class Timing` | Ka-band frequency plan and timing dataclasses. |
| `mixfeas.py:719` `classify_stress` | SG13G2 HBT VCE/VBE/IC stress limits — PDK device policy. |
| `linearity.py:565-579` `point_status` → `limit_violations` | Gates points on `excursion_v` / `current_a` DUT operating limits: LNA-block-specific. This is why M5's stamp is taken from `mixfeas.py`, not `linearity.py` (see Decision M5). |
| `sim/passive-p1/runner/smoke_cavity.py:202-203` | An inline ad-hoc `np.fft.rfft` with `np.hanning`, not a reusable mechanic and not coherent-bin discipline. Not a candidate. |

### Corrections to the curated inventory

Stated so the difference is auditable, not to re-litigate curation:

1. **M2 and M5 each have two upstream implementations, and M1 has three.**
   Issue #30's inventory named one `coherence_problems` (`mixfeas.py:464`) and
   one coherent DFT (`mixfeas.py:90`). At `6e5ebaf` there is also
   `linearity.py:118` `coherence_problems`, `linearity.py:167` `window_dft`
   and `pumped.py:170` `phasor_from_integrals`. **Upstream is therefore not a
   single master for M1, M2 or M5** — which is the central finding of this
   record.
2. **`collect.py:314` `iip3_fits` is a caller, not a second slope fit.** It
   calls `mf.fit_iip3` at `collect.py:328`; `sim/mixer-topology-feasibility/run.py:230`
   calls it too. The actual second *implementation* is
   `linearity.py:582` `fit_iip3`, and curation did cite that one.
3. **The two M5 implementations have diverged in what they report.**
   `mixfeas.py:935` reports the intersection of the two free-slope lines.
   `linearity.py:582` reports the intercept at the *ideal* slopes
   (mean of `pin + (P_fund − P_im3)/2`) and **cross-checks it** against the
   free-slope intersection within `free_fixed_tol_db`, rejecting the run when
   they disagree; it also bounds `max_point_spread_db`. On the same data the
   two can return different numbers. See "Findings to file on
   `sg13g2-sat-rx`".
4. **`sim/harness/` has its own upstream, and `sg13g2-sat-rx` is not it.**
   `sim/harness/__init__.py:1` names the package `sim-harness-core`,
   declares `HARNESS_VERSION = "1.0.0"` and records
   `UPSTREAM_PATTERN = "https://github.com/2AMLogic/gf180-sar-adc/tree/main/sim/harness"`,
   scaffolded by `everyblock/scaffold.sh`. `sim/harness/README.md:11`
   says, in bold: **"Do not fork or vendor a sibling canary's harness
   wholesale."** This changes M8's answer from a cost judgement to a
   prohibition by its own master.
5. **Upstream's citations hold at the new sha**, with the line numbers
   above replacing the `1f7f7c3` ones. Upstream still has **no
   `reuse.lock.json`** (absent at `6e5ebaf`) and no stamped-copy convention
   of its own (`grep -rliE 'stamped copy|reuse\.lock|one master' spec/ sim/
   docs/` returns nothing), so it is not a *declared* master for anything.
   That is what makes the pinned sha in this record load-bearing.

## Decision

**Four mechanics arrive as stamped copies; three are written here; the
harness layer is out of the shared set.** Per item:

### M1 — coherent single-bin DFT: **write it here**

Destination: `sim/bench/lib/coherent.py` (path proposed; the bench PR may
site it elsewhere and must then say so).

Reason. Upstream carries **three** mutually inconsistent conventions:
`dft_bin` returns `a·(sin φ + j cos φ)` from samples; `window_dft` returns a
real peak amplitude `2·|Σ x e^{−jω t}|/n`; `phasor_from_integrals` returns a
**cosine-referenced** phasor `2c/T − j·2s/T` from ngspice integrals — a
different phase reference *and* a conjugate sign relative to `dft_bin`.
Stamping one of three would import the ambiguity instead of resolving it,
and this repo's protocol fixes its own convention (rectangular window, every
tone on an exact bin centre, peak amplitude read at a named bin). The
mechanic is ~15 lines of arithmetic; writing it costs less than stamping it
and leaves one master — ours — for a quantity this repo must define anyway.

**This mechanic exists twice over in any case**, which is the second reason
not to stamp: `mixfeas.py:95-96` states `dft_bin` is "the same expression the
generated deck evaluates in ngspice; this pure Python copy is what the
analytic parser tests exercise", the deck half being generated by
`build_run_lines` (`mixfeas.py:519`). A stamp of the Python half alone leaves
the deck half unstamped and free to drift. This repo's bench PR must write
both halves against **this** repo's deck and make the Python half the
known-answer oracle for it — which only works if we own the convention.
Upstream's `window_dft` docstring is cited as the normalisation *reference*
the Python half must reproduce; the citation is not a copy.

### M2 — tone placement / coherence check: **take a stamped copy**

Master: `2AMLogic/sg13g2-sat-rx@6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947:sim/lna-linearity/linearity.py`,
symbol `coherence_problems` (`:118-139`).
Destination: `sim/bench/lib/coherence.py`.

Reason. Of the two implementations this one is strictly the more complete and
the more general: it takes a plain `{name: f_hz}` dict plus `window_s`,
`step_s` and `settle_discard_s` rather than a Ka-band `RunSpec`; it is the
only one that checks **the settling discard lands on a sample** (which this
repo's protocol needs: "discard ≥ 2 µs before the window"); and it bounds
sample density at ≥ 8 samples per period rather than merely inside
`(0, Nyquist)`. It has **zero** transitive dependencies — its body uses only
builtins (`abs`, `round`, `sorted`), not even `math`. It is
also already the de-facto upstream master: `sim/lna-headroom/headroom.py:139`
calls it through `L.placement_coherence`, so two upstream studies share it.
Its `tol = 1e-9` default and the 8-samples-per-period bound are policy this
repo sets at the call site, not inside the copy.

### M3 — window / PSD normalisation and cross-check: **take a stamped copy**

Master: `…@6e5ebaf:sim/mixer-nf-method/nfmethod.py`, symbols `window`
(`:97`), `enbw_bins` (`:106`), `one_sided_psd` (`:111`), `check_parseval`
(`:143`), `band_power` (`:164-184`).
Destination: `sim/bench/lib/psd.py`.

The exception these functions raise — `NormalizationError`, a subclass of
`MethodError` — is deliberately **not** in this list. Both are shared with M6
and are owned by the **shared-preamble entry** (`sim/bench/lib/nfcommon.py`),
which `psd.py` imports; see "Closure of a `symbols` list" below for why, and
for the rule that makes that import legal without patching a stamped copy.

Reason. This is the strongest stamp candidate in the inventory: ~90 lines,
self-contained, no study coupling, no policy constant, and it implements
exactly the discipline B-NF demands — a one-sided periodogram with the
window-power correction, ENBW reported in bins and in Hz, a Parseval
rejection test that catches a two-sided or window-uncorrected PSD, and a band
integration that refuses a band narrower than 4 × ENBW. Re-deriving a PSD
normalisation is the classic place a noise-figure bench goes quietly wrong by
a factor of two; a stamped copy with a named master is worth more here than
anywhere else in the bench. Upstream's 358-line
`sim/mixer-nf-method/tests/test_nfmethod.py` is cited as the reference test
set the bench PR should reproduce against the stamped copy.

**Consequence the bench PR must handle**: this copy needs **numpy**. This
repo currently declares no third-party Python dependency at all — there is no
`requirements*.txt` on `main` @ `9f2e9be`, and `scripts/check-python.sh`
byte-compiles with `python3 -I` and discovers `unittest` tests with the
standard library only. Upstream declares `numpy>=1.26,<3` in both
`requirements-test.txt` and `requirements-sim.txt`. The bench PR that takes
this stamp must add the dependency declaration and make CI install it, or the
stamped module will not import. The host rule in the operator's global
instructions forbids installing host-wide tools, so this means a venv or a
declared CI install, not a `pip install --user`.

### M4 — settling / convergence check: **write it here**

Destination: `sim/bench/lib/convergence.py`.

Reason. The mechanism without its constants is five comparisons; the
constants *are* the decision, and upstream's
(`CI_HALFWIDTH_MAX_DB = 0.25`, `MIN_SEEDS = 8`,
`DELTA_DURATION_MAX_DB = DELTA_TIMESTEP_MAX_DB = 0.25`,
`MAX_DURATION_DOUBLINGS = 3`, `nfmethod.py:62-68`) are the Ka-band study's
methodology-qualification limits, explicitly scoped by their own comment to
"issue #27 step 4/5". This repo's protocol fixes **< 0.1 dB** on the
following-window reproduction and on step halving, and ≥ 256 averages with
≤ 0.3 dB 1-σ for B-NF. Stamping would either import the wrong numbers or be
a stamp with local edits to its load-bearing content, which defeats
divergence detection. Write it here against this repo's protocol numbers, and
cite `convergence_failures` as the structural model (a list of named failure
strings, empty when clean) in the source comment.

### M5 — IM3 / IIP3 slope fit: **take a stamped copy**

Master: `…@6e5ebaf:sim/mixer-topology-feasibility/mixfeas.py`, symbols
`_finite` (`:915-916`), `_linfit` (`:924-932`), `fit_iip3` (`:935-1013`).
Destination: `sim/bench/lib/iip3.py`.

Reason. `mixfeas.py`'s `fit_iip3` is taken rather than `linearity.py`'s
because its transitive closure is **only** `_finite` and `_linfit` — nothing
block-specific — whereas `linearity.py:582`'s closure runs through
`point_status` (`:565`) into `limit_violations`, which gates points on
`excursion_v` / `current_a` DUT operating limits and would drag LNA device
policy into this repo. The stamped mechanic is exactly what the protocol
makes mandatory: IIP3 only from a contiguous run of ≥ `min_points` steps
whose least-squares slopes are 1 ± 0.1 and **3 ± 0.3** with bounded
residuals, above the extraction floor by a margin and below compression;
otherwise "IIP3 unavailable" with a reason, never a single-point
extrapolation. `../target-spec.md` B-IP3 says a result failing slope 3 ± 0.3
"is reported as compression-contaminated and not as an IIP3" — the stamped
function already enforces that.

**The fixed/free cross-check is added here, not edited in.**
`linearity.py:582` additionally reports the intercept at the ideal slopes and
rejects a run whose fixed-slope and free-slope answers disagree by more than
`free_fixed_tol_db`. That check is worth having, but editing it into the
stamped copy would make the copy's hash diverge from its master by design and
destroy the divergence signal. The bench PR therefore writes a **separate
local wrapper** (`sim/bench/lib/iip3_crosscheck.py`, written here, not
stamped) that calls the stamped `fit_iip3` and applies the fixed/free
comparison on its result. Rule, generally: **a stamped copy is taken
verbatim or not at all; local additions wrap it, they do not patch it.**

### M6 — SSB/DSB noise-factor definitions and known answers: **take a stamped copy**

Master: `…@6e5ebaf:sim/mixer-nf-method/nfmethod.py`, symbols `NoiseBudget`
(`:191-211`, including its `@dataclasses.dataclass` decorator line at `:191`),
`_validate_budget` (`:214`), `n_out_at_t0` (`:237`), `ssb_noise_factor`
(`:246`), `dsb_noise_factor` (`:251`), `db` (`:257`),
`attenuator_ideal_mixer_f_ssb` (`:261`), `y_factor_f_ssb` (`:274-287`).
Destination: `sim/bench/lib/noisefactor.py` (same `src` as M3, a second
entry — one entry per destination file).

The physical constants and exceptions these symbols reference — `K_B`, `T0_K`,
`MethodError`, `NormalizationError`, `ImageAccountingError` — are **not** in
this list either. `T0_K` is a default argument on two `NoiseBudget` fields and
on five of these functions, so it is evaluated at `def` time: a copy without it
raises `NameError` at import, not at first call. All five are shared with M3 and
are owned by the **shared-preamble entry** (`sim/bench/lib/nfcommon.py`), which
`noisefactor.py` imports — see "Closure of a `symbols` list" below.

Reason. The SSB/DSB distinction is the single most error-prone definition in
this project's riskiest row, and this code states it structurally rather than
by convention: `NoiseBudget` **rejects** `gain_image = None` as an omission
rather than defaulting it, and `dsb_noise_factor`'s docstring records that
DSB is "reported only beside, and labelled as, DSB; never substituted for the
SSB figure" — which is this repo's rule too. `attenuator_ideal_mixer_f_ssb`
is a closed-form known answer (`F_SSB = (1 + G_i/G_w)(1 + (L−1)T_att/T0)`,
giving 3.01 dB for a lossless equal-sideband case) that maps directly onto
**known-answer case 3** of `../target-spec.md`'s validation list ("ideal
multiplier … SSB NF = 3.01 dB … DSB NF = 0 dB"). Taking the reference
implementation of a known answer is strictly better than re-deriving the
oracle we intend to be checked by. Physical constants only
(`K_B = 1.380649e-23`, `T0_K = 300.15`) — no study policy, no band constant;
both arrive via `nfcommon.py`, not re-typed here.

### M7 — statistical interval on a noise figure: **write it here**

Destination: folded into `sim/bench/lib/convergence.py`.

Reason. `nf_interval` (`:306`) is a Student-*t* 95 % interval built on
`t975` (`:300`), which is a hard-coded table lookup sized for upstream's
`MIN_SEEDS = 8` regime. This repo's B-NF is specified as Welch averaging
with **≥ 256 independent averages** and a 1-σ statistical error ≤ 0.3 dB —
a different estimator and a different reported quantity (1-σ, not a 95 %
half-width). The mechanic is band-independent but answers a question we are
not asking. Write the 1-σ estimator the spec names.

### M8 — harness / `tb.json` manifest layer: **band-independent, but OUT of the shared set**

`sim/harness/` (29 files at `6e5ebaf`) is classified **band-independent** —
it self-declares `GENERIC CORE` in nine module docstrings and its only
Ka-band content is in docstrings naming callers. It is nevertheless **out of
the set of mechanics this record shares with `sg13g2-sat-rx`**, for three
reasons, the first of which is decisive:

1. **`sg13g2-sat-rx` is not its master.** `sim/harness/__init__.py:1`
   identifies the package as `sim-harness-core`, scaffolded by
   `everyblock/scaffold.sh`, with `HARNESS_VERSION = "1.0.0"` and
   `UPSTREAM_PATTERN` pointing at `2AMLogic/gf180-sar-adc`'s `sim/harness/`.
   `sim/harness/README.md:11` instructs, in bold, **"Do not fork or vendor a
   sibling canary's harness wholesale."** Stamping it *from sat-rx* would
   pin a downstream scaffolded instance as though it were the master — the
   precise error this record exists to prevent.
2. **It is not file-granular.** It is a Python package with internal relative
   imports (`testbench.py` does `from . import evidence as evidence_mod` and
   `from .corners import …`), so no subset of its files is independently
   stampable; the unit is the package.
3. **Adopting it is out of scope here** (issue #30), and it is an adoption
   decision with its own cost: `sim/harness/cli.py`, `runner.py`,
   `evidence.py`, `report.py` and `corners.py` would become this repo's
   evidence, corner and record-minting path, replacing whatever `sim/`
   currently does by hand.

**Recommendation for a separate issue** (not decided here): adopt
`sim-harness-core` via the scaffolder rather than by copying sat-rx, and
replace `scripts/check-tb-json.py`'s structural check with the harness's own
`tb.json` schema — which that script already anticipates, its docstring
saying "The schema check replaces this when the harness ships its schema".
**Named unknown blocking that issue**: `2AMLogic/everyblock` returns HTTP 404
to this repo's token (`gh api repos/2AMLogic/everyblock`, 2026-11-14), so the
scaffolder is not reachable from here. Whoever opens that issue must resolve
access first, or get `sim-harness-core` published somewhere this repo can pin
it. Until then this repo keeps `scripts/check-tb-json.py` and writes its
benches without the harness.

### Twice-upstream mechanics, per stamped item

AC requirement: for each item marked "take a stamped copy", whether the
mechanic also exists twice upstream (a Python implementation plus an ngspice
deck expression), since a stamp of the Python half alone leaves the deck half
unstamped.

| Item | Twice upstream? | Consequence |
|---|---|---|
| M2 `coherence_problems` | **No.** It is a pre-flight check on the declared frequency plan, run in Python before a deck is generated; it has no deck counterpart. | Stamp is complete. |
| M3 PSD stack | **No.** It post-processes a sampled record in Python (numpy `rfft`); the deck only writes the samples. | Stamp is complete. |
| M5 `fit_iip3` | **No.** It fits across runs, after per-run bin powers exist; nothing in a deck fits a slope. | Stamp is complete. But its *inputs* are per-bin powers, which the deck computes — and that extraction is M1, which is twice upstream and is written here. The stamp's completeness therefore depends on M1's two halves agreeing, which is M1's known-answer obligation. |
| M6 noise factors | **No.** Closed-form arithmetic over a budget assembled in Python. | Stamp is complete. |
| M1 (written here, not stamped) | **Yes** — `mixfeas.py:90` Python ↔ the deck expression generated by `build_run_lines` (`mixfeas.py:519`). | This is a stated reason for writing M1 here rather than stamping it; the bench PR owns both halves and must make the Python half the oracle for the deck half under `../target-spec.md`'s known-answer case 5 (rectangular/Hann/independent-DFT agreement < 0.05 dB). |

## The `reuse.lock.json` entry shape this record requires

**The decision: declare `"schema": 2`.** A schema-2 document carries
schema 1's `in_tree` array unchanged and adds a sibling `copies` array. Every
entry this repo's bench PR adds goes in `copies`.

**Why a version bump and not a silent additive key.** The fleet's only
existing lock file is `2AMLogic/sg13g2-bandgap`'s (`reuse.lock.json`, read
2026-11-14 via `gh api repos/2AMLogic/sg13g2-bandgap/contents/reuse.lock.json`),
whose entire content is:

```json
{
  "schema": 1,
  "in_tree": [
    { "block": "bandgap_amp", "sibling": "2AMLogic/sg13g2-opamp", "status": "evaluate" }
  ]
}
```

That is **block-level** tracking: a block name, a sibling repo and a status.
There is no commit sha, no source path and no content hash anywhere in
schema 1, so **schema 1 as it exists cannot express a stamped file copy** —
which is exactly what `../target-spec.md` demands. The fields `copies` adds
are the ones divergence detection runs on. A reader built against schema 1
that encountered a schema-1-labelled document containing `copies` would
ignore the array and report nothing wrong — a divergence check that
*could not run* while *looking like* one that passed. `.loom/docs/ci-principles.md`
forbids exactly that shape of failure. Bumping the number makes such a reader
fail loudly on an unknown version instead. Schema 2 is backwards-readable in
the direction that matters: a schema-1 document is a schema-2 document minus
`copies`.

### Entry fields (`copies[]`)

| Field | Required | Meaning |
|---|---|---|
| `sibling` | yes | Upstream repository, `owner/name`. |
| `commit` | yes | **Full 40-character** sha the copy was taken at. Not a branch, not a short sha. |
| `src` | yes | Path of the source file in `sibling` at `commit`. |
| `symbols` | yes | Ordered list of top-level **names** extracted from `src` — a `def`, a `class`, or a module-level assignment. The whole file is `["*"]`. The list must be *closed* in the sense defined below. |
| `dest` | yes | Path in this repo the extract was written to. One entry per `dest`. |
| `src_sha256` | yes | SHA-256 of the complete `src` file bytes at `commit`. Identifies what was read. |
| `extract_sha256` | yes | SHA-256 of the extracted text actually copied: the `symbols` in listed order, each taken by the extraction rule below, joined by one blank line, LF endings, trailing whitespace stripped, final newline. Deterministic from (`commit`, `src`, `symbols`). |
| `dest_sha256` | yes | SHA-256 of `dest` as committed here, including the header. Differs from `extract_sha256` by the header — defined below as the attribution block plus the `import` statements the extract references — which is why both are carried. |
| `license` | yes | Upstream licence identifier (`Apache-2.0` for both repos here). |
| `local_edits` | yes | `"none"` for a verbatim copy, else one line naming each edit. A stamped copy is taken verbatim; this field exists so that a non-`"none"` value is a visible exception, not a quiet one. |
| `divergence` | yes | How a mismatch is detected — the procedure below, stated per entry so an entry is self-describing. |
| `notes` | no | Free text: why this master and not the other, what wraps it locally. |

### Closure of a `symbols` list

A `symbols` list is only useful if the text it names **imports**. Two rules
make that true, and both were needed: measured against the first draft of this
record, the `noisefactor.py` entry named eight functions whose bodies and
default arguments reference five module-level names the list did not carry, so
the specified extract would have raised `NameError` on `T0_K` at import time —
an entry whose divergence check could not run while looking like one that
passed.

**1. The extraction rule, stated completely.** For each name in `symbols`, in
listed order, take:

- a **`def` or `class`**: from the first line of its decorator block, if it has
  one, through the last line of its body. (`NoiseBudget` is
  `@dataclasses.dataclass`-decorated; taking it from the `class` line would copy
  a plain class and silently change its semantics.)
- a **module-level assignment** (`NAME = expr`): from the `NAME =` line through
  the last line of the expression, inline comment included. `K_B` and `T0_K`
  are of this kind and are not reachable under a `def`/`class`-only rule.

Everything else in `src` — the module docstring, section-divider comments,
`import` statements, and any name not listed — is **not** part of the extract.

**2. The closure requirement.** Every module-level name that an extracted
symbol's body, signature, default arguments or decorator references must be
either (a) in the same entry's `symbols`, or (b) an `import` in the `dest`
header. There is no third option: an entry that satisfies neither does not
import, and the bench PR may not repair it by editing the extract (the
"verbatim or not at all" rule). The header is the attribution block plus those
imports, nothing else. It must carry `from __future__ import annotations`
wherever the extract's annotations would otherwise be evaluated too eagerly:
`noisefactor.py` needs it, because `gain_image: float | None` is a **dataclass
field** annotation (evaluated at class creation, and `X | Y` is 3.10+). The
other extracts carry it because upstream does and it costs nothing.

**3. Where a shared preamble goes when two entries share one `src`.** M3 and
M6 both extract from `nfmethod.py` into different `dest` files, and both need
the same five names: `K_B` (`:49`), `T0_K` (`:50`), `MethodError` (`:81-82`),
`NormalizationError` (`:85-86`), `ImageAccountingError` (`:89-90`).

**The decision: a third entry from this `src` owns them.** A `copies` entry
with the same `sibling`/`commit`/`src` and `dest: sim/bench/lib/nfcommon.py`
extracts exactly those five names; `psd.py` and `noisefactor.py` each carry
`from .nfcommon import …` in their header and list neither the constants nor
the exceptions in their own `symbols`.

Why this and not the alternatives:

- **Not duplication into both files.** Duplicating the exception *classes*
  creates two distinct types: `psd.py`'s `NormalizationError` and
  `noisefactor.py`'s would be unrelated classes, so an
  `except NormalizationError` around a call into one module would not catch the
  other's — a defect that only appears once both modules are used together,
  which is precisely how the bench uses them.
- **Not "let `noisefactor.py` import from `psd.py`".** That makes the noise
  module depend on the PSD module (and hence on numpy) for two physical
  constants, and makes `psd.py`'s `symbols` list a mixture of its own mechanic
  and someone else's preamble. The shared preamble is not part of either
  mechanic; giving it its own `dest` says so.
- **The cross-module import is a header line, not a patch.** It lives in the
  part of `dest` that `dest_sha256` covers and `extract_sha256` does not, so
  the extracted bodies stay byte-identical to upstream and divergence check 2
  still works. `local_edits` stays `"none"` for all three entries. Each
  entry's `notes` names the preamble import it carries, so the coupling is
  recorded rather than discovered.

Three entries from one `src` is the cost of the preamble being shared upstream
while the mechanics are split here. It is paid once, in the lock file, where a
reader can see it.

### Divergence detection

Two independent checks, both derivable from the entry alone:

1. **Local tamper**: `sha256(dest)` on disk must equal `dest_sha256`. Catches
   an edit to a stamped copy made without updating the entry.
2. **Upstream drift**: re-fetch `src` at `commit` and confirm
   `sha256 == src_sha256` (the pin resolves to what was read), then re-fetch
   `src` at the sibling's current default-branch head, re-extract `symbols`
   by the rule above, and compare with `extract_sha256`. A mismatch means the
   mechanic has moved upstream: the bench owner re-reads it, decides whether
   to re-stamp, and either way bumps `commit` and the hashes in one commit
   with the reason.

Check 1 is offline and belongs in `npm run check:ci`. Check 2 needs the
network and belongs in a scheduled job, reported as a finding rather than a
hard failure — a drifted upstream is news, not a broken build.

### Worked example (illustrative; **not** to be committed by this issue)

```json
{
  "schema": 2,
  "in_tree": [],
  "copies": [
    {
      "sibling": "2AMLogic/sg13g2-sat-rx",
      "commit": "6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947",
      "src": "sim/mixer-nf-method/nfmethod.py",
      "symbols": ["window", "enbw_bins", "one_sided_psd", "check_parseval",
                  "band_power"],
      "dest": "sim/bench/lib/psd.py",
      "src_sha256": "b52223ed42a5f1519c6014eafdcf6d16a4e87072a380166eb21ec1b3621a094a",
      "extract_sha256": "<computed by the bench PR>",
      "dest_sha256": "<computed by the bench PR>",
      "license": "Apache-2.0",
      "local_edits": "none",
      "divergence": "sha256(dest) == dest_sha256; re-extract symbols from src at sibling HEAD and compare extract_sha256",
      "notes": "M3 of spec/decision-records/0002. Header imports numpy, math, typing and `from .nfcommon import NormalizationError`. numpy>=1.26 required; see that record."
    },
    {
      "sibling": "2AMLogic/sg13g2-sat-rx",
      "commit": "6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947",
      "src": "sim/mixer-nf-method/nfmethod.py",
      "symbols": ["K_B", "T0_K", "MethodError", "NormalizationError",
                  "ImageAccountingError"],
      "dest": "sim/bench/lib/nfcommon.py",
      "src_sha256": "b52223ed42a5f1519c6014eafdcf6d16a4e87072a380166eb21ec1b3621a094a",
      "extract_sha256": "<computed by the bench PR>",
      "dest_sha256": "<computed by the bench PR>",
      "license": "Apache-2.0",
      "local_edits": "none",
      "divergence": "sha256(dest) == dest_sha256; re-extract symbols from src at sibling HEAD and compare extract_sha256",
      "notes": "Shared preamble for M3 and M6 (see 'Closure of a `symbols` list'). Imported by psd.py and noisefactor.py; no numpy."
    }
  ]
}
```

`src_sha256` values measured at `6e5ebaf` for the two masters this record
names, so the bench PR can check its pin resolves to what was read here:

| `src` | `src_sha256` at `6e5ebaf` |
|---|---|
| `sim/mixer-nf-method/nfmethod.py` | `b52223ed42a5f1519c6014eafdcf6d16a4e87072a380166eb21ec1b3621a094a` |
| `sim/mixer-topology-feasibility/mixfeas.py` | `dce5f3099ea3565e3affb4b1e23192e9163fc9571ccb78d78c58283c30308e8e` |
| `sim/lna-linearity/linearity.py` | `67097d9ec04e2eff5115fb2e81daba422e833c536764164f75068f4a7b68d048` |

### Entries the bench PR must add

Five, one per destination file — M2, M3, M5, M6, plus the shared preamble M3
and M6 both import. Every list below is closed in the sense of "Closure of a
`symbols` list": the only names an extract references and does not carry are
the `import`s named in its header column.

| `src` at `6e5ebaf` | `symbols` | `dest` | header imports beyond attribution |
|---|---|---|---|
| `sim/lna-linearity/linearity.py` | `coherence_problems` | `sim/bench/lib/coherence.py` | `from __future__ import annotations` (none other; the body uses only builtins) |
| `sim/mixer-nf-method/nfmethod.py` | `K_B`, `T0_K`, `MethodError`, `NormalizationError`, `ImageAccountingError` | `sim/bench/lib/nfcommon.py` | none |
| `sim/mixer-nf-method/nfmethod.py` | `window`, `enbw_bins`, `one_sided_psd`, `check_parseval`, `band_power` | `sim/bench/lib/psd.py` | `from __future__ import annotations`; `math`; `numpy as np`; `Mapping`, `Sequence` from `typing`; `NormalizationError` from `.nfcommon` |
| `sim/mixer-topology-feasibility/mixfeas.py` | `_finite`, `_linfit`, `fit_iip3` | `sim/bench/lib/iip3.py` | `from __future__ import annotations`; `math` |
| `sim/mixer-nf-method/nfmethod.py` | `NoiseBudget`, `_validate_budget`, `n_out_at_t0`, `ssb_noise_factor`, `dsb_noise_factor`, `db`, `attenuator_ideal_mixer_f_ssb`, `y_factor_f_ssb` | `sim/bench/lib/noisefactor.py` | `from __future__ import annotations`; `dataclasses`; `math`; `Mapping` from `typing`; `K_B`, `T0_K`, `MethodError`, `NormalizationError`, `ImageAccountingError` from `.nfcommon` |

The header-import column is a **statement of what the extract needs**, not a
licence to add anything else: an import the extract does not reference does not
belong in a stamped file. It was measured, not assumed — each list above was
extracted from `src` at `6e5ebaf` by the rule in "Closure of a `symbols` list"
and its free module-level names enumerated; for all five entries that set is
exactly the header column, with one noted asymmetry: `psd.py` references
`NormalizationError` but never `MethodError` (its base class), so only the
former is imported. `noisefactor.py` needs no numpy — M3's numpy consequence is
M3's alone. The bench PR should re-run that check rather than trust this
paragraph, since it is the check that would have caught the first draft.

`in_tree` is `[]` for this repo: no block-level reuse is claimed, only file
copies. **AC 4 is not vacuous** — copies are taken, and these are the
entries.

### What CI does and does not enforce

Read on `main` @ `9f2e9be`:

- `scripts/check-reuse-lock.sh:9-11` — "if `[ ! -f "$ROOT/reuse.lock.json" ]`
  … exit 0". With no lock file it **passes trivially**, and with one it applies
  only `check-tb-json.py`'s structural JSON contract (UTF-8, non-empty top-level
  object, no repeated keys). It checks **none** of the fields above.
- Therefore `npm run check:ci` passing on this record's PR is **not evidence
  that the entry shape is right**. AC 6 is a no-regression check, nothing more.
- Tightening `check-reuse-lock.sh` to enforce schema 2 and run divergence
  check 1 is **recommended** and is explicitly out of scope here (issue #30);
  it belongs to the bench PR or its own issue.

## Findings to file on `sg13g2-sat-rx`

Per `CLAUDE.md` scope discipline, these are findings on that repo and are
**not** acted on here. This record does not change `sg13g2-sat-rx`, and none
of its decisions depends on upstream acting:

1. **Two `fit_iip3` implementations that can disagree.**
   `sim/lna-linearity/linearity.py:582` and
   `sim/mixer-topology-feasibility/mixfeas.py:935` at `6e5ebaf` both fit an
   IM3 slope region; only the former cross-checks the ideal-slope intercept
   against the free-slope intersection and bounds the per-point spread. On
   the same rows they can return different IIP3 values. Upstream should name
   one master. This repo stamps `mixfeas.py`'s and will re-point if upstream
   names the other.
2. **Two `coherence_problems` and three single-bin extraction conventions.**
   `linearity.py:118` vs `mixfeas.py:464`; `mixfeas.py:90` `dft_bin`
   (sine-referenced, `sin φ + j cos φ`) vs `linearity.py:167` `window_dft`
   (real magnitude) vs `pumped.py:170` `phasor_from_integrals`
   (cosine-referenced, conjugate sign). Mixing two of these silently yields a
   wrong phase. Worth one master and one stated convention upstream.
3. **No `reuse.lock.json` and no stamped-copy convention upstream**, while
   two sibling blocks now consume its mechanics. If upstream wants to be a
   declared master, it needs the convention on its side too.

Filing these is a follow-up action on this record, not a blocker for it.

## Alternatives considered

- **Defer D4 again until a bench issue exists.** Rejected: its named owner
  (#3) is closed and no bench issue is open, so there is nothing to defer
  *to*; and the cost of deciding rises once bench code exists, because then
  there is a local implementation whose provenance has to be reconstructed
  rather than chosen.
- **Copy the mechanics now and record the decision implicitly in the bench
  PR.** Rejected: `../target-spec.md` requires the stamp, and an unstamped
  copy is precisely the "second implementation" `CLAUDE.md` forbids. It also
  inverts the order — the lock entry shape has to exist before an entry can
  be written to it.
- **Stamp everything band-independent, including M1, M4 and M7.** Rejected
  per item above: M1 has three inconsistent upstream conventions and a deck
  half we must own; M4's and M7's content *is* a tolerance policy that
  differs from this repo's protocol. A stamp whose load-bearing numbers are
  locally edited is not a stamp.
- **Write everything here, stamp nothing.** Rejected: it is the cheapest
  short-term path and the one the spec rules out. M3 in particular (PSD
  normalisation, ENBW, Parseval) is where a noise bench goes silently wrong,
  and a named master with a reference test set is worth more than a local
  re-derivation.
- **Take `fit_iip3` from `linearity.py` instead of `mixfeas.py`** (the more
  developed estimator). Rejected: its transitive closure reaches
  `point_status` → `limit_violations`, which is LNA DUT-limit policy. The
  extra capability is recovered by a local wrapper instead (M5).
- **Declare `sim/harness/` shared and stamp it from `sg13g2-sat-rx`.**
  Rejected: sat-rx is not its master, and its own README forbids vendoring a
  sibling's harness wholesale (M8).
- **Add `copies` under `"schema": 1`** rather than bumping to 2. Rejected:
  it creates a divergence check that cannot run but looks like one that
  passed.

## Trigger to revisit / what will decide this again

Any one of these supersedes a decision above and needs a new record (or a
revision of this one), not a quiet change:

- **`sg13g2-sat-rx` names a single master** for M1, M2 or M5 (finding 1 or 2
  above acted on), and it is not the one stamped here.
- **A stamped copy's divergence check 2 fires** and re-reading shows the
  mechanic changed materially — not merely moved.
- **A written-here mechanic fails its known-answer case.** If M1 cannot make
  `../target-spec.md`'s case 5 agree to < 0.05 dB across the rectangular FFT,
  the Hann FFT and the independent DFT, the "write it here" call for M1 is
  wrong and the upstream convention should be adopted wholesale instead.
- **`sim-harness-core` becomes reachable** (`2AMLogic/everyblock` resolves,
  or the package is published where this repo can pin it) — then M8's
  recommendation becomes an actionable adoption issue.
- **The spec's convergence or statistical numbers change.** M4 and M7 are
  written here *because* they encode this repo's numbers; a protocol change
  re-opens whether to stamp them.
- **A second block in the fleet adopts schema 2.** If the fleet converges on
  a different entry shape, this repo follows the fleet rather than keeping a
  private schema; the lock file is a shared artifact.

## Consequences

**What becomes possible.** The known-answer bench issue can be written: the
mechanics are enumerated, each has an owner, four have a named master path
with a hash, and the lock-file contract they are recorded under is specified
down to the field. D4 is closed as a blocker on that work.

**What this costs — the bad consequences, stated.**

- **A numpy dependency this repo does not yet have.** M3 and M6 need it.
  `scripts/check-python.sh` runs stdlib-only today and there is no
  `requirements*.txt`; the bench PR must add one and wire CI to install it
  (in a venv — the host rules forbid host-wide installs). Until it does, the
  stamped modules will not import, and `check-python.sh` will byte-compile
  them happily while any test that imports them fails.
- **A private schema until the fleet catches up.** Schema 2 is this repo's
  proposal, adopted by no other block. If the fleet standardises differently,
  this repo rewrites its lock file.
- **Divergence check 2 is unimplemented and unowned.** Nothing runs it today.
  Until someone does, "stamped" means "provenance recorded", not "provenance
  verified" — strictly better than an unstamped copy, strictly weaker than a
  checked one. Do not describe a stamped copy as verified against upstream
  until that job exists.
- **Five local files whose master is elsewhere.** A reviewer of
  `sim/bench/lib/` must know not to refactor `coherence.py`, `nfcommon.py`,
  `psd.py`, `iip3.py` or `noisefactor.py` in place: an improvement belongs
  upstream, or in a local wrapper. The `local_edits: "none"` field is where
  that rule is enforced, and it is enforced by convention, not by a check.
- **A shared preamble gets its own module, and two stamped files import it.**
  `nfcommon.py` exists for no reason a reader of the bench would guess: it is
  there because `nfmethod.py`'s constants and exceptions are shared upstream
  while the mechanics that use them are split across two destinations here. A
  future reader may be tempted to inline it into `noisefactor.py`; the entry
  shape forbids that, because inlining duplicates the exception classes into
  two distinct types.
- **Mechanics split across stamped and written halves.** M5's stamped fit is
  wrapped by a locally written cross-check; M1's Python half is the oracle for
  a deck half we also write. Two-part mechanics are harder to reason about
  than one-part ones. The alternative was worse in each case, but the cost is
  real.
- **The spec text is now slightly stale.** `../target-spec.md` still says D4
  "is decided when #3 builds the bench". Correcting that sentence is a spec
  edit and out of scope for issue #30; it should be folded into the next
  record that touches the measurement protocol. This record's Status section
  is the authoritative correction until then.
- **`npm run check:ci` cannot confirm any of this.** The record's contract is
  on the bench PR and on review, not on CI (see "What CI does and does not
  enforce").
