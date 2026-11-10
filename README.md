# Stroke Risk Prediction: a clinical referral decision through statistical inference

Course project for **Modern Applied Statistics for Data Science** (Dr Sein Minn, Asian Institute of Technology).

**Question:** Which patient characteristics are associated with stroke, by how much (with quantified uncertainty), and at what predicted-probability threshold does referring a patient for stroke-prevention counselling do more good than harm when the base rate is about 5%?

**Decision-maker:** a primary-care physician deciding whether to refer a patient.

**Team:** Pichayut Kungsuwan · Nyi Htut Oo · Takdanai Ruxthawonwong · Aphisit Jaemyaem · Chidsanuphong Pengchai · Nawee Pornsiriphanna

## Where to start

| If you want to… | Go to |
|-----------------|-------|
| Pick a task | [action_items.md](action_items.md) |
| Learn a method | [knowledge_base/](knowledge_base/README.md) |
| Read the proposal, grading criteria, professor feedback | [docs/](docs/README.md) |
| Understand the data | [data/README.md](data/README.md) (data card) |

## Repository layout

```
├── action_items.md      # task board: pick, own, finish
├── run_all.py           # one command: runs every notebook → results/
├── requirements.txt     # pinned package versions
├── data/                # NOT in git; see data/README.md to download
│   ├── raw/             # original CSV, never edited
│   ├── external/        # other source data (none currently)
│   ├── interim/         # intermediate outputs (e.g. imputed datasets)
│   └── processed/       # analysis-ready tables
├── docs/                # proposal, grading criteria, feedback, hypotheses
├── knowledge_base/      # shared statistics notes
├── notebooks/           # numbered analysis notebooks (01_…, 02_…)
├── src/                 # shared code: config (paths, seeds), data loading, helpers
├── results/
│   ├── figures/         # every figure in the report
│   ├── tables/          # every table in the report
│   └── test_log.md      # every statistical test run
└── reports/             # report and slides
```

## Getting started

```bash
git clone <repo-url>
cd Stroke_Prediction_MAS

python -m venv .venv
# Windows:     .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Download the data into `data/raw/` (instructions in [data/README.md](data/README.md)), then:

```bash
python run_all.py      # reproduce all results
jupyter lab            # or work interactively
```

## Reproducibility

- Random seed: **42** (`SEED` in [src/config.py](src/config.py)). Imputation m uses `SEED + m`.
- Bootstrap: 10,000 resamples; CV: stratified 5-fold; multiple imputation: m = 5 (20 if time allows); whole-pipeline bootstrap for the threshold CI: 200 resamples.
- Tested on Python 3.14.5 with the versions in [requirements.txt](requirements.txt).

## Team conventions

- Work on a branch, open a pull request, and get one teammate to review it.
- Never edit files in `data/raw/`.
- Log every statistical test in [results/test_log.md](results/test_log.md), including the ones that didn't work.
- Register hypotheses in [docs/hypotheses.md](docs/hypotheses.md) **before** running them.
- Before pushing a notebook: Restart & Run All.

## Data

Primary: fedesoriano (2021), [Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset), educational use only. Project origin: [Kaggle Playground Series S3E2](https://www.kaggle.com/competitions/playground-series-s3e2/data) (synthetic; not used for inference).
