# Professor feedback on the proposal

From Dr Sein Minn, on the proposal in [MAS_Proposal (1).pdf](MAS_Proposal%20(1).pdf).

## Original comment

> Hi guys,
>
> First of all, this is a careful proposal, and it's obvious you've opened the data rather than described it from the Kaggle page. The decision framing is right for a 5% event rate, and the PPV arithmetic in section 2 is the kind of thing I'd want every group to have done before choosing a model.
>
> Three things to think about before you build.
>
> Your entire result rests on the referral threshold, and the threshold rests on a ratio of two costs that you never state. Where does that number come from? And what happens to your recommendation when it moves?
>
> You plan multiple imputation and cross-validation. Think carefully about the order those happen in and what each fold is allowed to see. Also, imputation gives you more than one dataset. Decide now what you'll do with that.
>
> Your three hypotheses are things any clinician already knows. Nobody will be surprised that age raises stroke risk. Is there a hypothesis that actually bears on the referral decision?
>
> Two smaller ones. Patients with missing BMI have four times the stroke rate of everyone else. Please, identify why that could be, and whether filling in the missing values can recover whatever is going on there. And a recommended threshold is an estimate like any other; treat it like one.
>
> Good job. So excited to see the final presentation.

## What each point asks us to do

| # | Feedback | What we must deliver | Background | Action items |
|---|----------|----------------------|------------|--------------|
| F1 | The cost ratio is never stated | Name the ratio C_FN : C_FP and where it comes from. Show how the recommended threshold changes as the ratio moves (sensitivity analysis or decision curve). | [cost-ratio-and-threshold](../knowledge_base/02_cost_ratio_and_threshold.md) | A1, A2, A3 |
| F2 | Order of multiple imputation and cross-validation | Impute **inside** each fold, using only the training part. Decide in advance how the m imputed datasets are pooled. | [imputation-and-cv](../knowledge_base/03_multiple_imputation_and_cv.md) | B1, B2 |
| F3 | The hypotheses are obvious | Replace or add hypotheses that bear on the referral decision (for example, whether modifiable factors improve net benefit beyond age). | [decision-relevant-hypotheses](../knowledge_base/05_decision_relevant_hypotheses.md) | C1, C2 |
| F4 | Missing BMI has 4× the stroke rate | Explain why. Test whether imputation can recover the signal (MAR vs MNAR). | [missing-data-mechanisms](../knowledge_base/04_missing_data_mechanisms.md) | D1, D2, D3 |
| F5 | The threshold is an estimate | Give the recommended threshold a confidence interval (bootstrap the whole pipeline). | [threshold-uncertainty](../knowledge_base/06_threshold_uncertainty.md) | A4 |
