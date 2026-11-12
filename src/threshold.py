"""Track 5: referral threshold, decision curve and threshold uncertainty.

Used by notebooks/07_threshold_decision.ipynb (action items A2, A3, A4).

Conventions (KB 02, KB 06):

* Refer a patient when predicted risk p >= t.
* Cost ratio R = C_FN / C_FP. Costs are counted in units of one unnecessary
  referral (C_FP = 1), so a missed stroke costs R.
* Expected cost per 1,000 patients at threshold t:
      cost(t) = 1000 * (FP(t) + R * FN(t)) / n
* Net benefit (Vickers & Elkin 2006) at threshold t:
      NB(t) = TP/n - FP/n * t / (1 - t)
  At t = p* = 1 / (1 + R) the two are linked by
      cost(p*) = R * (1000 * prevalence - 1000 * NB(p*)),
  so the threshold that minimises expected cost at R is the threshold that
  maximises net benefit at p*. We use net_benefit() and p_star() from
  src/hypotheses.py so our numbers match Track 4's H1 and H2.
* Uncertainty in the threshold has two separate sources (KB 06), reported
  separately: sampling (bootstrap) and the cost ratio (sweep over R).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from src.config import ALPHA, N_FOLDS, N_IMPUTATIONS, SEED, TARGET
from src.hypotheses import net_benefit, p_star  # noqa: F401  (re-exported for the notebook)
from src.modeling import MODEL_COLS, BMIImputer, _fit_logit, _predict, design
from src.stats_utils import wilson_ci

# Thresholds searched: 0.5% to 30% in steps of 0.05 percentage points.
# Fewer than 5% of patients have predicted risk above 20%, so 30% covers
# every threshold a physician would consider.
THRESHOLD_GRID = np.round(np.arange(0.005, 0.30 + 1e-9, 0.0005), 4)


# ------------------------------------------------------- counts over a grid

def counts_over_grid(y, p, grid=THRESHOLD_GRID) -> dict[str, np.ndarray]:
    """TP, FP, FN, TN at every threshold in `grid` (refer when p >= t).

    Vectorised with sorted predictions, so a whole grid costs about as much as
    one sort. Used inside the bootstrap loops.
    """
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    grid = np.asarray(grid, float)
    p1 = np.sort(p[y == 1])
    p0 = np.sort(p[y == 0])
    # number of patients with p >= t = n - (number with p < t)
    tp = len(p1) - np.searchsorted(p1, grid, side="left")
    fp = len(p0) - np.searchsorted(p0, grid, side="left")
    return {"TP": tp, "FP": fp, "FN": len(p1) - tp, "TN": len(p0) - fp, "n": len(y)}


def expected_cost(y, p, R: float, grid=THRESHOLD_GRID) -> np.ndarray:
    """Expected cost per 1,000 patients at each threshold, in units of C_FP."""
    c = counts_over_grid(y, p, grid)
    return 1000.0 * (c["FP"] + R * c["FN"]) / c["n"]


def best_threshold(cost: np.ndarray, grid=THRESHOLD_GRID) -> float:
    """Threshold that minimises expected cost.

    The empirical cost is a step function, so the minimum is often a flat run
    of grid points. We return the middle of the first run that reaches the
    minimum, rather than its left edge.
    """
    cost = np.asarray(cost, float)
    i = int(np.argmin(cost))
    j = i
    while j + 1 < len(cost) and np.isclose(cost[j + 1], cost[i]):
        j += 1
    return float(grid[(i + j) // 2])


def flat_band(cost: np.ndarray, tol: float, grid=THRESHOLD_GRID) -> tuple[float, float]:
    """Contiguous range of thresholds around the minimum with cost <= (1 + tol) * min."""
    cost = np.asarray(cost, float)
    i = int(np.argmin(cost))
    ok = cost <= (1 + tol) * cost[i]
    lo = i
    while lo - 1 >= 0 and ok[lo - 1]:
        lo -= 1
    hi = i
    while hi + 1 < len(cost) and ok[hi + 1]:
        hi += 1
    return float(grid[lo]), float(grid[hi])


# ------------------------------------------------------------ A2: the sweep

def sweep_table(y, p, R: float, grid=THRESHOLD_GRID) -> pd.DataFrame:
    """Threshold sweep in physician units (A2). One row per threshold."""
    c = counts_over_grid(y, p, grid)
    n = c["n"]
    tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]
    ref = tp + fp
    with np.errstate(divide="ignore", invalid="ignore"):
        ppv = np.where(ref > 0, tp / ref, np.nan)
        out = pd.DataFrame({
            "threshold": grid,
            "referred": ref, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "referrals_per_1000": 1000 * ref / n,
            "strokes_caught_per_1000": 1000 * tp / n,
            "strokes_missed_per_1000": 1000 * fn / n,
            "sensitivity": tp / (tp + fn),
            "specificity": tn / (tn + fp),
            "ppv": ppv,
            "referrals_per_stroke_caught": np.where(tp > 0, ref / tp, np.nan),
            "net_benefit_per_1000": 1000 * (tp / n - fp / n * grid / (1 - grid)),
            f"expected_cost_per_1000_R{R:g}": 1000 * (fp + R * fn) / n,
        })
    return out


def operating_point(y, p, t: float, alpha: float = ALPHA) -> dict:
    """Physician-unit summary at one threshold, with Wilson CIs (sampling only)."""
    y = np.asarray(y, int)
    refer = np.asarray(p, float) >= t
    n = len(y)
    tp = int(np.sum(refer & (y == 1))); fp = int(np.sum(refer & (y == 0)))
    fn = int(np.sum(~refer & (y == 1))); tn = int(np.sum(~refer & (y == 0)))
    out = {"threshold": t, "n": n, "referred": tp + fp, "TP": tp, "FP": fp, "FN": fn, "TN": tn}
    for name, k, m, scale in (
        ("referrals_per_1000", tp + fp, n, 1000),
        ("strokes_caught_per_1000", tp, n, 1000),
        ("sensitivity", tp, tp + fn, 1),
        ("specificity", tn, tn + fp, 1),
        ("ppv", tp, tp + fp, 1),
    ):
        if m > 0:
            est, lo, hi = wilson_ci(k, m, alpha=alpha)
        else:
            est = lo = hi = np.nan
        out.update({name: scale * est, f"{name}_low": scale * lo, f"{name}_high": scale * hi})
    out["referrals_per_stroke_caught"] = (tp + fp) / tp if tp > 0 else np.nan
    return out


# ------------------------------------------------------ A3: decision curve

def decision_curve(y, preds: dict[str, np.ndarray], grid=THRESHOLD_GRID) -> pd.DataFrame:
    """Net benefit per 1,000 patients for each model plus refer-all and refer-none."""
    y = np.asarray(y, int)
    grid = np.asarray(grid, float)
    n = len(y)
    prev = y.mean()
    out = pd.DataFrame({"threshold": grid, "R": (1 - grid) / grid})
    for name, p in preds.items():
        c = counts_over_grid(y, p, grid)
        out[name] = 1000 * (c["TP"] / n - c["FP"] / n * grid / (1 - grid))
    out["Refer all"] = 1000 * (prev - (1 - prev) * grid / (1 - grid))
    out["Refer none"] = 0.0
    return out


def useful_range(dc: pd.DataFrame, model: str, competitors: list[str]) -> tuple[float, float] | None:
    """Widest contiguous threshold range where `model` beats every competitor."""
    better = (dc[model].to_numpy()[:, None] > dc[competitors].to_numpy()).all(axis=1)
    if not better.any():
        return None
    best, cur, start = (0, 0), 0, 0
    for i, b in enumerate(better):
        if b:
            if cur == 0:
                start = i
            cur += 1
            if cur > best[1] - best[0]:
                best = (start, i + 1)
        else:
            cur = 0
    t = dc["threshold"].to_numpy()
    return float(t[best[0]]), float(t[best[1] - 1])


# ----------------------------------------------- A4: threshold uncertainty

def strat_boot_index(y, rng: np.random.Generator) -> np.ndarray:
    """One stratified bootstrap resample: strokes and non-strokes resampled separately."""
    y = np.asarray(y, int)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    return np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])


def oof_mi_grouped(df: pd.DataFrame, groups, seed: int, m: int = N_IMPUTATIONS,
                   n_folds: int = N_FOLDS) -> np.ndarray:
    """Track 3's MI-inside-CV referral model, for one bootstrap resample.

    Same steps as `src.modeling.oof_predictions(..., models=("mi",))`:
    impute BMI on the training fold only (no outcome) m times, fit the
    logistic model on each, predict the test fold, average the m predictions.

    One change: folds are made with StratifiedGroupKFold on `groups` (the
    original patient id). A bootstrap resample repeats patients; without
    grouping, a copy of the same patient could sit in the training fold and
    the test fold, which makes the out-of-fold predictions look better than
    they are. Grouping keeps every copy of a patient in one fold.

    Random streams are seeded with (seed, fold, k) so no two resamples share
    an imputation stream.
    """
    X = design(df)
    y = df[TARGET].to_numpy(int)
    p = np.full(len(y), np.nan)
    sgk = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed % (2**32))
    for f, (tr, te) in enumerate(sgk.split(X, y, groups=groups)):
        Xtr, Xte, ytr = X.iloc[tr], X.iloc[te], y[tr]
        imp = BMIImputer(use_outcome=False).fit(Xtr)
        preds = []
        for k in range(m):
            rng = np.random.default_rng([seed, f, k])
            Xtr_k = imp.draw(Xtr, rng)
            Xte_k = imp.draw(Xte, rng)
            mdl = _fit_logit(Xtr_k[MODEL_COLS].to_numpy(), ytr)
            preds.append(_predict(mdl, Xte_k[MODEL_COLS].to_numpy()))
        p[te] = np.mean(preds, axis=0)
    return p


def pipeline_bootstrap(df: pd.DataFrame, R_values, B: int, seed: int = SEED,
                       m: int = N_IMPUTATIONS, grid=THRESHOLD_GRID, progress: bool = True):
    """Whole-pipeline stratified bootstrap of the cost-minimising threshold (A4).

    For b = 1..B: stratified resample of patients -> MI inside grouped CV ->
    out-of-fold predictions -> threshold that minimises expected cost, for
    every R in R_values.

    Returns (thresholds, costs):
      thresholds: DataFrame with one row per resample, columns b and t_star_R{R}
      costs: dict R -> array (B x len(grid)) of expected cost per 1,000
    """
    y = df[TARGET].to_numpy(int)
    rng = np.random.default_rng(seed)
    rows, costs = [], {R: np.empty((B, len(grid))) for R in R_values}
    for b in range(B):
        idx = strat_boot_index(y, rng)
        db = df.iloc[idx].reset_index(drop=True)
        p_b = oof_mi_grouped(db, groups=idx, seed=seed + 1 + b, m=m)
        y_b = db[TARGET].to_numpy(int)
        row = {"b": b}
        for R in R_values:
            c = expected_cost(y_b, p_b, R, grid)
            costs[R][b] = c
            row[f"t_star_R{R:g}"] = best_threshold(c, grid)
            row[f"min_cost_R{R:g}"] = float(c.min())
            row[f"cost_at_pstar_R{R:g}"] = float(c[np.argmin(np.abs(grid - p_star(R)))])
        rows.append(row)
        if progress and (b + 1) % 25 == 0:
            print(f"  resample {b + 1}/{B}", flush=True)
    return pd.DataFrame(rows), costs


def oof_only_bootstrap(y, p, R_values, B: int, seed: int = SEED, grid=THRESHOLD_GRID):
    """Cheaper bootstrap: resample patients with their OOF predictions held fixed.

    Ignores model-fitting and imputation variability, so its interval is too
    narrow (KB 06). Reported only for comparison with the whole-pipeline one.
    """
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    rng = np.random.default_rng(seed)
    rows = []
    for b in range(B):
        idx = strat_boot_index(y, rng)
        row = {"b": b}
        for R in R_values:
            row[f"t_star_R{R:g}"] = best_threshold(expected_cost(y[idx], p[idx], R, grid), grid)
        rows.append(row)
    return pd.DataFrame(rows)


def cross_fitted_selection(oof: pd.DataFrame, p_col: str, R: float, grid=THRESHOLD_GRID) -> pd.DataFrame:
    """Honest check of 'pick the threshold on the data' vs 'use p* = 1/(1+R)'.

    For each fold: choose the cost-minimising threshold on the other folds'
    OOF predictions, then apply it to this fold. Compare the total cost with
    applying the fixed rule p* to every fold. Avoids choosing and evaluating
    the threshold on the same patients (KB 02, common mistakes).
    """
    rows = []
    for f in sorted(oof["fold"].unique()):
        tr, te = oof[oof["fold"] != f], oof[oof["fold"] == f]
        t_f = best_threshold(expected_cost(tr[TARGET], tr[p_col], R, grid), grid)
        for rule, t in (("chosen on other folds", t_f), ("fixed p* = 1/(1+R)", p_star(R))):
            yy, pp = te[TARGET].to_numpy(int), te[p_col].to_numpy(float)
            fp = int(np.sum((pp >= t) & (yy == 0))); fn = int(np.sum((pp < t) & (yy == 1)))
            rows.append({"fold": f, "rule": rule, "threshold": t, "n": len(yy),
                         "FP": fp, "FN": fn, "cost": fp + R * fn})
    return pd.DataFrame(rows)
