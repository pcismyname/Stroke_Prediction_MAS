# Grading checklist

Built from [MAS Project Guidelines  Grading Criteria.pdf](MAS%20Project%20Guidelines%20%20Grading%20Criteria.pdf). Tick items as they are done and link the notebook or figure that proves each one.

## 1. Research question and decision (10)
- [ ] One paragraph: who uses the answer (primary-care physician), what they do next (refer / don't refer), what happens if we're wrong
- [ ] Cost ratio C_FN : C_FP stated, with its source (professor F1)
- [ ] Paragraph re-checked at the end of the project and still holds

## 2. Data and exploratory analysis (10)
- [ ] Data source and licence stated
- [ ] Every dropped row, missing value, transformation and outlier decision recorded with a reason (see [data/README.md](../data/README.md))
- [ ] Each figure in the report is interpreted in the text; no decorative figures
- [ ] Missing-BMI investigation (professor F4)

## 3. Distributional modeling evidence (15)
- [ ] At least one variable (avg_glucose_level) modelled with a distribution justified by how the data are generated
- [ ] Q–Q plot plus a formal goodness-of-fit test
- [ ] Where the fit breaks (the second glucose peak), say so and say what it means
- [ ] Never "it looked approximately Normal"

## 4. Estimation and uncertainty (15)
- [ ] Every reported estimate has an interval
- [ ] Coverage simulation showing the intervals can be trusted
- [ ] Intervals interpreted correctly (long-run coverage, **not** "95% probability")
- [ ] The recommended threshold has an interval (professor F5)

## 5. Hypothesis testing evidence (15)
- [ ] Hypotheses written down **before** looking at results (commit them with a date)
- [ ] At least one hypothesis that bears on the referral decision (professor F3)
- [ ] Assumption checks shown for each test, with fallback when they fail
- [ ] Effect sizes with CIs next to every p-value
- [ ] Every test that was run is reported, including non-significant ones and multiple attempts

## 6. Statistical modeling and validation (15)
- [ ] Logistic regression vs a sensible baseline (intercept-only, age-only)
- [ ] Diagnostics (calibration plot, influential points, linearity of logit for continuous predictors)
- [ ] Out-of-sample validation with imputation done inside folds (professor F2)
- [ ] Results in units a physician can act on (odds ratios, referrals per 1,000 patients, strokes caught)

## 7. Ethics and data handling (10)
- [ ] Source and licence; `id` column removed and stated
- [ ] Before/after results for every exclusion or transformation (missing BMI, "Other" gender, BMI > 60, under-18s)
- [ ] Error rates compared across age and gender groups

## 8. Documentation and reproducibility (10)
- [ ] One command reproduces every figure and number
- [ ] Pinned dependency versions ([requirements.txt](../requirements.txt))
- [ ] Random seeds fixed and stated ([src/config.py](../src/config.py))
- [ ] Data card ([data/README.md](../data/README.md))
