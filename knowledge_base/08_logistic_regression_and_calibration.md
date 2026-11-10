# Logistic regression and calibration

**Related criterion:** 6

## Interpreting coefficients for a physician

- exp(β) is an **odds ratio** per one-unit increase. Choose units a doctor understands: **per 10 years** of age, **per 50 mg/dL** of glucose, **per 5 kg/m²** of BMI.
- With a 5% base rate, odds ≈ risk, so the OR is roughly a risk ratio. Even so, also report **absolute risk** for typical patients, e.g. "a 70-year-old with hypertension: predicted risk 12% (95% CI …)".
- Use `statsmodels.api.Logit` / `smf.logit` for inference (SEs, CIs). scikit-learn gives no standard errors.

## Is the model big enough? Events per variable

249 events. Rule of thumb: ≥ 10–20 events per parameter, so at most about 12–24 parameters. Dummy variables count separately (work_type has 5 levels = 4 parameters). Keep the model lean.

## Diagnostics the model type demands

| Check | How |
|-------|-----|
| Linearity of the logit for continuous predictors | Fit restricted cubic splines (`patsy` `cr(age, df=4)`) and compare with the linear term by an LR test; plot the partial effect |
| Influential points | Cook's distance / dfbetas from `GLM(...).get_influence()` |
| Separation / sparse cells | Look for huge SEs. Only 2 strokes in under-18s and 1 "Other" gender record are risky. |
| Multicollinearity | VIF (age vs ever_married vs work_type are correlated) |

## Calibration (needed before applying the threshold)

On **out-of-fold** predictions:
1. **Reliability diagram:** bin predictions (deciles, or quantiles given the rarity) and plot observed rate against mean predicted rate, with CIs per bin. Or use a LOESS smooth.
2. **Calibration intercept and slope:** fit `y ~ logit(p_hat)`. Ideal: intercept 0, slope 1. A slope < 1 means overfitting (predictions too extreme).
3. **Brier score** with a bootstrap CI.
4. Hosmer–Lemeshow: report it if required, but note that it depends on the binning and has low power. Don't rely on it alone.

## Baselines to beat
- Intercept-only (everyone gets 4.87%), which is equivalent to "refer all" or "refer none"
- Age-only logistic regression

## Discrimination (reported "for completeness only", per the proposal)
AUC with a bootstrap CI, plus a precision–recall curve (more informative at 5% prevalence than ROC).

## Sources
- Hosmer, Lemeshow & Sturdivant (2013), *Applied Logistic Regression*, 3rd ed.
- Steyerberg, E. W. (2019). *Clinical Prediction Models*, 2nd ed.
- Van Calster, B., et al. (2019). Calibration: the Achilles heel of predictive analytics. *BMC Medicine*, 17, 230.
