"""Referral model: multiple imputation inside cross-validation (Track 3).

Used by notebooks/06_model.ipynb and, for the whole-pipeline bootstrap of the
threshold (A4), by notebooks/07_threshold_decision.ipynb.

Design decisions (see 06_model.ipynb for the reasons):

* Predictors are the proposal's modifiable + non-modifiable factors only:
  age, gender, heart disease (non-modifiable); hypertension, glucose, BMI,
  smoking status (modifiable). 9 parameters, about 28 events per parameter.
* ever_married, work_type and Residence_type are auxiliary variables: they
  help impute BMI but are not in the referral model.
* BMI is the only variable with missing values. It is imputed by Bayesian
  linear regression on log(BMI) with parameters drawn from their posterior
  (van Buuren 2018, Algorithm 3.1, "norm"), so each of the m datasets differs
  in both the regression parameters and the noise.
* Prediction set-up: the imputer is fitted on the training fold only and does
  NOT use the outcome, because a new patient's stroke status is unknown.
* Inference set-up (Rubin's rules ORs): the imputer uses the outcome
  (Moons et al., 2006), on the full data.
* m predicted probabilities per test patient are averaged (KB 03, option 1).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from src.config import ALPHA, N_FOLDS, N_IMPUTATIONS, SEED, TARGET

# Clinical units: one "unit" of each continuous predictor in the OR tables.
UNITS = {"age": 10.0, "avg_glucose_level": 50.0, "bmi": 5.0}

SMOKING_LEVELS = ["never smoked", "formerly smoked", "smokes", "Unknown"]
WORK_LEVELS = ["Private", "Self-employed", "Govt_job", "children_or_never"]

# Referral-model columns after `design()` (reference levels: female,
# never smoked). Continuous predictors are rescaled to clinical units.
MODEL_COLS = [
    "age", "male", "heart_disease", "hypertension", "avg_glucose_level", "bmi",
    "smoke_former", "smoke_current", "smoke_unknown",
]
AGE_ONLY_COLS = ["age"]
# Auxiliary variables for the BMI imputation model (in addition to the
# model predictors other than BMI).
AUX_COLS = ["ever_married", "self_employed", "govt_job", "children_or_never", "urban"]

LABELS = {
    "age": "Age (per 10 years)",
    "male": "Male (vs female)",
    "heart_disease": "Heart disease",
    "hypertension": "Hypertension",
    "avg_glucose_level": "Glucose (per 50 mg/dL)",
    "bmi": "BMI (per 5 kg/m²)",
    "smoke_former": "Formerly smoked (vs never)",
    "smoke_current": "Smokes (vs never)",
    "smoke_unknown": "Smoking unknown (vs never)",
    "bmi_missing": "BMI missing (indicator)",
}


# ------------------------------------------------------------------ data

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Analysis frame for modelling.

    Drops the single gender 'Other' record (gender is a predictor and one
    record cannot support a coefficient). Keeps the raw row number as
    `row_id` so predictions can be joined back to the raw CSV.
    """
    out = df.reset_index(names="row_id")
    out = out[out["gender"] != "Other"].reset_index(drop=True)
    return out


def design(df: pd.DataFrame) -> pd.DataFrame:
    """Numeric design matrix in clinical units. BMI stays NaN where missing."""
    X = pd.DataFrame(index=df.index)
    X["age"] = df["age"] / UNITS["age"]
    X["male"] = (df["gender"] == "Male").astype(float)
    X["heart_disease"] = df["heart_disease"].astype(float)
    X["hypertension"] = df["hypertension"].astype(float)
    X["avg_glucose_level"] = df["avg_glucose_level"] / UNITS["avg_glucose_level"]
    X["bmi"] = df["bmi"] / UNITS["bmi"]
    s = df["smoking_status"].astype(str)
    X["smoke_former"] = (s == "formerly smoked").astype(float)
    X["smoke_current"] = (s == "smokes").astype(float)
    X["smoke_unknown"] = (s == "Unknown").astype(float)
    # auxiliary
    X["ever_married"] = (df["ever_married"] == "Yes").astype(float)
    w = df["work_type"].astype(str)
    X["self_employed"] = (w == "Self-employed").astype(float)
    X["govt_job"] = (w == "Govt_job").astype(float)
    X["children_or_never"] = w.isin(["children", "Never_worked"]).astype(float)
    X["urban"] = (df["Residence_type"] == "Urban").astype(float)
    X["bmi_missing"] = df["bmi"].isna().astype(float)
    return X


# ------------------------------------------------------------ imputation

IMP_PREDICTORS = [c for c in MODEL_COLS if c != "bmi"] + AUX_COLS


class BMIImputer:
    """Bayesian normal linear regression imputation of log(BMI).

    fit() uses rows with observed BMI only. Each call to draw() samples
    (beta*, sigma*) from the posterior under a flat prior and returns
    imputed BMI (in model units, i.e. kg/m² / 5) for the rows asked for.
    """

    def __init__(self, use_outcome: bool = False):
        self.use_outcome = use_outcome

    def _Z(self, X: pd.DataFrame, y=None) -> np.ndarray:
        Z = X[IMP_PREDICTORS].to_numpy(float)
        if self.use_outcome:
            Z = np.column_stack([Z, np.asarray(y, float)])
        return np.column_stack([np.ones(len(Z)), Z])

    def fit(self, X: pd.DataFrame, y=None) -> "BMIImputer":
        obs = X["bmi"].notna().to_numpy()
        Z = self._Z(X, y)[obs]
        t = np.log(X["bmi"].to_numpy(float)[obs] * UNITS["bmi"])
        ZtZ = Z.T @ Z + 1e-6 * np.eye(Z.shape[1])  # tiny ridge for stability
        self.V_ = np.linalg.inv(ZtZ)
        self.beta_ = self.V_ @ Z.T @ t
        resid = t - Z @ self.beta_
        self.df_ = len(t) - Z.shape[1]
        self.rss_ = float(resid @ resid)
        self.chol_ = np.linalg.cholesky(self.V_)
        return self

    def draw(self, X: pd.DataFrame, rng: np.random.Generator, y=None) -> pd.DataFrame:
        """Return a copy of X with missing BMI filled by one posterior draw."""
        sigma2 = self.rss_ / rng.chisquare(self.df_)
        beta = self.beta_ + np.sqrt(sigma2) * self.chol_ @ rng.standard_normal(len(self.beta_))
        out = X.copy()
        miss = out["bmi"].isna().to_numpy()
        if miss.any():
            Z = self._Z(out, y)[miss]
            t = Z @ beta + np.sqrt(sigma2) * rng.standard_normal(miss.sum())
            out.loc[miss, "bmi"] = np.exp(t) / UNITS["bmi"]
        return out


# --------------------------------------------------------------- models

def _fit_logit(X: np.ndarray, y: np.ndarray) -> LogisticRegression:
    """Unpenalised maximum-likelihood logistic regression (same fit as statsmodels)."""
    model = LogisticRegression(C=np.inf, solver="lbfgs", max_iter=10_000, tol=1e-10)
    return model.fit(X, y)


def _predict(model: LogisticRegression, X: np.ndarray) -> np.ndarray:
    return model.predict_proba(X)[:, 1]


def oof_predictions(
    df: pd.DataFrame,
    seed: int = SEED,
    m: int = N_IMPUTATIONS,
    n_folds: int = N_FOLDS,
    models: tuple[str, ...] = ("intercept", "age_only", "complete_case", "mi", "mi_indicator"),
) -> pd.DataFrame:
    """Out-of-fold predicted stroke risk for each patient.

    df must come from `prepare()`. Returns one row per patient with columns
    row_id, fold, stroke and one column per model (prefixed `p_`).

    * intercept: training-fold stroke rate (everyone gets the same risk)
    * age_only: logistic regression on age
    * complete_case: full model fitted on training rows with BMI recorded;
      NaN for test patients with BMI missing (they can't be scored)
    * mi: full model, BMI imputed m times inside the fold, predictions averaged
    * mi_indicator: as mi, plus a BMI-missing indicator (action item D4)

    For imputation draw k in fold f the random stream is seeded with
    seed + k (config rule: imputation m uses SEED + m), offset by the fold.
    """
    X = design(df)
    y = df[TARGET].to_numpy(int)
    out = pd.DataFrame({"row_id": df["row_id"].to_numpy(), "fold": -1, TARGET: y})
    for name in models:
        out[f"p_{name}"] = np.nan

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    for f, (tr, te) in enumerate(skf.split(X, y)):
        out.loc[te, "fold"] = f
        Xtr, Xte, ytr = X.iloc[tr], X.iloc[te], y[tr]

        if "intercept" in models:
            out.loc[te, "p_intercept"] = ytr.mean()
        if "age_only" in models:
            mdl = _fit_logit(Xtr[AGE_ONLY_COLS].to_numpy(), ytr)
            out.loc[te, "p_age_only"] = _predict(mdl, Xte[AGE_ONLY_COLS].to_numpy())
        if "complete_case" in models:
            ok_tr = Xtr["bmi"].notna().to_numpy()
            ok_te = Xte["bmi"].notna().to_numpy()
            mdl = _fit_logit(Xtr.loc[ok_tr, MODEL_COLS].to_numpy(), ytr[ok_tr])
            out.loc[te[ok_te], "p_complete_case"] = _predict(mdl, Xte.loc[ok_te, MODEL_COLS].to_numpy())

        want_mi = [k for k in ("mi", "mi_indicator") if k in models]
        if want_mi:
            imp = BMIImputer(use_outcome=False).fit(Xtr)   # training fold only, no outcome
            preds = {k: [] for k in want_mi}
            for k in range(m):
                rng = np.random.default_rng([seed + k, f])
                Xtr_k = imp.draw(Xtr, rng)
                Xte_k = imp.draw(Xte, rng)
                for name in want_mi:
                    cols = MODEL_COLS + (["bmi_missing"] if name == "mi_indicator" else [])
                    mdl = _fit_logit(Xtr_k[cols].to_numpy(), ytr)
                    preds[name].append(_predict(mdl, Xte_k[cols].to_numpy()))
            for name in want_mi:
                out.loc[te, f"p_{name}"] = np.mean(preds[name], axis=0)
    return out


# ------------------------------------------------- inference (Rubin's rules)

def impute_full(df: pd.DataFrame, m: int = N_IMPUTATIONS, seed: int = SEED) -> list[pd.DataFrame]:
    """m completed design matrices for inference; the imputer uses the outcome."""
    X = design(df)
    y = df[TARGET].to_numpy(int)
    imp = BMIImputer(use_outcome=True).fit(X, y)
    return [imp.draw(X, np.random.default_rng(seed + k), y=y) for k in range(m)]


def fit_sm_logit(X: pd.DataFrame, y, cols=MODEL_COLS):
    """statsmodels Logit with intercept, for SEs and CIs."""
    return sm.Logit(np.asarray(y), sm.add_constant(X[cols], has_constant="add")).fit(disp=0)


def rubin_pool(estimates: np.ndarray, variances: np.ndarray, alpha: float = ALPHA) -> pd.DataFrame:
    """Rubin's rules for k parameters across m imputations.

    estimates, variances: arrays of shape (m, k). Returns pooled estimate,
    SE, Rubin degrees of freedom, CI, p-value, and the fraction of missing
    information (lambda = (1 + 1/m) B / T).
    """
    Q = np.asarray(estimates, float)
    U = np.asarray(variances, float)
    m = Q.shape[0]
    qbar = Q.mean(0)
    W = U.mean(0)
    B = Q.var(0, ddof=1)
    T = W + (1 + 1 / m) * B
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (1 + 1 / m) * B / W
        dof = np.where(B > 0, (m - 1) * (1 + 1 / r) ** 2, np.inf)
    se = np.sqrt(T)
    tcrit = stats.t.ppf(1 - alpha / 2, dof)
    p = 2 * stats.t.sf(np.abs(qbar / se), dof)
    return pd.DataFrame({
        "estimate": qbar, "se": se, "df": dof,
        "ci_low": qbar - tcrit * se, "ci_high": qbar + tcrit * se,
        "p_value": p, "fmi": (1 + 1 / m) * B / T,
    })


# ------------------------------------------------------------- metrics

def calibration_intercept_slope(y, p) -> tuple[float, float]:
    """Calibration-in-the-large (logit(y) ~ offset(logit p)) and slope (y ~ logit p)."""
    y = np.asarray(y, float)
    lp = np.log(p / (1 - p))
    slope = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit().params[1]
    citl = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial(), offset=lp).fit().params[0]
    return float(citl), float(slope)


def metrics(y, p) -> dict[str, float]:
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-12, 1 - 1e-12)
    brier = float(np.mean((p - y) ** 2))
    brier_ref = y.mean() * (1 - y.mean())
    constant = np.ptp(p) < 1e-3   # intercept-only: fold-to-fold noise only
    out = {
        "auc": 0.5 if constant else float(roc_auc_score(y, p)),
        "avg_precision": float(average_precision_score(y, p)),
        "brier": brier,
        "scaled_brier": 1 - brier / brier_ref,
        "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
    }
    if constant:
        out["cal_intercept"] = float(np.log(y.mean() / (1 - y.mean())) - np.log(p.mean() / (1 - p.mean())))
        out["cal_slope"] = np.nan
    else:
        out["cal_intercept"], out["cal_slope"] = calibration_intercept_slope(y, p)
    return out


def fast_auc(y: np.ndarray, p: np.ndarray) -> float:
    """AUC via the Mann-Whitney rank formula (handles ties)."""
    r = stats.rankdata(p)
    n1 = y.sum()
    n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def boot_metrics(y, preds: dict[str, np.ndarray], B: int = 2_000, seed: int = SEED) -> pd.DataFrame:
    """Stratified bootstrap of OOF metrics, same resamples for every model.

    Returns one row per resample with columns (model, metric) for
    metric in auc, brier, scaled_brier. Using the same resamples for every
    model gives paired CIs for differences between models.

    Resampling patients (keeping all 249 strokes' count per resample) captures
    the sampling variability of the evaluation set given the OOF
    predictions; it does not refit the models, so these CIs leave out
    model-fitting variability (see 06_model.ipynb, repeated-CV check).
    """
    y = np.asarray(y, int)
    rng = np.random.default_rng(seed)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    P = {k: np.asarray(v, float) for k, v in preds.items()}
    rows = []
    for _ in range(B):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        y_b = y[idx]
        ref = y_b.mean() * (1 - y_b.mean())
        row = {}
        for name, p in P.items():
            p_b = p[idx]
            row[(name, "auc")] = 0.5 if np.ptp(p_b) < 1e-3 else fast_auc(y_b, p_b)
            br = np.mean((p_b - y_b) ** 2)
            row[(name, "brier")] = br
            row[(name, "scaled_brier")] = 1 - br / ref
        rows.append(row)
    boots = pd.DataFrame(rows)
    boots.columns = pd.MultiIndex.from_tuples(boots.columns)
    return boots
