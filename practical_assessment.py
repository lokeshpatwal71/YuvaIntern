import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/student_performance.csv")
print("Dataset loaded successfully.")

print(df.head())

rows, cols = df.shape
print(f"Rows: {rows}, Columns: {cols}")

print(df.dtypes)

print(df.isnull().sum())

print("Duplicate rows:", df.duplicated().sum())
dups = df[df.duplicated(keep=False)].sort_values("Student_ID")
print(dups[["Student_ID", "Class", "Study_Hours", "Attendance", "Math", "English"]])

df = df.drop_duplicates().reset_index(drop=True)
for col in ["Study_Hours", "Attendance", "English"]:
    df[col] = df[col].fillna(df[col].median())

print("Rows after removing duplicates:", len(df))
print("Missing values remaining:", df.isnull().sum().sum())

cols = ["Study_Hours", "Attendance", "Math", "Science", "English"]
print("MEAN");   print(df[cols].mean().round(2))
print("MEDIAN"); print(df[cols].median().round(2))
print("Mode of Math (first of several ties):", df["Math"].mode()[0])
print("Number of tied modes in Math:", len(df["Math"].mode()))
print("Mode of Class:", df["Class"].mode()[0])

print(df[cols].std().round(2))
print("Variance of Math:", round(df["Math"].var(), 2))
print("Range of Math:", round(df["Math"].max() - df["Math"].min(), 1))

print(df["Math"].quantile([0.25, 0.50, 0.75, 0.90]))

def iqr_outliers(series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return series[(series < low) | (series > high)], low, high

for col in ["Study_Hours", "Math"]:
    found, low, high = iqr_outliers(df[col])
    print(f"{col}: bounds = ({low:.1f}, {high:.1f}), outliers = {found.tolist()}")

top = df[(df["Math"] >= 80) & (df["Attendance"] >= 90)]
print("Students with Math >= 80 and Attendance >= 90:", len(top))
print(top[["Student_ID", "Class", "Study_Hours", "Attendance", "Math"]].head())

low_att = df[df["Attendance"] < 75]
print("Students with Attendance below 75%:", len(low_att))

print(df.groupby("Class")[["Math", "Science", "English"]].mean().round(2))

summary = df.groupby("Internet").agg(
    Students=("Student_ID", "count"),
    Avg_Math=("Math", "mean"),
    Avg_Study=("Study_Hours", "mean"),
).round(2)
print(summary)
print(df.groupby("Parent_Edu")["Math"].mean().round(2).sort_values(ascending=False))
print(df.groupby("Gender")["Math"].mean().round(2))

df["Average"] = df[["Math", "Science", "English"]].mean(axis=1).round(2)
df["Level"] = pd.cut(df["Average"],
                     bins=[0, 50, 65, 80, 100],
                     labels=["Needs Support", "Average", "Good", "Excellent"])
print(df["Level"].value_counts().sort_index())

num_cols = ["Study_Hours", "Attendance", "Math", "Science", "English"]
corr = df[num_cols].corr().round(2)
print(corr)

sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4))
sns.histplot(df["Math"], bins=12, kde=True, color="steelblue")
plt.title("Distribution of Math Scores")
plt.xlabel("Math Score")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig("figures/fig_p_hist.png", dpi=150)
plt.show()

plt.figure(figsize=(7, 4))
sns.regplot(data=df, x="Study_Hours", y="Math",
            scatter_kws={"alpha": 0.6}, line_kws={"color": "red"})
plt.title("Study Hours vs Math Score")
plt.xlabel("Study Hours per Week")
plt.ylabel("Math Score")
plt.tight_layout()
plt.savefig("figures/fig_p_scatter.png", dpi=150)
plt.show()

plt.figure(figsize=(7, 4))
sns.boxplot(data=df, x="Class", y="Math", hue="Class", palette="Set2", legend=False)
plt.title("Math Scores by Class")
plt.tight_layout()
plt.savefig("figures/fig_p_box.png", dpi=150)
plt.show()

plt.figure(figsize=(7, 4.5))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig("figures/fig_p_heat.png", dpi=150)
plt.show()

print("Corr (Study_Hours, Math)  :", round(df["Study_Hours"].corr(df["Math"]), 2))
print("Corr (Attendance, Math)    :", round(df["Attendance"].corr(df["Math"]), 2))
print("Corr (Math, Science)       :", round(df["Math"].corr(df["Science"]), 2))
print("Corr (Study_Hours, English):", round(df["English"].corr(df["Study_Hours"]), 2))
print("Avg Math with internet     :", round(df[df["Internet"] == "Yes"]["Math"].mean(), 1))
print("Avg Math without internet  :", round(df[df["Internet"] == "No"]["Math"].mean(), 1))
level = df["Level"]
print("Share of 'Excellent' level :", round((level == "Excellent").mean() * 100, 1), "%")
print("Share needing support      :", round((level == "Needs Support").mean() * 100, 1), "%")
print("Best class by Math         :", df.groupby("Class")["Math"].mean().idxmax())
print("Students studying > 20 hrs :", (df["Study_Hours"] > 20).sum())
