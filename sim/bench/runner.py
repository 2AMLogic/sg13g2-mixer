"""Shared driver for the known-answer benches (V3).

Not a bench mechanic: record 0002's mechanics live in ``sim/bench/lib/``
(M1 coherent DFT, M2 coherence pre-flight, M3 PSD stack, M4 convergence
gate); this module is the plumbing that renders a deck, runs the pinned
ngspice once per step size, reads back the two halves of M1 (the deck's
``fft`` magnitudes from the log, the Python oracle from the written
samples), and slices the record into the analysis window and the
following window. One ``ngspice -b`` per run, sequentially, per the host
rules; the benches are single-corner behavioural decks.

Protocol constants (spec/target-spec.md "Measurement protocol" common
setup) are defined once here: 12.5 ps step, N = 2^19 analysis window,
rectangular window with coherent tones, >= 2 us of settling discarded
before the window, and the following-window / step-halving legs the M4
gate reads.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import time

from sim.bench.lib import coherent
from sim.bench.lib import convergence

# --- protocol constants (spec/target-spec.md, "Measurement protocol") ------
DT_S = 12.5e-12            # transient step (6.25 ps for the halved leg)
N_WINDOW = 2 ** 19         # analysis window, points = 6.5536 us at DT_S
DISCARD_S = 3.2768e-6      # settling discard (>= 2 us, 2^18 samples, on-grid)
BIN_HZ = 1.0 / (N_WINDOW * DT_S)   # 152.587890625 kHz bin width
F_IF = 64 * BIN_HZ         # 9.765625 MHz
F_LO = 15936 * BIN_HZ      # 2.431640625 GHz (low-side)
F_RF = 16000 * BIN_HZ      # 2.44140625 GHz (the LNA protocol's f1)
BIN_IF, BIN_LO, BIN_RF = 64, 15936, 16000
N_WINDOWS = 2              # analysis window + the following window

RS_RF = 50.0               # RF source impedance (stated on every figure)
R_LOAD = 1000.0            # R9 load, differential 1 k || 2 pF, single-ended half
C_LOAD = 2e-12
P_AVAIL_W = 1e-7           # -40 dBm available (small-signal drive of B-CG)
V_RF_OC = math.sqrt(8.0 * RS_RF * P_AVAIL_W)   # 6.3246 mV peak, open circuit


def step_plan(dt_s):
    """Sample counts for one step size: (n_full, n_window, tstart, tstop)."""
    if dt_s > DT_S or abs(DT_S / dt_s - round(DT_S / dt_s)) > 1e-9:
        raise ValueError(f"step {dt_s} is not DT or a whole subdivision")
    ratio = int(round(DT_S / dt_s))
    n_window = N_WINDOW * ratio
    n_full = n_window * N_WINDOWS
    return n_full, n_window, DISCARD_S, DISCARD_S + n_full * dt_s


def render_deck(recipe, body, node, dt_s, samples_path):
    """Fill the M1 deck-half template around a bench ``body`` (netlist)."""
    n_full, n_window, tstart, tstop = step_plan(dt_s)
    control = coherent.DECK_RECIPE.format(
        tstep=f"{dt_s:.6g}", tstop=f"{tstop:.9g}", tstart=f"{tstart:.6g}",
        n_full=n_full, n_win=n_window, node=node, samples=samples_path)
    return f"{body}\n.control\n{control}{recipe}\n.endc\n.end\n"


def _real_error(text, needle):
    # Only lines that look like simulator/interpreter diagnostics count;
    # ngspice logs also contain print output and banner lines.
    for line in text.splitlines():
        if needle.lower() not in line.lower():
            continue
        stripped = line.strip()
        if stripped.startswith(("*", "Note:", "Warning:", "FFT:")):
            continue
        if re.match(r"^[A-Za-z_][\w()#.\[\]]*\s*=", stripped):
            continue  # a print output line that happens to contain it
        return True
    return False


def run_ngspice(ngspice, deck_text, workdir, tag):
    """Run one ``ngspice -b`` in ``workdir``; return (log_text, wall_s)."""
    deck = os.path.join(workdir, f"deck-{tag}.cir")
    log = os.path.join(workdir, f"run-{tag}.log")
    with open(deck, "w", encoding="utf-8") as fh:
        fh.write(deck_text)
    t0 = time.monotonic()
    proc = subprocess.run([ngspice, "-b", "-o", log, deck],
                          capture_output=True, text=True, cwd=workdir)
    wall = time.monotonic() - t0
    if proc.returncode != 0:
        raise RuntimeError(f"ngspice exited {proc.returncode} ({tag}): {proc.stderr[-2000:]}")
    with open(log, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    for bad in ("Error:", "couldn't find", "failed"):
        if _real_error(text, bad):
            raise RuntimeError(f"ngspice reported an error ({tag}); see {log}")
    return text, wall


_PRINT_RE = re.compile(r"^\s*([A-Za-z_][\w()\[\]]*)\s*=\s*(-?[\d.]+(?:e[+-]?\d+)?)\s*$",
                       re.MULTILINE)


def parse_prints(log_text):
    """The ``print``ed control-block values from a run log, name -> float."""
    return {name: float(val) for name, val in _PRINT_RE.findall(log_text)}


def parse_samples(path):
    """Read a wrdata file: uniform-grid samples, values only (column 2)."""
    vals = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) >= 2:
                vals.append(float(parts[1]))
    return vals


def windows(samples, n_window):
    """Split the uniform record into (analysis window, following window)."""
    if len(samples) != 2 * n_window:
        raise ValueError(f"record has {len(samples)} samples, expected {2 * n_window}")
    return samples[:n_window], samples[n_window:]


def two_step_run(ngspice, body, recipe, node, workdir):
    """Both protocol legs (12.5 ps and 6.25 ps), sequentially.

    Returns {tag: {dt_s, n_window, prints, samples, wall_s}} with tag
    ``s1`` for the full step and ``s2`` for the halved step.
    """
    out = {}
    for tag, dt in (("s1", DT_S), ("s2", DT_S / 2.0)):
        n_full, n_window, _, _ = step_plan(dt)
        samples = os.path.join(workdir, f"samples-{tag}.txt")
        deck = render_deck(recipe, body, node, dt, samples)
        log, wall = run_ngspice(ngspice, deck, workdir, tag)
        out[tag] = {"dt_s": dt, "n_window": n_window,
                    "prints": parse_prints(log), "samples": parse_samples(samples),
                    "wall_s": wall}
    return out


def window_amplitudes(step, bins, deck_prefix="a_"):
    """Per name: deck fft amplitude, W1/W2 python DFT amplitudes, both-half delta.

    ``step`` is one ``two_step_run`` entry; ``bins`` maps a short name to
    its window bin index. The deck half read the analysis window (W1); the
    Python oracle reads W1 and W2 from the same run's written samples.
    """
    w1, w2 = windows(step["samples"], step["n_window"])
    out = {}
    for name, k in bins.items():
        deck_amp = step["prints"][f"{deck_prefix}{name}"]
        py_w1 = coherent.dft_amplitude(w1, k)
        py_w2 = coherent.dft_amplitude(w2, k)
        out[name] = {
            "deck_fft_v": deck_amp,
            "python_dft_w1_v": py_w1,
            "python_dft_w2_v": py_w2,
            "m1_delta_db": abs(coherent.db(deck_amp / py_w1)),
            "following_window_db": abs(coherent.db(py_w1 / py_w2)),
        }
    return out


def convergence_failures_for(figures):
    """M4 gate over {name: {following_window_db, step_halving_db}} figures."""
    out = []
    for name, fig in figures.items():
        out.extend(convergence.convergence_failures(
            fig["following_window_db"], fig.get("step_halving_db"), name=name))
    return out


def write_record(path, record):
    """Write one append-only result record (UTF-8 JSON, sorted keys)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
        fh.write("\n")


def ngspice_major(ngspice):
    """(major, version-first-line) of an ngspice binary, or raises."""
    try:
        proc = subprocess.run([ngspice, "--version"], capture_output=True,
                              text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"cannot run {ngspice}: {exc}") from exc
    m = re.search(r"ngspice-(\d+)", proc.stdout + proc.stderr)
    if not m:
        raise RuntimeError(f"{ngspice}: no version string")
    return int(m.group(1)), proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else "ngspice"


def db20(ratio):
    return 20.0 * math.log10(ratio)


def db10(ratio):
    return 10.0 * math.log10(ratio)
