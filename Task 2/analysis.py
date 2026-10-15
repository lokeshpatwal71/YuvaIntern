"""
analysis.py
-----------
Hands-On Data Lab Implementation: complete data analysis workflow in one script.

What this script does (same steps as the Jupyter notebook):
    1. Load the dataset
    2. Clean the data
    3. Add helpful new columns
    4. Perform basic analysis and statistics
    5. Create and save the visualizations
    6. Print the results

Run it from the project root folder:
    python src/analysis.py

It works from any folder because file paths are built from the location of this file.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw charts into files (no pop-up window needed)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ----------------------------------------------------------------------------
# Paths and settings
# ----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dataset.csv"
FIGURE_DIR = PROJECT_ROOT / "visualizations"

# Original column names -> clean, easy-to-type names
COLUMN_RENAME = {
    "Invoice ID": "invoice_id",
    "Branch": "branch",
    "City": "city",
    "Customer type": "customer_type",
    "Gender": "gender",
    "Product line": "product_line",
    "Unit price": "unit_price",
    "Quantity": "quantity",
    "Tax 5%": "tax_5pct",
    "Total": "total",
    "Date": "date",
    "Time": "time",
    "Payment": "payment",
    "cogs": "cogs",
    "gross margin percentage": "gross_margin_pct",
    "gross income": "gross_income",
    "Rating": "rating",
}

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def set_plot_style() -> None:
    """One professional look for all charts."""
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams.update({
        "figure.dpi": 100,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
    })


# ----------------------------------------------------------------------------
# 1. Load
# ----------------------------------------------------------------------------
def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Read the CSV file into a DataFrame."""
    return pd.read_csv(path)


# ----------------------------------------------------------------------------
# 2. Clean
# ----------------------------------------------------------------------------
def clean_data(raw: pd.DataFrame):
    """Clean the raw data. Returns (clean_dataframe, summary_of_changes)."""
    df = raw.rename(columns=COLUMN_RENAME).copy()
    summary = {"rows_before": len(df)}

    # Make text in the payment column consistent ("cash", "Cash " -> "Cash")
    summary["payment_values_before"] = df["payment"].nunique()
    df["payment"] = df["payment"].str.strip().str.capitalize()
    summary["payment_values_after"] = df["payment"].nunique()

    # Remove exact duplicate rows
    summary["duplicates_removed"] = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    # Fill missing ratings with the median rating
    summary["missing_ratings_filled"] = int(df["rating"].isnull().sum())
    df["rating"] = df["rating"].fillna(df["rating"].median())

    # Convert text dates/times into proper date types
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y")
    df["hour"] = pd.to_datetime(df["time"], format="%H:%M").dt.hour

    # Drop columns that carry no extra information
    # (gross_margin_pct never changes and gross_income is identical to tax_5pct)
    df = df.drop(columns=["gross_margin_pct", "gross_income"])

    summary["rows_after"] = len(df)
    return df, summary


# ----------------------------------------------------------------------------
# 3. New columns
# ----------------------------------------------------------------------------
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create new columns that make analysis easier."""
    df = df.copy()
    df["month"] = df["date"].dt.month_name()
    df["weekday"] = pd.Categorical(df["date"].dt.day_name(), categories=WEEKDAY_ORDER, ordered=True)
    df["is_weekend"] = df["date"].dt.dayofweek >= 5
    df["order_size"] = pd.qcut(df["total"], q=3, labels=["Small", "Medium", "Large"])
    return df


# ----------------------------------------------------------------------------
# 4. Analysis
# ----------------------------------------------------------------------------
def analyse(df: pd.DataFrame) -> dict:
    """Calculate the main results and return them in a dictionary."""
    results = {}
    results["total_revenue"] = df["total"].sum()
    results["mean_invoice"] = df["total"].mean()
    results["median_invoice"] = df["total"].median()
    results["std_invoice"] = df["total"].std()

    by_line = df.groupby("product_line")["total"].sum().sort_values(ascending=False)
    results["revenue_by_product_line"] = by_line
    by_branch = df.groupby(["branch", "city"])["total"].agg(["sum", "mean", "count"])
    results["by_branch"] = by_branch.sort_values("sum", ascending=False)
    results["payment_counts"] = df["payment"].value_counts()
    results["customer_type_summary"] = df.groupby("customer_type")["total"].agg(["mean", "median", "count"])
    results["revenue_by_hour"] = df.groupby("hour")["total"].sum()
    results["revenue_by_weekday"] = df.groupby("weekday", observed=True)["total"].sum()
    results["revenue_by_month"] = df.groupby("month")["total"].sum()

    corr_cols = ["unit_price", "quantity", "rating", "total", "hour"]
    results["correlation"] = df[corr_cols].corr(numeric_only=True)
    return results


# ----------------------------------------------------------------------------
# 5. Visualizations
# ----------------------------------------------------------------------------
def save_figure(fig, name: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def make_visualizations(df: pd.DataFrame, results: dict) -> list:
    """Create the 8 charts used in the project and save them as PNG files."""
    set_plot_style()
    saved = []

    # 1. Bar chart: revenue by product line
    fig, ax = plt.subplots(figsize=(9, 5))
    data = results["revenue_by_product_line"].sort_values()
    ax.barh(data.index, data.values, color=sns.color_palette("deep")[0])
    ax.bar_label(ax.containers[0], labels=[f"{v:,.0f}" for v in data.values], padding=3, fontsize=9)
    ax.set_title("Total Revenue by Product Line")
    ax.set_xlabel("Total revenue (Rs.)")
    ax.set_ylabel("Product line")
    ax.set_xlim(0, data.max() * 1.15)
    save_figure(fig, "01_revenue_by_product_line.png"); saved.append("01_revenue_by_product_line.png")

    # 2. Histogram: distribution of invoice totals
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df["total"], bins=30, kde=True, ax=ax)
    ax.axvline(df["total"].mean(), color="red", linestyle="--", label=f"Mean = {df['total'].mean():,.0f}")
    ax.axvline(df["total"].median(), color="green", linestyle="-", label=f"Median = {df['total'].median():,.0f}")
    ax.set_title("Distribution of Invoice Totals")
    ax.set_xlabel("Invoice total (Rs.)")
    ax.set_ylabel("Number of invoices")
    ax.legend()
    save_figure(fig, "02_invoice_total_distribution.png"); saved.append("02_invoice_total_distribution.png")

    # 3. Box plot: invoice total by branch
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="branch", y="total", order=["A", "B", "C"], hue="branch", legend=False, ax=ax)
    ax.set_title("Invoice Total by Branch")
    ax.set_xlabel("Branch")
    ax.set_ylabel("Invoice total (Rs.)")
    save_figure(fig, "03_invoice_total_by_branch.png"); saved.append("03_invoice_total_by_branch.png")

    # 4. Pie chart: payment methods
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    counts = results["payment_counts"]
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
           colors=sns.color_palette("deep")[:len(counts)], wedgeprops={"edgecolor": "white"})
    ax.set_title("Share of Invoices by Payment Method")
    save_figure(fig, "04_payment_method_share.png"); saved.append("04_payment_method_share.png")

    # 5. Scatter plot: rating vs total
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=df, x="rating", y="total", hue="customer_type", alpha=0.6, ax=ax)
    ax.set_title("Customer Rating vs Invoice Total")
    ax.set_xlabel("Customer rating (out of 10)")
    ax.set_ylabel("Invoice total (Rs.)")
    ax.legend(title="Customer type")
    save_figure(fig, "05_rating_vs_total.png"); saved.append("05_rating_vs_total.png")

    # 6. Heatmap: correlation matrix
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(results["correlation"], annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
                linewidths=0.5, ax=ax)
    ax.set_title("Correlation Heatmap of Numerical Variables")
    save_figure(fig, "06_correlation_heatmap.png"); saved.append("06_correlation_heatmap.png")

    # 7. Line chart: daily revenue over time
    fig, ax = plt.subplots(figsize=(11, 5))
    daily = df.groupby("date")["total"].sum()
    ax.plot(daily.index, daily.values, color="lightsteelblue", label="Daily revenue")
    ax.plot(daily.index, daily.rolling(7).mean(), color="darkblue", linewidth=2, label="7-day average")
    ax.set_title("Daily Revenue, January to March 2025")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue (Rs.)")
    ax.legend()
    fig.autofmt_xdate()
    save_figure(fig, "07_daily_revenue_trend.png"); saved.append("07_daily_revenue_trend.png")

    # 8. Bar chart: revenue by hour of day
    fig, ax = plt.subplots(figsize=(9, 5))
    hourly = results["revenue_by_hour"]
    ax.bar(hourly.index, hourly.values, color=sns.color_palette("deep")[2])
    ax.set_title("Total Revenue by Hour of the Day")
    ax.set_xlabel("Hour of day (24-hour clock)")
    ax.set_ylabel("Total revenue (Rs.)")
    ax.set_xticks(hourly.index)
    save_figure(fig, "08_revenue_by_hour.png"); saved.append("08_revenue_by_hour.png")

    return saved


# ----------------------------------------------------------------------------
# 6. Print results
# ----------------------------------------------------------------------------
def print_report(df: pd.DataFrame, summary: dict, results: dict) -> None:
    line = "=" * 60
    print(line); print("HANDS-ON DATA LAB: ANALYSIS REPORT"); print(line)

    print("\n--- Cleaning summary ---")
    print(f"Rows before cleaning        : {summary['rows_before']}")
    print(f"Duplicate rows removed      : {summary['duplicates_removed']}")
    print(f"Missing ratings filled      : {summary['missing_ratings_filled']}")
    print(f"Payment spellings           : {summary['payment_values_before']} -> {summary['payment_values_after']}")
    print(f"Rows after cleaning         : {summary['rows_after']}")

    print("\n--- Main numbers ---")
    print(f"Total revenue               : Rs. {results['total_revenue']:,.2f}")
    print(f"Average invoice             : Rs. {results['mean_invoice']:,.2f}")
    print(f"Median invoice              : Rs. {results['median_invoice']:,.2f}")
    print(f"Std. deviation of invoice   : Rs. {results['std_invoice']:,.2f}")

    print("\n--- Revenue by product line ---")
    print(results["revenue_by_product_line"].round(2).to_string())
    print("\n--- Revenue by branch ---")
    print(results["by_branch"].round(2).to_string())
    print("\n--- Payment methods ---")
    print(results["payment_counts"].to_string())
    print("\n--- Member vs Normal customers (invoice total) ---")
    print(results["customer_type_summary"].round(2).to_string())
    print("\n--- Correlation matrix ---")
    print(results["correlation"].round(2).to_string())


def main() -> None:
    raw = load_data()
    clean, summary = clean_data(raw)
    df = add_features(clean)
    results = analyse(df)
    print_report(df, summary, results)
    saved = make_visualizations(df, results)
    print(f"\nSaved {len(saved)} charts to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
