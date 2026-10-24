"""Plotting helpers. Every function saves a PNG and returns the saved path.

Palette: two fixed class colours (Benign = blue, Malignant = orange), chosen to be
colour-vision-deficiency safe; all charts use one y-axis, thin marks and a light grid.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

from data_cleaning import DIAGNOSIS_COL

COLORS = {"Benign": "#2a78d6", "Malignant": "#eb6834"}
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d3"
DIVERGING = LinearSegmentedColormap.from_list(
    "blue_gray_orange", [COLORS["Benign"], "#f1f0ec", COLORS["Malignant"]]
)


def setup_style() -> None:
    """Apply a clean, consistent Matplotlib style."""
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": 150,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "font.size": 10,
    })


def _save(fig: plt.Figure, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    return path


def plot_class_bar(df: pd.DataFrame, path: str | Path) -> Path:
    """Bar chart: number of samples (records) per diagnosis."""
    counts = df[DIAGNOSIS_COL].value_counts().reindex(["Benign", "Malignant"])
    total = counts.sum()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    bars = ax.bar(counts.index, counts.values, color=[COLORS[c] for c in counts.index],
                  width=0.55)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + total * 0.01,
                f"{v}  ({v / total * 100:.1f}%)", ha="center", va="bottom", color=INK)
    ax.set_ylim(0, counts.max() * 1.15)
    ax.set_title("Samples per diagnosis (n = %d)" % total)
    ax.set_xlabel("Diagnosis")
    ax.set_ylabel("Number of samples")
    ax.grid(axis="x", visible=False)
    return _save(fig, path)


def plot_hist_by_class(df: pd.DataFrame, col: str, path: str | Path,
                       xlabel: str) -> Path:
    """Histogram (with density curve) of one feature, split by diagnosis."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for label in ["Benign", "Malignant"]:
        sub = df.loc[df[DIAGNOSIS_COL] == label, col]
        sns.histplot(sub, bins=25, stat="density", color=COLORS[label], alpha=0.45,
                     edgecolor="white", linewidth=0.5, ax=ax, label=label, kde=True,
                     line_kws={"linewidth": 2})
    ax.set_title(f"Distribution of {xlabel} by diagnosis")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Density")
    ax.legend(title="Diagnosis")
    return _save(fig, path)


def plot_rate_line(rate_df: pd.DataFrame, xlabel: str, path: str | Path) -> Path:
    """Line chart: malignant share (%) across equal-frequency bins of one feature."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(rate_df["bin_mean"], rate_df["malignant_rate_pct"], color=COLORS["Malignant"],
            linewidth=2, marker="o", markersize=7, markeredgecolor="white",
            markeredgewidth=1.5)
    ax.set_ylim(-3, 105)
    ax.set_title(f"Share of malignant cases across {len(rate_df)} equal-size bins of {xlabel}")
    ax.set_xlabel(f"{xlabel} (mean value of each bin)")
    ax.set_ylabel("Malignant cases in bin (%)")
    return _save(fig, path)


def plot_scatter(df: pd.DataFrame, x: str, y: str, path: str | Path,
                 xlabel: str, ylabel: str) -> Path:
    """Scatter plot of two features coloured by diagnosis."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for label in ["Benign", "Malignant"]:
        sub = df[df[DIAGNOSIS_COL] == label]
        ax.scatter(sub[x], sub[y], s=28, alpha=0.75, color=COLORS[label],
                   edgecolor="white", linewidth=0.5, label=label)
    r = df[[x, y]].corr().iloc[0, 1]
    ax.set_title(f"{ylabel} vs {xlabel} (Pearson r = {r:.2f})")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(title="Diagnosis")
    return _save(fig, path)


def plot_boxplots(df: pd.DataFrame, cols: list[str], labels: list[str],
                  path: str | Path) -> Path:
    """Box plots (one panel per feature) comparing the two diagnoses."""
    n = len(cols)
    fig, axes = plt.subplots(1, n, figsize=(3.1 * n, 4.2))
    axes = np.atleast_1d(axes)
    for ax, c, lab in zip(axes, cols, labels):
        sns.boxplot(data=df, x=DIAGNOSIS_COL, y=c, order=["Benign", "Malignant"],
                    palette=COLORS, hue=DIAGNOSIS_COL, legend=False, width=0.55,
                    linewidth=1.2, fliersize=3, ax=ax)
        ax.set_title(lab, fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel(lab)
        ax.grid(axis="x", visible=False)
    fig.suptitle("Key features by diagnosis (box = IQR, line = median, dots = IQR outliers)",
                 fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, path)


def plot_corr_heatmap(df: pd.DataFrame, cols: list[str], labels: list[str],
                      path: str | Path) -> Path:
    """Correlation heatmap with a blue-gray-orange diverging scale centred on 0."""
    corr = df[cols].corr()
    corr.index = labels
    corr.columns = labels
    fig, ax = plt.subplots(figsize=(8.5, 7))
    sns.heatmap(corr, cmap=DIVERGING, vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                annot_kws={"size": 7.5}, linewidths=1, linecolor="white",
                cbar_kws={"label": "Pearson r", "shrink": 0.8}, square=True, ax=ax)
    ax.set_title("Correlation between the 10 'mean' features")
    ax.grid(False)
    return _save(fig, path)


def plot_auc_bar(cmp_df: pd.DataFrame, path: str | Path) -> Path:
    """Horizontal bars: separation AUC of every feature (0.5 = no separation)."""
    d = cmp_df["separation_auc"].sort_values()
    fig, ax = plt.subplots(figsize=(7.5, 8.5))
    ax.barh(d.index, d.values, color=COLORS["Benign"], height=0.65)
    ax.axvline(0.5, color=MUTED, linewidth=1, linestyle="--")
    ax.set_xlim(0.45, 1.0)
    ax.set_title("How well each feature separates malignant from benign (AUC)")
    ax.set_xlabel("Separation AUC (0.5 = none, 1.0 = perfect)")
    ax.set_ylabel("")
    ax.grid(axis="y", visible=False)
    return _save(fig, path)


def plot_skew_before_after(df: pd.DataFrame, col: str, path: str | Path,
                           label: str) -> Path:
    """Two histograms: raw vs log1p-transformed distribution of a skewed feature."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    raw = df[col]
    logv = np.log1p(raw)
    axes[0].hist(raw, bins=30, color=COLORS["Benign"], edgecolor="white")
    axes[0].set_title(f"{label}: raw (skew = {raw.skew():.2f})")
    axes[1].hist(logv, bins=30, color=COLORS["Benign"], edgecolor="white")
    axes[1].set_title(f"{label}: log(1 + x) (skew = {logv.skew():.2f})")
    for ax, xl in zip(axes, [label, f"log(1 + {label})"]):
        ax.set_xlabel(xl)
        ax.set_ylabel("Number of samples")
    fig.tight_layout()
    return _save(fig, path)


def plot_outlier_counts(counts: pd.Series, path: str | Path, n_rows: int,
                        top_n: int = 10) -> Path:
    """Bar chart of IQR-outlier counts for the features with the most outliers."""
    d = counts.sort_values(ascending=False).head(top_n)[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(d.index, d.values, color=COLORS["Benign"], height=0.6)
    for y, v in enumerate(d.values):
        ax.text(v + 0.5, y, str(v), va="center", color=INK)
    ax.set_title(f"Features with the most IQR outliers (top {top_n}, n = {n_rows} rows)")
    ax.set_xlabel("Number of rows flagged as outliers")
    ax.grid(axis="y", visible=False)
    return _save(fig, path)
