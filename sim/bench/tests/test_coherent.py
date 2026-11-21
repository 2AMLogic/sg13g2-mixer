"""Unit tests for mechanic M1 (coherent single-bin DFT), written here.

Known answers: a pure tone of peak amplitude A exactly at bin k must read A
whatever its phase, and the reading must be phase-independent — the property
known-answer case 5 grades across the deck half and this Python half.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from sim.bench.lib import coherent                      # noqa: E402


def tone(n, k, amp, phase):
    return [amp * math.cos(2.0 * math.pi * k * i / n + phase)
            for i in range(n)]


class TestDftAmplitude(unittest.TestCase):
    def test_exact_bin_returns_peak_amplitude_any_phase(self):
        n = 256
        for phase in (0.0, math.pi / 2, 0.7, -2.0):
            self.assertAlmostEqual(
                coherent.dft_amplitude(tone(n, 5, 0.3, phase), 5), 0.3, places=12)

    def test_amplitude_scales(self):
        n = 128
        for amp in (1e-3, 1.0, 12.5):
            self.assertAlmostEqual(
                coherent.dft_amplitude(tone(n, 3, amp, 0.0), 3), amp, places=12)

    def test_dc_offset_does_not_leak_into_exact_bin(self):
        n = 128
        x = [0.25 + 0.1 * math.cos(2.0 * math.pi * 7 * i / n) for i in range(n)]
        self.assertAlmostEqual(coherent.dft_amplitude(x, 7), 0.1, places=12)

    def test_bin_outside_half_length_rejected(self):
        with self.assertRaises(ValueError):
            coherent.dft_amplitude([0.0] * 8, 4)          # k must be < N/2
        with self.assertRaises(ValueError):
            coherent.dft_amplitude([0.0] * 8, -1)
        with self.assertRaises(ValueError):
            coherent.dft_amplitude([], 1)

    def test_db(self):
        self.assertAlmostEqual(coherent.db(10.0 ** (6.0 / 20.0)), 6.0, places=12)
        with self.assertRaises(ValueError):
            coherent.db(0.0)


if __name__ == "__main__":
    unittest.main()
