import os

import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)

rng = np.random.default_rng(42)
n = 120

students = pd.DataFrame({
    "Student_ID": [f"S{i:03d}" for i in range(1, n + 1)],
    "Gender": rng.choice(["Male", "Female"], n),
    "Class": rng.choice(["A", "B", "C"], n),
})
study = np.clip(rng.normal(12, 4, n), 2, 25)
study[[10, 57]] = [38.0, 42.5]
attend = np.clip(rng.normal(88, 7, n), 55, 100)
students["Study_Hours"] = study.round(1)
students["Attendance"] = attend.round(1)
students["Internet"] = rng.choice(["Yes", "No"], n, p=[0.8, 0.2])
students["Parent_Edu"] = rng.choice(["School", "Bachelor", "Master"], n, p=[0.4, 0.4, 0.2])

base = 20 + 1.6 * np.minimum(study, 25) + 0.3 * attend
base += np.where(students["Internet"] == "Yes", 3, 0)
students["Math"] = np.clip(base + rng.normal(0, 7, n), 0, 100).round(1)
science = 0.7 * students["Math"] + 20 + rng.normal(0, 6, n)
students["Science"] = np.clip(science, 0, 100).round(1)
english = 55 + 0.6 * np.minimum(study, 25) + rng.normal(0, 9, n)
students["English"] = np.clip(english, 0, 100).round(1)

for col, k in [("Study_Hours", 5), ("Attendance", 4), ("English", 3)]:
    students.loc[rng.choice(n, k, replace=False), col] = np.nan
students = pd.concat([students, students.iloc[[5, 40, 77]]], ignore_index=True)
students.to_csv("data/student_performance.csv", index=False)

rng = np.random.default_rng(2025)
n = 300
cat_price = {"Electronics": 450, "Furniture": 300, "Clothing": 40, "Stationery": 8}
days = np.arange(365)
w = np.where(days >= 273, 1.8, 1.0)
w = w / w.sum()
offsets = np.sort(rng.choice(days, n, p=w))
dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(offsets, unit="D")

category = rng.choice(list(cat_price), n, p=[0.25, 0.15, 0.35, 0.25])
discount = rng.choice([0, 5, 10, 15, 20], n, p=[0.4, 0.2, 0.2, 0.1, 0.1])
units = rng.integers(1, 11, n) + discount // 5
units[[30, 120, 210, 260]] = [65, 80, 72, 95]
price = np.array([cat_price[c] for c in category]) * rng.uniform(0.85, 1.15, n)

sales = pd.DataFrame({
    "Order_ID": [f"ORD{1001 + i}" for i in range(n)],
    "Order_Date": dates.strftime("%Y-%m-%d"),
    "Region": rng.choice(["North", "South", "East", "West"], n, p=[0.30, 0.25, 0.25, 0.20]),
    "Category": category,
    "Units": units,
    "Unit_Price": price.round(2),
    "Discount": discount,
    "Rating": rng.choice([1, 2, 3, 4, 5], n,
                          p=[0.04, 0.08, 0.20, 0.38, 0.30]).astype(float),
})
sales["Revenue"] = (sales["Units"] * sales["Unit_Price"]
                    * (1 - sales["Discount"] / 100)).round(2)

sales.loc[rng.choice(n, 14, replace=False), "Rating"] = np.nan
idx = rng.choice(n, 8, replace=False)
sales.loc[idx[:4], "Region"] = sales.loc[idx[:4], "Region"].str.lower()
sales.loc[idx[4:], "Region"] = sales.loc[idx[4:], "Region"].str.upper() + " "
sales = pd.concat([sales, sales.iloc[[15, 90, 150, 222, 280]]], ignore_index=True)
sales.to_csv("data/retail_sales.csv", index=False)
print("Created student_performance.csv", students.shape)
print("Created retail_sales.csv", sales.shape)
