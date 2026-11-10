# Pre-registered hypotheses

The grading criteria require hypotheses to be **stated before looking at results**. This file is our evidence: the git commit timestamp of each entry shows when it was written.

**Rules**
- Add entries; never edit or delete an old one. To change a hypothesis, add a new dated entry that says what changed and why.
- Commit this file **before** running the test.
- Every hypothesis here must appear in the report (or appendix), whatever the result.

Candidates and reasoning: [knowledge_base/05_decision_relevant_hypotheses.md](../knowledge_base/05_decision_relevant_hypotheses.md)

---

## Entry template

```
### H? — short name
- Date registered: YYYY-MM-DD   · Registered by:
- H₀:
- H₁:
- Test (and fallback if assumptions fail):
- Effect size reported:
- Significance level / multiplicity correction:
- Why it matters for the referral decision:
```

---

## Proposal hypotheses (from the submitted proposal; kept as descriptive checks)

### P1: Glucose differs between stroke and non-stroke patients
- H₀: mean glucose is equal; H₁: it differs
- Test: Welch's t-test; Mann–Whitney U if normality fails

### P2: Hypertension and stroke are associated
- H₀: independent; H₁: associated
- Test: two-proportion z-test or χ² test

### P3: Age increases stroke risk
- H₀: β_age = 0; H₁: β_age > 0
- Test: sign and size of the age coefficient, plus a trend test

---

## Decision-relevant hypotheses (to be registered: see action item C1)
