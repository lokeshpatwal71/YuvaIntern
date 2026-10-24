"""Data-quality auditing and cleaning functions for the WDBC dataset.

Every function is pure (returns new objects; never modifies the input) so the raw
data can never be overwritten by accident.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DIAGNOSIS_COL = "diagnosis"
OUTLIER_COUNT_COL = "outlier_feature_count"

# Features that must be strictly positive (physical sizes / textures / ratios).
STRICTLY_POSITIVE_BASES = [
    "radius", "texture", "perimeter", "area", "smoothness",
    "compactness", "symmetry", "fractal_dimension",
]
# Features that may legitimately be zero (a perfectly convex contour has no concavity).
NON_NEGATIVE_BASES = ["concavity", "concave_points"]


def standardise_column_name(name: str) -> str:
    """'mean concave points' -> 'concave_points_mean'; 'area error' -> 'area_se'."""
    name = name.strip().lower()
    if name.startswith("mean "):
        return name[5:].replace(" ", "_") + "_mean"
    if name.startswith("worst "):
        return name[6:].replace(" ", "_") + "_worst"
    if name.endswith(" error"):
        return name[:-6].replace(" ", "_") + "_se"
    return name.replace(" ", "_")


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to consistent snake_case names."""
    return df.rename(columns={c: standardise_column_name(c) for c in df.columns})


def decode_diagnosis(df: pd.DataFrame, class_names: list[str],
                     target_col: str = "target") -> pd.DataFrame:
    """Replace the integer class code by a labelled categorical ``diagnosis`` column.

    Raises ValueError if a code has no matching label (inconsistent labels).
    """
    if target_col not in df.columns:
        raise KeyError(f"Column '{target_col}' not found.")
    codes = df[target_col]
    valid = set(range(len(class_names)))
    bad = sorted(set(codes.dropna().unique()) - valid)
    if bad:
        raise ValueError(f"Unknown class codes {bad}; expected {sorted(valid)}.")
    labels = [c.capitalize() for c in class_names]
    out = df.drop(columns=[target_col]).copy()
    out[DIAGNOSIS_COL] = pd.Categorical(
        codes.map(dict(enumerate(labels))), categories=labels
    )
    return out


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Numeric measurement columns (excludes the diagnosis and derived flag columns)."""
    return [c for c in df.select_dtypes(include="number").columns if c != OUTLIER_COUNT_COL]


def missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """Missing count and percentage per column (all columns listed)."""
    n = len(df)
    counts = df.isna().sum()
    pct = (counts / n * 100) if n else counts * 0.0
    return pd.DataFrame({"missing_count": counts, "missing_pct": pct.round(3)})


def duplicate_count(df: pd.DataFrame, subset: list[str] | None = None) -> int:
    """Number of rows that duplicate an earlier row."""
    return int(df.duplicated(subset=subset).sum())


def handle_missing(df: pd.DataFrame, strategy: str = "report") -> pd.DataFrame:
    """Handle missing values with an explicit, configurable strategy.

    strategy:
      * ``"report"`` - leave data untouched (use when audit shows no gaps)
      * ``"median"`` - fill numeric NaN with the column median (robust to outliers)
      * ``"drop"``   - drop rows containing any NaN
    """
    if strategy == "report":
        return df.copy()
    if strategy == "drop":
        return df.dropna().reset_index(drop=True)
    if strategy == "median":
        out = df.copy()
        num = out.select_dtypes(include="number").columns
        out[num] = out[num].fillna(out[num].median())
        return out
    raise ValueError(f"Unknown strategy '{strategy}'. Use 'report', 'median' or 'drop'.")


def remove_duplicates(df: pd.DataFrame, subset: list[str] | None = None
                      ) -> tuple[pd.DataFrame, int]:
    """Drop exact duplicate rows (keeping the first). Returns (data, n_removed)."""
    before = len(df)
    out = df.drop_duplicates(subset=subset).reset_index(drop=True)
    return out, before - len(out)


def _base_of(col: str) -> str:
    for suf in ("_mean", "_se", "_worst"):
        if col.endswith(suf):
            return col[: -len(suf)]
    return col


def find_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    """Count values violating the physical validity rules, per column.

    Rule: strictly-positive features must be > 0; concavity features must be >= 0.
    Columns without violations are omitted; returns an empty frame if all valid.
    """
    rows = []
    for col in feature_columns(df):
        base = _base_of(col)
        if base in STRICTLY_POSITIVE_BASES:
            n_bad = int((df[col] <= 0).sum())
            rule = "> 0"
        elif base in NON_NEGATIVE_BASES:
            n_bad = int((df[col] < 0).sum())
            rule = ">= 0"
        else:
            continue
        if n_bad:
            rows.append({"column": col, "rule": rule, "violations": n_bad})
    return pd.DataFrame(rows, columns=["column", "rule", "violations"])


def count_zero_values(df: pd.DataFrame) -> pd.Series:
    """Zeros per numeric feature (only columns that have at least one)."""
    z = (df[feature_columns(df)] == 0).sum()
    return z[z > 0]


def isoperimetric_violations(df: pd.DataFrame) -> pd.Series:
    """Rows where perimeter^2 < 4*pi*area (geometrically impossible for a closed shape).

    Uses the mean perimeter and mean area columns. Returns a boolean Series.
    """
    for c in ("perimeter_mean", "area_mean"):
        if c not in df.columns:
            raise KeyError(f"Column '{c}' required for the geometric check.")
    return df["perimeter_mean"] ** 2 < 4 * np.pi * df["area_mean"]


def iqr_outlier_mask(df: pd.DataFrame, columns: list[str] | None = None,
                     k: float = 1.5) -> pd.DataFrame:
    """Boolean mask of Tukey-fence outliers (value < Q1-k*IQR or > Q3+k*IQR)."""
    cols = columns if columns is not None else feature_columns(df)
    q1 = df[cols].quantile(0.25)
    q3 = df[cols].quantile(0.75)
    iqr = q3 - q1
    return (df[cols] < q1 - k * iqr) | (df[cols] > q3 + k * iqr)


def add_outlier_count(df: pd.DataFrame, k: float = 1.5) -> pd.DataFrame:
    """Add ``outlier_feature_count`` (how many features of a row are IQR outliers).

    Rows are *flagged, not removed*: extreme tumour sizes are real clinical values.
    """
    out = df.copy()
    if len(out) == 0:
        out[OUTLIER_COUNT_COL] = pd.Series(dtype="int64")
        return out
    out[OUTLIER_COUNT_COL] = iqr_outlier_mask(out, k=k).sum(axis=1).astype(int)
    return out


def clean_dataset(raw: pd.DataFrame, class_names: list[str],
                  missing_strategy: str = "report") -> tuple[pd.DataFrame, dict]:
    """Full cleaning pipeline; returns (clean_df, log).

    Steps: standardise names -> decode label -> missing -> duplicates -> flag outliers.
    ``log`` records row/column counts and counts changed at each step.
    """
    log: dict = {"rows_raw": len(raw), "cols_raw": raw.shape[1]}
    df = standardise_columns(raw)
    df = decode_diagnosis(df, class_names)
    log["missing_before"] = int(df.isna().sum().sum())
    df = handle_missing(df, missing_strategy)
    log["missing_after"] = int(df.isna().sum().sum())
    df, n_dup = remove_duplicates(df)
    log["duplicates_removed"] = n_dup
    log["invalid_value_columns"] = len(find_invalid_values(df))
    df = add_outlier_count(df)
    log["rows_clean"] = len(df)
    log["cols_clean"] = df.shape[1]
    log["rows_with_outlier_flag"] = int((df[OUTLIER_COUNT_COL] > 0).sum())
    return df, log
