"""Shared preamble for the stamped bench mechanics (record 0002, M3/M6).

Stamped copy, taken verbatim from `2AMLogic/sg13g2-sat-rx`
@ 6e5ebaf57ee8ec2288f5bd3048fbfee9b7d41947,
`sim/mixer-nf-method/nfmethod.py`, symbols: [K_B, T0_K, MethodError,
NormalizationError, ImageAccountingError].

Upstream licence: Apache-2.0 (its LICENSE at that commit); this repo is
Apache-2.0. Recorded in `reuse.lock.json` (schema 2, entry per dest).
`local_edits: none` -- an improvement belongs upstream or in a local
wrapper, never patched here. Contract: spec/decision-records/0002
("Closure of a `symbols` list", rule 3): the constants and exception
classes shared upstream are owned here once, so `psd.py` (M3) and any
later noise-sideband mechanic import one type, not two.
"""

K_B = 1.380649e-23  # J/K (exact, SI 2019)

T0_K = 300.15       # reference temperature, K (27 C)

class MethodError(ValueError):
    """An estimator/accounting defect: never converted into a record status."""

class NormalizationError(MethodError):
    pass

class ImageAccountingError(MethodError):
    pass
