"""Automated tests for the analytics project (loading, cleaning, KPIs, charts).

Run from the project folder with:  python -m pytest
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import data_cleaning as dc  # noqa: E402
from src import data_loader as dl  # noqa: E402
from src import kpi_analysis as kpi  # noqa: E402
from src import visualization as viz  # noqa: E402


# --------------------------------------------------------------------- helpers
def small_raw():
    """A tiny raw table with the same problems as the real file."""
    return pd.DataFrame({
        "Date": ["2020-01-01", "2020-02-01", "2020-02-05", "2020-03-01", "2020-03-28"],
        "AAA": [10.0, 11.0, np.nan, 12.1, 12.1],
        "BBB": [np.nan, 5.0, np.nan, 5.5, 5.5],
    })


def monthly(values, start="2020-01-01"):
    idx = pd.date_range(start, periods=len(values), freq="MS")
    return pd.Series(values, index=idx, dtype=float)


# ------------------------------------------------------------------ data_loader
def test_load_raw_prices_from_csv(tmp_path):
    path = tmp_path / "prices.csv"
    path.write_text("# source comment\nDate,AAA\n2020-01-01,1.5\n2020-02-01,1.6\n")
    df = dl.load_raw_prices(path)
    assert list(df.columns) == ["Date", "AAA"]
    assert len(df) == 2


def test_load_raw_prices_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        dl.load_raw_prices(tmp_path / "nope.csv")


def test_load_raw_prices_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("Date,AAA\n")
    with pytest.raises(ValueError, match="no data rows"):
        dl.load_raw_prices(path)


def test_load_raw_prices_requires_date_column(tmp_path):
    path = tmp_path / "nodate.csv"
    path.write_text("Day,AAA\n2020-01-01,1\n")
    with pytest.raises(ValueError, match="Date"):
        dl.load_raw_prices(path)


def test_locate_unknown_sample_file():
    with pytest.raises(FileNotFoundError):
        dl.locate_sample_file("this_file_does_not_exist.csv")


def test_real_dataset_shape():
    raw = dl.load_raw_prices()
    assert raw.shape == (524, 11)
    assert raw.columns[0] == "Date"
    assert set(dl.COMPANY_NAMES) == set(raw.columns[1:])


def test_save_dataframe_creates_folder(tmp_path):
    out = dl.save_dataframe(pd.DataFrame({"a": [1]}), tmp_path / "new" / "x.csv", index=False)
    assert out.is_file()


# ---------------------------------------------------------------- data_cleaning
def test_ticker_columns_excludes_date():
    assert dc.ticker_columns(small_raw()) == ["AAA", "BBB"]


def test_empty_rows_detected():
    mask = dc.empty_row_mask(small_raw())
    assert mask.tolist() == [False, False, True, False, False]


def test_same_month_duplicates_detected():
    priced = dc.drop_empty_rows(small_raw())
    assert dc.same_month_duplicate_mask(priced).sum() == 1


def test_quality_report_counts():
    q = dc.quality_report(small_raw())
    assert q["rows"] == 5 and q["empty_rows"] == 1
    assert q["same_month_duplicates"] == 1
    assert q["exact_duplicate_rows"] == 0
    assert q["non_positive_prices"] == 0
    assert q["missing_cells"] == 3   # AAA 1 + BBB 2


def test_quality_report_rejects_empty_input():
    with pytest.raises(ValueError):
        dc.quality_report(pd.DataFrame(columns=["Date", "AAA"]))


def test_clean_prices_result_and_input_untouched():
    raw = small_raw()
    before = raw.copy()
    clean = dc.clean_prices(raw)
    pd.testing.assert_frame_equal(raw, before)            # raw data never modified
    assert len(clean) == 3 and clean.index.is_unique
    assert (clean.index.day == 1).all()
    assert clean.index.name == "Month"
    assert clean["BBB"].isna().sum() == 1                  # gap before first price is kept


def test_clean_prices_bad_date_raises():
    bad = small_raw()
    bad.loc[0, "Date"] = "not a date"
    with pytest.raises(ValueError):
        dc.clean_prices(bad)


def test_real_dataset_cleaning_result():
    clean = dc.clean_prices(dl.load_raw_prices())
    assert clean.shape == (390, 10)
    assert clean.index.min() == pd.Timestamp("1990-01-01")
    assert clean.index.max() == pd.Timestamp("2022-06-01")
    assert int(clean.isna().sum().sum()) == 585


# ----------------------------------------------------------------- kpi_analysis
def test_monthly_returns_values():
    r = kpi.monthly_returns(pd.DataFrame({"x": monthly([100, 110, 99])}))
    assert np.isnan(r["x"].iloc[0])
    assert r["x"].iloc[1] == pytest.approx(0.10)
    assert r["x"].iloc[2] == pytest.approx(-0.10)


def test_total_return_and_cagr():
    s = monthly([100] + [100] * 11 + [121])          # 12 monthly returns = 1 year
    assert kpi.total_return(s) == pytest.approx(0.21)
    assert kpi.cagr(s) == pytest.approx(0.21)
    two_years = monthly([100] + [100] * 23 + [121])
    assert kpi.cagr(two_years) == pytest.approx(0.10)  # sqrt(1.21) - 1


def test_kpis_return_nan_for_too_little_data():
    assert np.isnan(kpi.total_return(monthly([100])))
    assert np.isnan(kpi.cagr(monthly([100])))
    assert np.isnan(kpi.annualised_volatility(monthly([0.01])))
    assert np.isnan(kpi.cagr(monthly([0, 5])))        # zero start price: not meaningful


def test_annualised_volatility():
    r = monthly([0.01, -0.01, 0.01, -0.01])
    assert kpi.annualised_volatility(r) == pytest.approx(r.std(ddof=1) * np.sqrt(12))


def test_max_drawdown_depth_and_dates():
    s = monthly([100, 120, 90, 110, 60, 130])
    depth, peak, trough = kpi.max_drawdown(s)
    assert depth == pytest.approx(60 / 120 - 1)
    assert peak == pd.Timestamp("2020-02-01")
    assert trough == pd.Timestamp("2020-05-01")


def test_beta_and_correlation_of_scaled_series():
    market = monthly([0.01, -0.02, 0.03, 0.00, -0.01, 0.02])
    assert kpi.beta(2 * market, market) == pytest.approx(2.0)
    assert np.isnan(kpi.beta(monthly([0.01, 0.02]), monthly([0.01, 0.02])))   # fewer than 3 points


def test_calendar_year_returns():
    idx = pd.to_datetime(["2019-12-01", "2020-12-01", "2021-12-01"])
    prices = pd.DataFrame({"x": [100.0, 150.0, 120.0]}, index=idx)
    out = kpi.calendar_year_returns(prices)
    assert out.index.tolist() == [2020, 2021]
    assert out["x"].tolist() == pytest.approx([0.5, -0.2])


def test_downturn_table_uses_only_the_window():
    prices = pd.DataFrame({"x": [200, 100, 50, 60, 90]},
                          index=pd.date_range("2020-01-01", periods=5, freq="MS"))
    out = kpi.downturn_table(prices, {"w": ("2020-03", "2020-05")})
    assert out.loc["x", "w"] == pytest.approx(0.0)        # 50 -> 60 -> 90 never falls inside the window


def test_outlier_months_finds_extreme_value():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0, 0.01, 60), index=pd.date_range("2020-01-01", periods=60, freq="MS"))
    r.iloc[30] = 0.5
    out = kpi.outlier_months(pd.DataFrame({"x": r}))
    assert len(out) == 1 and out["month"].iloc[0] == r.index[30]


def test_outlier_months_empty_result_has_columns():
    out = kpi.outlier_months(pd.DataFrame({"x": monthly([0.01, -0.01, 0.0, 0.01, -0.01])}))
    assert out.empty and list(out.columns) == ["ticker", "month", "return", "z_score"]


def test_equal_weight_portfolio_and_index():
    r = pd.DataFrame({"a": [0.10, 0.00], "b": [0.00, 0.10]}, index=pd.date_range("2020-01-01", periods=2, freq="MS"))
    ew = kpi.equal_weight_portfolio(r)
    assert ew.tolist() == pytest.approx([0.05, 0.05])
    idx = kpi.index_from_returns(ew)
    assert idx.iloc[0] == 100 and idx.iloc[-1] == pytest.approx(100 * 1.05 ** 2)


def test_mean_pairwise_correlation_perfect_pair():
    a = monthly([0.01, 0.02, -0.01, 0.03])
    assert kpi.mean_pairwise_correlation(pd.DataFrame({"a": a, "b": 2 * a})) == pytest.approx(1.0)
    assert np.isnan(kpi.mean_pairwise_correlation(pd.DataFrame({"a": a})))


def test_headline_kpis_on_real_data():
    """Guards the numbers quoted in the report against accidental changes."""
    prices = dc.clean_prices(dl.load_raw_prices())
    core = ["IBM", "AAPL", "MSFT", "XRX", "AMZN", "GOOGL", "ADBE"]
    start = max(prices[t].first_valid_index() for t in core)
    window = prices.loc[start:, core + ["^GSPC", "^IXIC"]]
    table = kpi.kpi_table(window, market="^GSPC")
    assert len(window) == 214
    assert round(table.loc["AAPL", "cagr"] * 100, 1) == 35.9
    assert round(table.loc["XRX", "cagr"] * 100, 1) == -2.5
    assert round(table.loc["^GSPC", "max_drawdown"] * 100, 1) == -52.6
    assert round(float(table.loc["IBM", "beta_vs_market"]), 2) == 0.82


# ---------------------------------------------------------------- visualization
def test_label_known_and_unknown_ticker():
    assert viz.label("^GSPC") == "S&P 500"
    assert viz.label("ZZZ") == "ZZZ"


def test_save_figure_creates_png(tmp_path):
    viz.apply_style()
    prices = dc.clean_prices(dl.load_raw_prices())[["IBM", "AAPL", "MSFT"]].dropna()
    kt = kpi.kpi_table(prices, market="IBM")
    fig = viz.plot_cagr_bars(kt, "Test chart")
    path = viz.save_figure(fig, "chart.png", tmp_path / "figs")
    assert Path(path).is_file() and Path(path).stat().st_size > 1000


def test_all_real_figure_files_exist():
    figures = dl.FIGURES_DIR
    names = sorted(p.name for p in figures.glob("fig*.png"))
    assert len(names) == 12
    assert all((figures / n).stat().st_size > 10_000 for n in names)
