#!/usr/bin/env python3
"""KA2 -- hard-switched ideal-mixer known answer (spec check 2, V3).

A double-balanced ideal-switch mixer (switch resistance -> 0, square-wave
LO) delivers an IF voltage of 2/pi times the RF voltage
(spec/target-spec.md, "Known-answer validation" case 2); the voltage ratio
is graded within the protocol's convergence tolerance (0.1 dB), and the
power-gain diagnostic converts it with the stated source and load
impedances before any comparison with row R5. The switch is behavioural:
v_if = s(t) * V(rf) with s a +/-1 square wave (1 ps edges) at f_LO, so
the IF amplitude's closed form is (2/pi) * V_rf at bin 64.

M2 pre-flight, the M1 two-half agreement (< 0.05 dB) and the M4
convergence gate (following window, step halving) run on the same two
sequential ``ngspice -b`` legs. Behavioural elements only (no HBT models,
no PDK), single corner.

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

EDGE_S = 1.0e-12            # square-wave rise/fall time (stated on the figure)
TOL_IF_DB = 0.1             # protocol convergence tolerance (spec check 2)
TOL_M1_DB = 0.05            # protocol: deck fft vs independent DFT

_T_LO = 1.0 / runner.F_LO
_PW = _T_LO / 2.0 - EDGE_S

DECK_BODY = f"""* KA2: double-balanced ideal-switch mixer known answer -- spec check 2 (V3, behavioural).
* RF: -40 dBm available from 50 ohm ({runner.V_RF_OC * 1e3:.7g} mV peak, open circuit)
*     at f_RF = 2.44140625 GHz (bin 16000). LO: square wave +/-1 at f_LO =
* 2.431640625 GHz (bin 15936), {EDGE_S * 1e12:g} ps edges (switch resistance -> 0).
* DUT: behavioural switch mixer v(if) = s(t) * V(rf); ideal source into the
* R9 load (1 kohm || 2 pF), single-ended. IF voltage = 2/pi x RF voltage.
* No PDK, no HBT models. Voltage-ratio check; the power-gain diagnostic in
* the record uses the stated 50 ohm source and 1 kohm load before any
* comparison with row R5.
vrf srcrf 0 SIN(0 6.3245553m 2.44140625g)
rsrf srcrf rf 50
vlo lo 0 PULSE(-1 1 0 1p 1p {_PW * 1e12:.11f}p {_T_LO * 1e12:.11f}p)
bif if 0 V = V(lo) * V(rf)
rl if 0 1k
cl if 0 2p
"""

BINS = {"if": 64, "sum": 31936, "3lo_rf": 31808}


def expected_if_amplitude():
    """(2/pi) x the RF node amplitude (the RF node is open-circuit)."""
    return 2.0 / math.pi * runner.V_RF_OC


def power_gain_db(if_amplitude):
    """Diagnostic: IF-tone power in the stated load over RF available power."""
    p_if = if_amplitude ** 2 / (2.0 * runner.R_LOAD)
    return runner.db10(p_if / runner.P_AVAIL_W)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngspice", type=runner.ngspice_command,
                    default=os.environ.get("NGSPICE", "ngspice"))
    ap.add_argument("--record", help="output path (default: new UTC-stamped evidence record)")
    ap.add_argument("--workdir", default=os.path.join(ROOT, ".tools", "ka2-work"))
    ap.add_argument("--dump-deck", action="store_true")
    args = ap.parse_args(argv)

    if args.dump_deck:
        sys.stdout.write(runner.render_deck(
            BINS, DECK_BODY, "if", runner.DT_S, "samples-s1.txt"))
        return 0

    problems = coherence.coherence_problems(
        {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF},
        runner.N_WINDOW * runner.DT_S, runner.DT_S,
        settle_discard_s=runner.DISCARD_S)
    if problems:
        print("KA2: coherence pre-flight FAILED:", *problems, sep="\n  ", file=sys.stderr)
        return 1

    major, version = runner.ngspice_major(args.ngspice)
    if major != 46:
        print(f"KA2: ngspice major {major} != 46 pinned by sim/toolchain.json",
              file=sys.stderr)
        return 1

    os.makedirs(args.workdir, exist_ok=True)
    runs = runner.two_step_run(args.ngspice, DECK_BODY, BINS, "if", args.workdir)

    t0 = time.monotonic()
    readings = runner.tone_readings(runs, BINS)
    a_if_exp = expected_if_amplitude()
    deltas, failures = runner.grade_tones(readings, BINS, TOL_M1_DB)
    deltas["if_voltage_db"], if_failures = runner.grade_known_answer(
        readings, runner.db20, runner.db20(a_if_exp), TOL_IF_DB, "IF voltage")
    failures.extend(if_failures)
    power_gain = {
        leg: {window: power_gain_db(tones["if"]["python_dft_v"]) for window, tones in windows.items()}
        for leg, windows in readings.items()
    }
    post_s = time.monotonic() - t0

    record = {
        "schema": 2,
        "bench": "ka2-switch-mixer",
        "check": "spec/target-spec.md 'Known-answer validation' case 2 "
                 "(hard-switched ideal mixer): IF voltage = 2/pi x RF voltage",
        "kind": "simulated",
        "elements": "behavioural (switch B-source, pulse source, resistors, "
                    "capacitor; no semiconductor models, no PDK)",
        "corner": "single corner, nominal (behavioural elements carry no PVT)",
        "toolchain": {"ngspice": version, "python": platform.python_version()},
        "protocol": {
            "legs": {"s1": "12.5 ps", "s2": "6.25 ps"},
            "windows": {"w1": "analysis", "w2": "following"},
            "step_s": runner.DT_S, "step_halved_s": runner.DT_S / 2,
            "window_points": runner.N_WINDOW,
            "window_s": runner.N_WINDOW * runner.DT_S,
            "settle_discard_s": runner.DISCARD_S,
            "window": "rectangular (coherent tones); Hann cross-check is ka5's "
                      "graded reading, M1 two-half agreement gated here",
            "bins": dict(BINS),
            "tones_hz": {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF,
                         "sum": runner.F_RF + runner.F_LO,
                         "3lo_minus_rf": 3 * runner.F_LO - runner.F_RF},
            "ports": {"rf_source": f"{runner.RS_RF:.0f} ohm single-ended, "
                                   f"-40 dBm available ({runner.P_AVAIL_W * 1e7:g}e-7 W)",
                      "lo_source": f"ideal square wave +/-1, {EDGE_S * 1e12:g} ps edges",
                      "load": f"R9: {runner.R_LOAD:.0f} ohm || {runner.C_LOAD * 1e12:g} pF"},
            "sideband": "SSB (image tone absent)",
            "lo_edges_note": "LO edges are not on the sample grid; edge-time "
                             "quantisation is second-order on the fundamental "
                             "amplitude and is what the step-halving leg bounds",
        },
        "expected": {
            "if_amplitude_v": a_if_exp,
            "formula": "IF amplitude = (2/pi) * V_rf (square-wave fundamental 4/pi, "
                       "mixed down by 1/2); -3.92 dB voltage conversion into a "
                       "matched load",
            "power_gain_diagnostic_db": power_gain_db(a_if_exp),
        },
        "measured": {"tone_amplitudes": readings, "power_gain_diagnostic_db": power_gain},
        "deltas": deltas,
        "tolerances_db": {"if_voltage": TOL_IF_DB, "m1_deck_vs_python": TOL_M1_DB,
                          "following_window": 0.1, "step_halving": 0.1},
        "pass": not failures,
        "failures": failures,
        "wall_clock_s": {"ngspice_12.5ps": runs["s1"]["wall_s"],
                         "ngspice_6.25ps": runs["s2"]["wall_s"],
                         "post_processing": post_s},
        "command": "sim/ka2-switch-mixer/run.sh",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    }
    path = runner.save_bench_record(HERE, args.record, record)
    print(f"KA2 expected IF={a_if_exp:.6e} V, worst error={deltas['if_voltage_db']:.4f} dB")
    print(f"record: {path}  pass={not failures}")
    for line in failures:
        print("FAIL:", line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
