"""Reusable code for the Final Data Science Capstone Project.

Project: predicting one-year diabetes disease progression from baseline
patient measurements (regression) and identifying higher-risk patient groups.

Data: the Diabetes dataset of Efron, Hastie, Johnstone and Tibshirani (2004),
442 patients. scikit-learn ships the original, un-scaled values, so the data
can be loaded offline with no download, account or API key.

Every function is small, documented and free of hidden state, so it can be
tested (see tests/test_project_code.py) and re-used in the notebook.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.datasets import load_diabetes
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
TARGET = "progression"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "diabetes_raw.csv"
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "diabetes_clean_features.csv"
FIGURE_DIR = PROJECT_ROOT / "visualizations" / "generated_charts"

# Column meanings, taken from the dataset description shipped with scikit-learn.
FEATURE_LABELS = {
    "age": "Age (years)",
    "sex": "Sex (coded 1 and 2; the source does not say which is which)",
    "bmi": "Body mass index (kg/m^2)",
    "bp": "Average blood pressure",
    "s1": "tc - total serum cholesterol",
    "s2": "ldl - low-density lipoproteins",
    "s3": "hdl - high-density lipoproteins",
    "s4": "tch - total cholesterol / HDL",
    "s5": "ltg - possibly log of serum triglycerides level",
    "s6": "glu - blood sugar level",
}
BASE_FEATURES = list(FEATURE_LABELS)

# WHO adult cut-offs. The "Underweight" class (< 18.5) holds only 2 of the 442
# patients, so it is merged with "Normal" to keep every group large enough.
BMI_BINS = [0, 25, 30, np.inf]
BMI_LABELS = ["Under 25", "25 to 29.9", "30 and over"]
AGE_BINS = [0, 39, 49, 59, np.inf]
AGE_LABELS = ["19-39", "40-49", "50-59", "60+"]


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def load_raw_diabetes():
    """Return the original (un-scaled) diabetes data as a DataFrame.

    Columns: the ten baseline variables followed by ``progression``
    (a quantitative measure of disease progression one year after baseline).
    """
    bunch = load_diabetes(as_frame=True, scaled=False)
    df = bunch.frame.rename(columns={"target": TARGET})
    return df[BASE_FEATURES + [TARGET]].copy()


def save_raw_csv(df, path=RAW_CSV):
    """Write the raw data to CSV (creating the folder) and return the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def load_csv(path=RAW_CSV, required_columns=None):
    """Load a CSV with basic validation (missing file, empty file, columns)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"CSV file has no data rows: {path}")
    missing = [c for c in (required_columns or []) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


# ----------------------------------------------------------------------------
# Data quality
# ----------------------------------------------------------------------------
def quality_report(df):
    """Summarise the main data-quality facts of a table."""
    if df.empty:
        raise ValueError("Cannot assess an empty DataFrame")
    numeric = df.select_dtypes("number")
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "non_numeric_columns": [c for c in df.columns if c not in numeric.columns],
        "infinite_values": int(np.isinf(numeric).sum().sum()),
        "negative_values": int((numeric < 0).sum().sum()),
    }


def iqr_outlier_counts(df, columns, k=1.5):
    """Count values outside [Q1 - k*IQR, Q3 + k*IQR] for each column."""
    rows = []
    for col in columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - k * iqr, q3 + k * iqr
        mask = (df[col] < low) | (df[col] > high)
        rows.append({"column": col, "lower_fence": low, "upper_fence": high,
                     "outliers": int(mask.sum()), "share_%": 100 * mask.mean()})
    return pd.DataFrame(rows).set_index("column")


def vif_table(df, columns):
    """Variance inflation factor of each column (regressed on the others).

    VIF_j = 1 / (1 - R^2_j). Values above about 5-10 signal strong
    multicollinearity. Implemented with NumPy so no extra package is needed.
    """
    X = df[columns].to_numpy(dtype=float)
    X = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
    out = {}
    for j, col in enumerate(columns):
        others = np.delete(X, j, axis=1)
        design = np.column_stack([np.ones(len(X)), others])
        beta, *_ = np.linalg.lstsq(design, X[:, j], rcond=None)
        resid = X[:, j] - design @ beta
        r2 = 1 - resid.var() / X[:, j].var()
        out[col] = 1 / (1 - r2)
    return pd.Series(out, name="VIF")


# ----------------------------------------------------------------------------
# Feature engineering
# ----------------------------------------------------------------------------
def add_engineered_features(df):
    """Return a copy of ``df`` with the engineered columns added.

    * sex_2          1 if the sex code is 2, else 0 (binary version of ``sex``)
    * bmi_category   WHO-based BMI class: under 25, 25 to 29.9, 30 and over
    * age_group      19-39, 40-49, 50-59, 60+
    * ldl_hdl_ratio  s2 / s3, a common lipid-balance ratio
    """
    out = df.copy()
    out["sex_2"] = (out["sex"] == 2).astype(int)
    out["bmi_category"] = pd.cut(out["bmi"], bins=BMI_BINS, labels=BMI_LABELS, right=False)
    out["age_group"] = pd.cut(out["age"], bins=AGE_BINS, labels=AGE_LABELS)
    out["ldl_hdl_ratio"] = out["s2"] / out["s3"]
    return out


def make_preprocessor(numeric, categorical=(), scale=True):
    """ColumnTransformer: impute + scale numeric columns, impute + one-hot categoricals.

    The dataset has no missing values, so the imputers do nothing on the
    training data; they only make the pipeline safe for new, incomplete input.
    It is always placed inside a Pipeline, so every step is fitted on training
    data only (this prevents data leakage during cross-validation and testing).
    """
    num_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    parts = [("num", Pipeline(num_steps), list(numeric))]
    if categorical:
        cat_steps = [("impute", SimpleImputer(strategy="most_frequent")),
                     ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first",
                                              sparse_output=False))]
        parts.append(("cat", Pipeline(cat_steps), list(categorical)))
    return ColumnTransformer(parts)


def make_pipeline(model, numeric, categorical=(), scale=True):
    """Preprocessor + model in one scikit-learn Pipeline."""
    return Pipeline([("prep", make_preprocessor(numeric, categorical, scale)),
                     ("model", model)])


# ----------------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------------
def regression_metrics(y_true, y_pred):
    """MAE, MSE, RMSE and R^2 in one dictionary."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    if y_true.shape != y_pred.shape or y_true.size == 0:
        raise ValueError("y_true and y_pred must be non-empty and the same length")
    mse = mean_squared_error(y_true, y_pred)
    return {"MAE": mean_absolute_error(y_true, y_pred), "MSE": mse,
            "RMSE": float(np.sqrt(mse)), "R2": r2_score(y_true, y_pred)}


def bootstrap_metric_ci(y_true, y_pred, n_boot=2000, seed=RANDOM_STATE, level=95):
    """Percentile bootstrap confidence intervals for RMSE, MAE and R^2."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    rng = np.random.default_rng(seed)
    n = len(y_true)
    draws = {"RMSE": [], "MAE": [], "R2": []}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        m = regression_metrics(y_true[idx], y_pred[idx])
        for k in draws:
            draws[k].append(m[k])
    lo, hi = (100 - level) / 2, 100 - (100 - level) / 2
    return {k: (float(np.percentile(v, lo)), float(np.percentile(v, hi)))
            for k, v in draws.items()}


def ols_summary(X, y, names):
    """Ordinary-least-squares coefficients with standard errors, t and p values.

    X is a 2-D array without the intercept column. Returned as a DataFrame
    (the intercept is the first row). Classical OLS assumptions apply.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    design = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    dof = len(y) - design.shape[1]
    sigma2 = resid @ resid / dof
    cov = sigma2 * np.linalg.inv(design.T @ design)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    return pd.DataFrame({"coef": beta, "std_err": se, "t": t, "p_value": p},
                        index=["intercept"] + list(names))


def segment_summary(df, by, target=TARGET):
    """Mean/median of the target, size and difference from the overall mean."""
    overall = df[target].mean()
    g = df.groupby(by, observed=True)[target].agg(["count", "mean", "median"])
    g["diff_vs_overall"] = g["mean"] - overall
    return g


def save_figure(fig, filename, folder=FIGURE_DIR, dpi=150):
    """Save a Matplotlib figure as PNG (creating the folder) and return the path."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
