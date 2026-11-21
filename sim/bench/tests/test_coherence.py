"""Unit tests for mechanic M2 (stamped coherence pre-flight).

Edge cases from the V3 test plan: a deliberately broken plan (non-integer
cycles in the window, non-integer window in samples, settling discard off
the sample grid, fewer than 8 samples per period) must be flagged; the
repo's actual protocol plan must pass clean.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from sim.bench import runner                          # noqa: E402
from sim.bench.lib import coherence                   # noqa: E402


class TestCoherenceProblems(unittest.TestCase):
    def test_repo_protocol_plan_is_coherent(self):
        problems = coherence.coherence_problems(
            {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF},
            runner.N_WINDOW * runner.DT_S, runner.DT_S,
            settle_discard_s=runner.DISCARD_S)
        self.assertEqual(problems, [])

    def test_non_integer_cycles_flagged(self):
        # 4 Hz over a 1 s window at step 1/64 s: 4 periods, 16 samples per
        # period -- coherent. 4.5 Hz: half a period left over, must be flagged.
        ok = coherence.coherence_problems({"f": 4.0}, 1.0, 1.0 / 64)
        self.assertEqual(ok, [])
        bad = coherence.coherence_problems({"f": 4.5}, 1.0, 1.0 / 64)
        self.assertEqual(len(bad), 1)
        self.assertIn("not coherent", bad[0])

    def test_window_not_integer_samples_flagged(self):
        problems = coherence.coherence_problems(
            {"f": 64.0}, 1.0005, 1.0 / 2 ** 12)
        self.assertTrue(any("not an integer number" in p for p in problems))

    def test_settle_discard_off_grid_flagged(self):
        problems = coherence.coherence_problems(
            {"f": 1.0}, 1.0, 1.0 / 64, settle_discard_s=0.3)
        self.assertEqual(problems,
                         ["settling discard 0.3 s does not land on a sample "
                          "(19.200000)"])

    def test_too_few_samples_per_period_flagged(self):
        # 2 Hz: 2 periods in 1 s, 32 samples per period -- fine. 16 Hz: 16
        # coherent periods but only 4 samples per period, must be flagged.
        ok = coherence.coherence_problems({"f": 2.0}, 1.0, 1.0 / 64)
        self.assertEqual(ok, [])
        bad = coherence.coherence_problems({"f": 16.0}, 1.0, 1.0 / 64)
        self.assertEqual(len(bad), 1)
        self.assertIn("fewer than 8 samples per period", bad[0])

    def test_halved_step_plan_stays_coherent(self):
        problems = coherence.coherence_problems(
            {"rf": runner.F_RF, "lo": runner.F_LO, "if": runner.F_IF},
            runner.N_WINDOW * runner.DT_S / 2, runner.DT_S / 2,
            settle_discard_s=runner.DISCARD_S)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
