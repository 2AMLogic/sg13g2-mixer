"""Unit tests for mechanic M4 (settling / convergence gate), written here.

The gate encodes this repo's protocol numbers (< 0.1 dB following-window,
< 0.1 dB step halving) — not upstream's 0.25 dB policy constants, which the
stamp would have imported (record 0002, M4).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from sim.bench.lib import convergence                  # noqa: E402


class TestConvergenceGate(unittest.TestCase):
    def test_clean_below_tolerance(self):
        self.assertEqual(
            convergence.convergence_failures(0.099, 0.099, name="x"), [])

    def test_boundary_is_a_failure(self):
        # The protocol says reproduce to < 0.1 dB: a delta of exactly 0.1
        # has not reproduced the figure.
        self.assertEqual(len(convergence.convergence_failures(0.1, 0.1)), 2)

    def test_following_window_only_leg(self):
        out = convergence.convergence_failures(0.2, None)
        self.assertEqual(len(out), 1)
        self.assertIn("following-window", out[0])

    def test_missing_or_negative_rejected(self):
        self.assertTrue(convergence.convergence_failures(None))
        self.assertTrue(convergence.convergence_failures(-0.01, name="x"))
        self.assertTrue(convergence.convergence_failures(0.0, -1.0, name="x"))

    def test_named_failure_strings(self):
        out = convergence.convergence_failures(0.5, 0.5, name="b_cg")
        self.assertTrue(all(l.startswith("b_cg:") for l in out))
        self.assertIn("lengthen the settling discard", out[0])
        self.assertIn("fix the bench, do not proceed", out[1])


if __name__ == "__main__":
    unittest.main()
