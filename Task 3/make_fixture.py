"""
make_fixture.py - builds a SMALL SYNTHETIC test file with the same column layout as the
Global Superstore CSV. It is used ONLY to test that the code runs (tests/test_pipeline.py).

!!! This file is NOT real data. Never use it for your analysis or report. !!!
The real analysis must use the real dataset downloaded from Kaggle (see data/README.md).
"""
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID", "Customer Name",
           "Segment", "City", "State", "Country", "Postal Code", "Market", "Region", "Product ID", "Category",
           "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit", "Shipping Cost",
           "Order Priority"]


def make_fixture(path, n=3000, seed=7, encoding="iso-8859-2", excel=False):
    rng = np.random.default_rng(seed)
    geo = [("New York City", "New York", "United States", "US", "East"), ("Los Angeles", "California", "United States", "US", "West"),
           ("Wollongong", "New South Wales", "Australia", "APAC", "Oceania"), ("München", "Bayern", "Germany", "EU", "Central"),
           ("Sao Paulo", "Sao Paulo", "Brazil", "LATAM", "South"), ("Lagos", "Lagos", "Nigeria", "Africa", "Africa"),
           ("Toronto", "Ontario", "Canada", "Canada", "Canada")]
    cats = {"Furniture": ["Chairs", "Tables", "Bookcases"], "Office Supplies": ["Binders", "Paper", "Storage"],
            "Technology": ["Phones", "Copiers", "Accessories"]}
    base_margin = {"Chairs": 0.10, "Tables": -0.08, "Bookcases": 0.05, "Binders": 0.18, "Paper": 0.30, "Storage": 0.12,
                   "Phones": 0.20, "Copiers": 0.28, "Accessories": 0.22}
    scale = {"Furniture": 900, "Office Supplies": 120, "Technology": 700}
    order_ids = [f"ORD-{rng.integers(2011, 2015)}-{i:05d}" for i in rng.integers(1, 1200, n)]
    odate = pd.Timestamp("2011-01-01") + pd.to_timedelta(rng.integers(0, 4 * 365, n), unit="D")
    lines = []
    for i in range(n):
        g = geo[rng.integers(len(geo))]
        cat = rng.choice(list(cats)); sub = rng.choice(cats[cat])
        disc = rng.choice([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], p=[0.5, 0.1, 0.12, 0.08, 0.08, 0.06, 0.03, 0.03])
        sales = float(np.round(rng.lognormal(np.log(scale[cat]), 0.8), 3))
        profit = float(np.round(sales * (base_margin[sub] - 0.9 * disc) + rng.normal(0, sales * 0.05), 4))
        cid = rng.integers(1, 301)
        lines.append([i + 1, order_ids[i], odate[i], odate[i] + pd.Timedelta(days=int(rng.integers(0, 8))),
                      rng.choice(["Same Day", "First Class", "Second Class", "Standard Class"], p=[.05, .15, .2, .6]),
                      f"CU-{cid:05d}", f"Customer {cid} Müller" if cid % 7 == 0 else f"Customer {cid}",
                      rng.choice(["Consumer", "Corporate", "Home Office"], p=[.5, .3, .2]), g[0], g[1], g[2],
                      float(rng.integers(10000, 99999)) if g[3] == "US" else np.nan, g[3], g[4],
                      f"PRD-{cat[:3].upper()}-{rng.integers(1, 60):05d}", cat, sub,
                      f"{sub} model {rng.integers(1, 60)}", sales, int(rng.integers(1, 15)), disc, profit,
                      float(np.round(sales * rng.uniform(0.02, 0.12), 2)), rng.choice(["Critical", "High", "Medium", "Low"])])
    df = pd.DataFrame(lines, columns=COLUMNS)
    # --- messy bits that real data often has ---
    df.loc[5, "City"] = "  Toronto "                      # extra spaces
    df.loc[9, "Ship Date"] = df.loc[9, "Order Date"] - pd.Timedelta(days=3)    # impossible: shipped before ordered
    df.loc[15, "Quantity"] = 0                              # impossible quantity
    df = pd.concat([df, df.iloc[[2, 3, 4]]], ignore_index=True)                # 3 exact duplicate rows
    path = Path(path)
    if excel:
        df.to_excel(path, index=False)
    else:
        for col in ["Order Date", "Ship Date"]:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%d-%m-%Y")            # dd-mm-yyyy like the real CSV
        df.to_csv(path, index=False, encoding=encoding)
    return path


if __name__ == "__main__":
    out = make_fixture(Path(__file__).parent / "synthetic_test_fixture.csv")
    print("Created SYNTHETIC test file (not real data):", out)
