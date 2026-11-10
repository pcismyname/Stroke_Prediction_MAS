"""Reproduce every figure and number: run all notebooks in order.

Usage:  python run_all.py

Notebooks in notebooks/ run in filename order (01_..., 02_..., ...),
are executed in place, and write their outputs to results/.
"""

import subprocess
import sys
from pathlib import Path

from src.config import RAW_FILE

ROOT = Path(__file__).resolve().parent


def main() -> int:
    if not RAW_FILE.exists():
        print(f"Missing {RAW_FILE}. See data/README.md for how to download it.")
        return 1

    notebooks = sorted((ROOT / "notebooks").glob("[0-9][0-9]_*.ipynb"))
    if not notebooks:
        print("No numbered notebooks found in notebooks/ yet.")
        return 0

    for nb in notebooks:
        print(f"Running {nb.name} ...", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
             "--execute", "--inplace", "--ExecutePreprocessor.timeout=-1", str(nb)],
            cwd=ROOT,
        )
        if result.returncode != 0:
            print(f"FAILED: {nb.name}")
            return result.returncode
    print("All notebooks ran successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
