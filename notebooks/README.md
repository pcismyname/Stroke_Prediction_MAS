# notebooks/

`run_all.py` runs notebooks in filename order, so number them:

| Notebook | Content | Action items |
|----------|---------|--------------|
| `01_eda.ipynb` | Data overview, missingness, figures for the report | S2, D1 |
| `02_missing_bmi.ipynb` | Why missing BMI has 4× the stroke rate | D1–D3 |
| `03_distribution_glucose.ipynb` | Log-normal / Gamma / mixture fit | E1–E3 |
| `04_estimation.ipynb` | Intervals + coverage simulation | F1–F3 |
| `05_hypothesis_tests.ipynb` | Pre-registered tests | C1–C3 |
| `06_model.ipynb` | Logistic regression, MI inside CV, calibration | B1–B3, G1–G4 |
| `07_threshold_decision.ipynb` | Cost ratio, decision curve, threshold CI | A1–A4 |
| `08_fairness.ipynb` | Error rates by age and gender | H2 |

Rules:
- Import paths and seeds from `src.config`. Never hard-code a seed.
- Load data with `src.data.load_raw()`.
- Save figures to `results/figures/` and tables to `results/tables/` so the report can reference them.
- A notebook must run top to bottom on a fresh kernel (Kernel → Restart & Run All) before you push.
- Personal scratch notebooks: name them without a number prefix (e.g. `scratch_alice.ipynb`), so `run_all.py` skips them.
