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

import argparse
import datetime
import math
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from sim.bench import runner                      # noqa: E402
from sim.bench.lib import coherence               # noqa: E402

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

RECIPE = """let a_if = am[64]
let a_sum = am[31936]
let a_lofeed = am[15936]
let a_image = am[15872]
print a_if a_sum a_lofeed a_image
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngspice", default=os.environ.get("NGSPICE", "ngspice"))
    ap.add_argument("--record", default=os.path.join(
        HERE, "records",
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d") + "-v3.json"))
    ap.add_argument("--workdir", default=os.path.join(ROOT, ".tools", "ka1-work"))
    ap.add_argument("--dump-deck", action="store_true")
    args = ap.parse_args(argv)

    if args.dump_deck:
        sys.stdout.write(runner.render_deck(
            RECIPE, DECK_BODY, "if", runner.DT_S, "samples-s1.txt"))
        return 0

    problems = coherence.coherence_problems(
        {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF},
        runner.N_WINDOW * runner.DT_S, runner.DT_S,
        settle_discard_s=runner.DISCARD_S)
    if problems:
        print("KA1: coherence pre-flight FAILED:", *problems, sep="\n  ", file=sys.stderr)
        return 1

    major, version = runner.ngspice_major(args.ngspice)
    if major != 46:
        print(f"KA1: ngspice major {major} != 46 pinned by sim/toolchain.json",
              file=sys.stderr)
        return 1

    os.makedirs(args.workdir, exist_ok=True)
    runs = runner.two_step_run(args.ngspice, DECK_BODY, RECIPE, "if", args.workdir)

    t0 = time.monotonic()
    amps = {tag: runner.window_amplitudes(step, BINS) for tag, step in runs.items()}
    a_if_exp = expected_if_amplitude()
    cg_exp = b_cg_db(a_if_exp)
    cg_meas = b_cg_db(amps["s1"]["if"]["python_dft_w1_v"])
    cg_delta = abs(cg_meas - cg_exp)

    # following-window / step-halving deltas on the IF tone:
    fig_if = {
        "following_window_db": amps["s1"]["if"]["following_window_db"],
        "step_halving_db": abs(runner.db20(
            amps["s1"]["if"]["python_dft_w1_v"] / amps["s2"]["if"]["python_dft_w1_v"])),
    }
    failures = runner.convergence_failures_for({"b_cg_if_tone": fig_if})
    if cg_delta >= TOL_CG_DB:
        failures.append(f"B-CG delta {cg_delta:.4f} dB >= {TOL_CG_DB} dB "
                        f"(measured {cg_meas:.4f} vs closed form {cg_exp:.4f})")
    for name in ("if", "sum"):
        if amps["s1"][name]["m1_delta_db"] >= TOL_M1_DB:
            failures.append(f"M1 deck-vs-python delta on bin '{name}' "
                            f"{amps['s1'][name]['m1_delta_db']:.4f} dB >= {TOL_M1_DB} dB")
    post_s = time.monotonic() - t0

    record = {
        "schema": 1,
        "bench": "ka1-ideal-multiplier",
        "check": "spec/target-spec.md 'Known-answer validation' case 1 "
                 "(ideal multiplier, conversion gain): IF amplitude = k*A/2 x RF",
        "kind": "simulated",
        "elements": "behavioural (multiplier B-source, resistors, capacitor; "
                    "no semiconductor models, no PDK)",
        "corner": "single corner, nominal (behavioural elements carry no PVT)",
        "toolchain": {"ngspice": version, "python": platform.python_version()},
        "protocol": {
            "step_s": runner.DT_S, "step_halved_s": runner.DT_S / 2,
            "window_points": runner.N_WINDOW,
            "window_s": runner.N_WINDOW * runner.DT_S,
            "settle_discard_s": runner.DISCARD_S,
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
            "if_amplitude_v": a_if_exp,
            "sum_amplitude_v": a_if_exp,
            "b_cg_db": cg_exp,
            "formula": "IF amplitude = k*A/2 * V_rf; B-CG = (A_if^2/(2*1000)) / P_avail",
        },
        "measured": {
            "step_12.5ps": {name: amps["s1"][name] for name in BINS},
            "b_cg_db": cg_meas,
            "step_6.25ps_if_amplitude_v": amps["s2"]["if"]["python_dft_w1_v"],
            "image_and_feedthrough_note": "a_image (15872) and a_lofeed (15936) are "
                                          "reported levels of the image bin and LO "
                                          "feedthrough, expected at the numerical floor",
        },
        "deltas": {"b_cg_db": cg_delta,
                   "m1_deck_vs_python_db": max(amps["s1"][n]["m1_delta_db"]
                                               for n in ("if", "sum")),
                   "following_window_db": fig_if["following_window_db"],
                   "step_halving_db": fig_if["step_halving_db"]},
        "tolerances_db": {"b_cg": TOL_CG_DB, "m1_deck_vs_python": TOL_M1_DB,
                          "following_window": 0.1, "step_halving": 0.1},
        "pass": not failures,
        "failures": failures,
        "wall_clock_s": {"ngspice_12.5ps": runs["s1"]["wall_s"],
                         "ngspice_6.25ps": runs["s2"]["wall_s"],
                         "post_processing": post_s},
        "command": "sim/ka1-ideal-multiplier/run.sh",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    }
    runner.write_record(args.record, record)
    print(f"KA1 B-CG measured={cg_meas:.4f} dB expected={cg_exp:.4f} dB "
          f"delta={cg_delta:.4f} dB (tol {TOL_CG_DB}), "
          f"following-window={fig_if['following_window_db']:.4f} dB, "
          f"step-halving={fig_if['step_halving_db']:.4f} dB, "
          f"wall={runs['s1']['wall_s']:.1f}+{runs['s2']['wall_s']:.1f} s")
    print(f"record: {args.record}  pass={not failures}")
    for line in failures:
        print("FAIL:", line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
