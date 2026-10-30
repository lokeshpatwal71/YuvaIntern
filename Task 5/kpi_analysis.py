"""KPI calculations for the technology-stock performance review.

Conventions
-----------
* Input prices are monthly, one column per ticker, indexed by month.
* A monthly return is ``price_t / price_(t-1) - 1``.
* "Years" are ``number of monthly returns / 12``.
* The risk-free rate is assumed to be 0, so ``return_to_risk`` is CAGR divided by
  annualised volatility (a simplified Sharpe-style ratio).
"""

import numpy as np
import pandas as pd

MONTHS_PER_YEAR = 12


def monthly_returns(prices):
    """Percentage change between consecutive months (first month is NaN)."""
    return prices.pct_change(fill_method=None)


def _valid(series):
    return series.dropna()


def total_return(series):
    """Last price divided by first price, minus 1 (NaN-aware)."""
    s = _valid(series)
    if len(s) < 2:
        return np.nan
    return s.iloc[-1] / s.iloc[0] - 1


def cagr(series):
    """Compound annual growth rate based on monthly observations."""
    s = _valid(series)
    if len(s) < 2 or s.iloc[0] <= 0:
        return np.nan
    years = (len(s) - 1) / MONTHS_PER_YEAR
    return (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1


def annualised_volatility(returns):
    """Standard deviation of monthly returns multiplied by sqrt(12)."""
    r = _valid(returns)
    if len(r) < 2:
        return np.nan
    return r.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR)


def drawdown_series(series):
    """Percentage fall from the highest price reached so far (<= 0)."""
    s = _valid(series)
    return s / s.cummax() - 1


def max_drawdown(series):
    """Return (depth, peak_month, trough_month) of the largest peak-to-trough fall."""
    dd = drawdown_series(series)
    if dd.empty:
        return np.nan, pd.NaT, pd.NaT
    trough = dd.idxmin()
    peak = series.dropna().loc[:trough].idxmax()
    return dd.min(), peak, trough


def return_to_risk(series, returns):
    """CAGR divided by annualised volatility (risk-free rate assumed 0)."""
    vol = annualised_volatility(returns)
    if not vol or np.isnan(vol):
        return np.nan
    return cagr(series) / vol


def beta(stock_returns, market_returns):
    """Slope of stock returns on market returns: cov(stock, market) / var(market)."""
    both = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(both) < 3:
        return np.nan
    cov = np.cov(both.iloc[:, 0], both.iloc[:, 1], ddof=1)
    return cov[0, 1] / cov[1, 1]


def kpi_table(prices, market="^GSPC"):
    """One row per ticker with the main performance and risk KPIs."""
    rets = monthly_returns(prices)
    rows = {}
    for t in prices.columns:
        s = prices[t].dropna()
        r = rets[t].dropna()
        depth, peak, trough = max_drawdown(prices[t])
        rows[t] = {
            "first_month": s.index.min(),
            "last_month": s.index.max(),
            "months": len(s),
            "total_return": total_return(prices[t]),
            "cagr": cagr(prices[t]),
            "ann_volatility": annualised_volatility(rets[t]),
            "return_to_risk": return_to_risk(prices[t], rets[t]),
            "max_drawdown": depth,
            "drawdown_peak": peak,
            "drawdown_trough": trough,
            "pct_positive_months": (r > 0).mean(),
            "best_month": r.max(),
            "worst_month": r.min(),
            "beta_vs_market": beta(rets[t], rets[market]) if market in rets else np.nan,
            "corr_with_market": rets[t].corr(rets[market]) if market in rets else np.nan,
        }
    return pd.DataFrame(rows).T.infer_objects()


def window_prices(prices, start, end):
    """Rows between two months (inclusive), keeping only tickers with full data."""
    w = prices.loc[start:end]
    return w.dropna(axis=1, how="any")


def calendar_year_returns(prices):
    """Return for each full calendar year: December price / previous December price - 1.

    The result has one row per year and NaN where the previous December price is
    unavailable (for example the first year of a company's history).
    """
    december = prices[prices.index.month == 12]
    out = december.pct_change(fill_method=None)
    out.index = out.index.year
    out.index.name = "Year"
    return out.iloc[1:] if len(out) else out


def downturn_table(prices, windows):
    """Largest peak-to-trough fall inside each named window, for each ticker.

    ``windows`` maps a name to a (start, end) pair of month strings. Only prices
    inside the window are used, so the fall is measured from the window's own peak.
    """
    rows = {}
    for name, (start, end) in windows.items():
        w = prices.loc[start:end]
        rows[name] = {t: (max_drawdown(w[t])[0] if w[t].notna().sum() >= 2 else np.nan)
                      for t in prices.columns}
    return pd.DataFrame(rows)


def outlier_months(returns, z_threshold=3.0):
    """List monthly returns more than ``z_threshold`` standard deviations from the
    ticker's own mean, as a long table (ticker, month, return, z-score)."""
    out = []
    for t in returns.columns:
        r = returns[t].dropna()
        if len(r) < 3 or r.std(ddof=1) == 0:
            continue
        z = (r - r.mean()) / r.std(ddof=1)
        hit = z[z.abs() > z_threshold]
        for month, zval in hit.items():
            out.append({"ticker": t, "month": month, "return": r.loc[month], "z_score": zval})
    cols = ["ticker", "month", "return", "z_score"]
    if not out:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(out, columns=cols).sort_values("z_score", key=np.abs, ascending=False)


def equal_weight_portfolio(returns):
    """Hypothetical portfolio that holds every column in equal weight and is
    rebalanced every month (no costs, no taxes). Returns its monthly returns."""
    return returns.mean(axis=1, skipna=False).dropna()


def mean_pairwise_correlation(returns):
    """Average of the off-diagonal correlations between the columns of ``returns``."""
    corr = returns.corr().to_numpy()
    n = corr.shape[0]
    if n < 2:
        return np.nan
    return float(corr[np.triu_indices(n, k=1)].mean())


def index_from_returns(returns, start_value=100.0):
    """Turn monthly returns into a value series that starts at ``start_value``."""
    values = start_value * (1 + returns).cumprod()
    first = values.index[0] - pd.offsets.MonthBegin(1)
    return pd.concat([pd.Series([start_value], index=[first]), values])
