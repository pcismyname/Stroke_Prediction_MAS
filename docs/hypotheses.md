# Pre-registered hypotheses

The grading criteria require hypotheses to be **stated before looking at results**. This file is our evidence: the git commit timestamp of each entry shows when it was written.

**Rules**
- Add entries; never edit or delete an old one. To change a hypothesis, add a new dated entry that says what changed and why.
- Commit this file **before** running the test.
- Every hypothesis here must appear in the report (or appendix), whatever the result.

Candidates and reasoning: [knowledge_base/05_decision_relevant_hypotheses.md](../knowledge_base/05_decision_relevant_hypotheses.md)

---

## Entry template

```
### H? — short name
- Date registered: YYYY-MM-DD   · Registered by:
- H₀:
- H₁:
- Test (and fallback if assumptions fail):
- Effect size reported:
- Significance level / multiplicity correction:
- Why it matters for the referral decision:
```

---

## Proposal hypotheses (from the submitted proposal; kept as descriptive checks)

### P1: Glucose differs between stroke and non-stroke patients
- H₀: mean glucose is equal; H₁: it differs
- Test: Welch's t-test; Mann–Whitney U if normality fails

### P2: Hypertension and stroke are associated
- H₀: independent; H₁: associated
- Test: two-proportion z-test or χ² test

### P3: Age increases stroke risk
- H₀: β_age = 0; H₁: β_age > 0
- Test: sign and size of the age coefficient, plus a trend test

---

## Decision-relevant hypotheses (to be registered: see action item C1)

Main family for the report: **H1 and H2**, Holm-corrected together (α = 0.05). Appendix: **H5** (secondary) and the sensitivity analyses below. P1–P3 stay a separate Holm family (C3).

**Threshold used throughout:** p\* = 1 / (1 + R), with R = `COST_RATIO` in `src/config.py` (action item A1; set to R = 20, p\* = 4.8%, on 2026-11-12, see [cost_ratio.md](cost_ratio.md)). R is chosen from the cost reasoning in KB 02, not from these results. Every analysis is repeated over `COST_RATIO_GRID` (5, 10, 20, 50, 100) so the conclusion can be checked at other values of R.

**Common settings:** `SEED` from `src/config.py`; bootstrap B = 10,000, stratified by stroke; out-of-fold (OOF) predictions from stratified 5-fold CV; the one "Other" gender record excluded (n = 5,109; 249 strokes).

### H1: Do modifiable risk factors improve the referral decision beyond age?
- Date registered: 2026-11-11   · Registered by: James
- Data: full data (n = 5,109; 249 strokes)
- Models (logistic regression):
    base = stroke ~ bs(age, df=4) + gender + heart_disease
    full = base + hypertension + avg_glucose_level + smoking_status
  Age as a 4-df B-spline because the P3 linearity check rejected a linear age term (p = 0.039).
  Smoking "Unknown" kept as its own category. Glucose per 50 mg/dL.
  BMI not included: it is the only variable with missing values and its missingness is informative
  (Track 1, D2), so leaving it out keeps this test free of imputation assumptions. A BMI version is
  run as a sensitivity analysis (below).
- H₀: the added factors carry no information (all 5 added coefficients = 0)
- H₁: at least one is non-zero
- Test: likelihood-ratio test, full vs base (χ², 5 df)
- Effect size: ΔNB = NB(full) − NB(base) at p\*, on OOF predictions of both models (same folds),
  reported as net extra strokes caught per 1,000 patients with a paired bootstrap 95% CI;
  also ΔAUC with paired bootstrap CI
- Assumption checks: linearity of glucose (3-df spline vs linear, LR test); events per parameter
  (249 / 11 ≈ 23)
- Decision rule (stated in advance): recommend measuring these factors only if H₀ is rejected
  (after Holm) AND the ΔNB 95% CI lies above 0
- Known before registering: Track 3 (G2, test log 2026-11-11) compared its full MI model (with BMI)
  against age only: ΔAUC +0.006 (−0.001 to 0.013). H1 uses a different base model (age spline +
  sex + heart disease), excludes BMI, and its primary effect size is ΔNB at p\*, which nobody has computed.
- Why it matters: if H₀ holds, the doctor can refer on age, sex and heart disease alone, with no lab values

### H2: Does the referral model beat the best default strategy?
- Date registered: 2026-11-11   · Registered by: James
- Data: the team's referral model (Track 3: MI inside CV, no BMI-missing indicator), OOF predictions
  `p_mi` in `data/interim/oof_final.csv` (n = 5,109)
- Defaults: refer everyone, NB = π − (1 − π)·p\*/(1 − p\*); refer no one, NB = 0.
  "Best default" = the larger of the two at p\*
- H₀: NB(model) − NB(best default) ≤ 0
- H₁: NB(model) − NB(best default) > 0
- Test: paired bootstrap, 10,000 resamples of patients with predictions held fixed;
  one-sided p = share of resamples with difference ≤ 0
- Effect size: the difference as net strokes caught per 1,000 patients, with 95% bootstrap CI
- Stated limitation: holding predictions fixed ignores model-fitting variability, so the CI is somewhat
  narrow (the whole-pipeline bootstrap is Track 5's A4)
- Known before registering: Track 3's AUC and calibration results (G2, G4). No net benefit for any
  strategy has been computed.
- Why it matters: if H₀ holds, the model should not be used for referral at all

### H5 (appendix, secondary): In patients aged 60+, does glucose add information beyond what the doctor already knows?
- Date registered: 2026-11-11   · Registered by: James
- Data: age ≥ 60 (n = 1,376; 181 strokes)
- Models (logistic regression):
    base = stroke ~ age + gender + hypertension + heart_disease
    full = base + avg_glucose_level (per 50 mg/dL)
  BMI not included, for the same reason as H1.
- H₀: OR_glucose = 1
- H₁: OR_glucose ≠ 1
- Test: likelihood-ratio test, full vs base (χ², 1 df)
- Effect size: OR per 50 mg/dL with profile-likelihood 95% CI; absolute stroke risk at glucose 90 vs
  200 mg/dL for a typical patient in the subgroup
- Assumption checks: linearity of glucose and of age (3-df spline vs linear, LR tests)
- α = 0.05, reported with its raw p-value; not in the H1/H2 Holm family
- Known before registering: the full-sample adjusted glucose OR from Track 3 (1.23 per 50 mg/dL, all
  ages, model_or_mi.csv) and Track 2's glucose component stroke rates (all ages). Neither looked at
  the 60+ subgroup alone.
- Why it matters: tells the doctor whether ordering a glucose test changes the referral for older patients

### Sensitivity analyses (registered now; not in any Holm family; all reported in the appendix)
- G5 adults only (age ≥ 18; n = 4,253; 247 strokes): H1 refitted; H2 on the adult rows of the same predictions
- H1 and H2 at every R in `COST_RATIO_GRID` (5, 10, 20, 50, 100)
- H1 with BMI added to both models, complete cases only (n = 4,908)
- Error-rate table (action item H2): FN rate, FP rate and PPV of the referral model at p\*, by age band
  (< 60, ≥ 60) and gender, with Wilson 95% CIs and the difference between groups. Descriptive, no tests.

### Considered but not registered
- KB 05 H3 (calibration) and H4 (BMI missingness and stroke) were already run before this entry
  (Track 3 G4; Track 1 D2), so they cannot be pre-registered. They are reported as exploratory
  results by those tracks.
