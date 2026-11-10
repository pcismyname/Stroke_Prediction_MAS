# Action items

Pick a task: put your name in **Owner**, set **Status** to 🟡 In progress, and push. When done, set ✅ and link your notebook or file in **Output**.

**Status:** ⬜ To do · 🟡 In progress · ✅ Done · ⛔ Blocked

**Team:** Pichayut · Nyi Htut · Takdanai · Aphisit · Chidsanuphong · Nawee

Background reading for each group is in [knowledge_base/](knowledge_base/README.md). The professor's comments are in [docs/professor_feedback.md](docs/professor_feedback.md) (F1–F5). The grading checklist is in [docs/grading_checklist.md](docs/grading_checklist.md).

---

## S. Setup (do first)

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| S1 | Everyone: clone the repo, create the venv, install `requirements.txt`, download the data (see [README](README.md#getting-started)) | all | ⬜ | |
| S2 | Reproduce the proposal's EDA numbers in `notebooks/01_eda.ipynb` (5,110 rows, 249 strokes, 201 missing BMI, 19.9% vs 4.3%, glucose histogram) | | ⬜ | |
| S3 | Decide the meeting rhythm and who reviews whose notebooks | | ⬜ | |

## A. Cost ratio and referral threshold (Professor F1, F5) · Criteria 1, 4, 6

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| A1 | Choose the cost ratio R = C_FN / C_FP **and its source** (literature cost of stroke × counselling effectiveness vs cost of a session, or a capacity constraint, or elicitation). Write 1 paragraph with citations. Set `COST_RATIO` in [src/config.py](src/config.py). See [KB 02](knowledge_base/02_cost_ratio_and_threshold.md). | | ⬜ | |
| A2 | Threshold sweep table and plot: PPV, sensitivity, referrals / 1,000, strokes caught / 1,000, expected cost, all on out-of-fold predictions | | ⬜ | |
| A3 | Decision curve: net benefit vs threshold for model, age-only model, refer-all, refer-none. Shows "what happens when the ratio moves". | | ⬜ | |
| A4 | Bootstrap CI for the recommended threshold (whole pipeline) and the cost-curve flatness band. See [KB 06](knowledge_base/06_threshold_uncertainty.md). | | ⬜ | |

## B. Multiple imputation × cross-validation (Professor F2) · Criteria 6, 7

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| B1 | Write the pipeline: split → impute on the training fold → fit → predict test fold; m = 20 imputations; average predictions across imputations. See [KB 03](knowledge_base/03_multiple_imputation_and_cv.md). | | ⬜ | |
| B2 | Write down (in the report methods) the pooling decision: Rubin's rules for ORs, averaged predictions for performance | | ⬜ | |
| B3 | Complete-case vs MI results side by side (ORs and threshold) | | ⬜ | |

## C. Hypotheses (Professor F3) · Criterion 5

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| C1 | Team picks 2–3 decision-relevant hypotheses from [KB 05](knowledge_base/05_decision_relevant_hypotheses.md); register them in [docs/hypotheses.md](docs/hypotheses.md) and **commit before testing** | all | ⬜ | |
| C2 | Run the decision-relevant tests with assumption checks, effect sizes and CIs | | ⬜ | |
| C3 | Run the original proposal hypotheses P1–P3 as descriptive checks (appendix) with assumption checks and fallbacks | | ⬜ | |
| C4 | Keep [results/test_log.md](results/test_log.md) complete; apply Holm correction across the family | | ⬜ | |

## D. Missing BMI (Professor F4) · Criteria 2, 7

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| D1 | Compare missing vs recorded BMI groups on age, glucose, hypertension, heart disease, work type (table with CIs). Model `bmi_missing ~ covariates`. | | ⬜ | |
| D2 | Model `stroke ~ bmi_missing + covariates`: does the 4× excess survive adjustment? Interpret as MAR vs MNAR / reverse causation. See [KB 04](knowledge_base/04_missing_data_mechanisms.md). | | ⬜ | |
| D3 | Show whether MI recovers the signal; delta-adjustment sensitivity analysis (δ = −5…+5) on the BMI OR and the threshold | | ⬜ | |
| D4 | Write the paragraph explaining why we do **not** use a missing indicator in the referral model (report the AUC with and without it) | | ⬜ | |

## E. Distributional modeling · Criterion 3 (15 marks)

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| E1 | Data-generating justification for glucose (log-normal / Gamma / two-population mixture). See [KB 07](knowledge_base/07_distribution_fitting.md). | | ⬜ | |
| E2 | Fit the 3 candidates; Q–Q plots; parametric-bootstrap Anderson–Darling / KS; AIC/BIC table | | ⬜ | |
| E3 | Write "where the fit breaks and what it means" for the downstream tests | | ⬜ | |
| E4 | (Optional) Second variable: BMI, with and without values > 60 | | ⬜ | |

## F. Estimation and uncertainty · Criterion 4 (15 marks)

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| F1 | Helper functions in `src/`: stratified bootstrap CI, Wilson CI, effect sizes (Hedges' g, Cliff's δ, risk difference) | | ⬜ | |
| F2 | Coverage simulation: simulate from fitted distributions / model, check that 95% intervals cover ≈95%. See [KB 01](knowledge_base/01_confidence_intervals_and_bootstrap.md). | | ⬜ | |
| F3 | Review every interval statement in the report for correct interpretation (no "95% probability") | | ⬜ | |

## G. Model and validation · Criterion 6 (15 marks)

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| G1 | Logistic regression (statsmodels) with ORs in clinical units (per 10 yrs, per 50 mg/dL, per 5 kg/m²) + absolute risk for example patients | | ⬜ | |
| G2 | Baselines: intercept-only and age-only | | ⬜ | |
| G3 | Diagnostics: spline check for linearity of logit, influence, VIF, separation | | ⬜ | |
| G4 | Calibration: reliability diagram, calibration intercept/slope, Brier (out of fold). See [KB 08](knowledge_base/08_logistic_regression_and_calibration.md). | | ⬜ | |
| G5 | Sensitivity: adults-only (exclude < 18) vs full data | | ⬜ | |

## H. Ethics and data handling · Criterion 7

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| H1 | Fill in the before/after column of the cleaning log in [data/README.md](data/README.md) | | ⬜ | |
| H2 | Error rates (FN rate, FP rate, PPV) by age group and gender, with CIs | | ⬜ | |
| H3 | Write the 2–3 paragraph ethics section (licence, id removed, exclusions, disparities) | | ⬜ | |

## R. Reproducibility · Criterion 8

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| R1 | Before the deadline: fresh clone → `python run_all.py` reproduces every figure and number | | ⬜ | |
| R2 | Check that every number in the report traces to a file in `results/` | | ⬜ | |

## W. Report and presentation

| ID | Task | Owner | Status | Output |
|----|------|-------|--------|--------|
| W1 | Rewrite the research-question paragraph with the stated cost ratio (criterion 1) | | ⬜ | |
| W2 | Report draft, 3–4 pages + appendix | | ⬜ | |
| W3 | 12-minute slide deck | | ⬜ | |
| W4 | Rehearse the Q&A: prepare answers for F1–F5 and "what does your CI mean?" | all | ⬜ | |
