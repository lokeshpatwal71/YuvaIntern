"""Data-quality checks and cleaning steps for the monthly price table.

Every function takes a DataFrame and returns a new one (the input is never
modified), so the raw data stay untouched.
"""

import pandas as pd

from .data_loader import DATE_COLUMN


def ticker_columns(df):
    """Return the price columns (every column except ``Date``)."""
    return [c for c in df.columns if c != DATE_COLUMN]


def parse_dates(df):
    """Convert the ``Date`` column to datetime.

    Raises ValueError if any date cannot be parsed.
    """
    out = df.copy()
    out[DATE_COLUMN] = pd.to_datetime(out[DATE_COLUMN], errors="raise")
    return out


def empty_row_mask(df):
    """Boolean mask of rows in which every price column is missing."""
    return df[ticker_columns(df)].isna().all(axis=1)


def drop_empty_rows(df):
    """Remove rows that contain a date but no price at all."""
    return df.loc[~empty_row_mask(df)].copy()


def same_month_duplicate_mask(df):
    """Mark every row after the first one that falls in an already-seen month."""
    month = pd.to_datetime(df[DATE_COLUMN]).dt.to_period("M")
    return month.duplicated(keep="first")


def drop_same_month_duplicates(df):
    """Keep only the first row of each calendar month."""
    return df.loc[~same_month_duplicate_mask(df)].copy()


def quality_report(df):
    """Summarise the main data-quality facts of a raw price table.

    Returns a dict with row/column counts, missing values, empty rows, exact
    duplicate rows, duplicate dates, same-month duplicates, non-positive prices
    and whether the dates are in increasing order.
    """
    if df.empty:
        raise ValueError("Cannot assess an empty DataFrame")
    tickers = ticker_columns(df)
    dates = pd.to_datetime(df[DATE_COLUMN])
    prices = df[tickers]
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "first_date": dates.min(),
        "last_date": dates.max(),
        "dates_increasing": bool(dates.is_monotonic_increasing),
        "missing_cells": int(prices.isna().sum().sum()),
        "missing_by_column": prices.isna().sum().to_dict(),
        "empty_rows": int(empty_row_mask(df).sum()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "duplicate_dates": int(dates.duplicated().sum()),
        # Counted only among rows that contain prices (empty rows are reported separately).
        "same_month_duplicates": int(same_month_duplicate_mask(drop_empty_rows(df)).sum()),
        "non_positive_prices": int((prices <= 0).sum().sum()),
    }


def clean_prices(raw):
    """Full cleaning pipeline: parse dates, drop empty rows and repeated months.

    Returns a DataFrame indexed by month-start date with one column per ticker.
    Missing values that remain (for example before a company was listed) are kept
    as NaN on purpose - they are real gaps and are not filled.
    """
    df = parse_dates(raw)
    df = drop_empty_rows(df)
    df = drop_same_month_duplicates(df)
    df = df.sort_values(DATE_COLUMN)
    df[DATE_COLUMN] = df[DATE_COLUMN].dt.to_period("M").dt.to_timestamp()
    df = df.set_index(DATE_COLUMN)
    df.index.name = "Month"
    return df
