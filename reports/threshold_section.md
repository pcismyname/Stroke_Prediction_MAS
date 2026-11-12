# Referral threshold and its uncertainty (Track 5 draft for the report)

Draft text for the report, written from `notebooks/07_threshold_decision.ipynb`. Every number comes from a CSV in `results/tables/` (listed at the end). Owner: Nero (Track 5). Track 6 can cut or merge freely.

---

## Methods (short)

We refer a patient when the predicted stroke risk is at or above p\* = 1 / (1 + R), where R = C_FN / C_FP is the cost of a missed stroke relative to one unnecessary counselling referral (Pauker & Kassirer, 1980). We fixed R = 20 before running any threshold analysis, which gives p\* = 4.8% (see the research question). All predictions are out of fold, from the MI-inside-CV model of Section [model]. For each threshold we report referrals per 1,000 patients, strokes caught per 1,000, sensitivity, PPV and referrals per stroke caught, with Wilson 95% CIs. We compare strategies with net benefit, TP/n − FP/n · t/(1 − t), shown as net strokes caught per 1,000 patients (Vickers & Elkin, 2006). Minimising expected cost at R is the same as maximising net benefit at p\*.

To put a CI on the threshold itself, we ran a stratified bootstrap of the whole pipeline. Each resample re-ran the 5-fold CV with BMI imputed m = 5 times inside each training fold, and we took the threshold that minimised expected cost on that resample's out-of-fold predictions. We used B = 200 resamples, fewer than our other bootstraps, to keep the run time manageable. Because a bootstrap sample repeats patients, folds were grouped by patient so that no patient appears in both the training and the test fold. Uncertainty in R is handled separately, by repeating everything for R = 5, 10, 20, 50 and 100.

## Results

**Operating point.** At R = 20 the rule refers 302 patients per 1,000 (95% CI 290 to 315) and catches 198 of the 249 strokes, a sensitivity of 79.5% (74.1% to 84.1%). PPV is 12.8% (11.3% to 14.6%), so the physician makes about 7.8 referrals for each stroke caught. Lowering R to 10 cuts referrals to 184 per 1,000 but catches only 32 strokes per 1,000 instead of 39 (Table T5-1, Figure `threshold_sweep.png`).

**Decision curve (professor point F1).** The model has higher net benefit than both referring everyone and referring no one for every threshold from 0.5% to 20.7%, which covers the whole range R = 5 to 100 (Figure `decision_curve.png`). At R = 20 it gives 25.6 net strokes caught per 1,000, compared with 1.2 for referring everyone. The advantage is small at the extremes: at R = 5 few patients cross the 16.7% threshold, and at R = 100 referring everyone is almost as good. The full model and the age-only model give almost the same curve. They differ by less than one net stroke per 1,000 at most thresholds, and at R = 20 age-only is slightly higher. This matches hypothesis H1: for the referral decision, nearly all the value comes from age.

**Threshold CI (professor point F5).** On our data the threshold that minimises expected cost at R = 20 is 3.6%, with a 95% whole-pipeline bootstrap CI of 2.9% to 6.5%. The interval comes from a procedure that would capture the true cost-minimising threshold in about 95% of repeated samples. It contains our pre-stated rule of 4.8%, and the same is true at every R we tried (Figure `threshold_by_cost_ratio.png`). The cost curve is flat near its minimum: any threshold from about 2.75% to 4.5% gives a cost within 5% of the lowest value, which is roughly one missed stroke per 1,000 patients (Figure `threshold_uncertainty.png`).

The data-chosen 3.6% looks better than 4.8% partly because it was chosen and scored on the same patients. When we chose the threshold on four folds and tested it on the fifth, it saved only 0.4 missed-stroke equivalents per 1,000 patients compared with the fixed rule. Track 3's calibration check also showed a small wobble in the 2% to 6% risk band, which explains why the minimum sits slightly below p\*.

**Two sources of uncertainty.** Sampling moves the threshold within about 2.9% to 6.5%. The judgement about R moves it much further, from 16.7% at R = 5 to 1.0% at R = 100. The cost ratio is therefore the bigger source of uncertainty, which is why we state R and its source up front.

## Recommendation (for the conclusion)

We recommend referring patients whose predicted stroke risk is at least 4.8%, which corresponds to accepting 20 unnecessary referrals to catch one stroke. This would mean about 300 referrals per 1,000 patients and about 8 in 10 strokes caught. We keep this pre-stated value instead of the data-chosen 3.6%, because it lies inside the bootstrap CI and tuning it would gain very little. A clinic with spare counselling capacity could lower the threshold to about 3%. That catches about 30 more strokes per 5,109 patients for about 106 extra referrals per 1,000, at almost no change in expected cost.

## Limitations to mention

- B = 200 means each CI end rests on about 5 resamples, so the ends are approximate (roughly ±0.5 percentage points).
- The cheaper bootstrap, which keeps the predictions fixed, was not clearly narrower than the whole-pipeline one at R = 20. We report the whole-pipeline CI.
- R = 20 is a stated judgement, not a published cost figure.
- The model is evaluated on a single public dataset with 249 strokes; the threshold has not been checked on other patients.

## Table T5-1 (from `threshold_operating_points.csv`)

| R | p\* | Referrals / 1,000 | Strokes caught / 1,000 | Sensitivity (95% CI) | PPV (95% CI) | Referrals per stroke caught | Net strokes / 1,000 |
|---|---|---|---|---|---|---|---|
| 5 | 16.7% | 79 | 15.5 | 31.7% (26.3–37.7) | 19.7% (16.1–23.8) | 5.1 | 2.8 |
| 10 | 9.1% | 184 | 31.7 | 65.1% (59.0–70.7) | 17.2% (14.9–19.8) | 5.8 | 16.5 |
| **20** | **4.8%** | **302** | **38.8** | **79.5% (74.1–84.1)** | **12.8% (11.3–14.6)** | **7.8** | **25.6** |
| 50 | 2.0% | 489 | 45.4 | 93.2% (89.3–95.7) | 9.3% (8.2–10.5) | 10.8 | 36.5 |
| 100 | 1.0% | 616 | 47.8 | 98.0% (95.4–99.1) | 7.8% (6.9–8.7) | 12.9 | 42.1 |

## Where each number comes from

| Number | File |
|--------|------|
| Operating points, Table T5-1 | `results/tables/threshold_operating_points.csv` |
| Full sweep | `results/tables/threshold_sweep.csv` |
| Net benefit by R, model vs age-only vs defaults | `results/tables/decision_curve_summary.csv`, `decision_curve.csv` |
| 0.5%–20.7% useful range | `results/tables/decision_curve_useful_range.csv` |
| t̂, CI, flatness bands | `results/tables/threshold_ci.csv` |
| Per-resample thresholds (B = 200) | `results/tables/threshold_bootstrap_pipeline.csv` |
| Cross-fitted comparison (0.4 per 1,000) | `results/tables/threshold_selection_cv.csv` |
| Physician units at the CI ends | `results/tables/threshold_physician_units.csv` |
| Complete case vs MI check | `results/tables/threshold_simple_vs_final.csv` |

## References

- Pauker, S. G., & Kassirer, J. P. (1980). The threshold approach to clinical decision making. *New England Journal of Medicine, 302*(20), 1109–1117. https://doi.org/10.1056/NEJM198005153022003
- Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. *Medical Decision Making, 26*(6), 565–574. https://doi.org/10.1177/0272989X06295361
