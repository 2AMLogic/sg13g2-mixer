"""Tone placement / coherence pre-flight check (bench mechanic M2).

Stamped copy, taken verbatim from `2AMLogic/sg13g2-sat-rx`
@ 6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947,
`sim/lna-linearity/linearity.py`, symbols: [coherence_problems].

Upstream licence: Apache-2.0 (its LICENSE at that commit); this repo is
Apache-2.0. Recorded in `reuse.lock.json` (schema 2, entry per dest).
`local_edits: none` -- an improvement belongs upstream or in a local
wrapper, never patched here. Contract: spec/decision-records/0002 (M2).
"""
from __future__ import annotations

def coherence_problems(freqs: dict[str, float], window_s: float, step_s: float,
                       settle_discard_s: float = 0.0, tol: float = 1e-9) -> list[str]:
    """Why a set of analysed frequencies is NOT coherent with the window.

    Every frequency must complete an integer number of periods in the window,
    the window must be an integer number of samples, the settling discard must
    land on a sample, and the highest analysed frequency must be well below
    Nyquist (>= 8 samples per period). Returns [] when coherent."""
    out = []
    n = window_s / step_s
    if abs(n - round(n)) > tol * max(1.0, n):
        out.append(f"window {window_s:g} s is not an integer number of {step_s:g} s samples ({n:.6f})")
    d = settle_discard_s / step_s
    if abs(d - round(d)) > tol * max(1.0, d):
        out.append(f"settling discard {settle_discard_s:g} s does not land on a sample ({d:.6f})")
    for name, f in sorted(freqs.items()):
        cyc = f * window_s
        if abs(cyc - round(cyc)) > tol * max(1.0, cyc):
            out.append(f"{name} = {f:.9g} Hz completes {cyc:.6f} periods in the window: not coherent")
        if f * step_s > 1.0 / 8.0:
            out.append(f"{name} = {f:.9g} Hz has fewer than 8 samples per period at step {step_s:g} s")
    return out
