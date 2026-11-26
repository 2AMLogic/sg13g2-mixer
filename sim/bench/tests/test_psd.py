"""Unit tests for mechanic M3 (stamped window/PSD stack).

Reproduces, against this stamped copy, the reference behaviours upstream's
`sim/mixer-nf-method/tests/test_nfmethod.py` covers: window shapes and ENBW,
one-sided PSD normalisation of a known tone, the Parseval rejection test and
the band-width gate. Needs numpy (`sim/bench/mkenv.sh`); skipped when the
venv is absent so a stdlib-only `check-python.sh` run stays green.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

try:
    import numpy as np
except ImportError:                                    # pragma: no cover
    np = None

if np is not None:
    from sim.bench.lib import nfcommon, psd


@unittest.skipIf(np is None, "numpy not installed (sim/bench/mkenv.sh)")
class TestWindowAndEnbw(unittest.TestCase):
    def test_rect_window_is_flat_enbw_one(self):
        w = psd.window("rect", 64)
        self.assertEqual(w.shape, (64,))
        self.assertTrue(np.all(w == 1.0))
        self.assertAlmostEqual(psd.enbw_bins(w), 1.0, places=12)

    def test_periodic_hann_enbw_three_halves(self):
        w = psd.window("hann", 64)
        # periodic (DFT-even): w[0] is exactly 0, w[n/2] hits the maximum
        self.assertAlmostEqual(w[0], 0.0, places=12)
        self.assertAlmostEqual(float(w[32]), 1.0, places=12)
        self.assertAlmostEqual(psd.enbw_bins(w), 1.5, places=12)

    def test_unknown_window_rejected(self):
        with self.assertRaises(nfcommon.NormalizationError):
            psd.window("blackman?", 8)


@unittest.skipIf(np is None, "numpy not installed (sim/bench/mkenv.sh)")
class TestOneSidedPsd(unittest.TestCase):
    def test_known_tone_bin_power(self):
        n, fs, amp = 4096, 1.0e6, 0.2
        k = 37
        t = np.arange(n) / fs
        x = amp * np.cos(2.0 * math.pi * (k * fs / n) * t)
        f, p, meta = psd.one_sided_psd(x, fs, win="rect")
        self.assertAlmostEqual(meta["df_hz"], fs / n, places=12)
        # one-sided PSD: the tone's A^2/2 mean-square lands on one bin,
        # as a density: p[k] = (A^2/2) / df
        self.assertAlmostEqual(float(p[k]), amp ** 2 / 2.0 / meta["df_hz"],
                               delta=1e-12)
        ratio = psd.check_parseval(x, p, meta)
        self.assertAlmostEqual(ratio, 1.0, places=6)

    def test_too_short_record_rejected(self):
        with self.assertRaises(nfcommon.NormalizationError):
            psd.one_sided_psd([0.0] * 8, 1.0)


@unittest.skipIf(np is None, "numpy not installed (sim/bench/mkenv.sh)")
class TestBandPower(unittest.TestCase):
    def test_tone_band_power_matches_mean_square(self):
        n, fs, amp = 8192, 1.0e6, 0.2
        k = 820                      # tone at ~100.1 kHz, inside the band
        t = np.arange(n) / fs
        x = amp * np.cos(2.0 * math.pi * (k * fs / n) * t)
        f, p, meta = psd.one_sided_psd(x, fs, win="hann")
        p_band, bw = psd.band_power(f, p, meta, 90e3, 110e3)
        self.assertAlmostEqual(p_band, amp ** 2 / 2.0, delta=1e-8)
        self.assertAlmostEqual(bw, 20e3, delta=meta["df_hz"])

    def test_band_narrower_than_four_enbw_rejected(self):
        n, fs = 8192, 1.0e6
        x = np.random.default_rng(4).normal(0.0, 1e-3, n)
        f, p, meta = psd.one_sided_psd(x, fs, win="hann")
        with self.assertRaises(nfcommon.NormalizationError):
            psd.band_power(f, p, meta, 100e3, 100e3 + meta["enbw_hz"])

    def test_band_outside_nyquist_rejected(self):
        n, fs = 4096, 1.0e6
        x = np.random.default_rng(5).normal(0.0, 1e-3, n)
        f, p, meta = psd.one_sided_psd(x, fs, win="hann")
        with self.assertRaises(nfcommon.NormalizationError):
            psd.band_power(f, p, meta, 100e3, fs / 2 + 1.0)


if __name__ == "__main__":
    unittest.main()
