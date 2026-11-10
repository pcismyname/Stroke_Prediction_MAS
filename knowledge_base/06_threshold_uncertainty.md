# Uncertainty in the recommended threshold

**Related criteria:** 4, 6 · **Answers professor point F5**

> "A recommended threshold is an estimate like any other; treat it like one."

## Two separate sources of uncertainty

1. **Sampling uncertainty:** with only 249 strokes, a different sample of patients would give a different model and a different cost-minimising threshold. → Bootstrap CI.
2. **Cost-ratio uncertainty:** R is a judgement, not data. → Sensitivity analysis / decision curve ([note 02](02_cost_ratio_and_threshold.md)).

Report both, separately. Don't mix them into one interval.

## Bootstrap CI for the optimal threshold

Bootstrap the **whole pipeline**, not just the final predictions:

```
for b in 1..B:
    draw a stratified bootstrap sample (resample strokes and non-strokes separately)
    run the full pipeline on it: impute (inside CV) → fit → out-of-fold predictions
    find t*_b = threshold minimising expected cost at the chosen R
CI = 2.5th and 97.5th percentiles of t*_b
```

This is expensive (B × folds × imputations model fits). Practical options:
- Use B = 500–1,000 for this step instead of 10,000, and say so.
- A cheaper approximation: bootstrap only the out-of-fold predictions (resample patients, re-find t\*). It ignores model-fitting variability, so it will be too narrow. Label it as such if used.

## Show the flatness of the cost curve

The optimal threshold is often poorly identified because expected cost is nearly flat around the minimum. Plot expected cost per 1,000 patients against the threshold, with a bootstrap band. Report the **range of thresholds within X% of the minimum cost**. That range tells the physician more than a single number.

## Report in physician units

For the recommended threshold and its CI endpoints, report:
- referrals per 1,000 patients,
- strokes caught per 1,000 patients (sensitivity × prevalence × 1,000),
- referrals per stroke caught (= 1 / PPV).

## Common mistakes
- Reporting "the optimal threshold is 0.073" with no interval.
- Choosing the threshold and evaluating it on the same predictions. Use nested CV or a held-out set for the final evaluation.
