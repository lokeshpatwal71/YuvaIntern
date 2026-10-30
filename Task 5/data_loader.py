"""Data loading helpers for the Analytics Report & Insights project.

Dataset
-------
``Stocks.csv`` - monthly stock prices downloaded from Yahoo Finance
(https://finance.yahoo.com) for eight technology companies and two US market
indices. The file is shipped inside Matplotlib's ``sample_data`` folder, so it
is available on any computer where Matplotlib is installed - no download, no
account and no API key are needed.

The file is read from the installed Matplotlib package at run time and is not
copied into this repository (see README.md, "Dataset source and attribution").
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

SAMPLE_FILE_NAME = "Stocks.csv"
DATE_COLUMN = "Date"

# Ticker -> company name (taken from the well-known ticker symbols).
COMPANY_NAMES = {
    "IBM": "IBM",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "XRX": "Xerox",
    "AMZN": "Amazon",
    "DELL": "Dell",
    "GOOGL": "Alphabet (Google)",
    "ADBE": "Adobe",
    "^GSPC": "S&P 500 index",
    "^IXIC": "NASDAQ Composite index",
}
MARKET_TICKER = "^GSPC"       # benchmark used for beta and market comparison
INDEX_TICKERS = ["^GSPC", "^IXIC"]


def locate_sample_file(file_name=SAMPLE_FILE_NAME):
    """Return the path of a Matplotlib sample-data file.

    Raises
    ------
    FileNotFoundError
        If Matplotlib does not contain the requested sample file.
    """
    from matplotlib.cbook import get_sample_data  # imported here: optional at import time

    try:
        path = Path(get_sample_data(file_name, asfileobj=False))
    except (FileNotFoundError, OSError) as exc:
        raise FileNotFoundError(f"Matplotlib sample file not found: {file_name}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"Matplotlib sample file not found: {path}")
    return path


def load_raw_prices(path=None):
    """Load the raw price table exactly as stored (no cleaning).

    Parameters
    ----------
    path : str or Path, optional
        A CSV file with a ``Date`` column and one column per ticker. When omitted,
        the file bundled with Matplotlib is used.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is empty or has no ``Date`` column.
    """
    path = locate_sample_file() if path is None else Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    # The first line of the source file is a comment naming the data source.
    df = pd.read_csv(path, comment="#")
    if df.empty:
        raise ValueError(f"CSV file has no data rows: {path}")
    if DATE_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {DATE_COLUMN}")
    return df


def save_dataframe(df, path, index=True):
    """Save a DataFrame as CSV, creating the parent folder when needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path
