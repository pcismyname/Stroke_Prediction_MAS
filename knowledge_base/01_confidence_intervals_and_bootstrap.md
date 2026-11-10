# Confidence intervals and the bootstrap

**Related criterion:** 4 (Estimation and uncertainty)

## In one sentence

A 95% confidence interval comes from a procedure that, over many repeated samples, captures the true value about 95% of the time. A single computed interval either contains the truth or it doesn't.

## How to say it (and how not to)

| ✅ Correct | ❌ Wrong (costs marks) |
|-----------|----------------------|
| "If we repeated this study many times, about 95% of intervals built this way would contain the true odds ratio." | "There is a 95% probability that the true odds ratio is between 1.2 and 2.1." |
| "The data are consistent with odds ratios from 1.2 to 2.1." | "95% of patients have an odds ratio in this range." |
| "The interval excludes 1, so the data are not consistent with no association at the 5% level." | "The interval is narrow, so the result is important." (Width tells you precision, not importance.) |

The guidelines say directly that calling a CI a "95% probability" will be marked down.

## Percentile bootstrap

Use it when no simple formula exists or normality is doubtful: skewed glucose, small subgroups (only 249 strokes), or the optimal threshold.

1. Resample n rows **with replacement**.
2. Recompute the statistic.
3. Repeat B times (we use B = 10,000; see `N_BOOT` in [src/config.py](../src/config.py)).
4. The 2.5th and 97.5th percentiles of the B values form the 95% interval.

```python
import numpy as np
from src.config import SEED, N_BOOT

rng = np.random.default_rng(SEED)
def boot_ci(x, stat=np.mean, B=N_BOOT, alpha=0.05):
    n = len(x)
    stats = np.array([stat(x[rng.integers(0, n, n)]) for _ in range(B)])
    return np.quantile(stats, [alpha / 2, 1 - alpha / 2])
```

Use `scipy.stats.bootstrap(..., method="BCa")` when the statistic is skewed or biased. BCa usually covers better than the plain percentile method.

**With rare events, stratify:** resample strokes and non-strokes separately so every bootstrap sample keeps 249 strokes. Otherwise some samples get very few events and the interval is unstable.

## Showing the intervals can be trusted (coverage simulation)

The proposal promises this, and it is how we earn criterion 4.

1. Pick a "true" population model, e.g. the fitted log-normal for glucose, or the fitted logistic model.
2. Simulate a dataset of the same size (n = 5,110) from it.
3. Build the interval with exactly our procedure.
4. Record whether it contains the known true value.
5. Repeat about 1,000 times. Coverage = fraction of hits, which should be near 0.95. Report it with its own binomial CI.

If coverage is well below 95% (common for small subgroups), say so and switch method (e.g. BCa, a profile-likelihood CI for odds ratios, or a Wilson interval for proportions).

## Proportions: use Wilson, not Wald

For stroke rates in small groups (e.g. 40 strokes among 201 missing-BMI patients), the Wald interval p ± 1.96·SE covers poorly. Use `statsmodels.stats.proportion.proportion_confint(count, n, method="wilson")`.

## Sources
- Efron & Tibshirani (1993), *An Introduction to the Bootstrap*
- Wasserstein & Lazar (2016), ASA statement on p-values
