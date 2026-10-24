"""Loading of the raw Wisconsin Diagnostic Breast Cancer (WDBC) data.

The raw file ``data/raw/wdbc_breast_cancer_raw.csv`` is an unmodified copy of the
UCI WDBC dataset as bundled with scikit-learn (first line = metadata
``n_samples,n_features,class_0,class_1``; remaining lines = 30 features + class code).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_FEATURES = [
    "radius",
    "texture",
    "perimeter",
    "area",
    "smoothness",
    "compactness",
    "concavity",
    "concave points",
    "symmetry",
    "fractal dimension",
]
# Order used by the UCI file: 10 "mean" columns, 10 "error" (SE) columns, 10 "worst" columns.
RAW_FEATURE_NAMES = (
    [f"mean {b}" for b in BASE_FEATURES]
    + [f"{b} error" for b in BASE_FEATURES]
    + [f"worst {b}" for b in BASE_FEATURES]
)
RAW_TARGET_NAME = "target"


def project_root() -> Path:
    """Return the repository root (works from the root or from ``notebooks/``)."""
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "data" / "raw").is_dir():
            return candidate
    return here


def read_metadata(path: str | Path) -> dict:
    """Read the metadata header line of the raw file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        first = fh.readline().strip().split(",")
    return {
        "n_samples": int(first[0]),
        "n_features": int(first[1]),
        "class_names": first[2:],  # index in this list == integer class code
    }


def load_raw(path: str | Path) -> pd.DataFrame:
    """Load the raw dataset exactly as stored (no cleaning).

    Raises
    ------
    FileNotFoundError
        If the file does not exist (message explains how to obtain it).
    ValueError
        If the file shape does not match the metadata header.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found at '{path}'. See README.md ('Dataset') for how to "
            "obtain wdbc_breast_cancer_raw.csv."
        )
    meta = read_metadata(path)
    df = pd.read_csv(path, skiprows=1, header=None)
    expected_cols = meta["n_features"] + 1
    if df.shape != (meta["n_samples"], expected_cols):
        raise ValueError(
            f"Unexpected shape {df.shape}; header says "
            f"({meta['n_samples']}, {expected_cols})."
        )
    df.columns = RAW_FEATURE_NAMES + [RAW_TARGET_NAME]
    df.attrs["class_names"] = meta["class_names"]
    return df
