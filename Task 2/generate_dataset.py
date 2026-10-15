"""
generate_dataset.py
-------------------
Creates data/dataset.csv: a SYNTHETIC (computer-generated) supermarket sales dataset.

Important: this is NOT a real company's data. It was generated with a fixed random
seed so that everybody gets exactly the same file. Its column names and layout are
modelled on the public Kaggle "Supermarket sales" dataset, so the same analysis can
be tried on that real file later (see README).

A few realistic data-entry problems are included ON PURPOSE (a few blank ratings,
inconsistent text in the Payment column and a few duplicated invoice rows) so that
the data-cleaning part of the project has real work to do.

Run from the project root:   python src/generate_dataset.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "dataset.csv"

N_INVOICES = 1000
SEED = 2025


def build_clean_sales(rng: np.random.Generator) -> pd.DataFrame:
    """Create 1000 clean invoices (no problems yet)."""
    branch_city = {"A": "Mumbai", "B": "Delhi", "C": "Bengaluru"}
    price_range = {  # (min, max) unit price in rupees
        "Electronic accessories": (150, 900),
        "Fashion accessories": (100, 700),
        "Food and beverages": (50, 400),
        "Health and beauty": (80, 600),
        "Home and lifestyle": (200, 1000),
        "Sports and travel": (150, 950),
    }
    lines = list(price_range)

    # Dates: 1 Jan 2025 to 31 Mar 2025, weekends a little busier
    days = pd.date_range("2025-01-01", "2025-03-31")
    weights = np.where(days.dayofweek >= 5, 1.35, 1.0)
    dates = rng.choice(days, size=N_INVOICES, p=weights / weights.sum())

    # Time of day: busy around lunch and in the evening
    hours = np.arange(10, 21)
    hour_w = np.array([3, 4, 6, 7, 5, 4, 4, 5, 7, 8, 6], dtype=float)
    hour = rng.choice(hours, size=N_INVOICES, p=hour_w / hour_w.sum())
    minute = rng.integers(0, 60, size=N_INVOICES)

    branch = rng.choice(list(branch_city), size=N_INVOICES, p=[0.34, 0.32, 0.34])
    customer = rng.choice(["Member", "Normal"], size=N_INVOICES, p=[0.5, 0.5])
    product = rng.choice(lines, size=N_INVOICES)
    low = np.array([price_range[p][0] for p in product])
    high = np.array([price_range[p][1] for p in product])
    unit_price = np.round(rng.uniform(low, high), 2)

    quantity = np.where(
        customer == "Member",
        rng.choice(np.arange(1, 11), size=N_INVOICES, p=np.linspace(0.06, 0.14, 10) / np.linspace(0.06, 0.14, 10).sum()),
        rng.integers(1, 11, size=N_INVOICES),
    )

    cogs = np.round(unit_price * quantity, 2)
    tax = np.round(cogs * 0.05, 2)
    total = np.round(cogs + tax, 2)
    rating = np.round(np.clip(rng.normal(7.0, 1.6, size=N_INVOICES), 4.0, 10.0), 1)

    df = pd.DataFrame({
        "Invoice ID": "",
        "Branch": branch,
        "City": [branch_city[b] for b in branch],
        "Customer type": customer,
        "Gender": rng.choice(["Female", "Male"], size=N_INVOICES),
        "Product line": product,
        "Unit price": unit_price,
        "Quantity": quantity,
        "Tax 5%": tax,
        "Total": total,
        "Date": pd.to_datetime(dates),
        "Time": [f"{h:02d}:{m:02d}" for h, m in zip(hour, minute)],
        "Payment": rng.choice(["Cash", "Credit card", "Ewallet"], size=N_INVOICES),
        "cogs": cogs,
        "gross margin percentage": 4.761904762,
        "gross income": tax,
        "Rating": rating,
    })
    df = df.sort_values(["Date", "Time"]).reset_index(drop=True)
    df["Invoice ID"] = [f"INV-{i:05d}" for i in range(1, len(df) + 1)]
    df["Date"] = df["Date"].dt.strftime("%m/%d/%Y").str.lstrip("0").str.replace("/0", "/", regex=False)
    return df


def add_realistic_problems(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Add a few typical data-entry problems (deliberate, documented in the README)."""
    df = df.copy()
    df["Rating"] = df["Rating"].astype("float64")

    # 1) 12 invoices where the customer left the rating blank
    blank = rng.choice(len(df), size=12, replace=False)
    df.loc[blank, "Rating"] = np.nan

    # 2) Inconsistent text in the Payment column (typed differently by cashiers)
    messy = rng.choice(len(df), size=14, replace=False)
    df.loc[messy[:9], "Payment"] = df.loc[messy[:9], "Payment"].str.lower()
    df.loc[messy[9:], "Payment"] = df.loc[messy[9:], "Payment"] + " "

    # 3) 6 invoices accidentally entered twice (exact duplicate rows at the end)
    dup = rng.choice(len(df), size=6, replace=False)
    df = pd.concat([df, df.iloc[dup]], ignore_index=True)
    return df


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = add_realistic_problems(build_clean_sales(rng), rng)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows x {df.shape[1]} columns to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
