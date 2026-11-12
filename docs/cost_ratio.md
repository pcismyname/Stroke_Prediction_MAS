# Cost ratio decision (action item A1)

**Decision (2026-11-12):** R = C_FN / C_FP = **20**, so the referral threshold is
p\* = 1 / (1 + 20) = **4.76%**.

## Justification

**Source: elicitation (KB 02, option 3).** We asked: *"How many unnecessary
counselling referrals would we accept to catch one extra patient who goes on to
have a stroke?"* Our answer is 20.

Why 20 is reasonable for this setting:

1. **The two errors are very unequal.** A false positive costs one
   prevention-counselling session: some clinician time, and a patient who is
   reassured or given lifestyle advice they would probably benefit from anyway.
   A false negative is a stroke that was not acted on, which can mean death,
   permanent disability, long rehabilitation and lost working years. A missed
   stroke is clearly worth many wasted sessions, not just a few.
2. **Counselling does not prevent every stroke.** A referral only lowers risk;
   it does not remove it. So the benefit of a true positive is a *fraction* of
   the cost of a stroke (KB 02: R ≈ e · C_stroke / C_session). This keeps R
   well below the raw cost ratio of a stroke to a session, which is why we did
   not pick 50 or 100.
3. **The threshold lands at the population base rate.** p\* = 4.8% is almost
   exactly the stroke rate in the data (249 / 5,110 = 4.87%). The rule reads
   as: *refer a patient whose predicted risk is above the average patient's
   risk.* That is easy to explain to a clinician and to defend in Q&A.

## What this choice is not

- It is **not** derived from published cost figures; it is a stated judgement.
  We say so in the report.
- It was **not** tuned on results. It was fixed before any net-benefit,
  threshold or H2 analysis was run. (AUC and calibration were already known; they
  do not depend on R.)

## Sensitivity

Because R is a judgement, every threshold-dependent result (H1 ΔNB, H2, the
threshold sweep, the decision curve) is repeated over `COST_RATIO_GRID`
= 5, 10, 20, 50, 100 (p\* = 16.7%, 9.1%, 4.8%, 2.0%, 1.0%). The decision curve
(A3) shows the range of R over which the model beats refer-all and refer-none,
which answers professor point F1 ("what happens when it moves?").

## Sentence for the research question (W1)

> We assume missing a future stroke is 20 times as costly as an unnecessary
> counselling referral (R = 20, a stated judgement), which gives a referral
> threshold of 4.8% predicted risk; results are repeated for R from 5 to 100.
