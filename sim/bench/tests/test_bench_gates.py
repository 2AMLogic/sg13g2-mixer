"""Exercise the V3 entry points with small, coherent two-window records."""
import contextlib
import importlib.util
import io
import json
import math
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


class TestBenchGates(unittest.TestCase):
    def run_bench(self, bench, tone_errors=None, deck_errors=None):
        if bench is KA5:
            bins = bench.BINS
            amplitude = bench.expected_amplitude()
        else:
            bins = {name: 3 + 5 * i for i, name in enumerate(bench.BINS)}
            amplitude = bench.expected_if_amplitude()
        runs = synthetic_runs(bins, amplitude, tone_errors or {}, deck_errors or {})
        with tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
            path = Path(tmp, "result.json")
            stack.enter_context(mock.patch.object(bench, "BINS", bins))
            stack.enter_context(mock.patch.object(runner, "two_step_run", return_value=runs))
            stack.enter_context(mock.patch.object(runner, "ngspice_major", return_value=(46, "ngspice-46")))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            status = bench.main(["--workdir", tmp, "--record", str(path)])
            data = json.loads(path.read_text())
            self.assertEqual(data["pass"], status == 0)
            return data

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

    def test_nonfinite_oracle_prevents_signoff(self):
        with mock.patch.object(runner.coherent, "dft_amplitude", return_value=math.nan):
            with self.assertRaisesRegex(ValueError, "non-finite"):
                self.run_bench(KA1)


class TestToolchainPinGate(unittest.TestCase):
    """The expected ngspice major is read from sim/toolchain.json once, by
    the shared runner (issue #104): bumping the pin moves every bench."""

    def run_bench(self, bench, pin, stub_major):
        """(exit_code_or_message, parsed_record_or_None, batch_mock)."""
        if bench is KA5:
            bins = bench.BINS
            amplitude = bench.expected_amplitude()
        else:
            bins = {name: 3 + 5 * i for i, name in enumerate(bench.BINS)}
            amplitude = bench.expected_if_amplitude()
        runs = synthetic_runs(bins, amplitude, {}, {})
        with tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
            manifest = Path(tmp, "toolchain.json")
            manifest.write_text(json.dumps({"ngspice": {"major": pin}}))
            path = Path(tmp, "result.json")
            batch = mock.Mock(return_value=runs)
            stack.enter_context(mock.patch.object(bench, "BINS", bins))
            stack.enter_context(mock.patch.object(runner, "TOOLCHAIN_MANIFEST", manifest))
            stack.enter_context(mock.patch.object(runner, "two_step_run", batch))
            stack.enter_context(mock.patch.object(
                runner, "ngspice_major",
                return_value=(stub_major, f"ngspice-{stub_major} banner")))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            try:
                code = bench.main(["--workdir", tmp, "--record", str(path)])
            except SystemExit as exc:
                code = exc.code
            record = json.loads(path.read_text()) if path.exists() else None
            return code, record, batch

    def test_matching_pin_reaches_the_first_batch(self):
        benches = [(KA1, "KA1"), (KA2, "KA2")]
        if importlib.util.find_spec("numpy"):
            benches.append((KA5, "KA5"))
        for bench, name in benches:
            with self.subTest(bench=name):
                code, record, batch = self.run_bench(bench, pin=47, stub_major=47)
                self.assertEqual(code, 0)
                self.assertTrue(batch.called)
                self.assertTrue(record["pass"])
                self.assertEqual(record["toolchain"]["ngspice"], "ngspice-47 banner")

    def test_mismatched_major_exits_nonzero_before_the_first_batch(self):
        for bench, name in ((KA1, "KA1"), (KA2, "KA2"), (KA5, "KA5")):
            with self.subTest(bench=name):
                code, record, batch = self.run_bench(bench, pin=47, stub_major=46)
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
