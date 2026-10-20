"""
test_pipeline.py - basic validation checks for the project code.

Run from the project folder:   python tests/test_pipeline.py
(or with pytest:               pytest tests)

These tests use a SMALL SYNTHETIC test file created on the fly (tests/make_fixture.py).
They only prove that the code runs correctly; they do NOT produce any result for the report.
"""
import sys
import tempfile
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import analysis as ra                       # noqa: E402
from make_fixture import make_fixture       # noqa: E402

warnings.simplefilter("error", FutureWarning)
warnings.simplefilter("error", DeprecationWarning)


def test_full_pipeline_csv_and_excel():
    with tempfile.TemporaryDirectory() as tmp:
        csv = make_fixture(Path(tmp) / "fx.csv")
        xlsx = make_fixture(Path(tmp) / "fx.xlsx", excel=True)
        for path in (csv, xlsx):
            ctx = ra.run_pipeline(path, Path(tmp) / f"out_{path.suffix[1:]}", verbose=False)
            df, K = ctx["df"], ctx["results"]["kpis"]
            assert len(ctx["df_raw"]) == 3003 and len(df) == 2998, "3 duplicates + 2 invalid rows should be removed"
            assert df["order_date"].dtype.kind == "M", "order_date must be datetime"
            assert df[["sales", "profit", "quantity", "discount"]].notna().all().all()
            assert abs(K["total_sales"] - df["sales"].sum()) < 1e-6
            assert (Path(tmp) / f"out_{path.suffix[1:]}" / "summary.json").exists()
            assert len(list((Path(tmp) / f"out_{path.suffix[1:]}" / "figures").glob("*.png"))) >= 10
        print("  ok: full pipeline on CSV (latin2) and Excel")


def test_original_data_is_not_modified():
    with tempfile.TemporaryDirectory() as tmp:
        raw, _ = ra.standardise_columns(ra.read_dataset(make_fixture(Path(tmp) / "fx.csv"))[0])
        snapshot = raw.copy(deep=True)
        ra.clean_data(raw)
        pd.testing.assert_frame_equal(raw, snapshot)
        print("  ok: original DataFrame unchanged after cleaning")


def test_audit_log_adds_up():
    with tempfile.TemporaryDirectory() as tmp:
        raw, _ = ra.standardise_columns(ra.read_dataset(make_fixture(Path(tmp) / "fx.csv"))[0])
        clean, log = ra.clean_data(raw)
        audit = log.to_frame()
        assert audit["rows_removed"].sum() == len(raw) - len(clean)
        assert list(audit["step"]) == list(range(1, 8))
        print("  ok: audit log is consistent")


def test_date_format_detection():
    day_first = pd.Series(["31-07-2012", "05-02-2013"])
    month_first = pd.Series(["07/31/2012", "02/05/2013"])
    assert ra.detect_date_format(day_first)[1] == "%d-%m-%Y"
    assert ra.detect_date_format(month_first)[1] == "%m/%d/%Y"
    assert ra.detect_date_format(pd.Series(["2012-07-31 00:00:00"]))[1] == "%Y-%m-%d"
    print("  ok: date format detection")


def test_discount_percent_is_rescaled():
    with tempfile.TemporaryDirectory() as tmp:
        raw, _ = ra.standardise_columns(ra.read_dataset(make_fixture(Path(tmp) / "fx.csv"))[0])
        raw["discount"] = raw["discount"] * 100
        clean, log = ra.clean_data(raw)
        assert clean["discount"].max() <= 1.0
        print("  ok: discount stored as percent is rescaled")


def test_missing_required_column_gives_clear_error():
    with tempfile.TemporaryDirectory() as tmp:
        raw, _ = ra.standardise_columns(ra.read_dataset(make_fixture(Path(tmp) / "fx.csv"))[0])
        try:
            ra.check_schema(raw.drop(columns=["profit"]))
        except KeyError as err:
            assert "profit" in str(err)
        else:
            raise AssertionError("a missing 'profit' column must raise KeyError")
        print("  ok: missing required column is reported clearly")


def test_column_name_variants():
    assert ra.normalise_name("Sub-Category") == "sub_category"
    assert ra.normalise_name(" Order Date ") == "order_date"
    assert ra.normalise_name("Shipping Cost") == "shipping_cost"
    print("  ok: column names are standardised")


def test_missing_file_message():
    try:
        ra.find_data_file(ROOT / "data" / "does_not_exist.csv")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError")
    print("  ok: missing file gives FileNotFoundError")


if __name__ == "__main__":
    print("Running tests (synthetic test data only) ...")
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("ALL TESTS PASSED")
