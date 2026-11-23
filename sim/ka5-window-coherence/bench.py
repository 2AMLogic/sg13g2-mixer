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

BINS = {"tone": runner.BIN_IF}


def expected_amplitude():
    """Closed-form load amplitude: divider of R9 load vs the 50 ohm source."""
    w = 2.0 * math.pi * runner.F_IF
    z_load = 1.0 / (1.0 / runner.R_LOAD + 1j * w * runner.C_LOAD)
    return abs(z_load / (z_load + runner.RS_RF)) * TONE_V_OC


def hann_amplitude(samples, dt_s):
    from sim.bench.lib import psd
    freq, density, meta = psd.one_sided_psd(samples, 1.0 / dt_s, win="hann")
    psd.check_parseval(samples, density, meta)
    power, _ = psd.band_power(freq, density, meta, runner.F_IF - BAND_HALF_HZ,
                              runner.F_IF + BAND_HALF_HZ)
    return math.sqrt(2 * power)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngspice", type=runner.ngspice_command,
                    default=os.environ.get("NGSPICE", "ngspice"))
    ap.add_argument("--record", help="output path (default: new UTC-stamped evidence record)")
    ap.add_argument("--workdir", default=os.path.join(ROOT, ".tools", "ka5-work"))
    ap.add_argument("--dump-deck", action="store_true")
    args = ap.parse_args(argv)

    if args.dump_deck:
        sys.stdout.write(runner.render_deck(
            BINS, DECK_BODY, "out", runner.DT_S, "samples-s1.txt"))
        return 0

    # M2 pre-flight: the tone plan must be coherent with the window.
    problems = coherence.coherence_problems(
        {"tone": runner.F_IF}, runner.N_WINDOW * runner.DT_S, runner.DT_S,
        settle_discard_s=runner.DISCARD_S)
    if problems:
        print("KA5: coherence pre-flight FAILED:", *problems, sep="\n  ", file=sys.stderr)
        return 1

    version = runner.require_pinned_ngspice(args.ngspice, "KA5")

    os.makedirs(args.workdir, exist_ok=True)
    runs = runner.two_step_run(args.ngspice, DECK_BODY, BINS, "out", args.workdir)

    t0 = time.monotonic()
    readings = runner.tone_readings(runs, BINS, hann=hann_amplitude)
    deltas, failures = runner.grade_tones(
        readings, BINS, TOL_M1_DB, spread_tolerance_db=TOL_SPREAD_DB)
    post_s = time.monotonic() - t0

    record = {
        "schema": 2,
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
            "legs": {"s1": "12.5 ps", "s2": "6.25 ps"},
            "windows": {"w1": "analysis", "w2": "following"},
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
        "expected": {"reference_amplitude_v": expected_amplitude(),
                     "note": "closed-form divider reference, reported for "
                             "context; the graded check is the agreement of "
                             "the three readings"},
        "measured": {"tone_amplitudes": readings},
        "deltas": deltas,
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
    path = runner.save_bench_record(HERE, args.record, record)
    print(f"KA5 worst three-reading spread={deltas['reading_spread_db']:.5f} dB")
    print(f"record: {path}  pass={not failures}")
    for line in failures:
        print("FAIL:", line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
