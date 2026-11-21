"""Coherent single-bin DFT (bench mechanic M1) -- both halves, written here.

Record 0002 (spec/decision-records/0002-shared-bench-mechanics.md, M1)
decides this mechanic is written here, not stamped: upstream carries three
mutually inconsistent conventions (`dft_bin`, sine-referenced; `window_dft`,
real magnitude; `phasor_from_integrals`, cosine-referenced with a conjugate
sign), so a stamp would import the ambiguity instead of resolving it. This
repo's protocol (spec/target-spec.md, "Measurement protocol") fixes its own
convention: rectangular window, every tone on an exact bin centre, and the
peak amplitude read at a named bin. Upstream `window_dft`'s normalisation
(a real peak amplitude ``2 |sum x e^{-j w t}| / n``) is the reference this
module reproduces; the citation is not a copy.

Two halves, one convention (known-answer case 5 checks them against each
other to < 0.05 dB on every reported tone):

Python half
    :func:`dft_amplitude` -- the single-bin DFT over ``N`` uniformly spaced
    samples, returning the peak amplitude at bin ``k``:

        A(k) = (2 / N) * | sum_{n=0}^{N-1} x[n] * exp(-2j*pi*k*n/N) |

    For a tone of peak amplitude ``A`` exactly at bin ``k`` this returns
    ``A`` to numerical precision, whatever its phase. This half is the
    known-answer oracle for the deck half; it uses only the standard
    library (no numpy), so every bench that reads coherent tones can run
    without third-party dependencies.

Deck half
    :data:`DECK_RECIPE` -- the ngspice control-block expression that
    evaluates the same quantity in the simulator. With ``set
    specwindow=none`` (rectangular) and a record whose length is exactly a
    power of two sampled uniformly at the transient step, ``linearize np=N``
    followed by ``fft`` gives ``mag(v(x))[k]`` = peak amplitude of bin ``k``
    directly (ngspice 46 scales the one-sided spectrum by ``N/2``, which is
    the same normalisation as the Python half). Zero padding is avoided by
    making the linearised length exactly a power of two; a record of any
    other length is padded to the next power of two and the bin amplitude
    is diluted by ``N_padded / length``, so the benches never do that.
"""

from __future__ import annotations

import math

DECK_RECIPE = """\
set filetype=ascii
set specwindow=none
tran {tstep} {tstop} {tstart} {tstep}
linearize np={n_full} v({node})
wrdata {samples} v({node})
set uniform = $curplot
"""
"""Prepare the shared uniform record used by the deck FFTs and Python DFTs."""


def window_fft(node, bins, n_window, window, start_index):
    """Read the named bins from one window of the saved uniform plot."""
    lines = ["setplot $uniform", f"let lin-tstart = time[{start_index}]",
             f"linearize np={n_window} v({node})", f"fft v({node})",
             f"let am = mag(v({node}))"]
    for name, index in bins.items():
        label = f"a_{window}_{name}"
        lines.extend((f"let {label} = am[{index}]", f"print {label}"))
    return "\n".join(lines) + "\n"


def dft_amplitude(samples, bin_index):
    """Peak amplitude of ``bin_index`` over uniformly spaced ``samples``.

    ``samples`` is any sequence of ``N`` values taken at equal intervals,
    with every analysed tone on an exact bin centre (checked before this
    is called by the M2 stamp, ``coherence.coherence_problems``). Pure
    standard library: the complex phasor is advanced by recurrence, one
    multiply-add per sample, so no third-party dependency is needed to
    read a coherent tone. Returns the peak amplitude (volts for a voltage
    record), phase-independent for exact-bin tones.
    """
    n = len(samples)
    if n <= 0:
        raise ValueError("no samples")
    if not 0 <= bin_index < n / 2:
        raise ValueError(f"bin {bin_index} outside (0, N/2) for N={n}")
    step = complex(math.cos(-2.0 * math.pi * bin_index / n),
                   math.sin(-2.0 * math.pi * bin_index / n))
    z = 1.0 + 0.0j
    acc = 0.0 + 0.0j
    for x in samples:
        acc += z * x
        z *= step
    return 2.0 * abs(acc) / n


def db(ratio):
    """20*log10 of a positive amplitude ratio (the dB the gates read)."""
    if ratio <= 0:
        raise ValueError(f"non-positive ratio {ratio}")
    return 20.0 * math.log10(ratio)
