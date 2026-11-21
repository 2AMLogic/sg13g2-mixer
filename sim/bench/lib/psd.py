"""Window / PSD normalisation and cross-checks (bench mechanic M3).

Stamped copy, taken verbatim from `2AMLogic/sg13g2-sat-rx`
@ 6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947,
`sim/mixer-nf-method/nfmethod.py`, symbols: [window, enbw_bins,
one_sided_psd, check_parseval, band_power].

Upstream licence: Apache-2.0 (its LICENSE at that commit); this repo is
Apache-2.0. Recorded in `reuse.lock.json` (schema 2, entry per dest).
`local_edits: none` -- an improvement belongs upstream or in a local
wrapper, never patched here. Contract: spec/decision-records/0002 (M3);
the shared constants/exceptions it references arrive via the header
import below, which is part of the dest the lock hashes, not an edit.

numpy is required by this module (record 0002, M3 consequence):
`sim/bench/requirements.txt`, installed by CI and the bench cold start.
"""
from __future__ import annotations

import math
from typing import Mapping, Sequence

import numpy as np

from .nfcommon import NormalizationError

def window(name: str, n: int) -> np.ndarray:
    if name == "rect":
        return np.ones(n)
    if name == "hann":
        # periodic Hann (DFT-even), the usual choice for spectral estimation
        return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n) / n)
    raise NormalizationError(f"unknown window {name!r}")

def enbw_bins(w: np.ndarray) -> float:
    """Equivalent noise bandwidth of window ``w`` in DFT bins: N sum(w^2)/sum(w)^2."""
    return len(w) * float(np.sum(w * w)) / float(np.sum(w)) ** 2

def one_sided_psd(x: Sequence[float], fs: float, win: str = "hann",
                  detrend: bool = True) -> tuple[np.ndarray, np.ndarray, dict]:
    """One-sided periodogram PSD of a uniformly sampled record.

    Returns ``(f, psd, meta)``. Normalisation: ``psd = c |X_k|^2 / (fs sum w^2)``
    with ``c = 2`` for 0 < k < N/2 and ``c = 1`` for DC and Nyquist, so that
    ``sum(psd) * df`` equals the mean-square of the (windowed-power-corrected)
    record. ``meta`` carries ``df``, ``enbw_bins`` and ``enbw_hz``.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < 16:
        raise NormalizationError("record too short for a PSD estimate")
    if not (fs > 0 and math.isfinite(fs)):
        raise NormalizationError("sample rate must be positive and finite")
    if detrend:
        x = x - x.mean()
    w = window(win, n)
    spec = np.fft.rfft(x * w)
    psd = (np.abs(spec) ** 2) / (fs * float(np.sum(w * w)))
    scale = np.full(psd.shape, 2.0)
    scale[0] = 1.0
    if n % 2 == 0:
        scale[-1] = 1.0
    psd = psd * scale
    f = np.fft.rfftfreq(n, d=1.0 / fs)
    df = fs / n
    eb = enbw_bins(w)
    return f, psd, {"df_hz": df, "enbw_bins": eb, "enbw_hz": eb * df, "n": n,
                    "fs_hz": fs, "window": win, "one_sided": True}

def check_parseval(x: Sequence[float], psd: np.ndarray, meta: Mapping, rtol: float = 0.05) -> float:
    """Reject a PSD whose integral does not reproduce the record's variance.

    A two-sided PSD, a missing window-power correction or a wrong ``df`` all
    fail this check. Returns the ratio integral/variance.
    """
    x = np.asarray(x, dtype=float)
    var = float(np.var(x))
    if var <= 0:
        raise NormalizationError("zero-variance record: nothing to normalise")
    if not meta.get("one_sided"):
        raise NormalizationError("PSD is not declared one-sided")
    integral = float(np.sum(psd) * meta["df_hz"])
    ratio = integral / var
    if abs(ratio - 1.0) > rtol:
        raise NormalizationError(
            f"PSD integral / variance = {ratio:.4f} (expected 1 within {rtol}); "
            "two-sided, window-uncorrected or mis-scaled PSD")
    return ratio

def band_power(f: np.ndarray, psd: np.ndarray, meta: Mapping, f_lo: float, f_hi: float,
               min_enbw_multiple: float = 4.0) -> tuple[float, float]:
    """Integrate a one-sided PSD over [f_lo, f_hi]; returns (power, bandwidth_hz).

    The band must lie strictly inside (0, fs/2) and span at least
    ``min_enbw_multiple`` window ENBWs, otherwise window leakage, not the
    noise, sets the answer and the estimate is rejected.
    """
    if not meta.get("one_sided"):
        raise NormalizationError("band_power needs a one-sided PSD")
    nyq = meta["fs_hz"] / 2.0
    if not (0.0 < f_lo < f_hi < nyq):
        raise NormalizationError(f"band [{f_lo}, {f_hi}] Hz not inside (0, fs/2={nyq})")
    if (f_hi - f_lo) < min_enbw_multiple * meta["enbw_hz"]:
        raise NormalizationError(
            f"band {f_hi - f_lo:.4g} Hz narrower than {min_enbw_multiple} x ENBW "
            f"({meta['enbw_hz']:.4g} Hz)")
    sel = (f >= f_lo) & (f <= f_hi)
    nb = int(np.count_nonzero(sel))
    bw = nb * meta["df_hz"]
    return float(np.sum(psd[sel]) * meta["df_hz"]), bw
