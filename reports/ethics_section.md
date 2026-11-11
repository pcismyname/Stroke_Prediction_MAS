# Ethics and data handling (draft for the report, criterion 7)

Action item H3 (Track 1). Written to drop into the report section on ethics. Every number traces to a file in `results/`; sources are listed at the end.

---

**Data source, licence and privacy.** All results come from the Stroke Prediction Dataset (fedesoriano, 2021, Kaggle), 5,110 patient records with 249 strokes. The licence states that the data files belong to the original authors and that the source is confidential, so we use the data only for this course, credit the author, and do not make claims about any specific hospital or country. The file contains no names, dates or addresses. Its only per-record identifier, `id`, is dropped when the data are loaded (`src/data.py`) and is not used anywhere. We report only group-level results. Some groups are very small, such as the single patient with gender "Other", so we do not describe any individual record. Because the original population and collection process are undisclosed, we cannot confirm how consent was obtained, which is one more reason to treat the results as a course exercise and not as evidence for clinical use. The synthetic Kaggle Playground version of the data was where the project started, but it was not used for any result because it does not keep the missing-BMI pattern or the second glucose peak.

**Exclusions and their effect.** Every decision that changes the data is listed in the cleaning log (`data/README.md`) with the result with and without it (`results/tables/cleaning_before_after.csv`). None of them changes a conclusion. Keeping the 1,544 patients with smoking status "Unknown" retains 47 strokes that would otherwise be lost, and the current-smoking odds ratio is 1.46 with them and 1.48 without. Missing BMI is the most important case: dropping the 201 patients without BMI would remove 40 of the 249 strokes (16%), so the main model uses multiple imputation and the complete-case results are reported beside it (BMI odds ratio 0.99 against 1.02). The single "Other" gender record is excluded from the referral model because one record cannot support a coefficient, and it had no stroke, so the stroke rate is 4.87% either way. The 13 BMI values above 60 are kept (BMI odds ratio 1.02 kept, 1.03 removed). Patients under 18 are kept in the main analysis; removing them changes the age, hypertension and BMI odds ratios by at most 0.01. We also chose not to give the referral model a "BMI missing" indicator, even though it raised the AUC by 0.010 (95% CI 0.004 to 0.017), because the extra risk it captures looks like a feature of how this dataset was recorded and would not carry over to a clinic where BMI is measured before any stroke (`notebooks/02_missing_bmi.ipynb`, D4).

**Disparities and limits of use.** Missing data are not spread evenly. BMI is more often missing for men (adjusted odds ratio 1.34, 95% CI 1.00 to 1.79), current and former smokers, and patients with hypertension or heart disease, and these patients have a stroke rate of 19.9% against 4.3% for everyone else. Without the indicator, the model predicts 8.5% for them on average, so in this dataset it under-predicts risk for exactly the group with the least complete records. Physicians should not read a low predicted risk as reassuring when key measurements are missing. Children are a second group the model cannot serve: there are 856 patients under 18 but only 2 strokes, so performance cannot be checked for them and the threshold recommendation applies to adults only. Error rates (false-negative rate, false-positive rate and PPV) by age group and gender, with confidence intervals, are compared in [H2 table, Track 4: insert the key differences here]. The dataset has no ethnicity, income or insurance variables, so we cannot check fairness across those groups, and the model should be recalibrated and re-checked on a local population before any real use. Finally, the model is meant to support a referral decision for stroke-prevention counselling, not to replace the physician's judgement; a false negative means a patient who might have benefited is not referred, which is why the threshold is set from a stated cost ratio and reported with its uncertainty.

---

**Sources for the numbers**

| Number | File |
|--------|------|
| 5,110 rows, 249 strokes, 201 missing BMI, 856 under 18 | `results/tables/eda_proposal_check.csv` |
| Before/after for each exclusion | `results/tables/cleaning_before_after.csv` |
| 19.9% vs 4.3% stroke rate | `results/tables/eda_stroke_rate_by_missingness.csv` |
| Predictors of missing BMI (men OR 1.34) | `results/tables/missing_bmi_predictors_of_missingness.csv` |
| Indicator AUC gain 0.010 (0.004 to 0.017) | `results/tables/missing_bmi_indicator_auc.csv` |
| 8.5% predicted vs 19.9% observed | `results/tables/missing_bmi_indicator_calibration_by_group.csv` |
| Error rates by age and gender | H2 (Track 4), not yet available |

Reference: Sperrin, M., Martin, G. P., Sisk, R., & Peek, N. (2020). Missing data should be handled differently for prediction than for description or causal explanation. *Journal of Clinical Epidemiology*, 125, 183–187.
