# Real-World Dataset Analysis: Wisconsin Diagnostic Breast Cancer (WDBC)

## 1. Title and project details

| Field | Value |
|---|---|
| Project | Real-World Dataset Analysis Project (Yuva Intern) |
| Student name | Lokesh Patwal |
| Internship / program | Data Analyst Intern |
| Organization | Yuva Intern |
| Date | 24 October 2026 |
| Executed notebook | `notebooks/real_world_dataset_analysis.ipynb` |

All numbers in this report were produced by the executed notebook and are stored in `reports/key_results.json`. Nothing in this report is estimated or written from memory.

## 2. Abstract

This project analyses the Breast Cancer Wisconsin (Diagnostic) dataset: 569 digitised fine-needle-aspirate records, each with 30 numeric nucleus measurements and a benign/malignant diagnosis. A computed data-quality audit found **0 missing values, 0 duplicate rows and 0 invalid values**; the cleaning steps therefore standardised names and labels and flagged (not deleted) 171 records (30.1%) containing outlier values. The analysis shows that malignant records have much larger size and concavity measurements (for example `perimeter_worst`: 141.37 vs 87.01, +62.5%, Cohen's d = 2.60); that 27 of 30 features differ significantly between the classes; that the size features are almost redundant (r up to 0.998); that the malignant share rises from 1.8% to 96.5% between the lowest and highest ranges of `concave_points_worst`; and that outliers are concentrated in malignant cases and represent genuine variation. Nine charts support the findings.

## 3. Introduction

Fine-needle aspiration (FNA) is a minimally invasive way to sample a breast mass. In the WDBC dataset, a digitised image of the sample is processed and 10 properties of the cell nuclei (size, texture, shape irregularity) are computed; each is stored as a mean, a standard error and a "worst" (mean of the three largest) value. Understanding which properties differ between benign and malignant samples, and how reliable and redundant the measurements are, is a typical first step before any predictive work.

## 4. Problem statement

Which measurable properties of a cell nucleus differ most between benign and malignant breast masses, how strongly do they differ, and what must an analyst know about the data (redundancy between features, skewness, outliers, class balance) before using it for further modelling?

## 5. Objectives

1. Select a real-world dataset from a reliable source and understand its context.
2. Explore the dataset: structure, data types, distributions, missing values, duplicates, relationships.
3. Clean and preprocess the data.
4. Perform exploratory data analysis with Pandas, NumPy and statistical techniques.
5. Create meaningful visualisations.
6. Present insights, interpretations, conclusions and recommendations.

## 6. Dataset source and description

| Item | Detail |
|---|---|
| Name | Breast Cancer Wisconsin (Diagnostic), "WDBC" |
| Creators / publisher | W. H. Wolberg, W. N. Street, O. L. Mangasarian, University of Wisconsin; distributed by the UCI Machine Learning Repository |
| URL | <https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic> |
| Licence | Listed by UCI as CC BY 4.0 (attribution required). *Not re-verified in this build session because the UCI site was unreachable; please confirm on the dataset page.* |
| Copy used | `data/raw/wdbc_breast_cancer_raw.csv`, the copy bundled with scikit-learn 1.9.1 (569 rows, 30 features + class code). It was not diffed against a fresh UCI download. |
| Why suitable | Real clinical measurements; 30 numeric variables and a categorical label; enough rows for statistics; small enough for a student project; documented provenance. |
| Context | Medical diagnostics: separating malignant from benign breast masses from image-derived measurements. |
| Key variables | 10 base properties (radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension) × 3 forms (`_mean`, `_se`, `_worst`), and `diagnosis` (Malignant / Benign). |
| Known limitations | Single institution and era; no sample ID; measurement units not documented; 37% malignant share is a property of the sample, not the population. |

## 7. Analytical questions

Q1 class balance · Q2 distributions and skewness · Q3 malignant-vs-benign differences · Q4 correlations between features · Q5 malignant share across a key feature · Q6 outliers: errors or genuine variation.

## 8. Tools and technologies

Python 3.13.17, Jupyter notebook format, pandas 3.0.5, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, Seaborn 0.13.2, `unittest` / `pytest` for tests.

## 9. Methodology

Load raw data → inspect structure → audit data quality with computed checks → clean using justified rules (the raw file is never modified) → exploratory analysis where each analysis starts from a question → visualise → derive findings → conclusions and limitations. Reusable code is in `src/`; tests are in `tests/`.

## 10. Dataset exploration results

- Raw size: **569 rows × 31 columns** (30 float64 measurements + 1 integer class code).
- Class code mapping from the file header: 0 = malignant, 1 = benign.
- No identifier column and no text columns exist in the file.

Descriptive statistics of the 10 `_mean` features (from the cleaned data):

| Feature | mean | median | std | min | max | skew |
|---|---|---|---|---|---|---|
| radius_mean | 14.13 | 13.37 | 3.524 | 6.981 | 28.11 | 0.94 |
| texture_mean | 19.29 | 18.84 | 4.301 | 9.71 | 39.28 | 0.65 |
| perimeter_mean | 91.97 | 86.24 | 24.3 | 43.79 | 188.5 | 0.99 |
| area_mean | 654.9 | 551.1 | 351.9 | 143.5 | 2501 | 1.65 |
| smoothness_mean | 0.09636 | 0.09587 | 0.01406 | 0.05263 | 0.1634 | 0.46 |
| compactness_mean | 0.1043 | 0.09263 | 0.05281 | 0.01938 | 0.3454 | 1.19 |
| concavity_mean | 0.0888 | 0.06154 | 0.07972 | 0 | 0.4268 | 1.40 |
| concave_points_mean | 0.04892 | 0.0335 | 0.0388 | 0 | 0.2012 | 1.17 |
| symmetry_mean | 0.1812 | 0.1792 | 0.02741 | 0.106 | 0.304 | 0.73 |
| fractal_dimension_mean | 0.0628 | 0.06154 | 0.00706 | 0.04996 | 0.09744 | 1.30 |

Right skew is visible in the size features (mean above median; skew 0.94 for radius, 1.65 for area). Shape-irregularity features have the largest relative spread (coefficient of variation: `concavity_mean` 89.8%, `concave_points_mean` 79.3%).

## 11. Data-quality assessment

| Check | Result | Action |
|---|---|---|
| Missing values (all 31 columns) | 0 | none needed |
| Duplicate rows (all columns and 30 measurements) | 0 | none needed |
| Invalid values (positivity rules) | 0 | none needed |
| Impossible geometry (perimeter² < 4πA) | 0 | none needed |
| `worst ≥ mean` for all 10 properties | holds for every row | none needed |
| Zero values | 13 rows with zero concavity and zero concave points (same rows in all six concavity-type columns) | legitimate (convex outline), kept |
| Non-numeric feature columns | 0 | label decoded to text |
| Rows with ≥ 1 IQR outlier | 171 | flagged, not deleted |
| Features with \|skew\| > 1 | 22 of 30 | `log(1+x)` evaluated |

The dataset is already curated, so the audit honestly reports few problems.

## 12. Cleaning and preprocessing

| Step | Before | After |
|---|---|---|
| Rows | 569 | 569 |
| Columns | 31 | 32 (30 renamed measurements + `diagnosis` + `outlier_feature_count`) |
| Missing cells | 0 | 0 |
| Duplicate rows | 0 | 0 |
| Rows flagged as outlier | not computed | 171 |

Decisions: (1) column names renamed to `snake_case` with `_mean` / `_se` / `_worst` suffixes; (2) integer class code decoded to a categorical `diagnosis`; (3) missing-value strategy `"report"`, because nothing is missing and imputation would only add noise; (4) duplicates would be removed if found (none were); (5) outliers are **flagged, not removed**, because large nuclei are the signal being studied; (6) skewed features keep original values in the saved file. The cleaned file is `data/processed/wdbc_clean.csv`.

## 13. Statistical analysis

**Class balance.** 357 benign (62.74%) vs 212 malignant (37.26%).

**Group comparison** (Mann-Whitney U, effect size Cohen's d, separation AUC). 27 of 30 features differ at p < 0.05 and 26 after Bonferroni correction. The eight strongest features:

| Feature | Mean (malignant) | Mean (benign) | Difference of means (%) | Cohen's d | Separation AUC |
|---|---|---|---|---|---|
| perimeter_worst | 141.4 | 87.01 | +62.5 | 2.60 | 0.975 |
| radius_worst | 21.13 | 13.38 | +58.0 | 2.54 | 0.970 |
| area_worst | 1422 | 558.9 | +154.5 | 2.23 | 0.970 |
| concave_points_worst | 0.1822 | 0.07444 | +144.8 | 2.69 | 0.967 |
| concave_points_mean | 0.08799 | 0.02572 | +242.1 | 2.55 | 0.964 |
| perimeter_mean | 115.4 | 78.08 | +47.8 | 2.29 | 0.947 |
| area_mean | 978.4 | 462.8 | +111.4 | 2.08 | 0.938 |
| concavity_mean | 0.1608 | 0.04606 | +249.1 | 2.00 | 0.938 |

The weakest features are `texture_se` (AUC 0.512), `fractal_dimension_mean` (AUC 0.515), `smoothness_se` (AUC 0.531).

**Correlations.** Pairs with |r| ≥ 0.9 among the 10 mean features:

| Feature 1 | Feature 2 | Pearson r |
|---|---|---|
| radius_mean | perimeter_mean | 0.998 |
| radius_mean | area_mean | 0.987 |
| perimeter_mean | area_mean | 0.987 |
| concavity_mean | concave_points_mean | 0.921 |

Across all 30 features, 21 of 435 pairs have |r| ≥ 0.9.

**Malignant share by decile of `concave_points_worst`:**

| Decile | Mean worst concave points | Records | Malignant | Malignant share (%) |
|---|---|---|---|---|
| 1 | 0.020 | 58 | 1 | 1.7 |
| 2 | 0.050 | 56 | 0 | 0.0 |
| 3 | 0.065 | 57 | 2 | 3.5 |
| 4 | 0.079 | 57 | 1 | 1.8 |
| 5 | 0.091 | 57 | 5 | 8.8 |
| 6 | 0.110 | 58 | 12 | 20.7 |
| 7 | 0.138 | 55 | 26 | 47.3 |
| 8 | 0.163 | 57 | 51 | 89.5 |
| 9 | 0.193 | 57 | 57 | 100.0 |
| 10 | 0.239 | 57 | 57 | 100.0 |

**Outliers (IQR rule).** 171 records flagged: 53.8% of malignant vs 16.0% of benign; 2.21 vs 0.39 outlier features per record. Features with most outliers: `area_se` (65), `radius_se` (38), `perimeter_se` (38), `area_worst` (35).

**Skewness.** `log(1+x)` reduces `area_se` skewness from 5.45 to 0.85, but barely changes `fractal_dimension_se` (3.92 → 3.87) because its values are close to 0.

## 14. Visualisations with interpretations

![Figure 1](figures/fig01_class_bar.png)
**Figure 1: class balance.** 357 benign (62.7%) vs 212 malignant (37.3%).

![Figure 2](figures/fig02_hist_radius_mean.png)
**Figure 2: mean radius by diagnosis.** Means 12.15 (benign) vs 17.46 (malignant); the curves overlap in the middle range.

![Figure 3](figures/fig03_line_malignant_rate.png)
**Figure 3: malignant share across deciles of worst concave points.** Near 0–9% in the lowest five bins, 20.7%, 47.3%, 89.5% in bins 6–8, and 100% in the top two.

![Figure 4](figures/fig04_scatter_radius_vs_concave.png)
**Figure 4: mean radius vs mean concave points** (r = 0.82). The classes mix in the middle range (about radius 12–18).

![Figure 5](figures/fig05_boxplots_key_features.png)
**Figure 5: box plots.** Boxes for worst radius, perimeter and concave points barely overlap between the classes; mean texture overlaps far more.

![Figure 6](figures/fig06_corr_heatmap.png)
**Figure 6: correlation heatmap.** Radius, perimeter and area (r ≈ 0.99–1.00) and concavity / concave points / compactness (0.83–0.92) form redundant blocks.

![Figure 7](figures/fig07_feature_auc.png)
**Figure 7: separation AUC of all 30 features.** Best: `perimeter_worst` 0.975; weakest: `texture_se` 0.512.

![Figure 8](figures/fig08_skew_area_se.png)
**Figure 8: `area_se` before and after `log(1+x)`.** Skewness 5.45 → 0.85.

![Figure 9](figures/fig09_outlier_counts.png)
**Figure 9: features with most IQR outliers.** Led by `area_se` (65); mostly standard-error features.

## 15. Key findings supported by numbers

| # | Finding | Numerical evidence | Where |
|---|---|---|---|
| 1 | Mild class imbalance | 357 benign (62.74%) vs 212 malignant (37.26%) | Notebook Q1, Fig. 1 |
| 2 | Size and concavity features separate the classes strongly | `perimeter_worst` 141.37 vs 87.01 (+62.5%), d = 2.60, AUC 0.975; 27/30 features significant (26 after Bonferroni) | Q3, Figs. 5, 7 |
| 3 | Size features are almost redundant | r(radius, perimeter) = 0.998; r(radius, area) = 0.987; 21 of 435 pairs with \|r\| ≥ 0.9 | Q4, Fig. 6 |
| 4 | Malignancy rate jumps with worst concave points | 4 of 228 (1.8%) in lowest four deciles vs 165 of 171 (96.5%) in highest three | Q5, Fig. 3 |
| 5 | Outliers concentrate in malignant cases and are genuine | 171 of 569 rows (30.1%); 53.8% of malignant vs 16.0% of benign; 2.21 vs 0.39 outlier features per record | Q6, Fig. 9 |
| 6 | Heavy skew; three features carry no class signal | 22 of 30 features \|skew\| > 1; `texture_se`, `fractal_dimension_mean`, `smoothness_se` not significant (AUC 0.512, 0.515, 0.531) | Q2, Q3, Figs. 7, 8 |

## 16. Conclusions

The data are clean and strongly informative about the diagnosis. Malignant records have markedly larger size and concavity measurements; most features differ significantly between the classes; many features are redundant; and extreme values are genuine and concentrated in malignant cases rather than being errors.

## 17. Recommendations

1. Keep outlier records; flag rather than delete them.
2. Keep only one of radius / perimeter / area (or reduce dimensions) in any later model.
3. Prioritise the 'worst' size features and concave-point features; consider dropping the three non-significant features.
4. Apply `log(1+x)` only where it reduces skewness (e.g. `area_se`).
5. Report class-wise performance because of the 62.74% / 37.26% split.

## 18. Limitations and future scope

- The copy is curated: no missing values, duplicates or IDs, so the cleaning had little to repair, and per-patient duplicates cannot be checked.
- One institution and era; image-derived features; units undocumented; the 37% malignant share is a sample property.
- Associations only; no causal claims; no clinical use. The 30 tests are not independent.
- No date variable, so no time-trend analysis was possible.
- Future work: cross-validated interpretable model against the 62.74% baseline; replication on a second dataset; feature-interaction analysis.

## 19. References

1. Wolberg, W. H., Street, W. N., & Mangasarian, O. L. *Breast Cancer Wisconsin (Diagnostic)*. UCI Machine Learning Repository. <https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic>
2. Street, W. N., Wolberg, W. H., & Mangasarian, O. L. (1993). Nuclear feature extraction for breast tumor diagnosis. *Proc. SPIE 1905*.
3. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR* 12, 2825–2830 (source of the bundled data file).
4. pandas, NumPy, SciPy, Matplotlib and Seaborn documentation.

---

## Appendix: objective-to-evidence matrix

| Official objective | Implementation completed | Evidence produced | Notebook section / file | Verification status |
|---|---|---|---|---|
| 1. Select a real-world dataset | WDBC (UCI) chosen and documented: source, licence, context, variables, limitations | Dataset table; raw file; source citation | Notebook Sec. A, J; this report Sec. 6; `data/raw/wdbc_breast_cancer_raw.csv` | Verified: file loads, 569 × 30 and class counts match UCI documentation. **Not verified:** byte-level match to a fresh UCI download (UCI unreachable from build environment) |
| 2. Explore the dataset | Structure, dtypes, non-null counts, descriptive statistics, data dictionary, missing / duplicate / validity / skew / outlier audit | Printed tables and audit summary | Notebook Sec. C, D; Report Sec. 10, 11 | Verified: executed, 0 cell errors |
| 3. Clean and preprocess | Renaming, label decoding, missing / duplicate / invalid handling (none needed), outliers flagged, cleaned file saved | Before / after table (569 × 31 → 569 × 32); `wdbc_clean.csv` reloaded from disk and checked | Notebook Sec. E; `data/processed/wdbc_clean.csv`; `src/data_cleaning.py` | Verified: executed; raw file unchanged (equality check); 26 unit tests pass |
| 4. Perform EDA | Six question-driven analyses: balance, distribution / skew, group tests, correlations, rate by decile, outliers | Printed tables with p-values, effect sizes, AUC, correlations | Notebook Sec. F (Q1–Q6); Report Sec. 13 | Verified: executed; 17 consistency checks pass |
| 5. Create visualisations | Bar, histogram, line, scatter, box, heatmap, plus AUC bar, skew before / after, outlier bar | 9 PNG files, also embedded in the executed notebook | Notebook Sec. G; `reports/figures/fig01…fig09` | Verified: 9 images generated and viewed |
| 6. Present insights | Six numbered findings, conclusions, recommendations, limitations, this report | Sec. H outputs; this report; README | Notebook Sec. H–J; `reports/final_analysis_report.md` | Verified: findings are printed from calculated values; markdown numbers asserted against results |

**Execution status.** The notebook has 37 code cells, all executed top to bottom in one fresh session with 0 errors and no empty outputs. Jupyter was not available in the build environment, so the notebook was executed by a small custom runner that runs each cell in order and stores the real outputs and images in the `.ipynb`. To refresh the outputs with Jupyter, run `jupyter nbconvert --to notebook --execute --inplace notebooks/real_world_dataset_analysis.ipynb`. **Test status.** `python -m unittest discover -s tests -v`: 26 tests ran, 26 passed.
