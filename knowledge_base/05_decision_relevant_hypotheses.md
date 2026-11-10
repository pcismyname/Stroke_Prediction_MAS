# Hypotheses that bear on the referral decision

**Related criterion:** 5 · **Answers professor point F3**

> "Your three hypotheses are things any clinician already knows. Nobody will be surprised that age raises stroke risk. Is there a hypothesis that actually bears on the referral decision?"

## What makes a hypothesis decision-relevant?

Its answer changes what the physician does. "Age raises risk" doesn't, because every clinician already refers older patients. These questions would change the decision:

- Is a model better than the simple rules a doctor already uses?
- Do the *modifiable* factors add anything once we know age?
- Is the model trustworthy enough (calibrated) to apply the cost threshold?

## Candidate hypotheses (the team should pick 2–3 and pre-register them)

| ID | H₀ | H₁ | Test | Why it matters to the physician |
|----|----|----|------|--------------------------------|
| **H1** | Adding modifiable factors (hypertension, glucose, BMI, smoking) to an age + sex + heart-disease model does not improve net benefit at the chosen threshold: ΔNB = 0 | ΔNB > 0 | Paired bootstrap of ΔNB on out-of-fold predictions; also a likelihood-ratio test for the nested models | If H₀ holds, the doctor can refer on age alone and needs no lab values |
| **H2** | The model's net benefit at p\* is no better than the best default strategy, max(refer-all, refer-none) | Model NB > best default | Bootstrap CI for NB_model − NB_default | If H₀ holds, the model shouldn't be used at all |
| **H3** | The model is calibrated: calibration intercept = 0 and slope = 1 | Miscalibrated | Logistic recalibration of y on logit(p̂) out of fold; Wald tests | The threshold rule p\* = 1/(1+R) only works if probabilities are calibrated |
| **H4** | After adjusting for observed covariates, BMI missingness is not associated with stroke (OR = 1) | OR ≠ 1 | Logistic regression Wald / LR test | Decides whether MI under MAR is defensible ([note 04](04_missing_data_mechanisms.md)) |
| **H5** | Among patients aged ≥ 60, glucose adds no information beyond hypertension (OR_glucose = 1) | OR ≠ 1 | Logistic regression in the subgroup | Tells the doctor whether ordering a glucose test changes the referral for older patients |

## Keep the original three?

Yes, but move them to an appendix as **descriptive checks**, so we still report every test we ran (criterion 5 transparency). The main text should lead with the decision-relevant ones.

## Pre-registration (important for marks)

The guidelines say hypotheses must be "stated before you look at the results". Do it like this:

1. Write the final hypothesis list in [docs/hypotheses.md](../docs/hypotheses.md).
2. Commit it **before** running the tests. The git timestamp is the evidence.
3. If a hypothesis changes later, add a new dated entry. Never edit the old one.

## Multiple testing

With 5+ hypotheses, report both raw and Holm-adjusted p-values (`statsmodels.stats.multitest.multipletests(p, method="holm")`).
