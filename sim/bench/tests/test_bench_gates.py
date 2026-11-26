"""Exercise the V3 entry points with small, coherent two-window records."""
import contextlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM.parent))
from sim.bench import runner


def load_bench(directory):
    spec = importlib.util.spec_from_file_location(directory, SIM / directory / "bench.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


KA1 = load_bench("ka1-ideal-multiplier")
KA2 = load_bench("ka2-switch-mixer")
KA5 = load_bench("ka5-window-coherence")

DECK_PORTS = {
    "ka1-ideal-multiplier": ("rsrf srcrf rf 50", "rl if 0 1k", "cl if 0 2p"),
    "ka2-switch-mixer": ("rsrf srcrf rf 50", "rl if 0 1k", "cl if 0 2p"),
    "ka5-window-coherence": ("rs in out 50", "rl out 0 1k", "cl out 0 2p"),
}
PORT_CONSTANTS = ("RS_RF", "R_LOAD", "C_LOAD")


def dump_deck(bench):
    """A bench's 12.5 ps deck as ``--dump-deck`` prints it."""
    with contextlib.redirect_stdout(io.StringIO()) as out:
        status = bench.main(["--dump-deck"])
    if status != 0:
        raise AssertionError(f"--dump-deck exited {status}")
    return out.getvalue()


def element_line(deck, name):
    """The words of the deck's ``name`` element line."""
    lines = [line.split() for line in deck.splitlines() if line.split()[:1] == [name]]
    if len(lines) != 1:
        raise AssertionError(f"{name}: {len(lines)} element lines, expected one")
    return lines[0]


SI_SCALE = {"": 1.0, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
            "k": 1e3, "meg": 1e6, "g": 1e9, "t": 1e12}


def si(token):
    """An ngspice value with its scale suffix, in ohms or farads."""
    mantissa, suffix = re.fullmatch(
        r"(\d+(?:\.\d*)?(?:e[+-]?\d+)?)([a-z]*)", token).groups()
    return float(mantissa) * SI_SCALE[suffix]


def synthetic_runs(bins, amplitude, tone_errors, deck_errors):
    """Inject dB errors in the waveform or just the ngspice reading."""
    runs = {}
    for leg, n in (("s1", 256), ("s2", 512)):
        samples, prints = [], {}
        for window in ("w1", "w2"):
            values = [0.0] * n
            for tone, k in bins.items():
                key = (leg, window, tone)
                peak = amplitude * 10 ** (tone_errors.get(key, 0) / 20)
                if tone in ("image", "lofeed"):
                    peak = 0.0
                prints[f"a_{window}_{tone}"] = peak * 10 ** (deck_errors.get(key, 0) / 20)
                for i in range(n):
                    values[i] += peak * math.cos(2 * math.pi * k * i / n)
            samples.extend(values)
        runs[leg] = dict(n_window=n, samples=samples, prints=prints,
                         dt_s=1 / (n * runner.BIN_HZ), wall_s=0.0)
    return runs


def invoke_bench(bench, *, tone_errors=None, deck_errors=None, pin=46, stub_major=None):
    """Run a synthetic bench and return its exit status, optional record and batch mock."""
    if bench is KA5:
        bins = bench.BINS
        amplitude = bench.expected_amplitude()
    else:
        bins = {name: 3 + 5 * i for i, name in enumerate(bench.BINS)}
        amplitude = bench.expected_if_amplitude()
    runs = synthetic_runs(bins, amplitude, tone_errors or {}, deck_errors or {})
    if stub_major is None:
        stub_major = pin
    with tempfile.TemporaryDirectory() as tmp:
        manifest = Path(tmp, "toolchain.json")
        manifest.write_text(json.dumps({"ngspice": {"major": pin}}))
        path = Path(tmp, "result.json")
        with (
            mock.patch.object(bench, "BINS", bins),
            mock.patch.object(runner, "TOOLCHAIN_MANIFEST", manifest),
            mock.patch.object(runner, "two_step_run", return_value=runs) as batch,
            mock.patch.object(
                runner,
                "ngspice_major",
                return_value=(stub_major, f"ngspice-{stub_major} banner"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            try:
                status = bench.main(["--workdir", tmp, "--record", str(path)])
            except SystemExit as exc:
                status = exc.code
        record = json.loads(path.read_text()) if path.exists() else None
        return status, record, batch


def m4_limits(record):
    """The (following_window, step_halving) limits a record quotes."""
    tolerances = record["tolerances_db"]
    return tolerances["following_window"], tolerances["step_halving"]


class TestBenchGates(unittest.TestCase):
    def run_bench(self, bench, tone_errors=None, deck_errors=None):
        status, record, _ = invoke_bench(
            bench, tone_errors=tone_errors, deck_errors=deck_errors
        )
        self.assertIsNotNone(record, msg=status)
        self.assertEqual(record["pass"], status == 0)
        return record

    def test_ideal_mixer_controls_pass(self):
        for bench in (KA1, KA2):
            with self.subTest(bench=bench):
                self.assertTrue(self.run_bench(bench)["pass"])

    def test_closed_form_on_fine_leg_and_following_windows(self):
        for bench, base, bad in ((KA1, 0.0, 0.08), (KA2, 0.09, 0.18)):
            for leg, window in (("s2", "w1"), ("s1", "w2"), ("s2", "w2")):
                with self.subTest(bench=bench, leg=leg, window=window):
                    errors = {(s, w, "if"): base for s in ("s1", "s2") for w in ("w1", "w2")}
                    errors[leg, window, "if"] = bad
                    record = self.run_bench(bench, tone_errors=errors)
                    self.assertFalse(record["pass"])
                    self.assertTrue(all(f"{leg}/{window}" in msg for msg in record["failures"]))

    def test_wrong_measured_power_does_not_move_reference(self):
        correct = KA1.b_cg_db
        with mock.patch.object(KA1, "b_cg_db", side_effect=lambda a: correct(a) + 10 * math.log10(2)):
            record = self.run_bench(KA1)
        self.assertFalse(record["pass"])
        self.assertAlmostEqual(record["deltas"]["b_cg_db"], 10 * math.log10(2))

    def test_non_if_tones_require_convergence_and_agreement(self):
        for bench, tone in ((KA1, "sum"), (KA2, "3lo_rf")):
            with self.subTest(bench=bench):
                errors = {("s2", "w2", tone): 0.25}
                record = self.run_bench(bench, tone_errors=errors)
                reasons = " ".join(record["failures"])
                self.assertIn("following-window", reasons)
                self.assertIn("step-halving", reasons)
                record = self.run_bench(bench, deck_errors={("s2", "w2", tone): 0.06})
                self.assertIn("deck FFT vs DFT", " ".join(record["failures"]))

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "Hann PSD needs numpy")
    def test_all_three_readings_on_every_ka5_window(self):
        self.assertTrue(self.run_bench(KA5)["pass"])
        hann = KA5.hann_amplitude
        for index, (leg, window) in enumerate((("s1", "w1"), ("s1", "w2"),
                                               ("s2", "w1"), ("s2", "w2"))):
            with self.subTest(leg=leg, window=window):
                record = self.run_bench(KA5, deck_errors={(leg, window, "tone"): 20 * math.log10(2)})
                self.assertAlmostEqual(record["deltas"]["reading_spread_db"], 20 * math.log10(2), places=3)
                self.assertFalse(record["pass"])
                factors = iter(2 if i == index else 1 for i in range(4))
                with mock.patch.object(KA5, "hann_amplitude", side_effect=lambda x, dt: next(factors) * hann(x, dt)):
                    record = self.run_bench(KA5)
                self.assertIn(f"{leg}/{window} tone reading spread", " ".join(record["failures"]))

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "Hann PSD needs numpy")
    def test_ka5_convergence_is_checked_for_each_method(self):
        # All three readings agree within 0.05 dB in each window. Only the
        # deck moves by more than 0.1 dB across windows and across steps.
        key = ("s2", "w2", "tone")
        record = self.run_bench(KA5, tone_errors={key: 0.09}, deck_errors={key: 0.04})
        self.assertLess(record["deltas"]["reading_spread_db"], 0.05)
        self.assertFalse(record["pass"])
        self.assertTrue(all("deck_fft_v" in msg for msg in record["failures"]))
        self.assertAlmostEqual(record["deltas"]["following_window_db"], 0.13)
        self.assertAlmostEqual(record["deltas"]["step_halving_db"], 0.13)

    def test_record_m4_limits_are_read_from_the_grader(self):
        """A record's M4 limits are the grader's constants, not its own literals
        kept in step by hand (issue #112)."""
        grader = runner.convergence
        benches = [(KA1, "KA1", "sum"), (KA2, "KA2", "3lo_rf")]
        if importlib.util.find_spec("numpy"):
            benches.append((KA5, "KA5", "tone"))
        for bench, name, tone in benches:
            with self.subTest(bench=name):
                record = self.run_bench(bench)
                self.assertEqual(m4_limits(record), (0.1, 0.1))
                with (mock.patch.object(grader, "FOLLOWING_WINDOW_MAX_DB", 0.02),
                      mock.patch.object(grader, "STEP_HALVING_MAX_DB", 0.03)):
                    record = self.run_bench(bench, tone_errors={("s2", "w2", tone): 0.05})
                    limits = (grader.FOLLOWING_WINDOW_MAX_DB, grader.STEP_HALVING_MAX_DB)
                self.assertEqual(m4_limits(record), limits)
                reasons = " ".join(record["failures"])
                for limit in limits:
                    self.assertIn(f">= {limit} dB", reasons)

    def test_nonfinite_oracle_prevents_signoff(self):
        with mock.patch.object(runner.coherent, "dft_amplitude", return_value=math.nan):
            with self.assertRaisesRegex(ValueError, "non-finite"):
                self.run_bench(KA1)


class TestSharedScaffold(unittest.TestCase):
    """The CLI / record scaffold folded into the shared runner (issue #108)."""

    def test_bench_args_defaults_and_flags(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            args = runner.bench_args(os.path.join("x", ".tools", "kaX-work"), [])
        self.assertEqual(args.workdir, os.path.join("x", ".tools", "kaX-work"))
        self.assertIsNone(args.record)
        self.assertFalse(args.dump_deck)
        self.assertEqual(args.ngspice, "ngspice")
        with mock.patch.dict(os.environ, {"NGSPICE": "./.tools/ngspice-46/bin/ngspice"}):
            self.assertEqual(runner.bench_args("w", []).ngspice,
                             str(Path.cwd() / ".tools/ngspice-46/bin/ngspice"))
            picked = runner.bench_args("w", ["--dump-deck", "--ngspice", "bin/ngspice",
                                             "--record", "out.json", "--workdir", "scratch"])
        self.assertTrue(picked.dump_deck)
        self.assertEqual(picked.record, "out.json")
        self.assertEqual(picked.workdir, "scratch")
        self.assertEqual(picked.ngspice, str(Path.cwd() / "bin/ngspice"))

    def test_protocol_common_is_the_shared_record_block(self):
        self.assertEqual(runner.protocol_common(), {
            "legs": {"s1": "12.5 ps", "s2": "6.25 ps"},
            "windows": {"w1": "analysis", "w2": "following"},
            "step_s": runner.DT_S,
            "step_halved_s": runner.DT_S / 2,
            "window_points": runner.N_WINDOW,
            "window_s": runner.N_WINDOW * runner.DT_S,
            "settle_discard_s": runner.DISCARD_S,
        })

    def test_incoherent_benches_return_failure_before_running_ngspice(self):
        with (
            mock.patch.object(runner, "F_IF", runner.F_IF + runner.BIN_HZ / 2),
            mock.patch.object(subprocess, "run", side_effect=AssertionError("ngspice invoked")),
        ):
            for bench, name in ((KA1, "KA1"), (KA2, "KA2"), (KA5, "KA5")):
                with self.subTest(bench=name), contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(bench.main([]), 1)
                    self.assertTrue(err.getvalue().startswith(f"{name}: coherence pre-flight FAILED:\n"))
                    self.assertIn("not coherent", err.getvalue())

    def test_coherent_gate_passes_silently(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertTrue(runner.coherence_gate("KAX", {"if": runner.F_IF}))
        self.assertEqual(err.getvalue(), "")

    def test_bench_report_prints_and_returns_the_status(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(runner.bench_report("KAX ok", Path("r.json"), []), 0)
            self.assertEqual(runner.bench_report("KAX bad", Path("r.json"), ["boom"]), 1)
        self.assertEqual(out.getvalue(), "KAX ok\nrecord: r.json  pass=True\n"
                                         "KAX bad\nrecord: r.json  pass=False\n")
        self.assertEqual(err.getvalue(), "FAIL: boom\n")

    def test_wall_clock_and_date_shapes(self):
        runs = {"s1": {"wall_s": 1.5}, "s2": {"wall_s": 3.25}}
        self.assertEqual(runner.wall_clock(runs, 0.5), {"ngspice_12.5ps": 1.5,
                                                        "ngspice_6.25ps": 3.25,
                                                        "post_processing": 0.5})
        self.assertRegex(runner.record_date(), r"^\d{4}-\d{2}-\d{2}$")


class TestToolchainPinGate(unittest.TestCase):
    """The expected ngspice major is read from sim/toolchain.json once, by
    the shared runner (issue #104): bumping the pin moves every bench."""

    def test_matching_pin_reaches_the_first_batch(self):
        benches = [(KA1, "KA1"), (KA2, "KA2")]
        if importlib.util.find_spec("numpy"):
            benches.append((KA5, "KA5"))
        for bench, name in benches:
            with self.subTest(bench=name):
                code, record, batch = invoke_bench(bench, pin=47, stub_major=47)
                self.assertEqual(code, 0)
                self.assertTrue(batch.called)
                self.assertTrue(record["pass"])
                self.assertEqual(record["toolchain"]["ngspice"], "ngspice-47 banner")

    def test_mismatched_major_exits_nonzero_before_the_first_batch(self):
        for bench, name in ((KA1, "KA1"), (KA2, "KA2"), (KA5, "KA5")):
            with self.subTest(bench=name):
                code, record, batch = invoke_bench(bench, pin=47, stub_major=46)
                self.assertNotEqual(code, 0)
                self.assertIn(name, code)
                self.assertIn("46", code)
                self.assertIn("47", code)
                self.assertFalse(batch.called)
                self.assertIsNone(record)

    def test_dump_deck_stays_offline(self):
        for bench, name in ((KA1, "KA1"), (KA2, "KA2"), (KA5, "KA5")):
            with self.subTest(bench=name):
                with mock.patch.object(
                        runner, "ngspice_major",
                        side_effect=AssertionError("no simulator expected")):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        self.assertEqual(bench.main(["--dump-deck"]), 0)
                self.assertIn("wrdata", out.getvalue())


class TestDeckPorts(unittest.TestCase):
    """The source and load elements of each deck are the shared runner
    constants, read when the bench module is loaded (issue #122)."""

    def test_default_decks_keep_the_signed_off_port_elements(self):
        """At the default constants each deck carries the elements the
        committed records were produced from: names, nodes, values and units."""
        for name, lines in DECK_PORTS.items():
            with self.subTest(bench=name):
                deck = dump_deck(load_bench(name))
                for constant, line in zip(PORT_CONSTANTS, lines):
                    signed_off = line.split()
                    self.assertEqual(element_line(deck, signed_off[0]), signed_off)
                    self.assertEqual(si(signed_off[-1]), getattr(runner, constant))

    def test_port_elements_follow_the_constants(self):
        """Constants set to non-default values before the bench is loaded
        reach that deck's source resistor, load resistor and load capacitor."""
        ports = {"RS_RF": 75.0, "R_LOAD": 2200.0, "C_LOAD": 1.5e-12}
        for name, lines in DECK_PORTS.items():
            with self.subTest(bench=name):
                with mock.patch.multiple(runner, **ports):
                    deck = dump_deck(load_bench(name))
                for constant, line in zip(PORT_CONSTANTS, lines):
                    signed_off = line.split()
                    emitted = element_line(deck, signed_off[0])
                    self.assertEqual(emitted[:-1], signed_off[:-1])
                    self.assertTrue(
                        math.isclose(si(emitted[-1]), ports[constant], rel_tol=1e-12),
                        f"{constant}: deck has {emitted[-1]}, not {ports[constant]}")
                for stale in ("50 ohm", "1 kohm", "2 pF"):
                    self.assertNotIn(stale, deck)


class TestTwoStepRun(unittest.TestCase):
    def test_wrdata_names_the_sample_basename_under_a_spaced_workdir(self):
        """ngspice cannot quote a wrdata path, so the deck must name the
        leg's sample file relative to the simulator working directory while
        the Python reader keeps the joined path (issue #103)."""
        body = "* stub body for the shared-runner regression\nrl if 0 1k\n"
        written = {}

        def standin(cmd, **kwargs):
            self.assertEqual(cmd[1:3], ["-b", "-o"])
            log, deck = cmd[3], cmd[4]
            tag = Path(deck).name.removeprefix("deck-").removesuffix(".cir")
            lines = [l for l in Path(deck).read_text().splitlines()
                     if l.startswith("wrdata ")]
            self.assertEqual(len(lines), 1, f"{deck}: one wrdata command")
            self.assertEqual(lines[0].split(),
                             ["wrdata", f"samples-{tag}.txt", "v(if)"])
            samples = Path(kwargs["cwd"], lines[0].split()[1])
            samples.write_text("".join(f"{i} {i}\n" for i in range(4)))
            written[tag] = samples
            Path(log).write_text("* stand-in ngspice log\n")
            return subprocess.CompletedProcess(cmd, 0)

        with tempfile.TemporaryDirectory(suffix=" work with spaces") as tmp:
            with mock.patch.object(subprocess, "run", side_effect=standin):
                runs = runner.two_step_run("ngspice", body, {"if": 3}, "if", tmp)
            for tag in ("s1", "s2"):
                self.assertTrue(written[tag].is_file())
                self.assertEqual(runs[tag]["samples"], [0.0, 1.0, 2.0, 3.0])


class TestEvidence(unittest.TestCase):
    def test_reject_nonfinite_simulator_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "samples")
            for value in ("NaN", "inf", "-Inf", "1e999"):
                with self.subTest(value=value):
                    path.write_text(f"0 {value}\n")
                    with self.assertRaisesRegex(ValueError, "non-finite"):
                        runner.parse_samples(path)
                    with self.assertRaisesRegex(ValueError, "non-finite"):
                        runner.parse_prints(f"a_w2_if = {value}")

    def test_version_line_and_executable_paths(self):
        banner = "******\n** ngspice-46 : Circuit level simulation program\n******"
        proc = subprocess.CompletedProcess([], 0, stdout="", stderr=banner)
        with mock.patch.object(subprocess, "run", return_value=proc):
            self.assertEqual(runner.ngspice_major("ngspice"), (46, banner.splitlines()[1]))
        self.assertEqual(runner.ngspice_command("ngspice"), "ngspice")
        self.assertEqual(runner.ngspice_command("bin/ngspice"), str(Path.cwd() / "bin/ngspice"))

    def test_append_only_evidence_and_reusable_strict_json_scratch(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench = Path(tmp, "sim", "bench1")
            first = runner.save_bench_record(bench, None, {"run": 1})
            second = runner.save_bench_record(bench, None, {"run": 2})
            self.assertNotEqual(first, second)
            with self.assertRaises(FileExistsError):
                runner.save_bench_record(bench, first, {"run": 3})
            self.assertEqual(json.loads(first.read_text()), {"run": 1})
            scratch = Path(tmp, ".tools", "attest.json")
            for i in (1, 2):
                runner.save_bench_record(bench, scratch, {"run": i})
            with self.assertRaises(ValueError):
                runner.save_bench_record(bench, scratch, {"bad": math.nan})
            self.assertEqual(json.loads(scratch.read_text()), {"run": 2})
