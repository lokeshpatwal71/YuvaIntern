import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sales = pd.read_csv("data/retail_sales.csv")
print("Shape:", sales.shape)
print(sales.head())
sales.info()

print(sales.isnull().sum())
print("Duplicate rows:", sales.duplicated().sum())
print(sales["Region"].value_counts())

expected = (sales["Units"] * sales["Unit_Price"] * (1 - sales["Discount"] / 100)).round(2)
print("Revenue mismatches:", (abs(expected - sales["Revenue"]) > 0.01).sum())

sales = sales.drop_duplicates().reset_index(drop=True)
sales["Order_Date"] = pd.to_datetime(sales["Order_Date"])
sales["Region"] = sales["Region"].str.strip().str.title()
sales["Rating"] = sales["Rating"].fillna(sales["Rating"].median())
sales["Month"] = sales["Order_Date"].dt.month

assert (sales["Units"] > 0).all() and (sales["Revenue"] > 0).all()
assert sales["Order_ID"].is_unique
print("Rows after cleaning:", len(sales))
print(sales["Region"].value_counts())
print(sales[["Order_Date", "Rating"]].dtypes)
print("Missing values left:", sales.isnull().sum().sum())

print(sales[["Units", "Unit_Price", "Discount", "Rating", "Revenue"]].describe().round(2))
print(sales["Category"].value_counts())
first, last = sales["Order_Date"].min(), sales["Order_Date"].max()
print("Date range:", first.date(), "to", last.date())

q1, q3 = sales["Units"].quantile([0.25, 0.75])
iqr = q3 - q1
high = q3 + 1.5 * iqr
bulk = sales[sales["Units"] > high]
print("Upper bound for Units:", high)
print(bulk[["Order_ID", "Category", "Units", "Revenue"]])

print("Total revenue :", round(sales["Revenue"].sum(), 2))
print("Average order :", round(sales["Revenue"].mean(), 2))
print("Median order  :", round(sales["Revenue"].median(), 2))

by_cat = sales.groupby("Category")["Revenue"].agg(["count", "sum", "mean"]).round(2)
print(by_cat.sort_values("sum", ascending=False))
print(sales.groupby("Region")["Revenue"].sum().round(2).sort_values(ascending=False))

monthly = sales.groupby("Month")["Revenue"].sum().round(0)
print(monthly)
q4_share = monthly.loc[[10, 11, 12]].sum() / monthly.sum() * 100
print("Q4 share of revenue (%):", round(q4_share, 1))
print(sales.groupby("Discount")["Units"].mean().round(2))

corr = sales[["Units", "Unit_Price", "Discount", "Rating", "Revenue"]].corr().round(2)
print(corr)
print("Top 5 orders by revenue:")
print(sales.nlargest(5, "Revenue")[["Order_ID", "Category", "Units", "Revenue"]])

sns.set_theme(style="whitegrid")
monthly_rev = sales.groupby("Month")["Revenue"].sum()
plt.figure(figsize=(7, 4))
plt.plot(monthly_rev.index, monthly_rev.values, marker="o", color="darkgreen")
plt.title("Monthly Revenue (2025)")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(range(1, 13))
plt.tight_layout()
plt.savefig("figures/fig_m_line.png", dpi=150)
plt.show()

cat_rev = sales.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(7, 4))
sns.barplot(x=cat_rev.index, y=cat_rev.values, hue=cat_rev.index,
            palette="viridis", legend=False)
plt.title("Total Revenue by Category")
plt.xlabel("Category")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig("figures/fig_m_bar.png", dpi=150)
plt.show()

plt.figure(figsize=(7, 4))
sns.boxplot(data=sales, x="Region", y="Revenue", hue="Region",
            palette="Set3", legend=False)
plt.title("Order Revenue by Region")
plt.tight_layout()
plt.savefig("figures/fig_m_box.png", dpi=150)
plt.show()

plt.figure(figsize=(7, 4.5))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("Correlation Heatmap - Retail Sales")
plt.tight_layout()
plt.savefig("figures/fig_m_heat.png", dpi=150)
plt.show()

print("Average rating by category:")
print(sales.groupby("Category")["Rating"].mean().round(2))
print("Share of bulk orders (> 25 units) in revenue (%):",
      round(sales[sales["Units"] > 25]["Revenue"].sum() / sales["Revenue"].sum() * 100, 1))
print("Average units: no discount vs 20% discount:",
      round(sales[sales["Discount"] == 0]["Units"].mean(), 1), "vs",
      round(sales[sales["Discount"] == 20]["Units"].mean(), 1))
