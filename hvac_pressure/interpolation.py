"""
interpolation.py — Generic 1D, 2D, and 3D linear interpolation engine.

Used by the ASHRAE fitting lookup system to interpolate loss coefficients
from tabulated data. All interpolation is linear (not polynomial), consistent
with ASHRAE practice.
"""

from typing import List, Tuple, Optional
import bisect


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi] range."""
    return max(lo, min(hi, value))


def interp1d(x_vals: List[float], y_vals: List[float], x: float) -> float:
    """
    Linear interpolation / extrapolation-clamped on a 1D table.

    Parameters
    ----------
    x_vals : list of float
        Sorted list of parameter values (x-axis). Must be ascending.
    y_vals : list of float
        Corresponding coefficient values (y-axis).
    x : float
        Query value. Clamped to [x_vals[0], x_vals[-1]] if out of range.

    Returns
    -------
    float
        Interpolated coefficient.

    Raises
    ------
    ValueError
        If x_vals and y_vals have different lengths or fewer than 2 points.
    """
    if len(x_vals) != len(y_vals):
        raise ValueError("x_vals and y_vals must have the same length.")
    if len(x_vals) < 2:
        raise ValueError("At least 2 data points are required for interpolation.")

    x = _clamp(x, x_vals[0], x_vals[-1])

    # Find insertion point
    idx = bisect.bisect_right(x_vals, x)
    if idx == 0:
        return y_vals[0]
    if idx >= len(x_vals):
        return y_vals[-1]

    x0, x1 = x_vals[idx - 1], x_vals[idx]
    y0, y1 = y_vals[idx - 1], y_vals[idx]

    if x1 == x0:
        return y0

    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def interp2d(
    p1_vals: List[float],
    p2_vals: List[float],
    table: List[List[float]],
    p1: float,
    p2: float,
) -> float:
    """
    Bilinear interpolation on a 2D table.

    Parameters
    ----------
    p1_vals : list of float
        Sorted row axis values (param1). Must be ascending.
    p2_vals : list of float
        Sorted column axis values (param2). Must be ascending.
    table : list of list of float
        2D table where table[i][j] corresponds to (p1_vals[i], p2_vals[j]).
        Shape must be len(p1_vals) × len(p2_vals).
    p1 : float
        Query value for param1. Clamped to table bounds.
    p2 : float
        Query value for param2. Clamped to table bounds.

    Returns
    -------
    float
        Bilinearly interpolated coefficient.
    """
    p1 = _clamp(p1, p1_vals[0], p1_vals[-1])
    p2 = _clamp(p2, p2_vals[0], p2_vals[-1])

    # Row indices
    i1 = bisect.bisect_right(p1_vals, p1)
    if i1 == 0:
        i1 = 1
    if i1 >= len(p1_vals):
        i1 = len(p1_vals) - 1
    i0 = i1 - 1

    # Column indices
    j1 = bisect.bisect_right(p2_vals, p2)
    if j1 == 0:
        j1 = 1
    if j1 >= len(p2_vals):
        j1 = len(p2_vals) - 1
    j0 = j1 - 1

    p1_0, p1_1 = p1_vals[i0], p1_vals[i1]
    p2_0, p2_1 = p2_vals[j0], p2_vals[j1]

    # Four corner values
    q00 = table[i0][j0]
    q01 = table[i0][j1]
    q10 = table[i1][j0]
    q11 = table[i1][j1]

    # Normalised coordinates
    t1 = (p1 - p1_0) / (p1_1 - p1_0) if p1_1 != p1_0 else 0.0
    t2 = (p2 - p2_0) / (p2_1 - p2_0) if p2_1 != p2_0 else 0.0

    # Bilinear formula
    return (
        q00 * (1 - t1) * (1 - t2)
        + q10 * t1 * (1 - t2)
        + q01 * (1 - t1) * t2
        + q11 * t1 * t2
    )


def interp3d(
    p1_vals: List[float],
    p2_vals: List[float],
    p3_vals: List[float],
    table: List[List[List[float]]],
    p1: float,
    p2: float,
    p3: float,
) -> float:
    """
    Trilinear interpolation on a 3D table.

    Parameters
    ----------
    p1_vals : list of float
        Sorted axis values for dimension 1. Must be ascending.
    p2_vals : list of float
        Sorted axis values for dimension 2. Must be ascending.
    p3_vals : list of float
        Sorted axis values for dimension 3. Must be ascending.
    table : list[list[list[float]]]
        3D table where table[i][j][k] = C at (p1_vals[i], p2_vals[j], p3_vals[k]).
    p1, p2, p3 : float
        Query values. Each is clamped to its respective axis bounds.

    Returns
    -------
    float
        Trilinearly interpolated coefficient.
    """
    p1 = _clamp(p1, p1_vals[0], p1_vals[-1])
    p2 = _clamp(p2, p2_vals[0], p2_vals[-1])
    p3 = _clamp(p3, p3_vals[0], p3_vals[-1])

    def _idx(vals, v):
        i = bisect.bisect_right(vals, v)
        if i == 0:
            i = 1
        if i >= len(vals):
            i = len(vals) - 1
        return i - 1, i

    i0, i1 = _idx(p1_vals, p1)
    j0, j1 = _idx(p2_vals, p2)
    k0, k1 = _idx(p3_vals, p3)

    def _t(vals, i_lo, i_hi, v):
        d = vals[i_hi] - vals[i_lo]
        return (v - vals[i_lo]) / d if d != 0 else 0.0

    t1 = _t(p1_vals, i0, i1, p1)
    t2 = _t(p2_vals, j0, j1, p2)
    t3 = _t(p3_vals, k0, k1, p3)

    # Trilinear: interpolate along p3 first, then p2, then p1
    def _c(i, j, k):
        return table[i][j][k]

    c000 = _c(i0, j0, k0)
    c001 = _c(i0, j0, k1)
    c010 = _c(i0, j1, k0)
    c011 = _c(i0, j1, k1)
    c100 = _c(i1, j0, k0)
    c101 = _c(i1, j0, k1)
    c110 = _c(i1, j1, k0)
    c111 = _c(i1, j1, k1)

    return (
        c000 * (1 - t1) * (1 - t2) * (1 - t3)
        + c100 * t1 * (1 - t2) * (1 - t3)
        + c010 * (1 - t1) * t2 * (1 - t3)
        + c110 * t1 * t2 * (1 - t3)
        + c001 * (1 - t1) * (1 - t2) * t3
        + c101 * t1 * (1 - t2) * t3
        + c011 * (1 - t1) * t2 * t3
        + c111 * t1 * t2 * t3
    )
