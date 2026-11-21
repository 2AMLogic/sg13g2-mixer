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
