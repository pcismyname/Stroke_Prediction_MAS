# Knowledge base

Short notes on the statistics behind this project, so everyone on the team can learn a method once and use it the same way. Each note covers what the method is, why we need it here, how to do it in Python, and common mistakes.

## Index

| # | Note | Why it matters for us | Grading criterion |
|---|------|-----------------------|-------------------|
| 01 | [Confidence intervals and the bootstrap](01_confidence_intervals_and_bootstrap.md) | Every number needs an interval; how to say what a CI means | 4 |
| 02 | [Cost ratio and the referral threshold](02_cost_ratio_and_threshold.md) | Professor F1: where the threshold comes from | 1, 6 |
| 03 | [Multiple imputation inside cross-validation](03_multiple_imputation_and_cv.md) | Professor F2: order of steps, pooling m datasets | 6, 7 |
| 04 | [Missing-data mechanisms (MCAR/MAR/MNAR)](04_missing_data_mechanisms.md) | Professor F4: missing BMI has 4× the stroke rate | 2, 7 |
| 05 | [Hypotheses that bear on the decision](05_decision_relevant_hypotheses.md) | Professor F3: replace obvious hypotheses | 5 |
| 06 | [Uncertainty in the recommended threshold](06_threshold_uncertainty.md) | Professor F5: the threshold is an estimate | 4, 6 |
| 07 | [Fitting a distribution](07_distribution_fitting.md) | Glucose: log-normal / Gamma / mixture | 3 |
| 08 | [Logistic regression and calibration](08_logistic_regression_and_calibration.md) | Main model, odds ratios, calibration | 6 |
| 09 | [Hypothesis test assumptions and effect sizes](09_hypothesis_tests_and_effect_sizes.md) | Checking assumptions, choosing fallbacks | 5 |

## Adding a note

1. Copy [_template.md](_template.md) and name it `NN_short_topic.md`.
2. Add a row to the index above.
3. Cite a source (textbook, paper or lecture) for anything you didn't derive yourself.
4. If a note is wrong, fix it and say what changed in the commit message.
