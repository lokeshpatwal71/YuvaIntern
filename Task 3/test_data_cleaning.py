"""Automated tests (standard-library unittest; also discovered by pytest).

Run from the repository root:   python -m unittest discover -s tests -v
                           or:   pytest -v
"""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import analysis  # noqa: E402
import data_cleaning as dc  # noqa: E402
import data_loader as dl  # noqa: E402

RAW_PATH = ROOT / "data" / "raw" / "wdbc_breast_cancer_raw.csv"


def tiny_clean_frame() -> pd.DataFrame:
    """Small hand-made frame with the cleaned column layout (for unit tests only)."""
    return pd.DataFrame({
        "radius_mean": [10.0, 12.0, 14.0, 20.0, 22.0, 11.0],
        "area_mean": [300.0, 450.0, 600.0, 1250.0, 1500.0, 380.0],
        "perimeter_mean": [65.0, 80.0, 90.0, 130.0, 145.0, 72.0],
        "concavity_mean": [0.0, 0.05, 0.1, 0.3, 0.4, 0.02],
        "diagnosis": pd.Categorical(
            ["Benign", "Benign", "Benign", "Malignant", "Malignant", "Benign"],
            categories=["Benign", "Malignant"]),
    })


class TestColumnNames(unittest.TestCase):
    def test_standardise(self):
        self.assertEqual(dc.standardise_column_name("mean radius"), "radius_mean")
        self.assertEqual(dc.standardise_column_name("area error"), "area_se")
        self.assertEqual(dc.standardise_column_name("worst concave points"),
                         "concave_points_worst")

    def test_unexpected_columns_pass_through(self):
        df = pd.DataFrame({"Patient ID": [1], "mean radius": [2.0]})
        out = dc.standardise_columns(df)
        self.assertEqual(list(out.columns), ["patient_id", "radius_mean"])


class TestDecodeDiagnosis(unittest.TestCase):
    def test_decode_and_order(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "target": [0, 1, 1]})
        out = dc.decode_diagnosis(df, ["malignant", "benign"])
        self.assertEqual(list(out["diagnosis"]), ["Malignant", "Benign", "Benign"])
        self.assertNotIn("target", out.columns)
        self.assertTrue(isinstance(out["diagnosis"].dtype, pd.CategoricalDtype))

    def test_unknown_code_raises(self):
        df = pd.DataFrame({"target": [0, 2]})
        with self.assertRaises(ValueError):
            dc.decode_diagnosis(df, ["malignant", "benign"])

    def test_missing_target_column_raises(self):
        with self.assertRaises(KeyError):
            dc.decode_diagnosis(pd.DataFrame({"a": [1]}), ["m", "b"])


class TestMissingAndDuplicates(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({"a": [1.0, np.nan, 3.0, 3.0], "b": [4.0, 5.0, np.nan, np.nan]})

    def test_missing_report(self):
        rep = dc.missing_report(self.df)
        self.assertEqual(rep.loc["a", "missing_count"], 1)
        self.assertEqual(rep.loc["b", "missing_count"], 2)
        self.assertAlmostEqual(rep.loc["b", "missing_pct"], 50.0)

    def test_handle_missing_strategies(self):
        self.assertEqual(dc.handle_missing(self.df, "report").isna().sum().sum(), 3)
        self.assertEqual(len(dc.handle_missing(self.df, "drop")), 1)
        filled = dc.handle_missing(self.df, "median")
        self.assertEqual(filled.isna().sum().sum(), 0)
        self.assertEqual(filled.loc[1, "a"], 3.0)  # median of [1, 3, 3]
        with self.assertRaises(ValueError):
            dc.handle_missing(self.df, "zero")

    def test_input_not_modified(self):
        before = self.df.copy()
        dc.handle_missing(self.df, "median")
        pd.testing.assert_frame_equal(self.df, before)

    def test_duplicates(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": [5, 5, 6]})
        self.assertEqual(dc.duplicate_count(df), 1)
        out, removed = dc.remove_duplicates(df)
        self.assertEqual(removed, 1)
        self.assertEqual(len(out), 2)

    def test_empty_input(self):
        empty = pd.DataFrame({"a": pd.Series(dtype=float)})
        self.assertEqual(dc.duplicate_count(empty), 0)
        self.assertEqual(dc.missing_report(empty).loc["a", "missing_count"], 0)
        out = dc.add_outlier_count(empty)
        self.assertEqual(len(out), 0)


class TestValidityAndOutliers(unittest.TestCase):
    def test_invalid_values_detected(self):
        df = tiny_clean_frame()
        df.loc[0, "radius_mean"] = -1.0   # violates > 0
        df.loc[1, "concavity_mean"] = -0.1  # violates >= 0
        bad = dc.find_invalid_values(df).set_index("column")["violations"]
        self.assertEqual(bad["radius_mean"], 1)
        self.assertEqual(bad["concavity_mean"], 1)

    def test_zero_concavity_is_valid(self):
        df = tiny_clean_frame()  # row 0 has concavity_mean == 0
        self.assertTrue(dc.find_invalid_values(df).empty)
        self.assertEqual(dc.count_zero_values(df)["concavity_mean"], 1)

    def test_isoperimetric_flags_impossible_shape(self):
        df = pd.DataFrame({"perimeter_mean": [10.0, 100.0], "area_mean": [500.0, 500.0]})
        flags = dc.isoperimetric_violations(df)
        self.assertEqual(list(flags), [True, False])
        with self.assertRaises(KeyError):
            dc.isoperimetric_violations(pd.DataFrame({"x": [1]}))

    def test_iqr_outlier_flagged_not_removed(self):
        df = pd.DataFrame({"v": [10, 11, 12, 11, 10, 12, 11, 100.0]})
        mask = dc.iqr_outlier_mask(df)
        self.assertEqual(int(mask["v"].sum()), 1)
        self.assertTrue(mask.loc[7, "v"])
        out = dc.add_outlier_count(df)
        self.assertEqual(len(out), len(df))  # rows preserved
        self.assertEqual(int(out.loc[7, dc.OUTLIER_COUNT_COL]), 1)


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.df = tiny_clean_frame()

    def test_class_balance(self):
        cb = analysis.class_balance(self.df)
        self.assertEqual(cb.loc["Benign", "count"], 4)
        self.assertAlmostEqual(cb["percent"].sum(), 100.0, places=1)

    def test_compare_groups_structure_and_direction(self):
        cmp = analysis.compare_groups(self.df, ["radius_mean"])
        self.assertIn("cohens_d", cmp.columns)
        row = cmp.loc["radius_mean"]
        self.assertGreater(row["mean_malignant"], row["mean_benign"])
        self.assertEqual(row["auc_malignant_higher"], 1.0)  # perfectly separated
        self.assertGreater(row["cohens_d"], 0)

    def test_top_correlated_pairs(self):
        pairs = analysis.top_correlated_pairs(self.df, ["radius_mean", "area_mean",
                                                        "perimeter_mean"], 0.9)
        self.assertGreaterEqual(len(pairs), 1)
        self.assertTrue((pairs["pearson_r"].abs() >= 0.9).all())

    def test_rate_by_bin(self):
        out = analysis.rate_by_quantile_bin(self.df, "radius_mean", q=3)
        self.assertEqual(out["n"].sum(), len(self.df))
        self.assertTrue(out["malignant_rate_pct"].between(0, 100).all())

    def test_skew_log_rejects_negative(self):
        df = pd.DataFrame({"v": [-1.0, 2.0, 3.0]})
        with self.assertRaises(ValueError):
            analysis.skew_before_after_log(df, ["v"])

    def test_describe_structure(self):
        d = analysis.describe_numeric(self.df, ["radius_mean"])
        for col in ["mean", "median", "std", "variance", "q1", "q3", "skew"]:
            self.assertIn(col, d.columns)


@unittest.skipUnless(RAW_PATH.is_file(), "raw dataset not present")
class TestRealDataset(unittest.TestCase):
    """Integration tests on the real raw data file."""

    @classmethod
    def setUpClass(cls):
        cls.raw = dl.load_raw(RAW_PATH)
        cls.meta = dl.read_metadata(RAW_PATH)
        cls.clean, cls.log = dc.clean_dataset(cls.raw, cls.meta["class_names"])

    def test_raw_shape(self):
        self.assertEqual(self.raw.shape, (569, 31))

    def test_pipeline_preserves_rows_and_adds_expected_columns(self):
        self.assertEqual(len(self.clean), len(self.raw) - self.log["duplicates_removed"])
        self.assertIn("diagnosis", self.clean.columns)
        self.assertIn("radius_mean", self.clean.columns)
        self.assertEqual(self.clean.isna().sum().sum(), 0)

    def test_class_counts_match_documentation(self):
        counts = self.clean["diagnosis"].value_counts()
        self.assertEqual(counts["Malignant"], 212)
        self.assertEqual(counts["Benign"], 357)

    def test_raw_not_modified_by_cleaning(self):
        again = dl.load_raw(RAW_PATH)
        pd.testing.assert_frame_equal(self.raw, again)

    def test_missing_file_message(self):
        with self.assertRaises(FileNotFoundError):
            dl.load_raw(ROOT / "data" / "raw" / "does_not_exist.csv")

    def test_feature_names_match_scikit_learn(self):
        try:
            from sklearn.datasets import load_breast_cancer
        except ImportError:
            self.skipTest("scikit-learn not installed")
        sk = list(load_breast_cancer().feature_names)
        self.assertEqual(sk, dl.RAW_FEATURE_NAMES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
