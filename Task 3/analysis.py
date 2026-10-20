"""
analysis.py - Real-World Dataset Analysis Project
=================================================
Complete, reusable analysis pipeline for the Global Superstore Sales dataset
(or any dataset with the same kind of columns).

What this file contains
-----------------------
  PART A  Helpers: find / read the data file, standardise column names, schema check,
          date-format detection, data-quality assessment, and the cleaning steps.
  PART B  Analysis: KPIs, grouped tables, trends, customers, products, discounts,
          correlations, statistical tests, and automatic business insights.
  PART C  Charts, saving outputs, and the command-line entry point.

Run the whole project from the command line (from the project folder):
    python src/analysis.py                      # finds the file inside the data/ folder
    python src/analysis.py --data "C:/path/to/Global_Superstore2.csv"

The Jupyter notebook (real_world_dataset_analysis.ipynb) imports the functions from here.
Nothing in this file contains made-up results: every number is calculated from the data file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

if __name__ == "__main__":          # when run as a script, draw charts into files (no pop-up window)
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ----------------------------------------------------------------------------
# Settings (you can change these)
# ----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# File names we look for inside data/ (the first one found is used)
CANDIDATE_FILES = ["Global_Superstore2.csv", "Global_Superstore2.xlsx", "Global_Superstore.csv",
                   "Global_Superstore.xlsx", "Superstore.csv", "superstore.csv"]
# The Global Superstore CSV is not UTF-8; a published notebook reads it with 'latin2'.
# Encoding only affects accented letters in names, never the numbers.
ENCODINGS = ["utf-8", "latin2", "latin-1"]

# Columns the analysis cannot work without (names after standardisation)
REQUIRED_COLUMNS = ["order_id", "order_date", "sales", "quantity", "discount", "profit"]
# Columns of the documented 24-column Global Superstore layout
EXPECTED_COLUMNS = [
    "row_id", "order_id", "order_date", "ship_date", "ship_mode", "customer_id", "customer_name",
    "segment", "city", "state", "country", "postal_code", "market", "region", "product_id",
    "category", "sub_category", "product_name", "sales", "quantity", "discount", "profit",
    "shipping_cost", "order_priority",
]
DATE_FORMATS = ["%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%b-%Y", "%Y/%m/%d"]
NUMERIC_COLUMNS = ["sales", "quantity", "discount", "profit", "shipping_cost"]
HIGH_MISSING_THRESHOLD = 0.05      # columns with more than 5% missing are not imputed

DISCOUNT_BINS = [-0.001, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0]
DISCOUNT_LABELS = ["0%", "1-10%", "11-20%", "21-30%", "31-50%", "Above 50%"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ============================================================================
# PART A - LOADING, CHECKING AND CLEANING
# ============================================================================
def normalise_name(name: str) -> str:
    """'Sub-Category' -> 'sub_category', 'Row ID' -> 'row_id', ' Order Date ' -> 'order_date'."""
    return re.sub(r"[^0-9a-zA-Z]+", "_", str(name).strip()).strip("_").lower()


def find_data_file(data_path=None) -> Path:
    """Return the path of the dataset file.

    Order: 1) the path you pass in, 2) a known file name inside data/, 3) any csv/xlsx in data/.
    If nothing is found, a clear error explains how to download the dataset.
    """
    if data_path:
        path = Path(data_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"The file you gave does not exist: {path}")
        return path
    for name in CANDIDATE_FILES:
        if (DATA_DIR / name).exists():
            return DATA_DIR / name
    others = sorted(p for p in DATA_DIR.glob("*") if p.suffix.lower() in {".csv", ".xlsx", ".xls"})
    if others:
        return others[0]
    raise FileNotFoundError(
        "No dataset file found in the 'data' folder.\n"
        "Download 'Global_Superstore2.csv' from Kaggle (dataset: apoorvaappz/global-super-store-dataset)\n"
        f"and save it inside: {DATA_DIR}\n"
        "Or pass the full path:  python src/analysis.py --data \"C:/path/to/file.csv\""
    )


def read_dataset(path):
    """Read a CSV or Excel file. Returns (DataFrame, info_dict). The file itself is never changed."""
    path = Path(path)
    info = {"file": path.name, "size_mb": round(path.stat().st_size / 1e6, 2)}
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
        info["encoding"] = "n/a (Excel)"
        return df, info
    last_error = None
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            info["encoding"] = enc
            return df, info
        except UnicodeDecodeError as err:
            last_error = err
    raise ValueError(f"Could not read {path.name} with encodings {ENCODINGS}: {last_error}")


def standardise_columns(df: pd.DataFrame):
    """Rename columns to lowercase_with_underscores. Returns (new_df, mapping original->new)."""
    mapping = {c: normalise_name(c) for c in df.columns}
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("Two columns have the same name after standardisation: " + str(mapping))
    return df.rename(columns=mapping), mapping


def check_schema(df: pd.DataFrame) -> dict:
    """Compare the columns with what the analysis expects. Stops only if essential columns are missing."""
    cols = set(df.columns)
    report = {
        "missing_required": [c for c in REQUIRED_COLUMNS if c not in cols],
        "missing_optional": [c for c in EXPECTED_COLUMNS if c not in cols and c not in REQUIRED_COLUMNS],
        "extra_columns": [c for c in df.columns if c not in EXPECTED_COLUMNS],
    }
    if report["missing_required"]:
        raise KeyError(
            "These essential columns were not found: " + ", ".join(report["missing_required"]) +
            "\nColumns present: " + ", ".join(df.columns) +
            "\nTip: rename your columns or edit REQUIRED_COLUMNS at the top of src/analysis.py."
        )
    return report


def detect_date_format(series: pd.Series):
    """Find the date format that parses the most values. Returns (parsed_series, format_used, n_failed)."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series, "already datetime", int(series.isna().sum())
    text = series.astype("string").str.strip()
    text = text.str.replace(r"\s+00:00:00$", "", regex=True)      # Excel may keep a time part
    best_fmt, best_parsed, best_ok = None, None, -1
    for fmt in DATE_FORMATS:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        ok = int(parsed.notna().sum())
        if ok > best_ok:
            best_fmt, best_parsed, best_ok = fmt, parsed, ok
    return best_parsed, best_fmt, int(len(series) - best_ok)


def assess_quality(df: pd.DataFrame) -> dict:
    """Data-quality report on a DataFrame (does not change the data)."""
    n = len(df)
    missing = pd.DataFrame({"missing_count": df.isna().sum(), "missing_pct": (df.isna().mean() * 100).round(2)})
    q = {
        "rows": n, "columns": df.shape[1],
        "missing": missing[missing.missing_count > 0].sort_values("missing_count", ascending=False),
        "exact_duplicates": int(df.duplicated().sum()),
        "duplicates_ignoring_row_id": int(df.drop(columns=[c for c in ["row_id"] if c in df.columns]).duplicated().sum()),
        "row_id_unique": bool(df["row_id"].is_unique) if "row_id" in df.columns else None,
    }
    num = {c: pd.to_numeric(df[c], errors="coerce") for c in NUMERIC_COLUMNS if c in df.columns}
    invalid = {}
    if "sales" in num: invalid["sales < 0"] = int((num["sales"] < 0).sum())
    if "quantity" in num: invalid["quantity <= 0"] = int((num["quantity"] <= 0).sum())
    if "discount" in num:
        invalid["discount < 0"] = int((num["discount"] < 0).sum())
        invalid["discount > 1 (maybe stored as percent)"] = int((num["discount"] > 1).sum())
    if "shipping_cost" in num: invalid["shipping_cost < 0"] = int((num["shipping_cost"] < 0).sum())
    if "sales" in num and "profit" in num: invalid["profit > sales"] = int((num["profit"] > num["sales"]).sum())
    if {"order_date", "ship_date"} <= set(df.columns):
        od, _, _ = detect_date_format(df["order_date"]); sd, _, _ = detect_date_format(df["ship_date"])
        invalid["ship_date before order_date"] = int((sd < od).sum())
    q["invalid_values"] = pd.Series(invalid, name="rows", dtype="int64")
    return q


def iqr_bounds(series: pd.Series, k: float = 1.5):
    """IQR rule: values below Q1 - k*IQR or above Q3 + k*IQR are potential outliers."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


@dataclass
class AuditLog:
    """Records every cleaning step so nothing changes silently."""
    steps: list = field(default_factory=list)
    notes: dict = field(default_factory=dict)

    def add(self, step, description, rows_before, rows_after, affected=0, details=""):
        self.steps.append({"step": step, "description": description, "rows_before": rows_before,
                           "rows_after": rows_after, "rows_removed": rows_before - rows_after,
                           "affected": affected, "details": details})

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.steps)


def step_strip_text(df, log):
    """Step 1: remove leading/trailing spaces from text columns; empty text becomes missing."""
    df = df.copy(); n = len(df); changed = 0
    for c in df.select_dtypes(include=["object", "string"]).columns:
        before = df[c].astype("string")
        cleaned = before.str.strip().replace("", pd.NA)
        changed += int(((before != cleaned) & ~(before.isna() & cleaned.isna())).fillna(False).sum())
        df[c] = cleaned.astype(object)
    log.add(1, "Strip spaces from text columns; empty text -> missing", n, len(df), changed)
    return df


def step_convert_types(df, log):
    """Step 2: convert dates to datetime and numeric columns to numbers; check the discount scale."""
    df = df.copy(); n = len(df); notes = []
    for c in [c for c in ["order_date", "ship_date"] if c in df.columns]:
        parsed, fmt, failed = detect_date_format(df[c])
        df[c] = parsed
        notes.append(f"{c}: format {fmt}, unparseable={failed}")
        log.notes[f"{c}_format"] = fmt
    for c in [c for c in NUMERIC_COLUMNS if c in df.columns]:
        before_na = int(df[c].isna().sum())
        df[c] = pd.to_numeric(df[c], errors="coerce")
        new_na = int(df[c].isna().sum()) - before_na
        if new_na:
            notes.append(f"{c}: {new_na} values were not numeric -> missing")
    if "discount" in df.columns and df["discount"].max() > 1.0 and df["discount"].max() <= 100:
        df["discount"] = df["discount"] / 100.0
        notes.append("discount looked like percent (0-100) -> divided by 100")
    for c in [c for c in ["postal_code", "row_id"] if c in df.columns]:
        s = df[c].astype("string").str.replace(r"\.0$", "", regex=True)
        df[c] = s.astype(object)
    log.add(2, "Convert data types (dates, numbers); check discount scale", n, len(df), len(notes), "; ".join(notes))
    return df


def step_handle_missing(df, log):
    """Step 3: required columns -> drop rows; <5% missing -> fill; >=5% missing -> keep but do not use."""
    df = df.copy(); n = len(df); notes = []
    required = [c for c in REQUIRED_COLUMNS if c in df.columns]
    drop_mask = df[required].isna().any(axis=1)
    if drop_mask.any():
        notes.append(f"dropped {int(drop_mask.sum())} rows missing a required value ({', '.join(required)})")
        df = df.loc[~drop_mask]
    high = []
    for c in df.columns:
        miss = df[c].isna().mean()
        if miss == 0 or c in required:
            continue
        if miss >= HIGH_MISSING_THRESHOLD:
            high.append(f"{c} ({miss:.1%})")
        elif pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].fillna(df[c].median()); notes.append(f"{c}: filled {miss:.2%} with the median")
        elif not pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].fillna("Unknown"); notes.append(f"{c}: filled {miss:.2%} with 'Unknown'")
    if high:
        notes.append("kept but NOT used in the analysis (too many missing): " + ", ".join(high))
    log.notes["high_missing_columns"] = [h.split(" ")[0] for h in high]
    log.add(3, "Handle missing values", n, len(df), n - len(df), "; ".join(notes) or "no missing values in used columns")
    return df


def step_remove_duplicates(df, log):
    """Step 4: remove rows that are identical in EVERY column (true duplicates)."""
    n = len(df)
    possible = int(df.drop(columns=[c for c in ["row_id"] if c in df.columns]).duplicated().sum())
    df = df.drop_duplicates()
    log.add(4, "Remove exact duplicate rows", n, len(df), n - len(df),
            f"rows identical except Row ID (only reported, not removed): {possible}")
    return df


def step_remove_invalid(df, log):
    """Step 5: remove impossible records (negative sales, zero quantity, bad discount, ship before order)."""
    n = len(df)
    rules = {"sales < 0": df["sales"] < 0, "quantity <= 0": df["quantity"] <= 0,
             "discount < 0 or > 1": ~df["discount"].between(0, 1)}
    if "shipping_cost" in df.columns:
        rules["shipping_cost < 0"] = df["shipping_cost"] < 0
    if "ship_date" in df.columns:
        rules["ship_date before order_date"] = df["ship_date"] < df["order_date"]
    counts = {k: int(v.sum()) for k, v in rules.items()}
    bad = np.zeros(len(df), dtype=bool)
    for v in rules.values():
        bad |= v.fillna(False).to_numpy()
    df = df.loc[~bad]
    log.add(5, "Remove impossible values", n, len(df), int(bad.sum()), ", ".join(f"{k}: {v}" for k, v in counts.items()))
    return df


def step_add_features(df, log):
    """Step 6: new columns used in the analysis."""
    df = df.copy(); n = len(df)
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_quarter"] = df["order_date"].dt.quarter
    df["order_ym"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    if "ship_date" in df.columns:
        df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["profit_margin"] = np.where(df["sales"] > 0, df["profit"] / df["sales"], np.nan)
    df["discount_band"] = pd.cut(df["discount"], bins=DISCOUNT_BINS, labels=DISCOUNT_LABELS)
    df["is_loss"] = df["profit"] < 0
    log.add(6, "Create new columns", n, len(df), 0,
            "order_year, order_month, order_quarter, order_ym, shipping_days, profit_margin, discount_band, is_loss")
    return df


def step_flag_outliers(df, log):
    """Step 7: flag (do not remove) statistical outliers with the IQR rule and record them."""
    df = df.copy(); n = len(df); notes = []
    for c in [c for c in ["sales", "profit", "quantity", "shipping_cost"] if c in df.columns]:
        lo, hi = iqr_bounds(df[c])
        flag = (df[c] < lo) | (df[c] > hi)
        df[f"outlier_{c}"] = flag
        notes.append(f"{c}: {int(flag.sum())} rows ({flag.mean():.1%}) outside [{lo:,.1f}, {hi:,.1f}]")
    log.add(7, "Flag outliers (IQR rule) - kept in data", n, len(df), 0, "; ".join(notes))
    return df


def clean_data(df_std: pd.DataFrame):
    """Run all cleaning steps in order. The input DataFrame is never modified.
    Returns (clean_dataframe, AuditLog)."""
    log = AuditLog()
    df = df_std.copy()
    for step in (step_strip_text, step_convert_types, step_handle_missing, step_remove_duplicates,
                 step_remove_invalid, step_add_features, step_flag_outliers):
        df = step(df, log)
    return df.reset_index(drop=True), log


# ============================================================================
# PART B - ANALYSIS (EDA, statistics, insights)
# ============================================================================
def human(x, pos=None) -> str:
    """12345678 -> '12.3M', 45000 -> '45K'. Used for chart axis labels."""
    ax = abs(x)
    if ax >= 1e6:
        return f"{x / 1e6:.1f}M"
    if ax >= 1e3:
        return f"{x / 1e3:.0f}K"
    return f"{x:.0f}"


def n0(x) -> str:
    """Format a number with thousands separators and no decimals."""
    return f"{x:,.0f}"


def agg_table(df: pd.DataFrame, by, sort_by: str = "sales") -> pd.DataFrame:
    """Sales, profit, margin and loss statistics for each group in `by` (a column or list of columns)."""
    t = df.groupby(by, observed=True).agg(
        sales=("sales", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum"),
        lines=("order_id", "size"), orders=("order_id", "nunique"),
        avg_discount=("discount", "mean"), loss_lines=("is_loss", "sum"))
    t["profit_margin_pct"] = np.where(t["sales"] > 0, t["profit"] / t["sales"] * 100, np.nan)
    t["loss_line_pct"] = t["loss_lines"] / t["lines"] * 100
    return t.sort_values(sort_by, ascending=False)


def compute_results(df: pd.DataFrame) -> dict:
    """Calculate every table, KPI and statistic used in the notebook, charts and report."""
    has = lambda *cols: all(c in df.columns for c in cols)
    T, K, S = {}, {}, {}

    # ---- KPIs ----
    order_totals = df.groupby("order_id")["sales"].sum()
    K.update(
        date_min=str(df["order_date"].min().date()), date_max=str(df["order_date"].max().date()),
        n_lines=int(len(df)), n_orders=int(df["order_id"].nunique()),
        total_sales=float(df["sales"].sum()), total_profit=float(df["profit"].sum()),
        avg_order_value=float(order_totals.mean()), median_order_value=float(order_totals.median()),
        total_quantity=int(df["quantity"].sum()), avg_discount_pct=float(df["discount"].mean() * 100),
        share_discounted_lines_pct=float((df["discount"] > 0).mean() * 100),
        loss_lines=int(df["is_loss"].sum()), loss_line_pct=float(df["is_loss"].mean() * 100),
        total_loss_amount=float(df.loc[df["profit"] < 0, "profit"].sum()),
    )
    K["profit_margin_pct"] = K["total_profit"] / K["total_sales"] * 100
    if has("customer_id"):
        K["n_customers"] = int(df["customer_id"].nunique())
    if has("shipping_cost"):
        K["avg_shipping_cost"] = float(df["shipping_cost"].mean())
        K["shipping_cost_pct_of_sales"] = float(df["shipping_cost"].sum() / df["sales"].sum() * 100)
    if has("shipping_days"):
        K["avg_shipping_days"] = float(df["shipping_days"].mean())

    # ---- grouped tables ----
    for col in ["category", "market", "region", "segment", "ship_mode", "order_priority"]:
        if has(col):
            T[col] = agg_table(df, col)
    if has("category", "sub_category"):
        T["sub_category"] = agg_table(df, ["category", "sub_category"], sort_by="profit")
    if has("country"):
        T["country"] = agg_table(df, "country").head(15)
    year = agg_table(df, "order_year", sort_by="order_year").sort_index() if False else agg_table(df, "order_year").sort_index()
    year["sales_growth_pct"] = year["sales"].pct_change() * 100
    year["profit_growth_pct"] = year["profit"].pct_change() * 100
    T["year"] = year

    # ---- time trends ----
    monthly = df.groupby("order_ym").agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
    monthly["sales_12m_avg"] = monthly["sales"].rolling(12).mean()
    monthly["z_score_sales"] = (monthly["sales"] - monthly["sales"].mean()) / monthly["sales"].std()
    T["monthly"] = monthly
    ym = df.groupby(["order_year", "order_month"])[["sales", "profit"]].sum()
    T["seasonality"] = ym.groupby(level=1).mean().rename(index=lambda m: MONTH_NAMES[m - 1])
    T["sales_year_month"] = df.pivot_table(index="order_year", columns="order_month", values="sales", aggfunc="sum")

    # ---- products ----
    if has("product_name"):
        prod = df.groupby("product_name").agg(sales=("sales", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum"))
        T["products_top_profit"] = prod.sort_values("profit", ascending=False).head(10)
        T["products_bottom_profit"] = prod.sort_values("profit").head(10)
        T["products_top_sales"] = prod.sort_values("sales", ascending=False).head(10)
        K["n_products"] = int(len(prod))
        K["n_loss_products"] = int((prod["profit"] < 0).sum())
        K["loss_products_amount"] = float(prod.loc[prod["profit"] < 0, "profit"].sum())
        K["top10_products_profit_share_pct"] = float(T["products_top_profit"]["profit"].sum() / K["total_profit"] * 100)

    # ---- customers ----
    if has("customer_id"):
        cust = df.groupby("customer_id").agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        if has("customer_name"):
            cust["customer_name"] = df.groupby("customer_id")["customer_name"].first()
        T["customers_top"] = cust.sort_values("sales", ascending=False).head(10)
        K["repeat_customer_pct"] = float((cust["orders"] >= 2).mean() * 100)
        K["avg_orders_per_customer"] = float(cust["orders"].mean())
        K["top10_customers_sales_share_pct"] = float(T["customers_top"]["sales"].sum() / K["total_sales"] * 100)
        if has("segment"):
            seg = T["segment"].copy()
            seg["avg_order_value"] = seg["sales"] / seg["orders"]
            T["segment"] = seg

    # ---- discount vs profit ----
    band = df.groupby("discount_band", observed=True).agg(
        lines=("order_id", "size"), sales=("sales", "sum"), profit=("profit", "sum"),
        median_margin=("profit_margin", "median"), loss_lines=("is_loss", "sum"))
    band["profit_margin_pct"] = band["profit"] / band["sales"] * 100
    band["loss_line_pct"] = band["loss_lines"] / band["lines"] * 100
    T["discount_band"] = band

    # ---- correlations ----
    corr_cols = [c for c in ["sales", "quantity", "discount", "profit", "shipping_cost", "shipping_days", "profit_margin"] if c in df.columns]
    T["corr_pearson"] = df[corr_cols].corr(method="pearson")
    T["corr_spearman"] = df[corr_cols].corr(method="spearman")
    desc = df[corr_cols].describe().T
    desc["skew"] = df[corr_cols].skew()
    desc["kurtosis"] = df[corr_cols].kurt()
    T["describe"] = desc

    # ---- statistical tests (SciPy) ----
    valid = df[["discount", "profit_margin", "profit"]].dropna()
    if valid["discount"].nunique() > 1:
        rho, p = stats.spearmanr(valid["discount"], valid["profit_margin"])
        S["spearman_discount_margin"] = {"rho": float(rho), "p_value": float(p), "n": int(len(valid))}
        rho2, p2 = stats.spearmanr(valid["discount"], valid["profit"])
        S["spearman_discount_profit"] = {"rho": float(rho2), "p_value": float(p2), "n": int(len(valid))}
    groups = [g["profit_margin"].dropna().to_numpy() for _, g in df.groupby("discount_band", observed=True) if g["profit_margin"].notna().sum() >= 30]
    if len(groups) >= 2:
        h, p = stats.kruskal(*groups)
        S["kruskal_margin_by_discount_band"] = {"H": float(h), "p_value": float(p), "groups": len(groups)}
    no_disc = df.loc[df["discount"] == 0, "profit_margin"].dropna()
    disc = df.loc[df["discount"] > 0, "profit_margin"].dropna()
    if len(no_disc) >= 30 and len(disc) >= 30:
        u, p = stats.mannwhitneyu(no_disc, disc, alternative="two-sided")
        S["mannwhitney_discount_vs_none"] = {"U": float(u), "p_value": float(p), "median_margin_no_discount": float(no_disc.median()),
                                             "median_margin_discounted": float(disc.median())}
    out = {}
    if "outlier_profit" in df.columns:
        flagged = df["outlier_profit"]
        out["profit_outlier_lines"] = int(flagged.sum())
        out["profit_outlier_share_of_total_profit_pct"] = float(df.loc[flagged, "profit"].sum() / K["total_profit"] * 100)
        out["total_profit_without_profit_outliers"] = float(df.loc[~flagged, "profit"].sum())
    if "outlier_sales" in df.columns:
        flagged = df["outlier_sales"]
        out["sales_outlier_lines"] = int(flagged.sum())
        out["sales_outlier_share_of_total_sales_pct"] = float(df.loc[flagged, "sales"].sum() / K["total_sales"] * 100)
    S["outlier_sensitivity"] = out
    return {"kpis": K, "tables": T, "stats": S}


def build_insights(R: dict) -> list:
    """Turn the calculated results into findings. Each finding has an observation, numerical
    evidence, business significance and a practical recommendation. All numbers come from R."""
    K, T, S = R["kpis"], R["tables"], R["stats"]
    out = []

    def add(title, observation, evidence, significance, recommendation):
        out.append({"title": title, "observation": observation, "evidence": evidence,
                    "significance": significance, "recommendation": recommendation})

    # 1. overall
    add("Overall business performance",
        f"From {K['date_min']} to {K['date_max']} the business recorded {n0(K['n_orders'])} orders ({n0(K['n_lines'])} order lines) "
        f"with total sales of {n0(K['total_sales'])} and total profit of {n0(K['total_profit'])}.",
        f"Profit margin = {K['profit_margin_pct']:.1f}%; average order value = {n0(K['avg_order_value'])} "
        f"(median {n0(K['median_order_value'])}); average discount = {K['avg_discount_pct']:.1f}%.",
        "The overall margin is the benchmark against which every category, market and discount level should be judged.",
        "Track this margin monthly and investigate any segment that stays well below it.")

    # 2. category
    if "category" in T:
        c = T["category"]; top_s, top_p = c["sales"].idxmax(), c["profit"].idxmax()
        low_m = c["profit_margin_pct"].idxmin()
        rows = "; ".join(f"{i}: sales {n0(r.sales)}, profit {n0(r.profit)} ({r.profit_margin_pct:.1f}%)" for i, r in c.iterrows())
        same = "The same category leads in both sales and profit." if top_s == top_p else \
            f"The sales leader ({top_s}) is not the profit leader ({top_p}), so high sales do not automatically mean high profit."
        add("Category performance", f"{top_s} has the highest sales and {top_p} has the highest profit. {same}", rows,
            f"{low_m} has the lowest profit margin ({c.loc[low_m, 'profit_margin_pct']:.1f}%), so each unit of sales there contributes least to profit.",
            f"Give priority to {top_p} in stocking and promotion, and review pricing and costs in {low_m}.")

    # 3. sub-category
    if "sub_category" in T:
        sc = T["sub_category"].reset_index().sort_values("profit", ascending=False)
        best = sc.head(3); worst = sc.tail(3).iloc[::-1]
        loss = sc[sc["profit"] < 0]
        ev = ("Top 3 by profit: " + "; ".join(f"{r.sub_category} {n0(r.profit)}" for r in best.itertuples()) +
              ". Bottom 3: " + "; ".join(f"{r.sub_category} {n0(r.profit)}" for r in worst.itertuples()) + ".")
        if len(loss):
            obs = f"{len(loss)} sub-categories lose money overall: " + ", ".join(loss["sub_category"]) + "."
            rec = "Review prices, discounts and supplier costs for the loss-making sub-categories before the next season; consider dropping the worst performers."
            sig = f"Together they lose {n0(-loss['profit'].sum())}, reducing the profit earned by the others."
        else:
            obs = "No sub-category has a negative total profit."
            rec = f"Focus improvement efforts on the lowest-profit sub-categories ({', '.join(worst['sub_category'])})."
            sig = "All sub-categories contribute positively, but their contributions differ greatly."
        add("Sub-category profitability and loss-making sub-categories", obs, ev, sig, rec)

    # 4. market / region
    geo = "market" if "market" in T else ("region" if "region" in T else None)
    if geo:
        g = T[geo]; ts, tp, lm = g["sales"].idxmax(), g["profit"].idxmax(), g["profit_margin_pct"].idxmin()
        ev = "; ".join(f"{i}: sales {n0(r.sales)}, profit {n0(r.profit)} ({r.profit_margin_pct:.1f}%)" for i, r in g.iterrows())
        add(f"Performance by {geo}", f"{ts} has the highest sales and {tp} has the highest profit; {lm} has the lowest profit margin.", ev,
            f"{lm} converts sales into profit least efficiently ({g.loc[lm, 'profit_margin_pct']:.1f}%).",
            f"Protect and grow {tp}; investigate costs, discounts and shipping in {lm}.")

    # 5. time
    m = T["monthly"]; y = T["year"]; best_m, worst_m = m["sales"].idxmax(), m["sales"].idxmin()
    unusual = m[m["z_score_sales"].abs() >= 2]
    seas = T["seasonality"]["sales"].sort_values(ascending=False)
    yr_txt = "; ".join(f"{int(i)}: {n0(r.sales)}" + (f" ({r.sales_growth_pct:+.1f}%)" if pd.notna(r.sales_growth_pct) else "") for i, r in y.iterrows())
    unusual_txt = ("Unusual months (|z| >= 2): " + ", ".join(f"{d:%b %Y} ({v:+.1f} sd)" for d, v in unusual["z_score_sales"].items())
                   if len(unusual) else "No month is unusual by the |z| >= 2 rule.")
    add("Sales trend and seasonality",
        f"Yearly sales: {yr_txt}. The strongest month was {best_m:%b %Y} ({n0(m.loc[best_m, 'sales'])}) and the weakest was {worst_m:%b %Y} ({n0(m.loc[worst_m, 'sales'])}).",
        f"On average the best calendar months are {seas.index[0]} and {seas.index[1]}, the weakest are {seas.index[-1]} and {seas.index[-2]}. {unusual_txt}",
        "Demand is not flat through the year, so stock, staffing and marketing should follow the seasonal pattern.",
        f"Plan inventory and campaigns ahead of {seas.index[0]} and {seas.index[1]}, and investigate any unusual month before drawing conclusions.")

    # 6. products
    if "products_top_profit" in T:
        worst = T["products_bottom_profit"].iloc[0]
        add("Top and loss-making products",
            f"{n0(K['n_loss_products'])} of {n0(K['n_products'])} products ({K['n_loss_products'] / K['n_products'] * 100:.1f}%) have a negative total profit; "
            + (f"the 10 most profitable products produce {K['top10_products_profit_share_pct']:.1f}% of total profit." if K["total_profit"] > 0
             else "total profit is not positive, so a profit share is not meaningful."),
            f"Most profitable product: {T['products_top_profit'].index[0]} ({n0(T['products_top_profit'].iloc[0]['profit'])}). "
            f"Biggest loss: {T['products_bottom_profit'].index[0]} ({n0(worst['profit'])}). Total loss on loss-making products: {n0(-K['loss_products_amount'])}.",
            "Profit is concentrated in a small group of products while a long tail of products destroys value.",
            "Reprice, bundle or discontinue the worst loss-makers and make sure the best sellers never go out of stock.")

    # 7. customers
    if "repeat_customer_pct" in K:
        seg_txt = ""
        if "segment" in T:
            sg = T["segment"]
            seg_txt = " Segments: " + "; ".join(f"{i}: sales {n0(r.sales)}, margin {r.profit_margin_pct:.1f}%, avg order {n0(r.avg_order_value)}" for i, r in sg.iterrows()) + "."
        add("Customer purchasing patterns",
            f"{K['repeat_customer_pct']:.1f}% of the {n0(K['n_customers'])} customers ordered more than once (average {K['avg_orders_per_customer']:.1f} orders per customer).",
            f"The 10 biggest customers account for {K['top10_customers_sales_share_pct']:.1f}% of sales.{seg_txt}",
            "Repeat buyers and the largest customers drive a large part of revenue, so retaining them is cheaper than finding new ones.",
            "Introduce loyalty offers for repeat customers and focus acquisition on the segment with the best margin.")

    # 8. discount
    d = T["discount_band"]; sp = S.get("spearman_discount_margin"); mw = S.get("mannwhitney_discount_vs_none")
    first, last = d.index[0], d.index[-1]
    high = d.loc[[b for b in d.index if b in ("31-50%", "Above 50%")]] if len(d) else d
    high_loss = (high["loss_lines"].sum() / high["lines"].sum() * 100) if len(high) and high["lines"].sum() else float("nan")
    ev = "Profit margin by discount band: " + "; ".join(f"{i}: {r.profit_margin_pct:.1f}% (loss-making lines {r.loss_line_pct:.0f}%)" for i, r in d.iterrows()) + "."
    if sp:
        ev += f" Spearman correlation between discount and profit margin: rho = {sp['rho']:.2f} (p = {sp['p_value']:.2g}, n = {sp['n']:,})."
    if mw:
        ev += f" Median margin: {mw['median_margin_no_discount'] * 100:.1f}% without discount vs {mw['median_margin_discounted'] * 100:.1f}% with discount."
    add("Discount versus profitability",
        f"Profitability changes with the discount level: the margin is {d.loc[first, 'profit_margin_pct']:.1f}% for the '{first}' band and "
        f"{d.loc[last, 'profit_margin_pct']:.1f}% for the '{last}' band" + (f"; {high_loss:.0f}% of lines with discounts above 30% lose money." if high_loss == high_loss else "."),
        ev,
        "Deep discounts are associated with lower or negative margins. This is an association in observed data; it does not prove that discounts alone cause the losses "
        "(product mix and costs also differ).",
        "Set a discount ceiling for low-margin products, and run a controlled test before changing the policy.")

    # 9. shipping
    if "ship_mode" in T:
        sm = T["ship_mode"]; top = sm["lines"].idxmax()
        ev = "; ".join(f"{i}: {r.lines / sm['lines'].sum() * 100:.0f}% of lines" for i, r in sm.iterrows())
        extra = f" Average delivery time is {K['avg_shipping_days']:.1f} days." if "avg_shipping_days" in K else ""
        extra2 = f" Shipping cost equals {K['shipping_cost_pct_of_sales']:.1f}% of sales." if "shipping_cost_pct_of_sales" in K else ""
        add("Shipping behaviour", f"{top} is the most used ship mode ({sm.loc[top, 'lines'] / sm['lines'].sum() * 100:.0f}% of lines).{extra}{extra2}", ev,
            "Shipping cost reduces the real profit of an order, especially for low-value orders.",
            "Review shipping charges on small orders and check whether faster modes are used where they are needed.")

    # 10. data quality and outliers
    o = S.get("outlier_sensitivity", {})
    if o:
        add("Outliers and their influence",
            f"{n0(o.get('profit_outlier_lines', 0))} order lines are profit outliers (IQR rule) and {n0(o.get('sales_outlier_lines', 0))} are sales outliers.",
            f"Profit outliers add up to {o.get('profit_outlier_share_of_total_profit_pct', float('nan')):.1f}% of total profit (this can exceed 100% when losses offset gains); sales outliers carry "
            f"{o.get('sales_outlier_share_of_total_sales_pct', float('nan')):.1f}% of total sales. Total profit without the profit outliers would be {n0(o.get('total_profit_without_profit_outliers', 0))}.",
            "Outliers are genuine large orders or heavy losses rather than errors, so they were kept; however they have a large influence on totals and averages.",
            "Report medians next to means and review the largest losses individually.")
    return out


# ============================================================================
# PART C - CHARTS, SAVING OUTPUTS, MAIN PROGRAM
# ============================================================================
from matplotlib.ticker import FuncFormatter

AMOUNT_LABEL = "Amount (dataset currency units)"


def set_style() -> None:
    """One consistent, professional look for every chart."""
    sns.set_theme(style="whitegrid", context="notebook", palette="deep")
    plt.rcParams.update({"figure.dpi": 100, "savefig.dpi": 150, "axes.titlesize": 13,
                         "axes.titleweight": "bold", "axes.labelsize": 11, "legend.frameon": True})


def _money_axis(ax, axis="y"):
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(FuncFormatter(human))


def plot_category_bars(ax, tbl: pd.DataFrame, group_label: str):
    """Grouped bars: total sales and total profit for each group."""
    data = tbl[["sales", "profit"]]
    data.plot(kind="bar", ax=ax, rot=0, color=["#4C72B0", "#55A868"], width=0.75)
    for cont in ax.containers:
        ax.bar_label(cont, labels=[human(v) for v in cont.datavalues], padding=2, fontsize=8)
    ax.set_xlabel(group_label); ax.set_ylabel(AMOUNT_LABEL); _money_axis(ax)
    ax.legend(["Sales", "Profit"], title="Measure")
    ax.axhline(0, color="black", linewidth=0.8)


def plot_subcategory_profit(ax, tbl: pd.DataFrame):
    """Horizontal bars of profit per sub-category; losses in red."""
    d = tbl.reset_index().groupby("sub_category")["profit"].sum().sort_values()
    ax.barh(d.index, d.values, color=["#C44E52" if v < 0 else "#55A868" for v in d.values])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Total profit (dataset currency units)"); ax.set_ylabel("Sub-category"); _money_axis(ax, "x")


def plot_margin_heatmap(ax, df: pd.DataFrame, row="market", col="category"):
    """Heatmap: profit margin (%) for every combination of two dimensions."""
    piv = df.pivot_table(index=row, columns=col, values=["sales", "profit"], aggfunc="sum")
    margin = piv["profit"] / piv["sales"] * 100
    sns.heatmap(margin, annot=True, fmt=".1f", cmap="RdYlGn", center=0, linewidths=0.5, ax=ax,
                cbar_kws={"label": "Profit margin (%)"})
    ax.set_xlabel(col.replace("_", " ").title()); ax.set_ylabel(row.replace("_", " ").title())


def plot_distributions(axes, df: pd.DataFrame):
    """Histograms of sales (log scale) and profit (1st-99th percentile)."""
    pos = df.loc[df["sales"] > 0, "sales"]
    axes[0].hist(np.log10(pos), bins=50, color="#4C72B0", edgecolor="white")
    axes[0].set_xlabel("log10(Sales)   (1 = 10, 2 = 100, 3 = 1,000, 4 = 10,000)"); axes[0].set_ylabel("Number of order lines")
    axes[0].set_title("Distribution of Sales per Order Line")
    lo, hi = df["profit"].quantile([0.01, 0.99])
    prof = df.loc[df["profit"].between(lo, hi), "profit"]
    axes[1].hist(prof, bins=50, color="#55A868", edgecolor="white")
    axes[1].axvline(0, color="red", linestyle="--", label="Zero profit")
    axes[1].set_xlabel("Profit per order line (1st-99th percentile shown)"); axes[1].set_ylabel("Number of order lines")
    axes[1].set_title("Distribution of Profit per Order Line"); axes[1].legend()


def plot_monthly_trend(ax, monthly: pd.DataFrame):
    """Line chart: monthly sales and profit with a 12-month moving average of sales."""
    ax.plot(monthly.index, monthly["sales"], marker="o", markersize=3, label="Monthly sales", color="#4C72B0")
    ax.plot(monthly.index, monthly["profit"], marker="o", markersize=3, label="Monthly profit", color="#55A868")
    ax.plot(monthly.index, monthly["sales_12m_avg"], linewidth=2.5, linestyle="--", color="#C44E52", label="12-month average of sales")
    ax.set_xlabel("Month"); ax.set_ylabel(AMOUNT_LABEL); _money_axis(ax); ax.legend()


def plot_yearly_category(ax, df: pd.DataFrame):
    """Line chart: yearly sales for each category."""
    piv = df.pivot_table(index="order_year", columns="category", values="sales", aggfunc="sum")
    piv.plot(ax=ax, marker="o")
    ax.set_xticks(piv.index); ax.set_xlabel("Year"); ax.set_ylabel("Sales (dataset currency units)")
    _money_axis(ax); ax.legend(title="Category")


def plot_discount(axes, df: pd.DataFrame, band: pd.DataFrame):
    """Left: margin by discount band. Right: every order line, discount vs profit margin."""
    axes[0].bar(band.index.astype(str), band["profit_margin_pct"],
                color=["#C44E52" if v < 0 else "#55A868" for v in band["profit_margin_pct"]])
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("Discount band"); axes[0].set_ylabel("Profit margin (%)"); axes[0].set_title("Profit Margin by Discount Band")
    sample = df.dropna(subset=["profit_margin"]).sample(min(6000, len(df)), random_state=1)
    jitter = np.random.default_rng(1).normal(0, 0.004, len(sample))
    axes[1].scatter(sample["discount"] * 100 + jitter * 100, sample["profit_margin"].clip(-2, 1) * 100, s=6, alpha=0.2, color="#4C72B0")
    axes[1].axhline(0, color="red", linestyle="--", linewidth=1, label="Break-even")
    axes[1].set_xlabel("Discount (%)"); axes[1].set_ylabel("Profit margin per line (%, clipped to -200..100)")
    axes[1].set_title("Discount vs Profit Margin (sample of up to 6,000 lines)"); axes[1].legend()


def plot_box_profit(ax, df: pd.DataFrame):
    """Box plot of profit per order line by category (outliers visible, symmetric-log axis)."""
    sns.boxplot(data=df, x="category", y="profit", hue="category", legend=False, ax=ax, fliersize=2)
    ax.set_yscale("symlog", linthresh=100)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Category"); ax.set_ylabel("Profit per order line (symmetric log scale)")


def plot_corr(ax, corr: pd.DataFrame):
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax,
                cbar_kws={"label": "Pearson correlation"})


def plot_top_bottom_products(axes, tops: pd.DataFrame, bottoms: pd.DataFrame):
    for ax, d, color, title in [(axes[0], tops, "#55A868", "Top 10 Products by Profit"),
                                (axes[1], bottoms, "#C44E52", "10 Worst Products by Profit")]:
        names = [n if len(n) <= 34 else n[:31] + "..." for n in d.index]
        ax.barh(names[::-1], d["profit"].values[::-1], color=color)
        ax.set_title(title); ax.set_xlabel("Total profit (dataset currency units)"); ax.set_ylabel("Product"); ax.tick_params(axis="y", labelsize=8)
        _money_axis(ax, "x")


def plot_shipping(axes, df: pd.DataFrame, tbl: pd.DataFrame):
    days = df.groupby("ship_mode")["shipping_days"].mean().reindex(tbl.index)
    cost = df.groupby("ship_mode")["shipping_cost"].sum().reindex(tbl.index) / df.groupby("ship_mode")["sales"].sum().reindex(tbl.index) * 100
    axes[0].bar(days.index, days.values, color="#4C72B0"); axes[0].set_xlabel("Ship mode"); axes[0].set_ylabel("Average shipping days")
    axes[0].set_title("Average Delivery Time by Ship Mode")
    axes[1].bar(cost.index, cost.values, color="#DD8452"); axes[1].set_xlabel("Ship mode"); axes[1].set_ylabel("Shipping cost (% of sales)")
    axes[1].set_title("Shipping Cost as % of Sales")
    for ax in axes: ax.tick_params(axis="x", rotation=15)


def plot_seasonality_heatmap(ax, piv: pd.DataFrame):
    p = piv.copy(); p.columns = [MONTH_NAMES[int(c) - 1] for c in p.columns]
    sns.heatmap(p / 1000, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax, cbar_kws={"label": "Sales (thousands)"})
    ax.set_xlabel("Month"); ax.set_ylabel("Year")


def figure_interpretations(R: dict, df: pd.DataFrame) -> dict:
    """Plain-language interpretation for each chart, written from the calculated results."""
    T, K, S = R["tables"], R["kpis"], R["stats"]
    I = {}
    if "category" in T:
        c = T["category"]
        I["01_sales_profit_by_category.png"] = (
            f"{c['sales'].idxmax()} has the highest sales ({n0(c['sales'].max())}) and {c['profit'].idxmax()} has the highest profit ({n0(c['profit'].max())}). "
            f"Compare the two bars in each group: a category whose profit bar is very short compared with its sales bar has a low margin "
            f"(lowest margin: {c['profit_margin_pct'].idxmin()}, {c['profit_margin_pct'].min():.1f}%).")
    if "sub_category" in T:
        sc = T["sub_category"].reset_index().groupby("sub_category")["profit"].sum().sort_values()
        neg = (sc < 0).sum()
        I["02_profit_by_subcategory.png"] = (
            f"{sc.index[-1]} earns the most profit ({n0(sc.iloc[-1])}). " +
            (f"{neg} sub-categories are in red (net loss), the worst being {sc.index[0]} ({n0(sc.iloc[0])})." if neg else
             f"No sub-category is in red; the weakest is {sc.index[0]} ({n0(sc.iloc[0])}).") )
    geo = "market" if "market" in T else ("region" if "region" in T else None)
    if geo:
        g = T[geo]
        I["03_sales_profit_by_market.png"] = (f"{g['sales'].idxmax()} has the highest sales and {g['profit'].idxmax()} the highest profit. "
                                              f"Markets where the profit bar is small relative to the sales bar convert sales into profit poorly ({g['profit_margin_pct'].idxmin()} has the lowest margin, {g['profit_margin_pct'].min():.1f}%).")
        I["04_margin_heatmap_market_category.png"] = ("Green cells have a high profit margin and red cells a low or negative margin. Look for red cells: "
                                                      "they are market-category combinations that need pricing or cost review.")
    sk = R["tables"]["describe"]
    I["05_distributions.png"] = (f"Sales per order line are strongly right-skewed (skewness {sk.loc['sales', 'skew']:.1f}): most lines are small and a few are very large, so we use a log scale. "
                                 f"Profit is centred near zero with a long tail on both sides; lines left of the red dashed line lose money ({K['loss_line_pct']:.1f}% of all lines).")
    m = T["monthly"]
    I["06_monthly_trend.png"] = (f"Monthly sales range from {n0(m['sales'].min())} to {n0(m['sales'].max())}. The dashed 12-month average shows the long-term direction, "
                                 f"while the peaks and dips show seasonality. The strongest month is {m['sales'].idxmax():%b %Y}.")
    if "category" in T:
        I["07_yearly_sales_by_category.png"] = "Each line is one category. Rising lines show growth; lines that move apart show categories growing at different speeds."
    d = T["discount_band"]; sp = S.get("spearman_discount_margin")
    I["08_discount_vs_profit.png"] = (f"The left chart shows the profit margin falling from {d['profit_margin_pct'].iloc[0]:.1f}% (no discount) to {d['profit_margin_pct'].iloc[-1]:.1f}% in the highest band. " +
                                      (f"The scatter plot agrees: Spearman rho = {sp['rho']:.2f} (negative means a higher discount goes with a lower margin). " if sp else "") +
                                      "This shows association, not proof that discounts cause the losses.")
    if "category" in df.columns:
        I["09_profit_boxplot_by_category.png"] = ("The box shows the middle 50% of profit values and the dots show outliers (large profits and large losses). "
                                                  "A box that sits close to zero with many dots has small typical profit but occasional extreme results.")
    I["10_correlation_heatmap.png"] = ("Red = positive relationship, blue = negative. Sales and profit tend to move together, while discount tends to move against profit and margin. "
                                       "Correlation measures association only and does not show cause and effect.")
    if "products_top_profit" in T:
        I["11_top_bottom_products.png"] = (f"The left chart shows the products that earn the most profit, the right chart the products that lose the most. "
                                           f"The single biggest loss-maker is {T['products_bottom_profit'].index[0]} ({n0(T['products_bottom_profit'].iloc[0]['profit'])}).")
    if "ship_mode" in T and "shipping_days" in df.columns:
        I["12_shipping_analysis.png"] = "Faster ship modes deliver in fewer days; the right chart shows how much shipping costs relative to sales for each mode."
    I["13_sales_heatmap_year_month.png"] = "Darker cells are months with higher sales. Reading across a row shows the seasonal pattern within a year; reading down a column compares the same month across years."
    return I


def make_figures(df: pd.DataFrame, R: dict, out_dir: Path) -> list:
    """Draw all charts, save them as PNG files in out_dir and return a list of {file, title, interpretation}."""
    set_style()
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    T = R["tables"]; interp = figure_interpretations(R, df); saved = []

    def finish(fig, name, title):
        fig.tight_layout(); fig.savefig(out_dir / name, bbox_inches="tight"); plt.close(fig)
        saved.append({"file": name, "title": title, "interpretation": interp.get(name, "")})

    if "category" in T:
        fig, ax = plt.subplots(figsize=(8, 5)); plot_category_bars(ax, T["category"], "Category")
        ax.set_title("Total Sales and Profit by Category"); finish(fig, "01_sales_profit_by_category.png", "Total Sales and Profit by Category")
    if "sub_category" in T:
        fig, ax = plt.subplots(figsize=(8, 6)); plot_subcategory_profit(ax, T["sub_category"])
        ax.set_title("Total Profit by Sub-Category (red = loss)"); finish(fig, "02_profit_by_subcategory.png", "Total Profit by Sub-Category")
    geo = "market" if "market" in T else ("region" if "region" in T else None)
    if geo:
        fig, ax = plt.subplots(figsize=(9, 5)); plot_category_bars(ax, T[geo], geo.title())
        ax.set_title(f"Total Sales and Profit by {geo.title()}"); finish(fig, "03_sales_profit_by_market.png", f"Total Sales and Profit by {geo.title()}")
        if "category" in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5)); plot_margin_heatmap(ax, df, geo, "category")
            ax.set_title(f"Profit Margin (%) by {geo.title()} and Category"); finish(fig, "04_margin_heatmap_market_category.png", f"Profit Margin by {geo.title()} and Category")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5)); plot_distributions(axes, df)
    finish(fig, "05_distributions.png", "Distributions of Sales and Profit")
    fig, ax = plt.subplots(figsize=(11, 5)); plot_monthly_trend(ax, T["monthly"]); ax.set_title("Monthly Sales and Profit Trend")
    finish(fig, "06_monthly_trend.png", "Monthly Sales and Profit Trend")
    if "category" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5)); plot_yearly_category(ax, df); ax.set_title("Yearly Sales by Category")
        finish(fig, "07_yearly_sales_by_category.png", "Yearly Sales by Category")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); plot_discount(axes, df, T["discount_band"])
    finish(fig, "08_discount_vs_profit.png", "Discount versus Profit")
    if "category" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5)); plot_box_profit(ax, df); ax.set_title("Profit per Order Line by Category (outliers shown)")
        finish(fig, "09_profit_boxplot_by_category.png", "Profit per Order Line by Category")
    fig, ax = plt.subplots(figsize=(8, 6.5)); plot_corr(ax, T["corr_pearson"]); ax.set_title("Correlation Heatmap of Numerical Variables")
    finish(fig, "10_correlation_heatmap.png", "Correlation Heatmap")
    if "products_top_profit" in T:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5.5)); plot_top_bottom_products(axes, T["products_top_profit"], T["products_bottom_profit"])
        finish(fig, "11_top_bottom_products.png", "Top and Bottom Products by Profit")
    if "ship_mode" in T and "shipping_days" in df.columns and "shipping_cost" in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5)); plot_shipping(axes, df, T["ship_mode"])
        finish(fig, "12_shipping_analysis.png", "Shipping Analysis")
    fig, ax = plt.subplots(figsize=(10, 4.5)); plot_seasonality_heatmap(ax, T["sales_year_month"]); ax.set_title("Sales by Year and Month (thousands)")
    finish(fig, "13_sales_heatmap_year_month.png", "Sales Heatmap by Year and Month")
    return saved


def _jsonable(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return None if np.isnan(o) else float(o)
    if isinstance(o, (pd.Timestamp,)): return str(o.date())
    return str(o)


def run_pipeline(data_path=None, out_dir=None, make_charts=True, verbose=True) -> dict:
    """The whole project in one call. Returns a dictionary with every intermediate result."""
    out_dir = Path(out_dir) if out_dir else OUTPUT_DIR
    say = print if verbose else (lambda *a, **k: None)
    path = find_data_file(data_path)
    say(f"[1/6] Loading {path.name} ...")
    df_loaded, load_info = read_dataset(path)
    df_raw, name_map = standardise_columns(df_loaded)
    schema = check_schema(df_raw)
    say(f"      {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns (encoding: {load_info['encoding']})")
    if schema["missing_optional"]:
        say("      NOTE: optional columns not found (related analyses are skipped): " + ", ".join(schema["missing_optional"]))
    say("[2/6] Assessing data quality ...")
    quality = assess_quality(df_raw)
    say("[3/6] Cleaning data (original data is kept unchanged) ...")
    df, log = clean_data(df_raw)
    say(f"      {len(df_raw):,} -> {len(df):,} rows")
    say("[4/6] Calculating results and statistics ...")
    R = compute_results(df)
    insights = build_insights(R)
    figs = []
    if make_charts:
        say("[5/6] Creating charts ...")
        figs = make_figures(df, R, out_dir / "figures")
    say("[6/6] Saving tables and summary ...")
    save_outputs(out_dir, load_info, schema, quality, log, R, insights, figs, len(df_raw), len(df))
    return {"df_raw": df_raw, "df": df, "log": log, "quality": quality, "results": R, "insights": insights,
            "figures": figs, "load_info": load_info, "schema": schema, "out_dir": out_dir}


def save_outputs(out_dir, load_info, schema, quality, log, R, insights, figs, n_raw, n_clean):
    """Write tables (CSV) and summary.json so the report builder and you can reuse the real results."""
    out_dir = Path(out_dir); (out_dir / "tables").mkdir(parents=True, exist_ok=True)
    for name, tbl in R["tables"].items():
        tbl.to_csv(out_dir / "tables" / f"{name}.csv")
    log.to_frame().to_csv(out_dir / "tables" / "cleaning_audit.csv", index=False)
    quality["missing"].to_csv(out_dir / "tables" / "missing_values_before_cleaning.csv")
    quality["invalid_values"].to_csv(out_dir / "tables" / "invalid_values_before_cleaning.csv")
    summary = {
        "source_file": load_info["file"], "encoding": load_info["encoding"], "rows_raw": n_raw, "rows_clean": n_clean,
        "python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__,
        "schema": schema, "quality": {"exact_duplicates": quality["exact_duplicates"],
                                      "duplicates_ignoring_row_id": quality["duplicates_ignoring_row_id"],
                                      "invalid_values": quality["invalid_values"].to_dict()},
        "cleaning_audit": log.steps, "cleaning_notes": log.notes,
        "kpis": R["kpis"], "stats": R["stats"], "insights": insights, "figures": figs,
        "tables_preview": {k: R["tables"][k].reset_index().head(12).to_dict(orient="records")
                           for k in ["category", "market", "segment", "year", "discount_band", "ship_mode"] if k in R["tables"]},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=_jsonable), encoding="utf-8")


def print_summary(ctx: dict) -> None:
    K = ctx["results"]["kpis"]
    print("\n" + "=" * 70 + "\nPROJECT SUMMARY (calculated from your data file)\n" + "=" * 70)
    print(f"Period            : {K['date_min']} to {K['date_max']}")
    print(f"Orders / lines    : {K['n_orders']:,} / {K['n_lines']:,}")
    print(f"Total sales       : {K['total_sales']:,.2f}")
    print(f"Total profit      : {K['total_profit']:,.2f}  (margin {K['profit_margin_pct']:.2f}%)")
    print(f"Loss-making lines : {K['loss_lines']:,} ({K['loss_line_pct']:.1f}%)")
    print("\nCleaning audit:")
    print(ctx["log"].to_frame()[["step", "description", "rows_before", "rows_after", "affected"]].to_string(index=False))
    print("\nKey findings:")
    for i, ins in enumerate(ctx["insights"], 1):
        print(f" {i}. {ins['title']}: {ins['observation']}")
    print(f"\nCharts, tables and summary.json saved in: {ctx['out_dir']}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Real-World Dataset Analysis (Global Superstore)")
    parser.add_argument("--data", help="path to the dataset file (default: look inside the data/ folder)")
    parser.add_argument("--out", help="output folder (default: outputs/)")
    parser.add_argument("--no-charts", action="store_true", help="skip chart creation")
    args = parser.parse_args(argv)
    warnings.filterwarnings("ignore", category=FutureWarning)
    try:
        ctx = run_pipeline(args.data, args.out, make_charts=not args.no_charts)
    except (FileNotFoundError, KeyError, ValueError) as err:
        print("\nERROR:", err); sys.exit(1)
    print_summary(ctx)


if __name__ == "__main__":
    main()
