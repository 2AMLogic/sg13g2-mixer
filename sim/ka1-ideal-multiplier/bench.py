#!/usr/bin/env python3
"""KA1 -- ideal-multiplier conversion-gain known answer (spec check 1, V3).

A behavioural multiplier v_if = k * v_rf * v_lo with a sinusoidal LO of
amplitude A has an IF amplitude of exactly k*A/2 times the RF amplitude
(image-free); B-CG must return that within 0.05 dB
(spec/target-spec.md, "Known-answer validation" case 1). B-CG is read as
a power: IF-tone power delivered to the stated load over RF available
power from the 50 ohm source, at bin 64, SSB (no image tone); the closed
form applies the same impedances, so the graded delta measures the
extraction, not the port convention.

M2 pre-flight, the M1 two-half agreement (< 0.05 dB, bins 64 and 31936)
and the M4 convergence gate (following window, step halving) run on the
same two sequential ``ngspice -b`` legs. Behavioural elements only (no
HBT models, no PDK), single corner.

Usage: bench.py [--ngspice PATH] [--record PATH] [--workdir DIR]
       bench.py --dump-deck
"""

from __future__ import annotations

import math
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from sim.bench import runner                      # noqa: E402

K_MULT = 1.0                # multiplier constant k (stated on every figure)
A_LO = 0.2236               # LO peak amplitude (row-R3 per-side equivalent)
TOL_CG_DB = 0.05            # spec check 1 tolerance on B-CG
TOL_M1_DB = 0.05            # protocol: deck fft vs independent DFT

DECK_BODY = f"""* KA1: ideal-multiplier conversion-gain known answer -- spec check 1 (V3, behavioural).
* RF: -40 dBm available from 50 ohm ({runner.V_RF_OC * 1e3:.7g} mV peak, open circuit)
*     at f_RF = 2.44140625 GHz (bin 16000). LO: sinusoid, {A_LO} V peak at
* f_LO = 2.431640625 GHz (bin 15936), ideal source. DUT: behavioural multiplier
* v(if) = k * V(rf) * V(lo), k = {K_MULT}; ideal source into the R9 load
* (1 kohm || 2 pF), single-ended. No image tone (SSB). No PDK, no HBT models.
vrf srcrf 0 SIN(0 6.3245553m 2.44140625g)
rsrf srcrf rf 50
vlo lo 0 SIN(0 {A_LO} 2.431640625g)
bif if 0 V = {K_MULT} * V(rf) * V(lo)
rl if 0 1k
cl if 0 2p
"""

BINS = {"if": 64, "sum": 31936, "lofeed": 15936, "image": 15872}


def expected_if_amplitude():
    """k*A/2 times the RF node amplitude (the RF node is open-circuit)."""
    return K_MULT * A_LO / 2.0 * runner.V_RF_OC


def b_cg_db(if_amplitude):
    """B-CG power gain: IF-tone power in the stated load over RF available."""
    p_if = if_amplitude ** 2 / (2.0 * runner.R_LOAD)
    return runner.db10(p_if / runner.P_AVAIL_W)


def main(argv=None):
    args = runner.bench_args(os.path.join(ROOT, ".tools", "ka1-work"), argv)

    if args.dump_deck:
        return runner.dump_deck(BINS, DECK_BODY, "if")

    runner.coherence_gate(
        "KA1", {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF})

    version = runner.require_pinned_ngspice(args.ngspice, "KA1")

    os.makedirs(args.workdir, exist_ok=True)
    runs = runner.two_step_run(args.ngspice, DECK_BODY, BINS, "if", args.workdir)

    t0 = time.monotonic()
    readings = runner.tone_readings(runs, BINS)
    cg_exp = 10.0 * math.log10((K_MULT * A_LO / 2) ** 2 * 4 * runner.RS_RF / runner.R_LOAD)
    deltas, failures = runner.grade_tones(readings, ("if", "sum"), TOL_M1_DB)
    deltas["b_cg_db"], gain_failures = runner.grade_known_answer(
        readings, b_cg_db, cg_exp, TOL_CG_DB, "B-CG")
    failures.extend(gain_failures)
    gains = {}
    floor = {}
    for leg, windows in readings.items():
        gains[leg], floor[leg] = {}, {}
        for window, tones in windows.items():
            gains[leg][window] = b_cg_db(tones["if"]["python_dft_v"])
            floor[leg][window] = {name: tones.pop(name) for name in ("image", "lofeed")}
    post_s = time.monotonic() - t0

    record = {
        "schema": 2,
        "bench": "ka1-ideal-multiplier",
        "check": "spec/target-spec.md 'Known-answer validation' case 1 "
                 "(ideal multiplier, conversion gain): IF amplitude = k*A/2 x RF",
        "kind": "simulated",
        "elements": "behavioural (multiplier B-source, resistors, capacitor; "
                    "no semiconductor models, no PDK)",
        "corner": "single corner, nominal (behavioural elements carry no PVT)",
        "toolchain": {"ngspice": version, "python": platform.python_version()},
        "protocol": {
            **runner.protocol_common(),
            "window": "rectangular (coherent tones); Hann cross-check is ka5's "
                      "graded reading, M1 two-half agreement gated here",
            "bins": dict(BINS),
            "tones_hz": {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF,
                         "sum": runner.F_RF + runner.F_LO},
            "ports": {"rf_source": f"{runner.RS_RF:.0f} ohm single-ended, "
                                   f"-40 dBm available ({runner.P_AVAIL_W * 1e7:g}e-7 W)",
                      "lo_source": f"ideal, sinusoidal, {A_LO} V peak "
                                   f"(row-R3 per-side equivalent), {runner.RS_RF:.0f} ohm convention",
                      "load": f"R9: {runner.R_LOAD:.0f} ohm || {runner.C_LOAD * 1e12:g} pF"},
            "sideband": "SSB (image tone absent)",
        },
        "expected": {
            "if_amplitude_v": expected_if_amplitude(),
            "b_cg_db": cg_exp,
            "formula": "B-CG = 10*log10((k*A/2)^2 * 4*R_source/R_load)",
        },
        "measured": {"tone_amplitudes": readings, "b_cg_db": gains},
        "numerical_floor_diagnostics": {
            "note": "The ideal circuit has no image or LO feedthrough tone. Raw residual "
                    "voltages are recorded separately from graded tone levels.",
            "amplitudes": floor,
        },
        "deltas": deltas,
        "tolerances_db": {"b_cg": TOL_CG_DB, "m1_deck_vs_python": TOL_M1_DB,
                          "following_window": 0.1, "step_halving": 0.1},
        "pass": not failures,
        "failures": failures,
        "wall_clock_s": runner.wall_clock(runs, post_s),
        "command": "sim/ka1-ideal-multiplier/run.sh",
        "date": runner.record_date(),
    }
    path = runner.save_bench_record(HERE, args.record, record)
    return runner.bench_report(
        f"KA1 expected B-CG={cg_exp:.4f} dB, worst error={deltas['b_cg_db']:.4f} dB",
        path, failures)


if __name__ == "__main__":
    sys.exit(main())
