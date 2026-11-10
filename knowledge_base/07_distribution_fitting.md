# Fitting a distribution (avg_glucose_level)

**Related criterion:** 3 (15 marks)

## Step 1: Justify the family from how the data are generated

The guidelines require this *before* looking at fit statistics.

- Glucose is **strictly positive** and concentrations arise from many **multiplicative** physiological effects, which points to log-normal.
- Gamma is the other common model for positive, right-skewed measurements.
- The histogram has **two peaks** (~85 and ~210 mg/dL). A plausible mechanism is two sub-populations, non-diabetic and diabetic, which points to a **two-component mixture** (e.g. two log-normals = a Gaussian mixture on log(glucose)).

## Step 2: Fit by maximum likelihood

```python
from scipy import stats
x = df["avg_glucose_level"].to_numpy()
ln_params = stats.lognorm.fit(x, floc=0)
ga_params = stats.gamma.fit(x, floc=0)

from sklearn.mixture import GaussianMixture
gm = GaussianMixture(n_components=2, random_state=SEED).fit(np.log(x).reshape(-1, 1))
```

## Step 3: Evidence a skeptic can check

1. **Q–Q plot** against each fitted distribution. Describe where it departs (tails? the second peak?).
2. **Formal test.** A plain KS test with *estimated* parameters gives p-values that are too large. Use either:
   - `scipy.stats.goodness_of_fit(stats.lognorm, x, statistic="ad")`, a parametric-bootstrap Anderson–Darling test that handles estimated parameters, or
   - a hand-written parametric bootstrap of the KS statistic.
3. **Compare models** with AIC/BIC (log-normal vs Gamma vs 2-component mixture).
4. With n = 5,110, *any* small misfit is significant. Pair the p-value with a visual and an effect-size view (e.g. max CDF gap from KS = D).

## Step 4: Say where it breaks and what it means

E.g. "A single log-normal underestimates the density above 180 mg/dL, so a t-test on glucose that assumes a single population would be misleading. We use Mann–Whitney / bootstrap instead." Linking the misfit to a downstream decision is what earns the marks.

## Don't
- Remove outliers to make the Q–Q plot look better (explicitly called "analysis fraud in miniature").
- Write "approximately Normal".

## Optional second variable
BMI (positive, right-skewed, 13 values > 60) is a good second candidate. Report the fit with and without the extreme values, but keep them in the main analysis.
