"""Project-wide settings: paths, random seeds and analysis constants.

Import from here instead of hard-coding numbers in notebooks, so every
result can be reproduced and the seeds are stated in one place.
"""

from pathlib import Path

# ---- Paths ----
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_EXTERNAL = ROOT / "data" / "external"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"

RAW_FILE = DATA_RAW / "healthcare-dataset-stroke-data.csv"

# ---- Reproducibility ----
# Used for CV splits, bootstrap, permutation tests and imputation.
# For the m-th imputation use SEED + m.
SEED = 42

# ---- Analysis constants ----
N_BOOT = 10_000        # bootstrap resamples for CIs
N_BOOT_PIPELINE = 200  # resamples when bootstrapping the whole pipeline (threshold CI)
N_PERM = 10_000        # permutation test resamples
N_GOF_BOOT = 1_000     # parametric-bootstrap goodness-of-fit replicates
N_SIM = 1_000          # coverage-simulation replicates
N_FOLDS = 5            # stratified k-fold CV
N_IMPUTATIONS = 5      # multiple imputation datasets (m); raise to 20 if time allows
ALPHA = 0.05

# Cost ratio R = C_FN / C_FP (action item A1, decided 2026-11-12).
# R = 20: we accept 20 unnecessary counselling referrals to catch one stroke.
# Source: elicitation (a stated judgement, not published costs); see
# docs/cost_ratio.md. Threshold p* = 1 / (1 + R) = 4.76%, close to the 4.87%
# base rate. Results are repeated over COST_RATIO_GRID.
COST_RATIO = 20
COST_RATIO_GRID = [5, 10, 20, 50, 100]  # for sensitivity analysis

TARGET = "stroke"
