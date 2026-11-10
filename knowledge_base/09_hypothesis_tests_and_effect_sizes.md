# Hypothesis test assumptions and effect sizes

**Related criterion:** 5 ("Assumptions are graded, not assumed.")

## For each test: assumption → how to check → fallback → effect size

| Test | Key assumptions | How to show they hold | Fallback | Effect size (+ CI) |
|------|-----------------|-----------------------|----------|-------------------|
| Welch's t-test | Independent obs; means approximately Normal (CLT) | Q–Q plot of each group; with skew and n_stroke = 249, check by bootstrapping the mean difference | Mann–Whitney U, or a bootstrap / permutation test of the mean difference | Mean difference (bootstrap CI); Hedges' g |
| Mann–Whitney U | Independent obs. It tests P(X > Y) ≠ 0.5, **not** a difference in medians unless the shapes are equal. | State what it tests | Permutation test | Rank-biserial correlation or Cliff's δ (= P(X>Y) − P(X<Y)) |
| χ² test of independence | Expected count ≥ 5 in every cell | Print the expected table (`scipy.stats.chi2_contingency(...)[3]`) | Fisher's exact test | Risk difference and risk ratio / OR (Wilson or Newcombe CI) |
| Two-proportion z | n·p and n·(1−p) ≥ ~10 in both groups | Show the counts | Fisher's exact / Newcombe CI | Risk difference |
| Logistic regression Wald test | Correct link, linearity of logit, no separation, enough events | See [note 08](08_logistic_regression_and_calibration.md) | Likelihood-ratio test or profile-likelihood CI (more reliable than Wald with few events) | Odds ratio (CI) |
| Permutation test | Exchangeability under H₀ | Argue it from the design | — | Same as the statistic permuted |

## Transparency rules (from the guidelines)

- Report **every** test run, including failed or abandoned ones. Keep a log in [results/test_log.md](../results/test_log.md).
- If a test was run several ways (t-test, MWU, permutation), report all of them.
- Every p-value sits next to an effect size and its CI. "p < 0.001" alone earns nothing.
- With n = 5,110, trivial differences become significant. Judge importance by the effect size.

## Phrasing

- ✅ "Stroke patients had a mean glucose 26 mg/dL higher (95% CI 19 to 33; Welch t-test p < 0.001; Hedges' g = 0.55)."
- ❌ "Glucose was significant."
- ❌ "The mean is higher in strokes, which makes sense."
