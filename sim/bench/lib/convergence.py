"""Settling / convergence gate (bench mechanic M4) -- written here.

Record 0002 (spec/decision-records/0002-shared-bench-mechanics.md, M4)
decides this mechanic is written here, not stamped: upstream's
``convergence_failures`` is structurally the model (a list of named
failure strings, empty when clean -- that structure is cited, not copied),
but its thresholds are the Ka-band study's methodology-qualification
limits, and a stamp whose load-bearing numbers are locally edited is not
a stamp. The numbers below are this repo's protocol numbers, fixed by
``spec/target-spec.md`` "Measurement protocol"; changing them is a spec
change, not a bench tweak.

The V4 statistical interval (record 0002, M7: the 1-sigma Welch error,
<= 0.3 dB over >= 256 averages) also lands in this module, with the
noise benches that need it -- nothing here pre-empts it.
"""

from __future__ import annotations

FOLLOWING_WINDOW_MAX_DB = 0.1
"""The same analysis on the following window must reproduce every reported
figure to better than this (protocol "Settling"), else the settling discard
is lengthened and the run repeated."""

STEP_HALVING_MAX_DB = 0.1
"""Halving the time step (12.5 ps -> 6.25 ps) must move a reported figure
by less than this before the result is reported (protocol "Time-step
convergence")."""


def convergence_failures(following_window_db, step_halving_db=None,
                         name="figure"):
    """Named convergence failures for one reported figure; [] when clean.

    ``following_window_db`` is |window - following window| in dB for the
    figure; ``step_halving_db`` is |step - step/2| in dB (``None`` when the
    halved-step run has not been made -- the caller then only learns about
    the following-window leg, and a reported result still needs both).
    """
    out = []
    if following_window_db is None or following_window_db < 0:
        out.append(f"{name}: following-window delta missing or negative")
    elif following_window_db >= FOLLOWING_WINDOW_MAX_DB:
        out.append(
            f"{name}: following-window delta {following_window_db:.4f} dB "
            f">= {FOLLOWING_WINDOW_MAX_DB} dB: lengthen the settling discard "
            "and repeat the run")
    if step_halving_db is not None:
        if step_halving_db < 0:
            out.append(f"{name}: step-halving delta negative")
        elif step_halving_db >= STEP_HALVING_MAX_DB:
            out.append(
                f"{name}: step-halving delta {step_halving_db:.4f} dB "
                f">= {STEP_HALVING_MAX_DB} dB: fix the bench, do not proceed "
                "(V3 stop condition)")
    return out
