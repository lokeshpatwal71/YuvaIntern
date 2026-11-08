"""Automated tests for src/project_code.py.

Run from the project folder with:  python -m pytest -v
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import joblib  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from sklearn.linear_model import LinearRegression  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import project_code as pc  # noqa: E402


# ---------------------------------------------------------------- helpers
def small_frame(n=40, seed=0):
    """Small synthetic table with the same columns as the real data (tests only)."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.integers(20, 70, n).astype(float),
        "sex": rng.integers(1, 3, n).astype(float),
        "bmi": rng.uniform(19, 35, n),
        "bp": rng.uniform(70, 120, n),
        "s1": rng.uniform(120, 250, n),
        "s2": rng.uniform(70, 160, n),
        "s3": rng.uniform(30, 80, n),
        "s4": rng.uniform(2, 7, n),
        "s5": rng.uniform(3.5, 5.5, n),
        "s6": rng.uniform(70, 110, n),
    })
    df[pc.TARGET] = 100 + 5 * df["bmi"] + rng.normal(0, 5, n)
    return df


# ---------------------------------------------------------------- loading
def test_load_raw_diabetes_has_expected_shape_and_columns():
    df = pc.load_raw_diabetes()
    assert df.shape == (442, 11)
    assert list(df.columns) == pc.BASE_FEATURES + [pc.TARGET]


def test_load_raw_diabetes_returns_original_unscaled_units():
    df = pc.load_raw_diabetes()
    # first patient of the original data: age 59, BMI 32.1, progression 151
    assert df.loc[0, "age"] == 59
    assert df.loc[0, "bmi"] == pytest.approx(32.1)
    assert df.loc[0, pc.TARGET] == 151
    assert df["age"].min() >= 19 and df["bmi"].between(15, 45).all()


def test_save_raw_csv_roundtrip(tmp_path):
    df = pc.load_raw_diabetes()
    path = pc.save_raw_csv(df, tmp_path / "new_folder" / "raw.csv")
    assert path.is_file()
    back = pc.load_csv(path, required_columns=["age", pc.TARGET])
    pd.testing.assert_frame_equal(back, df, check_dtype=False)


def test_load_csv_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        pc.load_csv(tmp_path / "nope.csv")


def test_load_csv_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("a,b\n")
    with pytest.raises(ValueError, match="no data rows"):
        pc.load_csv(path)


def test_load_csv_missing_required_column(tmp_path):
    path = tmp_path / "cols.csv"
    path.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        pc.load_csv(path, required_columns=["a", "zzz"])


def test_saved_raw_csv_matches_loader():
    """The CSV shipped in data/raw/ equals the data returned by the loader."""
    shipped = pc.load_csv(pc.RAW_CSV)
    pd.testing.assert_frame_equal(shipped, pc.load_raw_diabetes(), check_dtype=False)


# ---------------------------------------------------------------- data quality
def test_quality_report_on_real_data_is_clean():
    rep = pc.quality_report(pc.load_raw_diabetes())
    assert rep["rows"] == 442 and rep["columns"] == 11
    assert rep["missing_cells"] == 0
    assert rep["duplicate_rows"] == 0
    assert rep["non_numeric_columns"] == []
    assert rep["infinite_values"] == 0


def test_quality_report_detects_missing_duplicate_and_infinite():
    df = small_frame(10)
    df.loc[0, "bmi"] = np.nan
    df.loc[1, "bp"] = np.inf
    df = pd.concat([df, df.iloc[[2]]], ignore_index=True)  # one duplicated row
    rep = pc.quality_report(df)
    assert rep["missing_cells"] == 1
    assert rep["duplicate_rows"] == 1
    assert rep["infinite_values"] == 1


def test_quality_report_rejects_empty_table():
    with pytest.raises(ValueError):
        pc.quality_report(pd.DataFrame())


def test_iqr_outlier_counts_known_values():
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]})
    out = pc.iqr_outlier_counts(df, ["x"])
    assert out.loc["x", "outliers"] == 1
    assert out.loc["x", "share_%"] == pytest.approx(10.0)


def test_iqr_outlier_counts_no_outliers():
    df = pd.DataFrame({"x": np.arange(20, dtype=float)})
    assert pc.iqr_outlier_counts(df, ["x"]).loc["x", "outliers"] == 0


def test_vif_independent_columns_close_to_one():
    rng = np.random.default_rng(1)
    df = pd.DataFrame(rng.normal(size=(500, 3)), columns=list("abc"))
    assert (pc.vif_table(df, list("abc")) < 1.2).all()


def test_vif_detects_collinearity():
    rng = np.random.default_rng(2)
    a = rng.normal(size=300)
    df = pd.DataFrame({"a": a, "b": a + rng.normal(scale=0.05, size=300), "c": rng.normal(size=300)})
    v = pc.vif_table(df, list("abc"))
    assert v["a"] > 100 and v["b"] > 100 and v["c"] < 1.5


# ---------------------------------------------------------------- feature engineering
def test_engineered_features_values_and_boundaries():
    df = small_frame(5)
    df["bmi"] = [18.0, 24.9, 25.0, 29.9, 30.0]
    df["age"] = [19, 39, 40, 59, 60]
    df["sex"] = [1, 2, 1, 2, 1]
    out = pc.add_engineered_features(df)
    assert list(out["sex_2"]) == [0, 1, 0, 1, 0]
    assert [str(x) for x in out["bmi_category"]] == [
        "Under 25", "Under 25", "25 to 29.9", "25 to 29.9", "30 and over"]
    assert [str(x) for x in out["age_group"]] == ["19-39", "19-39", "40-49", "50-59", "60+"]
    assert out["ldl_hdl_ratio"].iloc[0] == pytest.approx(df["s2"].iloc[0] / df["s3"].iloc[0])


def test_add_engineered_features_does_not_modify_input():
    df = small_frame(5)
    before = df.copy()
    pc.add_engineered_features(df)
    pd.testing.assert_frame_equal(df, before)


def test_engineered_features_on_real_data_have_no_missing_values():
    out = pc.add_engineered_features(pc.load_raw_diabetes())
    assert out[["sex_2", "bmi_category", "age_group", "ldl_hdl_ratio"]].isna().sum().sum() == 0
    assert out["bmi_category"].value_counts().sum() == 442


# ---------------------------------------------------------------- pipeline / leakage
def test_pipeline_fits_and_predicts_with_missing_input():
    df = pc.add_engineered_features(small_frame(60))
    cols = ["age", "sex_2", "bmi", "bp"]
    model = pc.make_pipeline(LinearRegression(), cols).fit(df[cols], df[pc.TARGET])
    new = df[cols].head(3).copy()
    new.loc[new.index[0], "bmi"] = np.nan          # imputer must handle this
    pred = model.predict(new)
    assert pred.shape == (3,) and np.isfinite(pred).all()


def test_preprocessor_scaler_learns_only_from_training_rows():
    """No leakage: the fitted scaler mean equals the TRAINING mean, not the full-data mean."""
    df = small_frame(50)
    train, test = df.iloc[:40], df.iloc[40:]
    prep = pc.make_preprocessor(["bmi"]).fit(train[["bmi"]])
    scaler = prep.named_transformers_["num"].named_steps["scale"]
    assert scaler.mean_[0] == pytest.approx(train["bmi"].mean())
    assert scaler.mean_[0] != pytest.approx(df["bmi"].mean())
    assert prep.transform(test[["bmi"]]).shape == (10, 1)


def test_preprocessor_one_hot_encodes_categorical_columns():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "g": ["a", "b", "a", "c"]})
    prep = pc.make_preprocessor(["x"], ["g"]).fit(df)
    assert prep.transform(df).shape == (4, 3)      # 1 numeric + 2 dummy columns (first dropped)


# ---------------------------------------------------------------- metrics
def test_regression_metrics_known_values():
    m = pc.regression_metrics([1, 2, 3, 4], [1, 2, 3, 6])
    assert m["MAE"] == pytest.approx(0.5)
    assert m["MSE"] == pytest.approx(1.0)
    assert m["RMSE"] == pytest.approx(1.0)
    assert m["R2"] == pytest.approx(1 - 4 / 5)


def test_regression_metrics_perfect_prediction():
    m = pc.regression_metrics([3, 5, 7], [3, 5, 7])
    assert m["RMSE"] == 0 and m["R2"] == pytest.approx(1.0)


def test_regression_metrics_rejects_bad_input():
    with pytest.raises(ValueError):
        pc.regression_metrics([1, 2], [1])
    with pytest.raises(ValueError):
        pc.regression_metrics([], [])


def test_bootstrap_ci_is_reproducible_and_brackets_estimate():
    rng = np.random.default_rng(3)
    y = rng.normal(150, 70, 89)
    pred = y + rng.normal(0, 50, 89)
    a = pc.bootstrap_metric_ci(y, pred, n_boot=300)
    b = pc.bootstrap_metric_ci(y, pred, n_boot=300)
    assert a == b                                   # same seed -> same result
    point = pc.regression_metrics(y, pred)["RMSE"]
    assert a["RMSE"][0] < point < a["RMSE"][1]


def test_ols_summary_recovers_exact_line():
    x = np.arange(10, dtype=float)
    y = 2 + 3 * x + np.array([0.1, -0.1] * 5)      # tiny noise
    out = pc.ols_summary(x.reshape(-1, 1), y, ["x"])
    assert out.loc["x", "coef"] == pytest.approx(3, abs=0.05)
    assert out.loc["intercept", "coef"] == pytest.approx(2, abs=0.2)
    assert out.loc["x", "p_value"] < 1e-6


def test_ols_summary_matches_numpy_least_squares():
    df = small_frame(80)
    X = df[["bmi", "bp"]].to_numpy()
    out = pc.ols_summary(X, df[pc.TARGET], ["bmi", "bp"])
    design = np.column_stack([np.ones(len(X)), X])
    expected, *_ = np.linalg.lstsq(design, df[pc.TARGET].to_numpy(), rcond=None)
    assert out["coef"].to_numpy() == pytest.approx(expected)


def test_segment_summary_counts_and_difference():
    df = pd.DataFrame({"g": ["a", "a", "b", "b", "b"], pc.TARGET: [10.0, 20.0, 30.0, 40.0, 50.0]})
    seg = pc.segment_summary(df, "g")
    assert seg.loc["a", "count"] == 2 and seg.loc["b", "count"] == 3
    assert seg.loc["a", "mean"] == pytest.approx(15.0)
    assert seg.loc["b", "diff_vs_overall"] == pytest.approx(40.0 - 30.0)


# ---------------------------------------------------------------- figures
def test_save_figure_creates_png(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    path = pc.save_figure(fig, "chart.png", tmp_path / "figs", dpi=50)
    plt.close(fig)
    assert path.is_file() and path.stat().st_size > 0


# ---------------------------------------------------------------- shipped results
def test_all_expected_charts_exist():
    charts = sorted(p.name for p in pc.FIGURE_DIR.glob("fig*.png"))
    assert len(charts) == 17 and charts[0].startswith("fig01") and charts[-1].startswith("fig17")


def test_saved_model_reproduces_saved_test_predictions():
    """The stored model gives the same predictions as results/test_predictions.csv."""
    bundle = joblib.load(ROOT / "models" / "best_model.joblib")
    processed = pd.read_csv(pc.PROCESSED_CSV)
    test = processed[processed["split"] == "test"].set_index("patient_id")
    saved = pd.read_csv(ROOT / "results" / "test_predictions.csv").set_index("patient_id")
    assert len(test) == len(saved) == 89
    assert set(test.index) == set(saved.index)
    test = test.loc[saved.index]                    # same patient order as the saved file
    pred = bundle["model"].predict(test[bundle["features"]])
    assert pred == pytest.approx(saved["predicted"].to_numpy(), abs=1e-2)
    assert test[pc.TARGET].to_numpy() == pytest.approx(saved["actual"].to_numpy())


def test_train_and_test_patients_do_not_overlap():
    processed = pd.read_csv(pc.PROCESSED_CSV)
    counts = processed["split"].value_counts()
    assert counts["train"] == 353 and counts["test"] == 89
    assert processed["patient_id"].is_unique


def test_evaluation_table_has_baseline_and_selected_model():
    table = pd.read_csv(ROOT / "results" / "model_evaluation_results.csv")
    assert "Baseline (mean)" in set(table["model"])
    assert table["selected"].sum() == 1
    baseline = table.loc[table["model"] == "Baseline (mean)", "test_rmse"].iloc[0]
    chosen = table.loc[table["selected"], "test_rmse"].iloc[0]
    assert chosen < baseline
