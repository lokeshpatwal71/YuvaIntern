"""Statistical analysis helpers for the WDBC dataset."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from data_cleaning import DIAGNOSIS_COL, feature_columns


def describe_numeric(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Mean, median, std, variance, quartiles, range, skewness and kurtosis per column."""
    cols = columns if columns is not None else feature_columns(df)
    d = df[cols]
    out = pd.DataFrame({
        "mean": d.mean(),
        "median": d.median(),
        "std": d.std(),
        "variance": d.var(),
        "min": d.min(),
        "q1": d.quantile(0.25),
        "q3": d.quantile(0.75),
        "max": d.max(),
        "skew": d.skew(),
        "kurtosis": d.kurt(),
    })
    return out


def class_balance(df: pd.DataFrame, col: str = DIAGNOSIS_COL) -> pd.DataFrame:
    """Counts and percentages per class label."""
    counts = df[col].value_counts()
    return pd.DataFrame({"count": counts, "percent": (counts / counts.sum() * 100).round(2)})


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    """Cohen's d (pooled SD) for a - b."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    pooled = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled else float("nan")


def compare_groups(df: pd.DataFrame, columns: list[str] | None = None,
                   group_col: str = DIAGNOSIS_COL, positive: str = "Malignant",
                   negative: str = "Benign") -> pd.DataFrame:
    """Compare a numeric feature between two diagnosis groups.

    Returns per feature: group means/medians, % difference of means, Cohen's d,
    Mann-Whitney U p-value and the rank-based separation AUC
    (probability a random malignant case has a larger value than a random benign one;
    ``separation_auc`` = max(auc, 1-auc), 0.5 = no separation, 1.0 = perfect).
    """
    cols = columns if columns is not None else feature_columns(df)
    pos = df[df[group_col] == positive]
    neg = df[df[group_col] == negative]
    rows = []
    for c in cols:
        a, b = pos[c], neg[c]
        u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        auc = u / (len(a) * len(b))
        rows.append({
            "feature": c,
            f"mean_{positive.lower()}": a.mean(),
            f"mean_{negative.lower()}": b.mean(),
            f"median_{positive.lower()}": a.median(),
            f"median_{negative.lower()}": b.median(),
            "pct_diff_of_means": (a.mean() - b.mean()) / b.mean() * 100,
            "cohens_d": cohens_d(a, b),
            "mannwhitney_p": p,
            "auc_malignant_higher": auc,
            "separation_auc": max(auc, 1 - auc),
        })
    return pd.DataFrame(rows).set_index("feature").sort_values("separation_auc", ascending=False)


def top_correlated_pairs(df: pd.DataFrame, columns: list[str] | None = None,
                         threshold: float = 0.9) -> pd.DataFrame:
    """Unique feature pairs with |Pearson r| >= threshold, strongest first."""
    cols = columns if columns is not None else feature_columns(df)
    corr = df[cols].corr()
    iu = np.triu_indices_from(corr, k=1)
    pairs = pd.DataFrame({
        "feature_1": corr.index[iu[0]],
        "feature_2": corr.columns[iu[1]],
        "pearson_r": corr.values[iu],
    })
    pairs = pairs[pairs["pearson_r"].abs() >= threshold]
    return pairs.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False
                             ).reset_index(drop=True)


def correlation_with_diagnosis(df: pd.DataFrame, columns: list[str] | None = None,
                               group_col: str = DIAGNOSIS_COL,
                               positive: str = "Malignant") -> pd.Series:
    """Point-biserial correlation of each feature with (diagnosis == positive)."""
    cols = columns if columns is not None else feature_columns(df)
    y = (df[group_col] == positive).astype(int)
    return df[cols].corrwith(y).sort_values(key=lambda s: s.abs(), ascending=False)


def rate_by_quantile_bin(df: pd.DataFrame, col: str, q: int = 10,
                         group_col: str = DIAGNOSIS_COL,
                         positive: str = "Malignant") -> pd.DataFrame:
    """Share of ``positive`` cases within equal-frequency bins of ``col``."""
    work = pd.DataFrame({
        "value": df[col],
        "is_pos": (df[group_col] == positive).astype(int),
    })
    work["bin"] = pd.qcut(work["value"], q=q, duplicates="drop")
    g = work.groupby("bin", observed=True)
    out = pd.DataFrame({
        "bin_mean": g["value"].mean(),
        "n": g.size(),
        "malignant_count": g["is_pos"].sum(),
        "malignant_rate_pct": g["is_pos"].mean() * 100,
    }).reset_index(drop=True)
    return out


def skew_before_after_log(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Skewness of raw vs log1p-transformed values (all inputs must be >= 0)."""
    rows = []
    for c in columns:
        if (df[c] < 0).any():
            raise ValueError(f"Column '{c}' has negative values; log1p not applicable.")
        rows.append({"feature": c, "skew_raw": df[c].skew(),
                     "skew_log1p": np.log1p(df[c]).skew()})
    return pd.DataFrame(rows).set_index("feature")
