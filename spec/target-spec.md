# Target specification

**Status: PROPOSED — ratified by the operator's approval of the PR that
carries it** (issue [#2](https://github.com/2AMLogic/sg13g2-mixer/issues/2);
decision record
[0001](decision-records/0001-target-spec-ratification.md)). This is the same
ratification-via-PR path `sg13g2-lna` used. No row below is ratified until
that approval lands; an agent does not mark a row ratified, and no value was
relaxed to make a result pass. Every row that carries a number from the former
README draft carries it unchanged.

Row status vocabulary:

- **PROPOSED** — becomes binding when this PR is approved.
- **DERIVED** — computed from other rows by the arithmetic shown; changes only
  when its inputs change.
- **INTERFACE** — copied from `sg13g2-lna` at the pinned commit (below); owned
  upstream, not decided here.
- **DEFERRED** — an explicit open item with an owner (decision record §Deferred).

Everything in this document is a *target*. No figure in it is a result; every
result that eventually answers a row is a **simulated** figure, labelled with
its corner and testbench, and lives append-only under `sim/`.

## Interface to `sg13g2-lna`

Source: `2AMLogic/sg13g2-lna` at commit
[`5532789887c6c10abbaba541fb9294ce72b8cf5e`](https://github.com/2AMLogic/sg13g2-lna/tree/5532789887c6c10abbaba541fb9294ce72b8cf5e),
files `spec/target-spec.md` and `spec/ratified-rows.json`, read 2026-10-17.
`sg13g2-lna` `main` has moved since (HEAD `02c5ba2…` at read time); this
document does **not** re-pin silently — a re-pin is its own decision record.
The LNA's current pass/fail standing is not restated here; read its
[spec](https://github.com/2AMLogic/sg13g2-lna/blob/5532789887c6c10abbaba541fb9294ce72b8cf5e/spec/target-spec.md)
("Status vs. the committed evidence" column).

| LNA row | Value copied | LNA status | Used here as |
|---|---|---|---|
| Band | 2400–2483.5 MHz | RATIFIED | the RF band of this block |
| Port convention | 50 Ω ports, T0 = 290 K for NF | RATIFIED (Gain/NF/S11/S22 rows) | the RF-input reference impedance |
| Supply | 1.80 V ± 10 % (1.62–1.98 V), single rail | RATIFIED | this block's supply |
| Gain (S21) | > 15 dB across band | RATIFIED | G1 in the cascade |
| Noise figure | < 1.5 dB across band, T0 = 290 K | RATIFIED | F1 in the cascade |
| Output match (S22) | < −10 dB, 50 Ω reference | RATIFIED | what the mixer RF input must be matched *to* (requirement stated below, not a claim about the LNA) |
| IIP3 numeric | > 0 dBm (former draft) | **NOT RATIFIED** (`status: not-ratified` in `ratified-rows.json`) | an *assumption* in the cascade, provisional |
| IIP3 protocol | two-tone, f1 = 2.44140625 GHz, Δ = 7.62939453125 MHz, FFT N = 65536 at 4 ps, rectangular window, coherent bins, 1 µs discarded, double drive levels with 3:1 IM3 slope check | RATIFIED | the pattern this block's IIP3 bench follows (parameters adapted below) |
| Corner box | process {typ, bcs, wcs} × {−40, 27, 125} °C × {1.62, 1.80, 1.98} V | RATIFIED | the base of this block's PVT box |
| PDK pin | IHP-Open-PDK v0.3.0, `5cccb161f7492697cfa52eb14dc03beb00bdca9e` (`sim/pdk.json` there) | — | referenced here; the pin is *committed* by [#3](https://github.com/2AMLogic/sg13g2-mixer/issues/3), not this issue |

**Interface requirement placed on this block (and findings that go upstream).**
The mixer RF input must present a 50 Ω single-ended match to the LNA output
(S11 < −10 dB across the band, row R2). The LNA's own S22 row is ratified; its
committed design's standing against that row is the LNA repo's to track. Any
output-match or linearity shortfall found when the two are cascaded is filed on
`sg13g2-lna`, not worked around here.

## Cascade arithmetic

Inputs: G1 = 15 dB (LNA gain, ratified minimum), NF1 = 1.5 dB (LNA NF, ratified
maximum), IIP3_LNA = 0 dBm (**the unratified LNA draft, assumed, provisional**).
All ports 50 Ω, T0 = 290 K. The ratified LNA values are worst-case-direction
bounds (gain a minimum, NF a maximum), so the cascade below is conservative in
gain and in NF; it is not a prediction of the committed LNA.

### Noise

Friis with a single-sideband mixer figure, F = F1 + (F_mix − 1)/G1:

| Mixer SSB NF (row) | F_mix | Cascade NF (Friis, SSB) | Cascade NF (image unrejected, F = 2·F1 + (F_mix − 2)/G1) |
|---|---|---|---|
| 15 dB (fallback) | 31.62 | **3.77 dB** | 5.75 dB |
| 12 dB (target) | 15.85 | **2.75 dB** | 5.14 dB |
| 9 dB (stretch) | 7.94 | **2.13 dB** | 4.79 dB |

The second column matters because the single low IF (1–50 MHz class) puts the
image 2×IF from the signal, inside the LNA band: the LNA's own noise at the
image frequency folds into the IF too. The SSB-Friis column assumes that
image-band noise is absent; the "unrejected" column assumes the LNA presents
the same noise in both sidebands. Which applies is a system fact (image
filtering, or the I/Q stretch), not a mixer property, so **the mixer NF row is
a standalone SSB figure** with the image termination stated in the bench
protocol; the cascade table is the context for choosing it. The 12 dB target
costs 1.25 dB of cascade NF over the LNA alone on the SSB-Friis view
(1.5 → 2.75 dB); every 3 dB of mixer NF improvement buys back less than
0.7 dB of cascade NF at this LNA gain. Gain row R5 matters as much as NF row
R6: the mixer NF is divided by G1 = 15 dB (31.6×).

### Linearity

1/IIP3_tot = 1/IIP3_LNA + G1/IIP3_mix, all in mW and referred to the LNA input:

| Mixer IIP3 (row R7) | Cascade IIP3 at LNA input (IIP3_LNA = 0 dBm, assumed) |
|---|---|
| −5 dBm (fallback) | −20.0 dBm |
| 0 dBm (target) | −15.1 dBm |
| +5 dBm (stretch) | −10.4 dBm |

Reading: the mixer, not the LNA, sets the cascade IIP3 at any LNA gain near
15 dB; the cascade is 15 dB worse than the mixer's own IIP3 plus a small LNA
term. The numeric IIP3 target for the **standalone mixer** is therefore kept at
the former README draft and is **not derived from the cascade**, because the
upstream number it would derive from is itself unratified. Stated inversely
(and provisionally): holding a cascade IIP3 of −10 / −12 / −15 dBm with the
assumed 0 dBm LNA needs a mixer IIP3 of +5.5 / +3.3 / +0.1 dBm. Mixer targets
are standalone; the cascade requirement is recorded here so the system-level
consequence is visible, and it must be re-derived when the LNA IIP3 is
ratified (decision record, Deferred D1).

## PVT corner box

Applies to every recorded result (project rule: PVT corners on every recorded
result). Model files live in
`<PDK_ROOT>/ihp-sg13g2/libs.tech/ngspice/models/`; section names below were
read from the v0.3.0 install on 2026-10-17.

| Axis | Values | File : section |
|---|---|---|
| HBT process | typ, bcs, wcs | `cornerHBT.lib` : `hbt_typ`, `hbt_bcs`, `hbt_wcs` |
| MOS process (LV; only if LV MOS is used) | typ, slow, fast, SF, FS | `cornerMOSlv.lib` : `mos_tt`, `mos_ss`, `mos_ff`, `mos_sf`, `mos_fs` |
| MOS process (HV; only if HV MOS is used) | same | `cornerMOShv.lib` : `mos_tt`, `mos_ss`, `mos_ff`, `mos_sf`, `mos_fs` |
| Resistor | typ, bcs, wcs | `cornerRES.lib` : `res_typ`, `res_bcs`, `res_wcs` |
| Capacitor | typ, bcs, wcs | `cornerCAP.lib` : `cap_typ`, `cap_bcs`, `cap_wcs` |
| Temperature | −40, 27, 125 °C | `.temp` |
| Supply | 1.62, 1.80, 1.98 V | `VDD` |
| LO drive | nominal −6, −3, 0, +3, +6 dB around the row-R3 level (swept; the nominal-drive cell is the recorded one for the process/T/V grid) | bench parameter |

Process sections are applied as a consistent set (all `typ`, all slow, all
fast) unless a result states otherwise. The HBT library ships exactly three
real sections; there is no independent SF/FS HBT corner. Mismatch/`*_stat`
sections exist in the same files and are **not** in this box; Monte Carlo is a
separate stated scope when it is added, and until then no row has statistical
evidence.

**HBT model-card validity window** (`npn13G2`, `sg13g2_hbt_mod.lib` header, read from
the v0.3.0 install 2026-10-17; same statement `sg13g2-lna` records): maximum
collector-to-emitter voltage 1.6 V, `ic < 0.003·Nx A`,
`vbe` 0.65–0.96 V, `vce` 0.4–2.0 V, −40…+125 °C, `NX` = 1–10. A mixer
switching quad drives devices through cut-off and saturation every LO cycle, so
it will leave the `vbe` / `vce` window transiently by construction. **Rule:**
every simulated result reports, per corner, the peak `vce`, `vbe` and `ic/Nx`
seen by each HBT over the analysis window, and flags a
cell that exceeds the window or `vce_max`. Peak `vce` above 1.6 V is a reliability
finding, not a footnote; a cell outside the window is reported as
**outside model validity** and cannot be counted as meeting a row.

Not covered (disclosed, not hidden): there is no inductor SPICE/EM model in
the PDK (per `sg13g2-lna`), so passive-inductor-dependent topologies cannot be
simulated with PDK models; layout/parasitic extraction, pads/package, and
self-heating beyond the VBIC thermal network at ambient.

## Ratified-target table

Columns: **Fallback / Target / Stretch** are the three levels of the
maturity ladder. "Binding conditions" are the conditions every figure must
state. "Bench" names the planned testbench (protocols in the next section).
Row ids are stable (`R1`…); the README table is derived from this one.

| ID | Parameter | Fallback | Target | Stretch | Binding conditions | Bench | Status |
|---|---|---|---|---|---|---|---|
| R1 | RF band | 2400–2483.5 MHz | 2400–2483.5 MHz | — | LNA band, copied from the pinned `sg13g2-lna` (INTERFACE). In-band sweep ≥ 11 points across the band, LO retuned per point (fixed IF) | B-CG | INTERFACE |
| R2 | RF input | 50 Ω single-ended; ideal balun at the bench boundary, its use stated on every figure | 50 Ω single-ended, S11 < −10 dB across band; single-to-differential conversion by an **active** stage, no inductors | on-chip balun included | S11 from the transient bench's small-signal-at-LO-on mapping (B-S11 below), LO at row-R3 level; 50 Ω source | B-S11 | PROPOSED |
| R3 | LO input | 0 dBm available from 50 Ω, sine, differential, **low-side** LO, f_LO = f_RF − f_IF | same | same, on-chip LO buffer included in power | Waveform: sinusoid; amplitude swept ±6 dB around nominal (PVT box). Frequency plan: low-side (image at f_LO − f_IF, 2·f_IF below signal). LO source is ideal in every bench; this row is the requirement on whatever supplies it | all | PROPOSED |
| R4 | LO phase noise (requirement on the LO source) | ≤ −100 dBc/Hz @ 1 MHz | ≤ −110 dBc/Hz @ 1 MHz | ≤ −120 dBc/Hz @ 1 MHz | **Provisional placeholder** pending a system blocker/reciprocal-mixing budget that does not exist yet; not verified in simulation by this block (the bench LO is ideal). Deferred D2 | — | PROPOSED, provisional |
| R5 | Conversion gain (voltage, 50 Ω source, row-R9 load; stated as power-equivalent also) | > 5 dB | > 10 dB | > 15 dB | SSB signal (image tone absent), f_IF = 9.765625 MHz, RF at −40 dBm available (small-signal regime verified by a 6 dB lower step differing < 0.2 dB), PVT box | B-CG | PROPOSED (README draft values, unchanged) |
| R6 | SSB noise figure | < 15 dB | < 12 dB | < 9 dB | **SSB**, T0 = 290 K, source 50 Ω at 290 K on the RF port, image-frequency port terminated by the same 50 Ω source at 290 K, noise evaluated at the IF over the B-NF band, LO at row-R3 level, PVT box. Not a DSB number; DSB = SSB − 3 dB is *not* assumed, it is measured | B-NF | PROPOSED (README draft values, unchanged) |
| R7 | IIP3 (input-referred, available source power) | > −5 dBm | > 0 dBm | > +5 dBm | Two-tone, tones as in B-IP3, standalone mixer; cascade value is derived (above) and is provisional because the LNA IIP3 is unratified | B-IP3 | PROPOSED (README draft values, unchanged); cascade view DERIVED/provisional |
| R8 | Input P1dB (available source power) | > −15 dBm | > −10 dBm | > −5 dBm | Single-tone compression at f_IF, 1 dB below the small-signal conversion gain, PVT box. Consistency: P1dB ≈ IIP3 − 9.6 dB for a third-order-dominated stage (−14.6 / −9.6 / −4.6 dBm, rounded down) — the measured values need not satisfy it | B-P1 | PROPOSED |
| R9 | IF | f_IF = 9.765625 MHz (64 bins of the B-CG window), single low IF; load: differential 1 kΩ ∥ 2 pF (the stated load); IF −1 dB bandwidth ≥ 10 MHz centred on f_IF | same; IF output differential, source impedance reported | zero-IF quadrature (I/Q) pair | f_IF is a bench-coherent value inside the 1–50 MHz class; the load is a placeholder for a following filter/ADC driver and is part of the figure, changing it re-states every R5–R8 figure. Zero-IF I/Q does not drive the core architecture until the single-IF target closes | B-CG | PROPOSED |
| R10 | LO-to-RF isolation | > 30 dB | > 40 dB | > 50 dB | Power at the LO fundamental measured at the RF port into 50 Ω, referred to the LO available power, with the RF port terminated in 50 Ω, PVT box | B-ISO | PROPOSED (README draft values, unchanged) |
| R11 | LO-to-IF isolation | > 20 dB | > 30 dB | > 40 dB | LO-fundamental power at the IF port into the R9 load, referred to the LO available power; measured on the same FFT as B-ISO | B-ISO | PROPOSED |
| R12 | RF-to-IF isolation | > 20 dB | > 30 dB | > 40 dB | RF-fundamental power at the IF port with LO at row-R3 level, referred to the RF available power | B-ISO | PROPOSED |
| R13 | Supply / DC power | 1.80 V ± 10 %, < 20 mW | 1.80 V ± 10 %, < 10 mW | < 5 mW | Supply is the LNA's (INTERFACE); power is whole block including LO buffer and bias, excluding the LO source, DC from the transient average over the analysis window, PVT box | B-CG (DC) | Supply INTERFACE; power PROPOSED (README draft values, unchanged) |
| R14 | Area | < 0.10 mm² | < 0.05 mm² | < 0.03 mm² | Placeholder with no evidence basis; core only, pads and fill excluded, measured from the layout bounding box. To be re-baselined when a schematic exists, through a decision record | layout | PROPOSED, provisional |
| R15 | Signoff | DRC + LVS clean | DRC + LVS clean, post-layout re-verified | — | `klt` DRC and LVS reports, same corner box re-run on the extracted netlist | layout | PROPOSED (README draft values, unchanged) |

## Measurement protocol

There is no periodic steady-state analysis in ngspice. **Every number below
comes from a transient run**, so each states the same set: LO drive, FFT
length and window, discarded settling time, SSB or DSB, port impedances. The
numbers here are the bench contract; a bench may tighten them but may not
loosen them without a decision record.

**Common setup (all benches).**

- Time step 12.5 ps (≥ 33 points per LO period at 2.4 GHz); analysis window
  N = 2^19 = 524 288 points = 6.5536 µs; bin width Δ = 152.587890625 kHz.
- Window: **rectangular**, with all tones placed on exact bin centres
  (coherent sampling) so there is no leakage; a Hann-windowed FFT is the
  cross-check. ngspice `fft` and an independent coherent DFT of the same
  samples must agree to < 0.05 dB on every reported tone (as `sg13g2-lna`
  does).
- Tone placement (bin index × Δ): f_RF = 16 000 Δ = 2.44140625 GHz (the LNA
  protocol's f1); f_IF = 64 Δ = 9.765625 MHz; f_LO = f_RF − f_IF = 15 936 Δ =
  2.431640625 GHz (low-side); image at f_LO − f_IF = 15 872 Δ. In-band points
  of the R1 sweep keep f_IF fixed and retune RF and LO to bins.
- Settling: discard ≥ 2 µs before the window (≥ 10× the slowest IF/bias time
  constant, to be confirmed per design); convergence check — the same
  analysis on the following window must reproduce every reported figure to
  < 0.1 dB, or the discard is lengthened and the run repeated.
- Ports: RF source 50 Ω (single-ended, balun per R2 and stated), LO source
  50 Ω, IF load per R9. Every recorded figure states LO drive, FFT length and
  window, discarded time, SSB/DSB, and these impedances.
- Time-step convergence: a result is reported only if halving the step (6.25 ps)
  moves it < 0.1 dB on a sampled corner.

**B-CG — conversion gain.** One RF tone at −40 dBm available (a 6 dB lower
step must agree within 0.2 dB, else report compression), LO at row-R3 level.
CG = IF-tone power delivered to the R9 load over RF available power, read at
bin 64; the image bin carries no tone. SSB. DC power from the same run.
Sweep: 11 in-band points × PVT box × LO drive sweep.

**B-NF — SSB noise figure.** Direct output-noise method, because there is no
pnoise: noise is injected as explicit transient noise sources (thermal for
the 50 Ω source and each resistor, shot and base-resistance thermal for each
HBT at its instantaneous bias, computed from the simulated operating point
each LO phase), the IF output noise PSD is estimated by Welch averaging over
the B-NF band (f_IF ± 1 MHz) with a Hann window and ≥ 256 independent
averages (statistical error reported; ≤ 0.3 dB 1-σ), and
NF_SSB = N_out,total / N_out,signal-source, where N_out,signal-source is the
IF noise PSD due to the signal-sideband source alone (kT0 · G_c², with G_c the
B-CG conversion gain at the same bias), and the total comes from the run with
all noise sources active. Both sidebands are modelled: the image port is
terminated by a 50 Ω source at 290 K, so its noise folds into N_out,total as
the SSB definition requires. **This method is itself
the main risk in the project and is not assumed to work:** the first work item
under this row is to confirm that ngspice transient noise sources reproduce a
known noise PSD (below) and what injection of per-device noise looks like; if
they cannot, the spec records the shortfall in a decision record rather than
substituting a different quantity. Mixer-flicker noise at IF is included
(f_IF is low) and reported per device class.

**B-IP3 — IIP3.** Two tones f1 = f_RF (bin 16 000), f2 = f1 + 50 Δ
(= f1 + 7.62939453125 MHz, the LNA's tone spacing), LO as above. IF tones at
bins 64 and 114; IM3 at bins 14 and 164 (all distinct from harmonics and
from each other). Drive at two tone levels (2 dB apart or ≥ 6 dB apart,
double levels as in the LNA protocol), **the 3:1 IM3 slope check is
mandatory**; a result that fails slope 3 ± 0.3 is reported as compression-
contaminated and not as an IIP3. IIP3 = P_in,avail + (P_IF − P_IM3)/2.
SSB signal, no image tone; 50 Ω source, R9 load.

**B-P1 — P1dB.** Single tone at bin 16 000, available power swept from −40 dBm
up in 1 dB steps until CG falls 1 dB (interpolated); same window, LO and
load; reported with the compression tolerance.

**B-S11 — RF input match.** S11 of the RF port with the LO on is extracted
by a single-tone transient at −40 dBm available: S11 from the reflected
wave a_reflected / a_incident at the RF frequency on the same FFT. Small-signal
S11 with the LO off is reported alongside but does not satisfy R2.

**B-ISO — isolation.** One run per pair with the third port terminated in
its stated impedance: LO tone present, RF tone absent for LO-to-RF and
LO-to-IF; RF tone present for RF-to-IF. Powers read at the fundamentals on
the same FFT.

**Known-answer validation (before the bench touches the design).** A bench
change or a new corner set re-runs these first; nothing is recorded as a
design result until all pass.

1. *Ideal multiplier, conversion gain.* Behavioural multiplier v_out =
   k · v_RF · v_LO with a sinusoidal LO of amplitude A. The IF amplitude is
   exactly k·A/2 times the RF amplitude (image-free). B-CG must return that
   within 0.05 dB.
2. *Hard-switched ideal mixer.* A double-balanced ideal-switch mixer
   (switch resistance → 0, square-wave LO) delivers an IF voltage of 2/π ×
   the RF voltage (conversion gain −3.92 dB into a matched load); B-CG must
   match within the stated convergence tolerance.
3. *Noise.* The ideal multiplier fed from the 290 K 50 Ω source with no added
   noise has SSB NF = 3.01 dB (image noise folds in) and DSB NF = 0 dB; B-NF
   must return both within its stated statistical error. A second case adds a
   noise generator of known PSD at the output and must return the closed-form
   NF.
4. *IIP3.* The ideal multiplier followed by (or preceded by) a polynomial
   y = a1·x + a3·x³ with known coefficients has IIP3 amplitude
   √(4·a1/(3·|a3|)) (input-referred, converted to available power); B-IP3 must
   return it within 0.5 dB with the 3:1 slope check passing.
5. *Window/coherence.* A single coherent tone must read the same power on the
   rectangular and Hann FFT and on the independent DFT within 0.05 dB.

The shared, band-independent parts of this bench (tone placement, coherent
DFT, convergence and slope checks) have one master. If `sg13g2-sat-rx`'s
bench code is taken, it comes by a stamped copy tracked in `reuse.lock.json`,
not a second implementation; reading its methodology is not copying its code.
Which of its mechanics are band-independent is decided when #3 builds the
bench (decision record, Deferred D4).

## What this specification does not do

- Design the LNA, restate its pass/fail status, or choose its operating point.
- Design the LO source (R3/R4 are requirements on it).
- Pin the PDK, build the OSDI models or run a smoke simulation (#3).
- Contain any simulation result.
