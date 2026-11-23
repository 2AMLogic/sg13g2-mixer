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

import datetime
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
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


def render_deck(bins, body, node, dt_s, samples_path):
    """Fill the M1 deck-half template around a bench ``body`` (netlist).

    ``samples_path`` is interpolated verbatim into ``wrdata``, which cannot
    quote a path: pass a name relative to the simulator working directory
    (``run_ngspice`` runs there), never an absolute path that may contain
    spaces.
    """
    n_full, n_window, tstart, tstop = step_plan(dt_s)
    control = coherent.DECK_RECIPE.format(
        tstep=f"{dt_s:.6g}", tstop=f"{tstop:.9g}", tstart=f"{tstart:.6g}",
        n_full=n_full, node=node, samples=samples_path)
    first = coherent.window_fft(node, bins, n_window, "w1", 0)
    following = coherent.window_fft(node, bins, n_window, "w2", n_window)
    return f"{body}\n.control\n{control}{first}{following}.endc\n.end\n"


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


_PRINT_RE = re.compile(r"^\s*(a_\w+)\s*=\s*(\S+)\s*$", re.MULTILINE)


def finite(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"non-finite measurement: {value}")
    return value


def parse_prints(log_text):
    """The printed FFT amplitudes, indexed by window and tone."""
    return {name: finite(val) for name, val in _PRINT_RE.findall(log_text)}


def parse_samples(path):
    """Read ngspice wrdata time/value pairs, rejecting malformed records."""
    vals = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            timestamp, amplitude = line.split()
            finite(timestamp)
            vals.append(finite(amplitude))
    return vals


def windows(samples, n_window):
    """Split the uniform record into (analysis window, following window)."""
    if len(samples) != 2 * n_window:
        raise ValueError(f"record has {len(samples)} samples, expected {2 * n_window}")
    return samples[:n_window], samples[n_window:]


def two_step_run(ngspice, body, bins, node, workdir):
    """Both protocol legs (12.5 ps and 6.25 ps), sequentially.

    Returns {tag: {dt_s, n_window, prints, samples, wall_s}} with tag
    ``s1`` for the full step and ``s2`` for the halved step.
    """
    workdir = tempfile.mkdtemp(dir=os.path.abspath(workdir), prefix="run-")
    out = {}
    for tag, dt in (("s1", DT_S), ("s2", DT_S / 2.0)):
        n_full, n_window, _, _ = step_plan(dt)
        samples = os.path.join(workdir, f"samples-{tag}.txt")
        deck = render_deck(bins, body, node, dt, os.path.basename(samples))
        log, wall = run_ngspice(ngspice, deck, workdir, tag)
        out[tag] = {"dt_s": dt, "n_window": n_window,
                    "prints": parse_prints(log), "samples": parse_samples(samples),
                    "wall_s": wall}
    return out


def tone_readings(runs, bins, hann=None):
    """Read every tone in both windows on both legs, in peak volts."""
    readings = {}
    for leg, run in runs.items():
        readings[leg] = {}
        for window, samples in zip(("w1", "w2"), windows(run["samples"], run["n_window"])):
            tones = {}
            for name, index in bins.items():
                methods = {
                    "deck_fft_v": finite(run["prints"][f"a_{window}_{name}"]),
                    "python_dft_v": finite(coherent.dft_amplitude(samples, index)),
                }
                if hann is not None:
                    methods["hann_fft_v"] = finite(hann(samples, run["dt_s"]))
                tones[name] = methods
            readings[leg][window] = tones
    return readings


def grade_tones(readings, tones, m1_tolerance_db, *, spread_tolerance_db=None):
    """Grade agreement of methods and M4 convergence on every reported tone.

    Each summary is the worst delta across the two steps and two windows.
    Numerical-floor bins are recorded separately by the calling bench.
    """
    deltas = dict(m1_deck_vs_python_db=0.0, following_window_db=0.0, step_halving_db=0.0)
    failures = []
    for leg, windows_read in readings.items():
        for window, tone_values in windows_read.items():
            for tone in tones:
                methods = tone_values[tone]
                where = f"{leg}/{window} {tone}"
                m1 = abs(db20(methods["deck_fft_v"] / methods["python_dft_v"]))
                deltas["m1_deck_vs_python_db"] = max(deltas["m1_deck_vs_python_db"], m1)
                if m1 >= m1_tolerance_db:
                    failures.append(f"{where} deck FFT vs DFT: {m1:.4f} dB >= {m1_tolerance_db}")
                if spread_tolerance_db is not None:
                    three = (methods["deck_fft_v"], methods["hann_fft_v"], methods["python_dft_v"])
                    spread = db20(max(three) / min(three))
                    deltas["reading_spread_db"] = max(deltas.get("reading_spread_db", 0), spread)
                    if spread >= spread_tolerance_db:
                        failures.append(f"{where} reading spread: {spread:.4f} dB >= {spread_tolerance_db}")
                for method, value in methods.items():
                    # Each edge of the four measurements is graded once.
                    following = abs(db20(value / windows_read["w2"][tone][method]))
                    halving = abs(db20(value / readings["s2"][window][tone][method]))
                    deltas["following_window_db"] = max(deltas["following_window_db"], following)
                    deltas["step_halving_db"] = max(deltas["step_halving_db"], halving)
                    failures.extend(convergence.convergence_failures(
                        following, halving, name=f"{where} {method}"))
    return deltas, failures


def grade_known_answer(readings, measure_db, expected_db, tolerance_db, label):
    """Compare each independent IF reading with the closed form."""
    worst = 0.0
    failures = []
    for leg, windows_read in readings.items():
        for window, tones in windows_read.items():
            for method, amplitude in tones["if"].items():
                delta = abs(finite(measure_db(amplitude)) - expected_db)
                worst = max(worst, delta)
                if delta >= tolerance_db:
                    failures.append(f"{leg}/{window} {method} {label}: "
                                    f"{delta:.4f} dB >= {tolerance_db}")
    return worst, failures


def write_record(path, record, *, replace=False):
    """Publish strict JSON atomically. Replacing an output is opt-in for scratch."""
    payload = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        try:
            tmp.write(payload.encode("utf-8"))
            tmp.close()
            if replace:
                os.replace(tmp.name, path)
            else:
                os.link(tmp.name, path)
        finally:
            Path(tmp.name).unlink(missing_ok=True)


def save_bench_record(bench_dir, requested_path, record):
    directory = Path(bench_dir, "records")
    if requested_path is None:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H%M%S%fZ")
        path = directory / f"{stamp}-v3.json"
    else:
        path = Path(requested_path)
    # All sim/<bench>/records trees hold append-only evidence, even if named
    # explicitly. The signoff inventory names reusable outputs under .tools/.
    sim_dir = directory.parent.parent.resolve()
    parent = path.parent.resolve()
    evidence = any(p.name == "records" and p.parent.parent == sim_dir
                   for p in (parent, *parent.parents))
    write_record(path, record, replace=not evidence)
    return path


def ngspice_command(command):
    """Resolve caller-relative paths before the simulator changes directory."""
    return os.path.abspath(command) if os.sep in command else command


TOOLCHAIN_MANIFEST = Path(__file__).resolve().parents[1] / "toolchain.json"


def pinned_ngspice_major():
    """The required ngspice major, from sim/toolchain.json."""
    with open(TOOLCHAIN_MANIFEST, encoding="utf-8") as fh:
        return int(json.load(fh)["ngspice"]["major"])


def require_pinned_ngspice(ngspice, bench):
    """The detected banner, after checking the major against the pin.

    One gate shared by every bench entry point: the expected major is read
    from sim/toolchain.json (resolved next to this runner), never repeated
    per bench, so bumping the pin alone moves every bench with it. Raises
    SystemExit (nonzero exit) naming the bench and both majors before any
    simulator batch starts; on match the detected banner is returned for
    the evidence record.
    """
    major, banner = ngspice_major(ngspice)
    pinned = pinned_ngspice_major()
    if major != pinned:
        raise SystemExit(
            f"{bench}: ngspice major {major} != {pinned} pinned by sim/toolchain.json")
    return banner


def ngspice_major(ngspice):
    """(major, version-bearing banner line) of an ngspice binary, or raises."""
    try:
        proc = subprocess.run([ngspice, "--version"], capture_output=True,
                              text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"cannot run {ngspice}: {exc}") from exc
    for line in (proc.stdout + "\n" + proc.stderr).splitlines():
        match = re.search(r"ngspice-(\d+)\b", line)
        if match:
            return int(match.group(1)), line.strip()
    raise RuntimeError(f"{ngspice}: no version string")


def db20(ratio):
    return coherent.db(ratio)


def db10(ratio):
    return 10.0 * math.log10(ratio)
