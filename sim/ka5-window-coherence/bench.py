#!/usr/bin/env python3
"""KA5 -- window/coherence known answer (spec check 5, V3, behavioural).

One coherent tone at f_IF (bin 64) must read the same power on the
rectangular FFT, the Hann FFT and the independent DFT within 0.05 dB
(spec/target-spec.md, "Known-answer validation" case 5). The rectangular
reading comes from ngspice's own ``fft`` (the deck half of mechanic M1),
the independent DFT from ``sim/bench/lib/coherent.py`` (the Python half),
and the Hann reading from the stamped PSD stack (M3, ``psd.py``): a
one-sided periodogram with the window-power correction, integrated over a
band around the tone with ``band_power``. This bench is where M1's two
halves are shown to agree; every other bench inherits that agreement.

Also applies the M2 pre-flight (tone/window coherence) and the M4
convergence gate (following window, step halving) from the same run.
Behavioural elements only (no HBT models, no PDK), single corner: two
sequential ``ngspice -b`` runs (12.5 ps, 6.25 ps).

Usage: bench.py [--ngspice PATH] [--record PATH] [--workdir DIR]
       bench.py --dump-deck   (print the 12.5 ps deck, nothing runs)
"""

from __future__ import annotations

import argparse
import cmath
import datetime
import math
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from sim.bench import runner                      # noqa: E402
from sim.bench.lib import coherence               # noqa: E402
from sim.bench.lib import coherent                # noqa: E402

TONE_V_OC = 2.0e-3          # tone source, peak, open circuit
BAND_HALF_HZ = 512e3        # Hann integration band half-width around f_IF
TOL_SPREAD_DB = 0.05        # spec check 5 tolerance (three readings)
TOL_M1_DB = 0.05            # protocol: deck fft vs independent DFT

DECK_BODY = f"""* KA5: window/coherence known answer -- spec check 5 (V3, behavioural).
* One coherent tone at f_IF = 9.765625 MHz (bin 64): {TONE_V_OC * 1e3:g} mV peak
* ideal single-ended source through 50 ohm into the R9 load (1 kohm || 2 pF).
* No PDK, no HBT models; image-free single tone. Record node: out.
vin in 0 SIN(0 2m 9.765625meg)
rs in out 50
rl out 0 1k
cl out 0 2p
"""

RECIPE = """let a_tone = am[64]
print a_tone
"""

BINS = {"tone": runner.BIN_IF}


def expected_amplitude():
    """Closed-form load amplitude: divider of R9 load vs the 50 ohm source."""
    w = 2.0 * math.pi * runner.F_IF
    z_load = 1.0 / (1.0 / runner.R_LOAD + 1j * w * runner.C_LOAD)
    return abs(z_load / (z_load + runner.RS_RF)) * TONE_V_OC


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngspice", default=os.environ.get("NGSPICE", "ngspice"))
    ap.add_argument("--record", default=os.path.join(
        HERE, "records",
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d") + "-v3.json"))
    ap.add_argument("--workdir", default=os.path.join(ROOT, ".tools", "ka5-work"))
    ap.add_argument("--dump-deck", action="store_true")
    args = ap.parse_args(argv)

    if args.dump_deck:
        sys.stdout.write(runner.render_deck(
            RECIPE, DECK_BODY, "out", runner.DT_S, "samples-s1.txt"))
        return 0

    # M2 pre-flight: the tone plan must be coherent with the window.
    problems = coherence.coherence_problems(
        {"tone": runner.F_IF}, runner.N_WINDOW * runner.DT_S, runner.DT_S,
        settle_discard_s=runner.DISCARD_S)
    if problems:
        print("KA5: coherence pre-flight FAILED:", *problems, sep="\n  ", file=sys.stderr)
        return 1

    major, version = runner.ngspice_major(args.ngspice)
    if major != 46:
        print(f"KA5: ngspice major {major} != 46 pinned by sim/toolchain.json",
              file=sys.stderr)
        return 1

    os.makedirs(args.workdir, exist_ok=True)
    runs = runner.two_step_run(args.ngspice, DECK_BODY, RECIPE, "out", args.workdir)

    # numpy and the M3 stamp are needed only beyond this point; --dump-deck
    # and the M2 pre-flight stay standard-library.
    from sim.bench.lib import psd                 # noqa: E402
    import numpy as np                            # noqa: E402

    t0 = __import__("time").monotonic()
    amps = {tag: runner.window_amplitudes(step, BINS) for tag, step in runs.items()}
    s1, s2 = amps["s1"]["tone"], amps["s2"]["tone"]

    # The three readings of check 5, analysis window, full step (12.5 ps).
    w1, _ = runner.windows(runs["s1"]["samples"], runs["s1"]["n_window"])
    fs = 1.0 / runner.DT_S
    f, psd_v1, meta = psd.one_sided_psd(w1, fs, win="hann")
    parseval = psd.check_parseval(w1, psd_v1, meta)
    p_hann, bw_hann = psd.band_power(f, psd_v1, meta,
                                     runner.F_IF - BAND_HALF_HZ,
                                     runner.F_IF + BAND_HALF_HZ)
    a_hann = math.sqrt(2.0 * p_hann)

    spec = np.fft.rfft(w1)
    a_rect_np = float(2.0 * abs(spec[runner.BIN_IF]) / len(w1))

    readings = {
        "rectangular_fft_deck_v": s1["deck_fft_v"],
        "independent_dft_v": s1["python_dft_w1_v"],
        "hann_fft_v": a_hann,
    }
    spread_db = max(coherent.db(a / b) for a in readings.values()
                    for b in readings.values())
    aux = {
        "rectangular_fft_numpy_v": a_rect_np,
        "expected_reference_v": expected_amplitude(),
        "hann_band_hz": [runner.F_IF - BAND_HALF_HZ, runner.F_IF + BAND_HALF_HZ],
        "hann_band_bins": 2 * int(round(BAND_HALF_HZ / runner.BIN_HZ)) + 1,
        "enbw_hz": meta["enbw_hz"],
        "parseval_ratio": parseval,
        "following_window_db": s1["following_window_db"],
        "step_halving_db": abs(coherent.db(s1["python_dft_w1_v"] / s2["python_dft_w1_v"])),
    }
    post_s = __import__("time").monotonic() - t0

    figures = {"tone_power": {
        "following_window_db": aux["following_window_db"],
        "step_halving_db": aux["step_halving_db"]}}
    failures = runner.convergence_failures_for(figures)
    if spread_db >= TOL_SPREAD_DB:
        failures.append(f"reading spread {spread_db:.4f} dB >= {TOL_SPREAD_DB} dB "
                        "(rectangular / Hann / independent DFT disagree)")
    if s1["m1_delta_db"] >= TOL_M1_DB:
        failures.append(f"M1 deck-vs-python delta {s1['m1_delta_db']:.4f} dB "
                        f">= {TOL_M1_DB} dB")

    record = {
        "schema": 1,
        "bench": "ka5-window-coherence",
        "check": "spec/target-spec.md 'Known-answer validation' case 5 "
                 "(window/coherence): one coherent tone, same power on "
                 "rectangular FFT, Hann FFT and independent DFT",
        "kind": "simulated",
        "elements": "behavioural (ideal source, resistors, capacitor; no "
                    "semiconductor models, no PDK)",
        "corner": "single corner, nominal (behavioural elements carry no PVT)",
        "toolchain": {"ngspice": version, "python": platform.python_version()},
        "protocol": {
            "step_s": runner.DT_S, "step_halved_s": runner.DT_S / 2,
            "window_points": runner.N_WINDOW,
            "window_s": runner.N_WINDOW * runner.DT_S,
            "settle_discard_s": runner.DISCARD_S,
            "window": "rectangular (coherent tones); Hann cross-check is the "
                      "third reading of this check",
            "bins": {"tone": runner.BIN_IF},
            "tones_hz": {"tone": runner.F_IF},
            "ports": {"source": f"{runner.RS_RF:.0f} ohm single-ended, "
                                f"{TONE_V_OC * 1e3:g} mV peak open circuit",
                      "load": f"R9: {runner.R_LOAD:.0f} ohm || {runner.C_LOAD * 1e12:g} pF"},
        },
        "expected": {"reference_amplitude_v": aux["expected_reference_v"],
                     "note": "closed-form divider reference, reported for "
                             "context; the graded check is the agreement of "
                             "the three readings"},
        "measured": {
            "readings_v": readings,
            "auxiliary": aux,
            "step_halved": {"independent_dft_v": s2["python_dft_w1_v"],
                            "deck_fft_v": s2["deck_fft_v"]},
        },
        "deltas": {"reading_spread_db": spread_db,
                   "m1_deck_vs_python_db": s1["m1_delta_db"],
                   "following_window_db": aux["following_window_db"],
                   "step_halving_db": aux["step_halving_db"]},
        "tolerances_db": {"reading_spread": TOL_SPREAD_DB, "m1_deck_vs_python": TOL_M1_DB,
                          "following_window": 0.1, "step_halving": 0.1},
        "pass": not failures,
        "failures": failures,
        "wall_clock_s": {"ngspice_12.5ps": runs["s1"]["wall_s"],
                         "ngspice_6.25ps": runs["s2"]["wall_s"],
                         "post_processing": post_s},
        "command": "sim/ka5-window-coherence/run.sh",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    }
    runner.write_record(args.record, record)
    print(f"KA5 spread={spread_db:.4f} dB (tol {TOL_SPREAD_DB}), "
          f"M1 delta={s1['m1_delta_db']:.5f} dB, "
          f"following-window={aux['following_window_db']:.4f} dB, "
          f"step-halving={aux['step_halving_db']:.4f} dB, "
          f"wall={runs['s1']['wall_s']:.1f}+{runs['s2']['wall_s']:.1f} s")
    print(f"record: {args.record}  pass={not failures}")
    for line in failures:
        print("FAIL:", line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
