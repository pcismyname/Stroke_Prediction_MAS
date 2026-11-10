# Action items: 2-day plan

Pick a task: put your name in **Owner**, set **Status** to 🟡, and push. When done, set ✅ and link your notebook or file in **Output**.

**Status:** ⬜ To do · 🟡 In progress · ✅ Done · ⛔ Blocked
**Priority:** 🔴 Must (needed for a grading criterion or a professor point) · 🔵 Optional (only if time allows)

**Team:** Pichayut · Nyi Htut · Takdanai · Aphisit · Chidsanuphong · Nawee

Background reading: [knowledge_base/](knowledge_base/README.md) · Professor comments (F1–F5): [docs/professor_feedback.md](docs/professor_feedback.md) · Grading checklist: [docs/grading_checklist.md](docs/grading_checklist.md)

---

## Timeline

| When | Milestone |
|------|-----------|
| **Day 1, first hour (everyone together)** | S1 setup done · **A1 cost ratio chosen** · **C1 hypotheses committed**. These two decisions block other work, so settle them first. |
| Day 1, ~14:00 | Track 3 shares **simple out-of-fold predictions** (complete cases, no imputation) in `data/interim/oof_simple.csv` so Track 5 can start |
| Day 1, end | Each track has its main notebook running; results saved to `results/` |
| Day 2, ~12:00 | Final imputation-based predictions available; all figures and tables in `results/` |
| Day 2, ~16:00 | Report and slides drafted; R1 fresh-clone test |
| Day 2, evening | W4 Q&A rehearsal (everyone) |

**Critical path:** A1 cost ratio → B1 imputation pipeline → out-of-fold predictions → A2–A4 threshold → report. If you are blocked, say so in the group chat immediately.

## Tracks (one person each)

| Track | Focus | Owner |
|-------|-------|-------|
| 1 | EDA, missing BMI, ethics | Win |
| 2 | Distribution fitting, intervals | Ton |
| 3 | Imputation + CV pipeline, model (**strongest coder**) | |
| 4 | Hypotheses and tests, sensitivity analyses | |
| 5 | Threshold, decision curve, threshold CI | |
| 6 | Report, slides, merging, reproducibility | |

---

## S. Setup: Day 1 morning, everyone

| ID | Pri | Task | Owner | Status | Output |
|----|-----|------|-------|--------|--------|
| S1 | 🔴 | Clone, create venv, `pip install -r requirements.txt`, download the data (see [data/README.md](data/README.md)) | all | ⬜ | |
| A1 | 🔴 | **Choose the cost ratio R = C_FN / C_FP and its source.** Set `COST_RATIO` in [src/config.py](src/config.py). See [KB 02](knowledge_base/02_cost_ratio_and_threshold.md). | all | ⬜ | |
| C1 | 🔴 | **Pick 2–3 decision-relevant hypotheses** from [KB 05](knowledge_base/05_decision_relevant_hypotheses.md); write them in [docs/hypotheses.md](docs/hypotheses.md) and **commit before testing** | all | ⬜ | |

## Track 1: EDA, missing BMI, ethics · Criteria 2, 7 · Professor F4

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| S2 | 🔴 | 1 | Reproduce the proposal's EDA numbers in `notebooks/01_eda.ipynb` (5,110 rows, 249 strokes, 201 missing BMI, 19.9% vs 4.3%, glucose histogram) | ✅ | [01_eda.ipynb](notebooks/01_eda.ipynb) |
| D1 | 🔴 | 1 | Compare the missing-BMI and recorded-BMI groups (age, glucose, hypertension, heart disease, work type) with CIs; model `bmi_missing ~ covariates`. See [KB 04](knowledge_base/04_missing_data_mechanisms.md). | ✅ | [02_missing_bmi.ipynb](notebooks/02_missing_bmi.ipynb) |
| D2 | 🔴 | 1 | Model `stroke ~ bmi_missing + covariates`: does the 4× excess survive adjustment? Interpret MAR vs MNAR / reverse causation. | ✅ | [02_missing_bmi.ipynb](notebooks/02_missing_bmi.ipynb) |
| D4 | 🔴 | 1 | Paragraph: why no missing-indicator in the referral model (report AUC with and without it; needs Track 3) | ⛔ | Waiting on Track 3 (B1) |
| D3 | 🔵 | 2 | Delta-adjustment sensitivity (δ = −5…+5) on the BMI OR | ⬜ | |
| H1 | 🔴 | 2 | Fill in the before/after column of the cleaning log in [data/README.md](data/README.md) | ⬜ | |
| H3 | 🔴 | 2 | Ethics section, 2–3 paragraphs (licence, id removed, exclusions, disparities) | ⬜ | |

## Track 2: Distribution and intervals · Criteria 3, 4

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| E1 | 🔴 | 1 | Data-generating justification for glucose (log-normal / Gamma / two-population mixture). See [KB 07](knowledge_base/07_distribution_fitting.md). | ✅ | [03_distribution_glucose](notebooks/03_distribution_glucose.ipynb) |
| E2 | 🔴 | 1 | Fit the 3 candidates; Q–Q plots; parametric-bootstrap Anderson–Darling; AIC/BIC table | ✅ | [03_distribution_glucose](notebooks/03_distribution_glucose.ipynb), [glucose_qq.png](results/figures/glucose_qq.png) |
| E3 | 🔴 | 1 | "Where the fit breaks and what it means" for the downstream tests | ✅ | [03_distribution_glucose](notebooks/03_distribution_glucose.ipynb) (last section) |
| F1 | 🔴 | 1 | Helpers in `src/stats_utils.py`: stratified bootstrap CI, Wilson CI, Hedges' g, Cliff's δ, risk difference. **Share early, since Tracks 4 and 5 use them.** | ✅ | [src/stats_utils.py](src/stats_utils.py) |
| F2 | 🔴 | 2 | Coverage simulation for **one** interval type (e.g. glucose mean or age OR). See [KB 01](knowledge_base/01_confidence_intervals_and_bootstrap.md). | ✅ | [04_estimation](notebooks/04_estimation.ipynb), [coverage_simulation.png](results/figures/coverage_simulation.png) |
| F3 | 🔴 | 2 | Review every interval sentence in the report (no "95% probability") | ⬜ | |
| E4 | 🔵 | — | Second variable: BMI, with and without values > 60 | ⬜ | |

## Track 3: Imputation + CV pipeline, model · Criterion 6 · Professor F2

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| B0 | 🔴 | 1 | **By ~14:00:** simple complete-case logistic model, stratified 5-fold, save out-of-fold predictions to `data/interim/oof_simple.csv` for Track 5 | ⬜ | |
| B1 | 🔴 | 1 | Full pipeline: split → impute on the training fold → fit → predict the test fold; average predictions over m imputations. Use m = 5 for speed (20 if time allows). See [KB 03](knowledge_base/03_multiple_imputation_and_cv.md). | ⬜ | |
| G1 | 🔴 | 1–2 | Logistic regression (statsmodels), Rubin's-rules ORs in clinical units (per 10 yrs, per 50 mg/dL, per 5 kg/m²) + absolute risk for example patients | ⬜ | |
| G2 | 🔴 | 2 | Baselines: intercept-only and age-only | ⬜ | |
| G4 | 🔴 | 2 | Calibration: reliability diagram, calibration intercept/slope, Brier (out of fold). See [KB 08](knowledge_base/08_logistic_regression_and_calibration.md). | ⬜ | |
| B2 | 🔴 | 2 | Methods paragraph on the pooling decision (Rubin's rules for ORs; averaged predictions for performance) | ⬜ | |
| B3 | 🔴 | 2 | Complete-case vs MI ORs side by side | ⬜ | |
| G3 | 🔵 | 2 | Diagnostics: spline linearity check + influence (skip VIF / separation if short on time) | ⬜ | |

## Track 4: Hypothesis tests and sensitivity · Criterion 5 · Professor F3

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| C2 | 🔴 | 1 | Run the decision-relevant tests from C1, with assumption checks, effect sizes and CIs. See [KB 09](knowledge_base/09_hypothesis_tests_and_effect_sizes.md). | ⬜ | |
| C4 | 🔴 | 1–2 | Keep [results/test_log.md](results/test_log.md) complete; Holm correction across the family | ⬜ | |
| C3 | 🔴 | 2 | Original proposal hypotheses P1–P3, run quickly as an appendix item | ⬜ | |
| G5 | 🔴 | 2 | Sensitivity: adults-only (exclude < 18) vs full data | ⬜ | |
| H2 | 🔴 | 2 | One table: FN rate, FP rate, PPV by age group and gender, with CIs | ⬜ | |

## Track 5: Threshold and decision · Criteria 1, 4, 6 · Professor F1, F5

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| A2 | 🔴 | 1 | Threshold sweep table and plot: PPV, sensitivity, referrals / 1,000, strokes caught / 1,000, expected cost (start on `oof_simple.csv`, swap in the final predictions on day 2) | ⬜ | |
| A3 | 🔴 | 1 | Decision curve: net benefit for model, age-only, refer-all, refer-none, across the cost-ratio range | ⬜ | |
| A4 | 🔴 | 2 | Bootstrap CI for the recommended threshold + cost-curve flatness band. **Use B ≈ 200 and m = 5 to keep the runtime manageable, and state that in the report.** See [KB 06](knowledge_base/06_threshold_uncertainty.md). | ⬜ | |

## Track 6: Report, slides, reproducibility · Criteria 1, 8

| ID | Pri | Day | Task | Status | Output |
|----|-----|-----|------|--------|--------|
| W1 | 🔴 | 1 | Rewrite the research-question paragraph with the stated cost ratio | ⬜ | |
| W2a | 🔴 | 1 | Report skeleton in `reports/` with sections matching the 8 criteria; fill in as results land | ⬜ | |
| W2 | 🔴 | 2 | Report, 3–4 pages + appendix | ⬜ | |
| W3 | 🔴 | 2 | 12-minute slide deck | ⬜ | |
| R1 | 🔴 | 2 | Fresh clone → `python run_all.py` reproduces every figure and number | ⬜ | |
| R2 | 🔴 | 2 | Every number in the report traces to a file in `results/` | ⬜ | |
| W4 | 🔴 | 2 eve | Q&A rehearsal (everyone): answers for F1–F5 and "what does your CI mean?" | ⬜ | |
