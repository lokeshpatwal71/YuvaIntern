# Real-World Dataset Analysis: Wisconsin Diagnostic Breast Cancer (WDBC)

Yuva Intern project: *Analyze a real-world dataset and present findings.*

A complete, executed analysis of 569 real clinical records: data-quality audit, cleaning, exploratory analysis, 9 charts, 6 numbered findings, a final report and automated tests.

| | |
|---|---|
| Student | Lokesh Patwal |
| Program | Data Analyst Intern, Yuva Intern |
| Date | 24 October 2026 |

## Where to look first

1. **Executed notebook:** [`notebooks/real_world_dataset_analysis.ipynb`](notebooks/real_world_dataset_analysis.ipynb): every cell has real output and charts.
2. **Final report:** [`reports/final_analysis_report.md`](reports/final_analysis_report.md) (19 sections + objective-to-evidence matrix).
3. **Charts:** [`reports/figures/`](reports/figures/) (9 PNG files).

## Official objectives and evidence

| Objective | Evidence | Where |
|---|---|---|
| 1. Select a real-world dataset | UCI WDBC documented (source, licence, variables, limitations) | Notebook Sec. A, J · Report Sec. 6 |
| 2. Explore the dataset | Structure, dtypes, statistics, data dictionary, audit of missing / duplicate / invalid / skewed / outlier values | Notebook Sec. C, D |
| 3. Clean and preprocess | Before/after table (569 × 31 → 569 × 32), cleaned file reloaded and checked, raw file unchanged | Notebook Sec. E · `data/processed/wdbc_clean.csv` |
| 4. Exploratory data analysis | Six question-driven analyses with p-values, effect sizes, correlations | Notebook Sec. F (Q1–Q6) |
| 5. Visualisations | Bar, histogram, line, scatter, box, heatmap + 3 more | Notebook Sec. G · `reports/figures/` |
| 6. Insights and interpretations | 6 findings with numbers, conclusions, recommendations, limitations | Notebook Sec. H–J · Report |

The full matrix with verification status is at the end of the [final report](reports/final_analysis_report.md).

## Dataset

**Breast Cancer Wisconsin (Diagnostic)**: W. H. Wolberg, W. N. Street, O. L. Mangasarian, University of Wisconsin; UCI Machine Learning Repository: <https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic>. Listed by UCI as CC BY 4.0 (attribution required); please confirm on that page.

`data/raw/wdbc_breast_cancer_raw.csv` is the copy bundled with scikit-learn (`sklearn.datasets.load_breast_cancer`): 569 records × 30 numeric features + class code (212 malignant, 357 benign). It is never modified; the cleaned file is written to `data/processed/`. To recreate the raw file from scikit-learn (checked: the values equal the committed file):

```python
from sklearn.datasets import load_breast_cancer
import numpy as np, pandas as pd

d = load_breast_cancer()
out = "data/raw/wdbc_breast_cancer_raw.csv"
with open(out, "w") as fh:   # line 1 = metadata, as read by src/data_loader.py
    fh.write(f"{d.data.shape[0]},{d.data.shape[1]},{','.join(d.target_names)}\n")
pd.DataFrame(np.c_[d.data, d.target]).to_csv(out, mode="a", header=False, index=False)
```

## Project structure

```
README.md  requirements.txt  .gitignore  LICENSE
data/raw/wdbc_breast_cancer_raw.csv        original data (never edited)
data/processed/wdbc_clean.csv              cleaned data (written by the notebook)
notebooks/real_world_dataset_analysis.ipynb
src/data_loader.py  data_cleaning.py  analysis.py  visualization.py
tests/test_data_cleaning.py                26 automated tests
reports/final_analysis_report.md  key_results.json  figures/fig01…fig09
```

## Setup and run

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter notebook notebooks/real_world_dataset_analysis.ipynb   # Run > Run All Cells
# or, headless (refreshes outputs, charts, processed data and key_results.json):
jupyter nbconvert --to notebook --execute --inplace notebooks/real_world_dataset_analysis.ipynb
```

Running the notebook regenerates `data/processed/wdbc_clean.csv`, all 9 charts in `reports/figures/` and `reports/key_results.json`. A consistency cell at the end fails loudly if a number quoted in the text disagrees with the calculated results.

## Tests

```bash
python -m unittest discover -s tests -v     # or: pytest -v
```

Last run: 26 tests, 26 passed (normal cases, missing values, duplicates, empty input, unexpected columns, row preservation, real-data integration tests).

## Summary of actual findings

1. Mild class imbalance: 357 benign (62.74%) vs 212 malignant (37.26%).
2. Size and concavity features separate the classes strongly: `perimeter_worst` 141.37 vs 87.01 (+62.5%), Cohen's d = 2.60, AUC 0.975; 27 of 30 features differ significantly (26 after Bonferroni).
3. Size features are almost redundant: r(radius, perimeter) = 0.998; 21 of 435 feature pairs have |r| ≥ 0.9.
4. Malignant share rises from 1.8% (4 of 228, lowest four deciles of `concave_points_worst`) to 96.5% (165 of 171, highest three deciles).
5. 30.1% of records contain outliers: 53.8% of malignant vs 16.0% of benign. They pass all validity checks and are kept (flagged).
6. 22 of 30 features are strongly skewed; three features (`texture_se`, `fractal_dimension_mean`, `smoothness_se`) show no significant class difference.

## Honest notes and limitations

- The dataset is already curated: **0 missing values, 0 duplicates, 0 invalid values** were found, and the report says so rather than inventing problems.
- The notebook was executed with a small custom runner because Jupyter could not be installed in the build environment; outputs and images are real. Re-running it with Jupyter (command above) is recommended before submission.
- The raw file is scikit-learn's bundled copy; it was not diffed against a fresh UCI download (UCI was unreachable from the build environment).
- One institution and era, no sample IDs, undocumented units, 37% malignant share is a sample property. Findings are associations, not causation, and not for clinical use.

## References

Wolberg, Street & Mangasarian, *Breast Cancer Wisconsin (Diagnostic)*, UCI ML Repository · Street, Wolberg & Mangasarian (1993), Nuclear feature extraction for breast tumor diagnosis, *Proc. SPIE 1905* · Pedregosa et al. (2011), scikit-learn, *JMLR* 12.

Code licence: MIT (see `LICENSE`). The data keeps its own licence and attribution requirement.
