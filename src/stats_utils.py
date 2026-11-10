"""Shared helpers for intervals and effect sizes (action item F1).

Every function returns plain numbers so results can go straight into tables.
Randomness always comes from a numpy Generator seeded from src.config.SEED.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_confint,
)

from src.config import ALPHA, N_BOOT, SEED


def _rng(seed: int | np.random.Generator | None) -> np.random.Generator:
    if isinstance(seed, np.random.Generator):
        return seed
    return np.random.default_rng(SEED if seed is None else seed)


# ---------------------------------------------------------------- bootstrap

def boot_ci(
    x,
    stat: Callable[[np.ndarray], float] = np.mean,
    B: int = N_BOOT,
    alpha: float = ALPHA,
    seed=None,
) -> tuple[float, float, float]:
    """Percentile bootstrap CI for a one-sample statistic.

    Returns (estimate, lower, upper).
    """
    x = np.asarray(x)
    rng = _rng(seed)
    idx = rng.integers(0, len(x), size=(B, len(x)))
    boots = np.apply_along_axis(stat, 1, x[idx])
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(stat(x)), float(lo), float(hi)


def boot_ci_diff(
    x,
    y,
    stat: Callable[[np.ndarray], float] = np.mean,
    B: int = N_BOOT,
    alpha: float = ALPHA,
    seed=None,
) -> tuple[float, float, float]:
    """Percentile bootstrap CI for stat(x) - stat(y).

    Each group is resampled separately (stratified), so every bootstrap
    sample keeps the original group sizes, e.g. all 249 strokes.
    Returns (estimate, lower, upper).
    """
    x, y = np.asarray(x), np.asarray(y)
    rng = _rng(seed)
    bx = x[rng.integers(0, len(x), size=(B, len(x)))]
    by = y[rng.integers(0, len(y), size=(B, len(y)))]
    diffs = np.apply_along_axis(stat, 1, bx) - np.apply_along_axis(stat, 1, by)
    lo, hi = np.quantile(diffs, [alpha / 2, 1 - alpha / 2])
    return float(stat(x) - stat(y)), float(lo), float(hi)


# -------------------------------------------------------------- proportions

def wilson_ci(count: int, n: int, alpha: float = ALPHA) -> tuple[float, float, float]:
    """Wilson score CI for a proportion. Returns (p, lower, upper)."""
    lo, hi = proportion_confint(count, n, alpha=alpha, method="wilson")
    return count / n, float(lo), float(hi)


def risk_difference(
    c1: int, n1: int, c2: int, n2: int, alpha: float = ALPHA
) -> tuple[float, float, float]:
    """p1 - p2 with Newcombe's hybrid score CI. Returns (diff, lower, upper)."""
    lo, hi = confint_proportions_2indep(
        c1, n1, c2, n2, method="newcomb", compare="diff", alpha=alpha
    )
    return c1 / n1 - c2 / n2, float(lo), float(hi)


def risk_ratio(
    c1: int, n1: int, c2: int, n2: int, alpha: float = ALPHA
) -> tuple[float, float, float]:
    """p1 / p2 with a log-scale CI. Returns (ratio, lower, upper)."""
    lo, hi = confint_proportions_2indep(
        c1, n1, c2, n2, method="log", compare="ratio", alpha=alpha
    )
    return (c1 / n1) / (c2 / n2), float(lo), float(hi)


# ------------------------------------------------------------- effect sizes

def hedges_g(x, y) -> float:
    """Standardised mean difference (x - y) with small-sample correction."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    nx, ny = len(x), len(y)
    sp = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    d = (x.mean() - y.mean()) / sp
    return float(d * (1 - 3 / (4 * (nx + ny) - 9)))


def cliffs_delta(x, y) -> float:
    """Cliff's delta = P(X > Y) - P(X < Y). Ranges from -1 to 1."""
    x, y = np.asarray(x), np.asarray(y)
    u = stats.mannwhitneyu(x, y, alternative="two-sided").statistic
    return float(2 * u / (len(x) * len(y)) - 1)


def fmt_ci(est: float, lo: float, hi: float, digits: int = 2, pct: bool = False) -> str:
    """Format as 'est (lo to hi)' for tables and the report."""
    k = 100 if pct else 1
    unit = "%" if pct else ""
    return f"{est * k:.{digits}f}{unit} ({lo * k:.{digits}f} to {hi * k:.{digits}f})"
