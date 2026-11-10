# Missing-data mechanisms: why does missing BMI have 4× the stroke rate?

**Related criteria:** 2, 7 · **Answers professor point F4**

> "Patients with missing BMI have four times the stroke rate of everyone else. Please identify why that could be, and whether filling in the missing values can recover whatever is going on there."

## The facts (from the proposal EDA)

| Group | n | Strokes | Stroke rate |
|-------|---|---------|-------------|
| BMI recorded | 4,909 | 209 | 4.3% |
| BMI missing | 201 | 40 | 19.9% |

## The three mechanisms

| Mechanism | Meaning | Can MI fix it? |
|-----------|---------|----------------|
| **MCAR** (completely at random) | Missingness unrelated to anything | Yes, though even complete-case is unbiased. **Already ruled out**: the stroke rates differ. |
| **MAR** (at random, given observed data) | Missingness explained by observed variables (age, glucose, work type …) | Yes. MI conditioned on those variables gives valid inference. |
| **MNAR** (not at random) | Missingness depends on the missing value itself or on unobserved factors | **No.** MI under MAR is biased; only sensitivity analysis helps. |

## Possible explanations to investigate

1. **Older, sicker patients (MAR).** If the missing-BMI patients are older or have more hypertension or diabetes, the high stroke rate may simply follow from age and glucose. *Test:* compare covariate distributions between missing and recorded groups.
2. **Recorded after the stroke (reverse causation).** BMI may be missing *because* of the stroke: a patient admitted with an acute stroke can't stand on a scale, or the record came from a different clinical pathway. Then missingness is a consequence of the outcome, not a risk factor.
3. **A different data source.** Records missing BMI may come from a different hospital or form with a different stroke prevalence. The dataset's origin is undisclosed (see the data card), so we can't check this directly. State it as a limitation.

## Analyses to run

1. **What predicts missingness?** Logistic regression `bmi_missing ~ age + hypertension + heart_disease + glucose + work_type + ...`. Large, significant predictors make MAR more plausible.
2. **Does the excess risk survive adjustment?** Logistic regression `stroke ~ bmi_missing + age + hypertension + heart_disease + glucose + ...`.
   - If the adjusted OR for `bmi_missing` ≈ 1, observed covariates explain the gap. MAR is plausible and MI is fine.
   - If the adjusted OR stays well above 1, the missingness carries information that no observed variable explains. That points to MNAR or a data-collection artefact.
3. **Does imputation recover it?** Impute BMI (MI), then check whether the *imputed* BMI values for these 201 patients predict their stroke rate. Imputed values are drawn from the observed BMI distribution given covariates, so they are typically ordinary BMIs. **MI cannot recreate information that lives in the fact of missingness itself.**
4. **Sensitivity analysis (delta adjustment).** Shift the imputed BMI for missing patients by δ (e.g. −5, −2, 0, +2, +5) and show how the BMI odds ratio and the recommended threshold change. If conclusions don't move, MNAR doesn't matter much for our decision.

## What this means for the referral model

**Do not put a "BMI missing" indicator in the referral model**, even though it would raise the AUC. If BMI is missing because the stroke already happened, the model learns a data-collection artefact that won't exist in a primary-care clinic, where BMI is measured before any stroke. Report this choice and what the AUC would have been with the indicator (analytical honesty, criterion 7).

## Sources
- Little, R. J. A., & Rubin, D. B. (2019). *Statistical Analysis with Missing Data*, 3rd ed.
- van Buuren (2018), *Flexible Imputation of Missing Data*, ch. 1–3 and 9.2 (sensitivity analysis)
- Sperrin, M., et al. (2020). Missing data should be handled differently for prediction than for description or causal explanation. *J Clin Epidemiol*, 125, 183–187.
