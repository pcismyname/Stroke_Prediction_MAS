# Multiple imputation inside cross-validation

**Related criteria:** 6, 7 · **Answers professor point F2**

> "Think carefully about the order those happen in and what each fold is allowed to see. Also, imputation gives you more than one dataset. Decide now what you'll do with that."

## The rule

**Split first, impute second.** The imputation model is part of the model. It must be fitted on the training fold only, then applied to the test fold. Imputing the whole dataset before splitting lets test rows influence the imputed training values. That is leakage, and it makes CV scores optimistic.

```
WRONG:  impute(all data) → split into folds → fit/evaluate
RIGHT:  split into folds → for each fold: fit imputer on train → impute train & test → fit model on train → predict test
```

## The outcome in the imputation model (subtle)

- **For inference** (odds ratios, Rubin's rules): include `stroke` in the imputation model. Leaving it out biases the BMI–stroke association toward zero (Moons et al., 2006).
- **For prediction on a test fold:** the outcome of test patients is unknown in real use, so the imputer applied to test rows must not use the test `stroke` values. Fit the imputer on training rows, *without* the outcome as an input when it will be applied to test rows.

So we may need two imputation set-ups: one for inference on the full data, and one inside CV for prediction. Write down which is which.

## What to do with m imputed datasets (decide now)

How many: a common rule is m ≥ the percentage of incomplete cases (≈ 4% here), so m = 5 is a floor. We use `N_IMPUTATIONS = 5` in [src/config.py](../src/config.py) because of the 2-day timeline; 20 gives more stable pooled SEs if time allows.

**A. Coefficients / odds ratios → Rubin's rules**

For each of m datasets, fit the model and get estimate Q_i and variance U_i.

- Pooled estimate: Q̄ = mean(Q_i)
- Within-imputation variance: W = mean(U_i)
- Between-imputation variance: B = var(Q_i) (with m − 1 denominator)
- Total variance: **T = W + (1 + 1/m) · B**

Pool on the log-odds scale, then exponentiate to get the OR and its CI. `statsmodels.imputation.mice.MICE` does this automatically.

**B. Predictive performance (AUC, Brier, net benefit, threshold)**

Pre-register one of these options:

1. **Average predictions:** inside each fold, impute m times, fit m models, and average the m predicted probabilities for each test patient. Evaluate once. This mirrors how the model would be used.
2. **Average metrics:** compute the metric on each of the m datasets and average. Simpler, but it doesn't give a single deployable model.

Our recommendation is option 1 for the threshold and net benefit analysis.

## Code sketch (scikit-learn)

```python
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from src.config import SEED, N_IMPUTATIONS, N_FOLDS

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof = np.zeros(len(y))
for train, test in skf.split(X, y):
    probs = []
    for m in range(N_IMPUTATIONS):
        pipe = Pipeline([
            ("impute", IterativeImputer(sample_posterior=True, random_state=SEED + m)),
            ("model", LogisticRegression(penalty=None, max_iter=1000)),
        ])
        pipe.fit(X.iloc[train], y.iloc[train])        # imputer sees only training rows
        probs.append(pipe.predict_proba(X.iloc[test])[:, 1])
    oof[test] = np.mean(probs, axis=0)                 # average over imputations
```

`sample_posterior=True` is required. Without it every imputation is identical and it isn't *multiple* imputation.

## Also report
- A complete-case analysis next to the MI analysis (the proposal promises both).
- A note that MI assumes MAR. See [note 04](04_missing_data_mechanisms.md) for why that may not hold for BMI.

## Sources
- Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys.*
- van Buuren, S. (2018). *Flexible Imputation of Missing Data*, 2nd ed. (free online: stefvanbuuren.name/fimd)
- Moons, K. G. M., et al. (2006). Using the outcome for imputation of missing predictor values was preferred. *J Clin Epidemiol*, 59, 1092–1101.
