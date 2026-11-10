# Cost ratio and the referral threshold

**Related criteria:** 1, 6 · **Answers professor point F1**

> "Your entire result rests on the referral threshold, and the threshold rests on a ratio of two costs that you never state. Where does that number come from? And what happens to your recommendation when it moves?"

## In one sentence

If missing a stroke (false negative) costs R times as much as an unnecessary referral (false positive), refer every patient whose predicted risk exceeds **p\* = 1 / (1 + R)**, provided the predicted risks are calibrated.

## Derivation

For a patient with predicted stroke probability p:

- Expected cost if we **refer**: (1 − p) · C_FP (a wasted slot if they would not have had a stroke)
- Expected cost if we **don't refer**: p · C_FN (a missed stroke)

Refer when p · C_FN > (1 − p) · C_FP, which gives

$$p > p^* = \frac{C_{FP}}{C_{FP} + C_{FN}} = \frac{1}{1 + R}, \qquad R = \frac{C_{FN}}{C_{FP}}$$

| R = C_FN / C_FP | Threshold p\* | Meaning |
|---|---|---|
| 5 | 16.7% | A missed stroke is 5× worse than a wasted slot |
| 10 | 9.1% | |
| 19.5 | 4.9% | Threshold equals the base rate |
| 20 | 4.8% | |
| 50 | 2.0% | Refer almost everyone with any risk |
| 100 | 1.0% | |

**This only works if p is calibrated.** If the model says 10% but the true rate among such patients is 5%, the rule refers the wrong people. Check calibration first ([note 08](08_logistic_regression_and_calibration.md)).

## Where can R come from? (pick one, state it, then vary it)

1. **Literature costs.** The cost of a stroke (acute care, rehab, lost productivity, QALYs) versus the cost of one counselling session. Be careful: a referral does not prevent every stroke. If counselling cuts risk by a fraction e, the benefit of a true positive is e · C_stroke, so R ≈ e · C_stroke / C_session.
2. **Capacity constraint.** If the clinic can counsel only K patients per 1,000, the threshold is whatever gives K referrals. R is then *implied* rather than chosen; report the implied value.
3. **Elicitation.** "How many unnecessary referrals would you accept to catch one extra stroke?" If a clinician answers N, then R ≈ N and p\* = 1/(1+N). This is the most transparent option for the report.

Whatever we choose, **state the number and its source in the research-question paragraph.**

## What happens when R moves: decision curve analysis

Net benefit at threshold p_t (Vickers & Elkin, 2006):

$$NB(p_t) = \frac{TP}{n} - \frac{FP}{n} \cdot \frac{p_t}{1 - p_t}$$

Plot NB against p_t (equivalently against R) for:

- our model,
- **refer everyone**: NB = π − (1 − π) · p_t/(1 − p_t), with π = 0.0487,
- **refer no one**: NB = 0,
- an age-only model (shows whether the extra variables help).

The model is useful only over the range of p_t where it beats all of these. This plot directly answers "what happens when the ratio moves?"

```python
import numpy as np
def net_benefit(y, p, thresholds):
    n = len(y)
    out = []
    for t in thresholds:
        pred = p >= t
        tp = np.sum(pred & (y == 1)); fp = np.sum(pred & (y == 0))
        out.append(tp / n - fp / n * t / (1 - t))
    return np.array(out)
```

Also report the threshold sweep in physician units: referrals per 1,000 patients, strokes caught per 1,000, and referrals needed per stroke caught (= 1/PPV).

## Common mistakes
- Choosing the threshold that maximises Youden's J or F1. Neither uses the costs.
- Picking the threshold on the same data used to report performance (optimistic). Pick it on out-of-fold predictions.
- Using SMOTE or class weights and then applying p\* = 1/(1+R). Resampling distorts probabilities, so the rule no longer holds. If you rebalance, recalibrate.

## Sources
- Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis. *Medical Decision Making*, 26(6), 565–574.
- Pauker, S. G., & Kassirer, J. P. (1980). The threshold approach to clinical decision making. *NEJM*, 302, 1109–1117.
