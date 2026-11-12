"""Track 4: decision-relevant hypothesis tests registered in docs/hypotheses.md.

Used by notebooks/05_hypothesis_tests.ipynb (H1, H5, G5 and the BMI sensitivity
analysis) and by notebooks/08_fairness.ipynb (H2, its G5 check, the error-rate
table and the Holm correction across H1 and H2), which reads Track 3's
out-of-fold predictions.

Everything here follows the registered entries (2026-11-11):

* Data: `prepare()` from src/modeling.py, i.e. the single gender "Other"
  record dropped (n = 5,109; 249 strokes), raw row number kept as `row_id`.
* Glucose in units of 50 mg/dL, BMI in units of 5 kg/m² (same units as
  Track 3's OR tables).
* Smoking "Unknown" is its own category; reference level "never smoked".
* Out-of-fold (OOF) predictions use the same stratified 5-fold split as
  Track 3 (StratifiedKFold, shuffle, random_state = SEED), so on the full
  data the folds are identical to Track 3's.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import optimize, stats
from sklearn.model_selection import StratifiedKFold

from src.config import ALPHA, N_BOOT, N_FOLDS, SEED, TARGET
from src.modeling import boot_metrics, fast_auc, prepare
from src.stats_utils import risk_difference, wilson_ci

GLU_UNIT = 50.0   # mg/dL
BMI_UNIT = 5.0    # kg/m²
SMOKE = "C(smoking_status, Treatment('never smoked'))"
H1_ADDED = f"hypertension + glu50 + {SMOKE}"   # the 5 parameters H1 tests


# ------------------------------------------------------------------ data

def h_frame(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Analysis frame for H1/H5: prepare() plus plain-string categoricals and unit-scaled columns.

    Gender and smoking are converted to plain strings so the unused "Other"
    gender level does not create an all-zero column in the design matrix.
    """
    d = prepare(df_raw)
    d["gender"] = d["gender"].astype(str)
    d["smoking_status"] = d["smoking_status"].astype(str)
    d["glu50"] = d["avg_glucose_level"] / GLU_UNIT
    d["bmi5"] = d["bmi"] / BMI_UNIT
    return d


# -------------------------------------------------------------- formulas

def h1_formulas(data: pd.DataFrame, with_bmi: bool = False) -> tuple[str, str]:
    """Registered H1 models: base = age spline + sex + heart disease; full = base + 5 modifiable terms.

    The B-spline boundaries are fixed at the min and max age of `data`. On the
    whole of `data` this is exactly patsy's default bs(age, df=4); fixing them
    only matters inside cross-validation, where a test fold can contain an age
    just outside the training fold's range.
    """
    lo, hi = float(data["age"].min()), float(data["age"].max())
    age = f"bs(age, df=4, lower_bound={lo!r}, upper_bound={hi!r})"
    base = f"{TARGET} ~ {age} + C(gender) + heart_disease"
    if with_bmi:
        base += " + bmi5"
    return base, f"{base} + {H1_ADDED}"


def h5_formulas() -> tuple[str, str]:
    """Registered H5 models (age ≥ 60): base = what the doctor knows without a lab test; full adds glucose."""
    base = f"{TARGET} ~ age + C(gender) + hypertension + heart_disease"
    return base, f"{base} + glu50"


# ------------------------------------------------------------- LR tests

def _logit(formula: str, data: pd.DataFrame):
    fit = smf.logit(formula, data).fit(disp=0, maxiter=200)
    if not fit.mle_retvals.get("converged", True):
        raise RuntimeError(f"Logistic regression did not converge: {formula}")
    return fit


def lr_test(data: pd.DataFrame, f_small: str, f_big: str) -> dict:
    """Likelihood-ratio test of nested logistic regressions fitted on the same rows."""
    m0, m1 = _logit(f_small, data), _logit(f_big, data)
    if int(m0.nobs) != int(m1.nobs):
        raise ValueError("Nested models were fitted on different rows")
    stat = 2 * (m1.llf - m0.llf)
    k = int(round(m1.df_model - m0.df_model))
    return {
        "n": int(m1.nobs),
        "events": int(data[TARGET].sum()),
        "params_big": int(round(m1.df_model)),             # excluding the intercept
        "events_per_param": data[TARGET].sum() / m1.df_model,
        "lr_stat": stat,
        "lr_df": k,
        "p_value": float(stats.chi2.sf(stat, k)),
        "_small": m0,
        "_big": m1,
    }


def spline_vs_linear(data: pd.DataFrame, formula: str, term: str, df_spline: int) -> dict:
    """Linearity check: replace the linear `term` in `formula` by bs(term, df_spline) and LR-test (df_spline − 1 df)."""
    if f" {term}" not in formula:
        raise ValueError(f"{term!r} not found in formula")
    spline = formula.replace(f" {term}", f" bs({term}, df={df_spline})", 1)
    out = lr_test(data, formula, spline)
    return {"term": term, "spline_df": df_spline, "lr_stat": out["lr_stat"],
            "lr_df": out["lr_df"], "p_value": out["p_value"]}


# --------------------------------------------------------- OOF and ΔAUC

def oof_two_models(data: pd.DataFrame, f_base: str, f_full: str,
                   seed: int = SEED, n_folds: int = N_FOLDS) -> pd.DataFrame:
    """OOF predicted risk from the base and full models, same folds for both.

    Spline knots are re-estimated in each training fold (patsy remembers them
    for the test fold), so no information from the test fold leaks in.
    """
    data = data.reset_index(drop=True)
    y = data[TARGET].to_numpy(int)
    out = pd.DataFrame({"row_id": data["row_id"].to_numpy(), "fold": -1, TARGET: y,
                        "p_base": np.nan, "p_full": np.nan})
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    for f, (tr, te) in enumerate(skf.split(np.zeros(len(y)), y)):
        out.loc[te, "fold"] = f
        for col, formula in (("p_base", f_base), ("p_full", f_full)):
            fit = _logit(formula, data.iloc[tr])
            out.loc[te, col] = fit.predict(data.iloc[te]).to_numpy()
    return out


def paired_delta_auc(oof: pd.DataFrame, B: int = N_BOOT, seed: int = SEED) -> dict:
    """AUC of each model and ΔAUC (full − base) with a paired stratified bootstrap CI.

    Same resampling scheme as Track 3 (boot_metrics): predictions held fixed,
    patients resampled within stroke / no-stroke so every resample keeps the
    observed number of strokes.
    """
    y = oof[TARGET].to_numpy(int)
    p0, p1 = oof["p_base"].to_numpy(float), oof["p_full"].to_numpy(float)
    boots = boot_metrics(y, {"base": p0, "full": p1}, B=B, seed=seed)
    d = boots[("full", "auc")] - boots[("base", "auc")]
    lo, hi = d.quantile([ALPHA / 2, 1 - ALPHA / 2]).to_numpy()
    a0, a1 = fast_auc(y, p0), fast_auc(y, p1)
    return {"auc_base": a0, "auc_full": a1, "delta_auc": a1 - a0,
            "delta_auc_low": float(lo), "delta_auc_high": float(hi)}


def h1_analysis(data: pd.DataFrame, label: str, with_bmi: bool = False,
                B: int = N_BOOT, seed: int = SEED) -> tuple[dict, pd.DataFrame]:
    """The R-free part of H1 on `data`: LR test (5 df) and ΔAUC. Returns (one result row, OOF predictions)."""
    f_base, f_full = h1_formulas(data, with_bmi=with_bmi)
    lr = lr_test(data, f_base, f_full)
    oof = oof_two_models(data, f_base, f_full, seed=seed)
    row = {"analysis": label, **{k: v for k, v in lr.items() if not k.startswith("_")},
           **paired_delta_auc(oof, B=B, seed=seed)}
    return row, oof


# ------------------------------------------------------------------- H5

def profile_ci(data: pd.DataFrame, f_base: str, term: str, alpha: float = ALPHA) -> tuple[float, float, float]:
    """Profile-likelihood CI for the coefficient of `term` added to f_base (logit scale).

    The coefficient is held fixed through an offset while the other
    coefficients are re-estimated; the CI is where the log-likelihood drops
    by chi2(1)_{1-alpha} / 2 from its maximum.
    """
    fam = sm.families.Binomial()
    full = smf.glm(f"{f_base} + {term}", data, family=fam).fit()
    b, se, llmax = full.params[term], full.bse[term], full.llf
    target = llmax - stats.chi2.ppf(1 - alpha, 1) / 2
    x = data[term].to_numpy(float)

    def gap(beta: float) -> float:
        return smf.glm(f_base, data, family=fam, offset=beta * x).fit().llf - target

    def root(direction: int) -> float:
        step = 2 * se
        while gap(b + direction * step) > 0:
            step *= 2
        return optimize.brentq(gap, b, b + direction * step, xtol=1e-10)

    return float(b), root(-1), root(+1)


def risk_at(fit, newdata: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    """Predicted risk with a Wald CI on the logit scale (GLM fit)."""
    sf = fit.get_prediction(newdata).summary_frame(alpha=alpha)
    return pd.DataFrame({"risk": sf["mean"].to_numpy(), "ci_low": sf["mean_ci_lower"].to_numpy(),
                         "ci_high": sf["mean_ci_upper"].to_numpy()}, index=newdata.index)


# ------------------------------------------------- net benefit (needs R)
#
# Net benefit at threshold p* (Vickers & Elkin 2006; KB 02):
#     NB = TP/n − FP/n · p*/(1 − p*),   refer when predicted risk ≥ p*.
# It is the share of patients who are true referrals, minus the false
# referrals weighted by how many of them one stroke is worth (1/R).
# NB × 1,000 = net strokes caught per 1,000 patients.
# Written as a mean of one number per patient, so a bootstrap resample's NB
# is just the mean over the resampled patients.

def p_star(R: float) -> float:
    """Referral threshold for cost ratio R = C_FN / C_FP."""
    return 1.0 / (1.0 + R)


def nb_contrib(y, p, pt: float) -> np.ndarray:
    """Each patient's contribution to net benefit at threshold pt (NB = the mean of these)."""
    y = np.asarray(y, int)
    refer = np.asarray(p, float) >= pt
    return np.where(refer, np.where(y == 1, 1.0, -pt / (1 - pt)), 0.0)


def net_benefit(y, p, pt: float) -> float:
    return float(nb_contrib(y, p, pt).mean())


def strat_boot_means(y, C: np.ndarray, B: int = N_BOOT, seed: int = SEED) -> np.ndarray:
    """Column means of C over B stratified bootstrap resamples of patients (B × k).

    Same scheme as Track 3's boot_metrics: patients resampled within
    stroke / no-stroke, so each resample keeps the observed number of strokes;
    predictions held fixed. Every column uses the same resamples (paired).
    """
    y = np.asarray(y, int)
    C = np.asarray(C, float).reshape(len(y), -1)
    rng = np.random.default_rng(seed)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    out = np.empty((B, C.shape[1]))
    for b in range(B):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        out[b] = C[idx].mean(axis=0)
    return out


def _ci(x: np.ndarray, alpha: float = ALPHA) -> tuple[float, float]:
    lo, hi = np.quantile(x, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def delta_nb(oof: pd.DataFrame, R_values, B: int = N_BOOT, seed: int = SEED) -> pd.DataFrame:
    """H1 effect size: ΔNB = NB(full) − NB(base) at p* = 1/(1+R), paired stratified bootstrap CI.

    One row per R. NB values are also given per 1,000 patients. `share_le_0`
    is the share of resamples with ΔNB ≤ 0 (descriptive; H1's test is the LR test).
    """
    y = oof[TARGET].to_numpy(int)
    p0, p1 = oof["p_base"].to_numpy(float), oof["p_full"].to_numpy(float)
    D = np.column_stack([nb_contrib(y, p1, p_star(R)) - nb_contrib(y, p0, p_star(R)) for R in R_values])
    boots = strat_boot_means(y, D, B=B, seed=seed)
    rows = []
    for j, R in enumerate(R_values):
        pt = p_star(R)
        nb0, nb1 = net_benefit(y, p0, pt), net_benefit(y, p1, pt)
        lo, hi = _ci(boots[:, j])
        rows.append({"R": R, "p_star": pt, "nb_base": nb0, "nb_full": nb1,
                     "delta_nb": nb1 - nb0, "delta_nb_low": lo, "delta_nb_high": hi,
                     "delta_per_1000": 1000 * (nb1 - nb0), "per_1000_low": 1000 * lo,
                     "per_1000_high": 1000 * hi, "share_le_0": float(np.mean(boots[:, j] <= 0)),
                     "ci_above_0": lo > 0})
    return pd.DataFrame(rows)


def h2_test(y, p, R_values, B: int = N_BOOT, seed: int = SEED) -> pd.DataFrame:
    """H2: NB(model) − NB(best default) at p* = 1/(1+R), one-sided paired bootstrap.

    Best default = the larger of refer-all and refer-none (NB = 0), chosen
    again inside every resample. With stratified resampling the stroke rate is
    the same in every resample, so the choice never changes within one R.
    p_one_sided = share of resamples with difference ≤ 0 (as registered).
    """
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    cols = []
    for R in R_values:
        pt = p_star(R)
        cols += [nb_contrib(y, p, pt), nb_contrib(y, np.ones_like(p), pt)]
    boots = strat_boot_means(y, np.column_stack(cols), B=B, seed=seed)
    rows = []
    for j, R in enumerate(R_values):
        pt = p_star(R)
        nb_m, nb_all = net_benefit(y, p, pt), net_benefit(y, np.ones_like(p), pt)
        best = max(nb_all, 0.0)
        diff_b = boots[:, 2 * j] - np.maximum(boots[:, 2 * j + 1], 0.0)
        lo, hi = _ci(diff_b)
        k = int(np.sum(diff_b <= 0))
        rows.append({"R": R, "p_star": pt, "n": len(y), "events": int(y.sum()),
                     "nb_model": nb_m, "nb_refer_all": nb_all, "nb_refer_none": 0.0,
                     "best_default": "refer all" if nb_all > 0 else "refer none",
                     "diff": nb_m - best, "diff_low": lo, "diff_high": hi,
                     "diff_per_1000": 1000 * (nb_m - best), "per_1000_low": 1000 * lo,
                     "per_1000_high": 1000 * hi, "n_boot_le_0": k, "B": B,
                     "p_one_sided": k / B})
    return pd.DataFrame(rows)


# ---------------------------------------------------- error-rate table

def error_rates(y, p, pt: float) -> dict:
    """Counts at threshold pt plus FN rate, FP rate and PPV with Wilson 95% CIs."""
    y = np.asarray(y, int)
    refer = np.asarray(p, float) >= pt
    tp = int(np.sum(refer & (y == 1))); fn = int(np.sum(~refer & (y == 1)))
    fp = int(np.sum(refer & (y == 0))); tn = int(np.sum(~refer & (y == 0)))
    out = {"n": len(y), "strokes": tp + fn, "referred": tp + fp, "TP": tp, "FN": fn, "FP": fp, "TN": tn}
    for name, k, m in (("fn_rate", fn, tp + fn), ("fp_rate", fp, fp + tn), ("ppv", tp, tp + fp)):
        est, lo, hi = wilson_ci(k, m) if m > 0 else (np.nan, np.nan, np.nan)
        out.update({name: est, f"{name}_low": lo, f"{name}_high": hi, f"{name}_k": k, f"{name}_m": m})
    return out


def error_rate_table(df: pd.DataFrame, p_col: str, pt: float, groups: dict[str, pd.Series]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Error rates overall and per group, plus the between-group differences (Newcombe 95% CIs).

    `groups` maps a grouping name to a Series of group labels (2 levels each).
    Returns (rates, differences); differences are level 2 − level 1 in the
    order the levels appear in sorted order.
    """
    y, p = df[TARGET].to_numpy(int), df[p_col].to_numpy(float)
    rates = [{"grouping": "all", "group": "all", **error_rates(y, p, pt)}]
    diffs = []
    for gname, g in groups.items():
        levels = sorted(pd.unique(g))
        per = {}
        for lev in levels:
            m = (g == lev).to_numpy()
            per[lev] = error_rates(y[m], p[m], pt)
            rates.append({"grouping": gname, "group": lev, **per[lev]})
        a, b = per[levels[0]], per[levels[1]]
        for name in ("fn_rate", "fp_rate", "ppv"):
            d, lo, hi = risk_difference(b[f"{name}_k"], b[f"{name}_m"], a[f"{name}_k"], a[f"{name}_m"])
            diffs.append({"grouping": gname, "metric": name,
                          "comparison": f"{levels[1]} − {levels[0]}",
                          "diff": d, "diff_low": lo, "diff_high": hi})
    return pd.DataFrame(rates), pd.DataFrame(diffs)
