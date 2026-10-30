"""Chart helpers (Matplotlib + Seaborn) for the technology-stock performance review.

On a computer without a screen Matplotlib automatically draws into files, so no
special backend setting is needed here.

Colour rules used in every chart
--------------------------------
* Each company keeps ONE colour in every chart (colour follows the entity).
* The two market indices are always grey (S&P 500 dark grey, NASDAQ lighter grey).
* Heatmaps use one blue ramp (magnitude) or an orange-grey-blue ramp (gains vs losses).
* Charts that use colour also have a legend or direct labels and a table in the
  notebook, so no information depends on colour alone.
"""

import warnings
from pathlib import Path

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter, PercentFormatter  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e6e5e1"

TICKER_COLORS = {
    "IBM": "#2a78d6",
    "AAPL": "#eb6834",
    "MSFT": "#1baf7a",
    "XRX": "#eda100",
    "AMZN": "#e87ba4",
    "GOOGL": "#008300",
    "ADBE": "#6250d6",
    "DELL": "#e34948",
    "^GSPC": "#52514e",
    "^IXIC": "#9a9992",
    "EQUAL_WEIGHT": "#0b0b0b",
}
LABELS = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "EQUAL_WEIGHT": "Equal-weight basket (7 stocks)"}

DIVERGING = LinearSegmentedColormap.from_list(
    "orange_grey_blue", ["#d95926", "#f0efec", "#2a78d6"])
SEQUENTIAL = LinearSegmentedColormap.from_list("blue_seq", ["#f1f6fd", "#2a78d6", "#0f3a73"])


def label(ticker):
    """Readable name for a ticker."""
    return LABELS.get(ticker, ticker)


def apply_style():
    """Set a clean, readable Matplotlib style (thin grid, no top/right frame)."""
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK_SECONDARY, "axes.titlecolor": INK,
        "axes.titleweight": "bold", "axes.titlesize": 12, "axes.labelsize": 10,
        "xtick.color": INK_SECONDARY, "ytick.color": INK_SECONDARY, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 9,
        "lines.linewidth": 1.8, "figure.dpi": 100, "savefig.dpi": 150,
    })


def _line_style(ticker):
    return {"color": TICKER_COLORS[ticker], "linestyle": "--" if ticker == "^IXIC" else "-",
            "linewidth": 2.6 if ticker == "EQUAL_WEIGHT" else (
                1.4 if ticker in ("^GSPC", "^IXIC") else 1.8)}


def save_figure(fig, file_name, folder, close=True):
    """Save a figure as PNG (creating the folder if needed) and return the file path.

    Use ``close=False`` in a notebook so the chart is still shown below the cell.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / file_name
    fig.savefig(path, bbox_inches="tight")
    if close:
        plt.close(fig)
    return path


def plot_cagr_bars(kpis, title, subtitle=None):
    """Horizontal bars of CAGR, sorted high to low, with the history length in the label."""
    d = kpis.sort_values("cagr")
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(d))
    ax.barh(y, d["cagr"], color=[TICKER_COLORS[t] for t in d.index], height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{label(t)}  (from {d.loc[t, 'first_month']:%Y})" for t in d.index])
    for yi, v in zip(y, d["cagr"]):
        ax.text(v + 0.004, yi, f"{v:.1%}", va="center", fontsize=9, color=INK)
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlim(0, d["cagr"].max() * 1.12)
    ax.set_xlabel("Compound annual growth rate (CAGR) of price")
    ax.grid(axis="y", visible=False)
    ax.set_title(title, loc="left", pad=26 if subtitle else 6)
    if subtitle:
        ax.text(0, 1.025, subtitle, transform=ax.transAxes, fontsize=9, color=INK_SECONDARY)
    return fig


def plot_growth_of_100(prices, title):
    """Line chart of 100 invested at the first month, on a log scale."""
    idx = prices / prices.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for t in idx.columns:
        ax.plot(idx.index, idx[t], label=label(t), **_line_style(t))
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylabel("Value of 100 invested in the first month (log scale)")
    ax.set_xlabel("Month")
    ax.set_title(title, loc="left")
    ax.legend(ncol=3, loc="upper left", title="Equal start = 100")
    return fig


def plot_risk_return(kpis, title):
    """Scatter: annualised volatility (x) against CAGR (y), every point labelled."""
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for t, row in kpis.iterrows():
        ax.scatter(row["ann_volatility"], row["cagr"], s=90, color=TICKER_COLORS[t],
                   edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.annotate(label(t), (row["ann_volatility"], row["cagr"]), xytext=(7, 5),
                    textcoords="offset points", fontsize=9, color=INK)
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlabel("Annualised volatility (risk)")
    ax.set_ylabel("CAGR (growth)")
    ax.set_title(title, loc="left")
    return fig


def plot_drawdowns(prices, title):
    """Small multiples: percentage below the previous peak, one panel per ticker."""
    cols = list(prices.columns)
    ncols = 3
    nrows = int(np.ceil(len(cols) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 2.5 * nrows), sharex=True, sharey=True)
    for ax, t in zip(axes.ravel(), cols):
        s = prices[t].dropna()
        dd = s / s.cummax() - 1
        ax.fill_between(dd.index, dd, 0, color=TICKER_COLORS[t], alpha=0.55, linewidth=0)
        ax.plot(dd.index, dd, color=TICKER_COLORS[t], linewidth=1)
        ax.set_title(label(t), loc="left", fontsize=10)
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        ax.xaxis.set_major_locator(mdates.YearLocator(6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for ax in axes.ravel()[len(cols):]:
        ax.set_visible(False)
    fig.suptitle(title, x=0.01, ha="left", fontweight="bold", fontsize=12)
    fig.supylabel("Fall from previous peak", fontsize=10, color=INK_SECONDARY)
    fig.tight_layout()
    return fig


def plot_return_boxplot(returns, title):
    """Box plot of monthly returns for each ticker (box = middle 50 %, dots = outliers)."""
    cols = list(returns.columns)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = [returns[t].dropna() for t in cols]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=True,
                    flierprops={"marker": "o", "markersize": 3.5, "markerfacecolor": INK_SECONDARY,
                                "markeredgecolor": SURFACE, "alpha": 0.7},
                    medianprops={"color": INK, "linewidth": 1.6},
                    whiskerprops={"color": INK_SECONDARY}, capprops={"color": INK_SECONDARY})
    for patch, t in zip(bp["boxes"], cols):
        patch.set_facecolor(TICKER_COLORS[t])
        patch.set_alpha(0.75)
        patch.set_edgecolor(SURFACE)
    ax.set_xticks(range(1, len(cols) + 1))
    ax.set_xticklabels([label(t) for t in cols])
    ax.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel("Monthly return")
    ax.set_title(title, loc="left")
    return fig


def plot_return_histograms(returns, title, bins=None):
    """Small-multiple histograms of monthly returns on a shared axis."""
    cols = list(returns.columns)
    ncols = 3
    nrows = int(np.ceil(len(cols) / ncols))
    bins = np.linspace(-0.4, 0.6, 41) if bins is None else bins
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 2.6 * nrows), sharex=True, sharey=True)
    for ax, t in zip(axes.ravel(), cols):
        r = returns[t].dropna()
        ax.hist(r.clip(bins[0], bins[-1]), bins=bins, color=TICKER_COLORS[t], alpha=0.85,
                edgecolor=SURFACE, linewidth=0.5)
        ax.axvline(0, color=INK_SECONDARY, linewidth=0.8)
        ax.set_title(label(t), loc="left", fontsize=10)
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    for ax in axes.ravel()[len(cols):]:
        ax.set_visible(False)
    fig.suptitle(title, x=0.01, ha="left", fontweight="bold", fontsize=12)
    fig.supxlabel("Monthly return (values beyond the axis limits are placed in the end bins)",
                  fontsize=9, color=INK_SECONDARY)
    fig.supylabel("Number of months", fontsize=10, color=INK_SECONDARY)
    fig.tight_layout()
    return fig


def plot_correlation_heatmap(corr, title):
    """Annotated heatmap of a correlation matrix with a single-hue ramp."""
    fig, ax = plt.subplots(figsize=(8.5, 6.8))
    names = [label(t) for t in corr.columns]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PendingDeprecationWarning)  # raised inside seaborn
        sns.heatmap(corr.values, annot=True, fmt=".2f", cmap=SEQUENTIAL, vmin=0, vmax=1,
                    xticklabels=names, yticklabels=names, linewidths=2, linecolor=SURFACE,
                    cbar_kws={"label": "Correlation of monthly returns"}, ax=ax,
                    annot_kws={"fontsize": 8})
    ax.tick_params(axis="x", labelrotation=45)
    ax.tick_params(axis="y", labelrotation=0)
    ax.grid(False)
    ax.set_title(title, loc="left")
    return fig


def plot_beta_bars(kpis, title):
    """Bars of beta against the market, with a reference line at 1."""
    d = kpis.sort_values("beta_vs_market")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    y = np.arange(len(d))
    ax.barh(y, d["beta_vs_market"], color=[TICKER_COLORS[t] for t in d.index], height=0.62)
    ax.axvline(1, color=INK, linewidth=1.2, linestyle=":")
    ax.text(1.01, len(d) - 0.45, "Beta = 1 (moves with market)", fontsize=8.5, color=INK_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels([label(t) for t in d.index])
    for yi, v in zip(y, d["beta_vs_market"]):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9)
    ax.set_xlabel("Beta versus the S&P 500 (monthly returns)")
    ax.grid(axis="y", visible=False)
    ax.set_title(title, loc="left")
    return fig


def plot_beta_scatter(returns, market, title):
    """Small multiples: stock return (y) against market return (x) with a fitted line."""
    cols = [c for c in returns.columns if c != market]
    ncols = 3
    nrows = int(np.ceil(len(cols) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 3 * nrows), sharex=True, sharey=True)
    for ax, t in zip(axes.ravel(), cols):
        d = returns[[t, market]].dropna()
        ax.scatter(d[market], d[t], s=14, color=TICKER_COLORS[t], alpha=0.6, linewidth=0)
        slope, intercept = np.polyfit(d[market], d[t], 1)
        xs = np.array([d[market].min(), d[market].max()])
        ax.plot(xs, intercept + slope * xs, color=INK, linewidth=1.3)
        ax.set_title(f"{label(t)}  (slope = {slope:.2f})", loc="left", fontsize=10)
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    for ax in axes.ravel()[len(cols):]:
        ax.set_visible(False)
    fig.suptitle(title, x=0.01, ha="left", fontweight="bold", fontsize=12)
    fig.supxlabel("S&P 500 monthly return", fontsize=10, color=INK_SECONDARY)
    fig.supylabel("Stock monthly return", fontsize=10, color=INK_SECONDARY)
    fig.tight_layout()
    return fig


def plot_yearly_heatmap(yearly, title, vlim=0.6):
    """Heatmap of calendar-year returns (orange = loss, grey = near zero, blue = gain)."""
    d = yearly.T
    fig, ax = plt.subplots(figsize=(14, 0.55 * len(d) + 1.6))
    annot = d.map(lambda v: "" if np.isnan(v) else f"{v * 100:.0f}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PendingDeprecationWarning)  # raised inside seaborn
        sns.heatmap(d, annot=annot, fmt="", cmap=DIVERGING, vmin=-vlim, vmax=vlim, center=0,
                    linewidths=1.5, linecolor=SURFACE, yticklabels=[label(t) for t in d.index],
                    cbar_kws={"label": "Calendar-year return (colour capped at ±60 %)", "format":
                              PercentFormatter(1, decimals=0)}, ax=ax, annot_kws={"fontsize": 7})
    ax.set_xlabel("Calendar year (cell text = return in %; blank = no full-year data)")
    ax.set_ylabel("")
    ax.grid(False)
    ax.set_title(title, loc="left")
    return fig


def plot_downturns(table, title):
    """Grouped bars: largest fall inside each named stress window, per ticker."""
    names = list(table.columns)
    tickers = list(table.index)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    width = 0.8 / len(names)
    hatches = ["", "//", ".."]
    for j, name in enumerate(names):
        x = np.arange(len(tickers)) + j * width
        vals = table[name].values
        ax.bar(x, vals, width=width * 0.92, color=[TICKER_COLORS[t] for t in tickers],
               alpha=[0.95, 0.75, 0.55][j % 3], hatch=hatches[j % 3], edgecolor=SURFACE,
               linewidth=0.8)
        for xi, v in zip(x, vals):
            if np.isnan(v):
                ax.text(xi, -0.01, "n/a", ha="center", va="top", fontsize=7.5,
                        color=INK_SECONDARY, rotation=90)
    ax.set_xticks(np.arange(len(tickers)) + width * (len(names) - 1) / 2)
    ax.set_xticklabels([label(t) for t in tickers])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax.set_ylabel("Largest peak-to-trough fall inside the window")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor="#c9c8c2", hatch=hatches[j % 3],
                             edgecolor=SURFACE) for j in range(len(names))]
    ax.set_ylim(min(np.nanmin(table.values) * 1.08, -0.1), 0.06)
    ax.legend(handles, names, loc="upper center", bbox_to_anchor=(0.5, -0.08),
              title="Window (bar fill pattern)", ncol=len(names))
    ax.set_title(title, loc="left")
    return fig
