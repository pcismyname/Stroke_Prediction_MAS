"""Load the raw stroke dataset with consistent types."""

import pandas as pd

from src.config import RAW_FILE

CATEGORICAL = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
BINARY = ["hypertension", "heart_disease", "stroke"]
CONTINUOUS = ["age", "avg_glucose_level", "bmi"]


def load_raw() -> pd.DataFrame:
    """Read the raw CSV and drop the `id` column (see data/README.md, decision 1)."""
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"{RAW_FILE} not found. Download it first: see data/README.md."
        )
    df = pd.read_csv(RAW_FILE)
    df = df.drop(columns="id")
    df[CATEGORICAL] = df[CATEGORICAL].astype("category")
    return df
