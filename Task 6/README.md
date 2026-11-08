# Final Data Science Capstone Project

## Predicting One-Year Diabetes Disease Progression from Baseline Patient Measurements

*A regression capstone with model comparison, error analysis and high-risk patient insights.*

> **Built for:** Yuva Intern - *Final Data Science Capstone Project* ("Showcase all learned skills in a comprehensive final project").
> **Author:** Lokesh Patwal (Data Science Intern) · **Internship period:** 01 October 2026 - 26 November 2026

> **Educational notice.** This is a learning project on a historical research dataset. It is **not** a medical device and gives **no** medical advice. The patient groups, assumed clinic and recommendations are analytical examples only.

---

## 1. Project summary

Using ten measurements taken when a patient first enters a diabetes study (age, sex, body-mass index, blood pressure and six blood-serum values), the project predicts a numeric score of **disease progression one year later**, measures how reliable the prediction is, explains where and why it fails, and finds which patient groups are at the highest risk of fast progression.

**Headline results (all calculated by the executed notebook):**

| Result | Value |
|---|---|
| Patients / predictors | 442 patients, 10 predictors, 1 numeric target |
| Data quality | 0 missing values, 0 duplicate rows |
| Train / test split | 353 / 89 patients (stratified, `random_state = 42`) |
| Selected model | **Linear Regression** (simplest of five statistically tied models) |
| Test RMSE / MAE / R² | **52.0** / **41.7** / **0.55** (95 % bootstrap interval for R²: 0.39 to 0.67) |
| Baseline (always predict the average) | RMSE 77.7, R² -0.00 |
| Improvement over baseline | RMSE **33 % lower**, MAE 37 % lower |
| Cross-validated RMSE / R² (training data) | 55.2 / 0.47 |
| Finding "fast progressors" (top 25 %), ROC-AUC | **0.92** (BMI alone 0.84) |

**Main findings.** BMI, serum triglycerides (`s5`) and blood pressure are the most dependable indicators of faster progression; engineered features did not improve prediction; flexible models (Random Forest, Gradient Boosting) were no better than a linear model; the model squeezes extreme predictions toward the average, so it is best used to **rank** patients rather than to give exact scores; about half of the variation is unexplained, so better data matters more than a more complex algorithm.

## 2. How the project was chosen

Three candidate projects were compared against the selection criteria (real, obtainable data; measurable objective; scope for cleaning, EDA and modelling; feasible with free tools):

| Candidate | Outcome |
|---|---|
| Customer churn prediction | Not chosen: the usual public dataset (Kaggle / IBM Telco) could not be downloaded in the build environment, and invented data would make every result meaningless |
| Employee attrition analysis | Not chosen: same data-access problem |
| **Diabetes disease-progression prediction** | **Chosen:** real, published research data available offline, numeric target, interpretable predictors, room for cleaning, EDA, several models and error analysis |

If you obtain the Telco churn CSV yourself you can reuse the structure of this project (`src/project_code.py` and the notebook sections) for a classification version.

## 3. Official objectives and where they are met

| # | Official objective | Evidence (file / notebook section) | Checked |
|---|---|---|---|
| 1 | Define the capstone problem | Notebook sections 1-3; report Chapters 1-2 | notebook executed; text reviewed |
| 2 | Collect and prepare data | Notebook sections 4-11; `src/project_code.py`; `data/`; report Chapters 4, 6, 7 | data checks executed; 32 tests pass |
| 3 | Apply data-science techniques | Notebook sections 12 and 15; report Chapter 8 | executed |
| 4 | Build and evaluate the solution | Notebook sections 12-13; `results/model_evaluation_results.csv`; `models/best_model.joblib`; report Chapter 9 | executed; saved model re-checked by a test |
| 5 | Analyse results, errors, limitations, improvements | Notebook sections 13.1, 14, 17, 19; report Chapters 9, 12 | executed |
| 6 | Generate insights and recommendations | Notebook sections 15-16; 17 charts in `visualizations/generated_charts/`; report Chapters 10-11 | executed |
| 7 | Document and present the capstone | `README.md`; `reports/Final Data Science Capstone Project.docx`; `presentation/Final_Project_Presentation.pptx`; `reports/Viva_Preparation.docx` | files created; see the honesty notes in section 11 |

## 4. Dataset

* **Name:** Diabetes dataset of Efron, Hastie, Johnstone and Tibshirani (2004), as distributed with scikit-learn (`sklearn.datasets.load_diabetes`).
* **Source named by scikit-learn:** <https://www4.stat.ncsu.edu/~boos/var.select/diabetes.html> (the page could not be opened from the build environment; the data were read from the copy bundled with scikit-learn). Paper: Efron B., Hastie T., Johnstone I., Tibshirani R. (2004), *Least Angle Regression*, Annals of Statistics 32(2), 407-499, <https://web.stanford.edu/~hastie/Papers/LARS/LeastAngle_2002.pdf>.
* **Size:** 442 patients, 10 predictors (`age`, `sex`, `bmi`, `bp`, `s1`-`s6`) and the target `progression` (25 to 346; no unit stated in the source).
* **Conditions of use:** a widely used public research dataset; scikit-learn states no separate data licence. It is used here for education with full citation.
* **Limitations:** only 442 patients, one source, unknown selection, undocumented sex codes, target without a unit, baseline values only.
* **Reproducible loading (no download, no account):**

```python
from sklearn.datasets import load_diabetes
frame = load_diabetes(as_frame=True, scaled=False).frame      # original, un-scaled units
```

A plain CSV copy is saved to `data/raw/diabetes_raw.csv` by the notebook.

## 5. Model comparison (selected by cross-validation only)

| Model | CV RMSE (train) | Test RMSE | Test MAE | Test R² |
|---|---|---|---|---|
| Ridge | 55.0 | 52.5 | 42.3 | 0.54 |
| Lasso | 55.0 | 52.6 | 42.6 | 0.54 |
| Linear Regression **(selected)** | 55.2 | 52.0 | 41.7 | 0.55 |
| Random Forest | 56.1 | 54.8 | 43.6 | 0.50 |
| Gradient Boosting | 56.2 | 55.2 | 43.9 | 0.49 |
| Decision Tree | 61.7 | 60.6 | 47.0 | 0.39 |
| Baseline (mean) | 76.9 | 77.7 | 66.6 | -0.00 |

Rule fixed in advance: among models within one standard error of the best cross-validated RMSE, choose the simplest. The test set was used once, at the end.

## 6. Project structure

```
Final_Data_Science_Capstone/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/diabetes_raw.csv                 original, un-scaled data (442 rows)
│   └── processed/diabetes_clean_features.csv  data + engineered columns + train/test label
├── notebooks/
│   └── Final_Data_Science_Capstone.ipynb    the complete, executed analysis
├── src/
│   └── project_code.py                      reusable, tested functions
├── models/
│   └── best_model.joblib                    selected model (Linear Regression pipeline)
├── visualizations/generated_charts/         17 charts (fig01 ... fig17)
├── reports/
│   ├── Final Data Science Capstone Project.docx            full report
│   └── Viva_Preparation.docx                viva questions, scripts, simple explanations
├── presentation/
│   └── Final_Project_Presentation.pptx      15 slides with speaker notes
├── results/
│   ├── model_evaluation_results.csv         all models: CV, train and test metrics
│   ├── test_predictions.csv                 actual vs predicted for the 89 test patients
│   └── key_results.json                     every number quoted in the notebook, report and slides
└── tests/
    └── test_project_code.py                 32 automated tests
```

## 7. Setup (Windows)

1. Install Python 3.10 or newer from <https://www.python.org/downloads/> (tick **Add python.exe to PATH**).
2. Open the project folder in Command Prompt or PowerShell:

```
cd Final_Data_Science_Capstone
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS / Linux use `source venv/bin/activate`.

**Google Colab (optional).** Upload the folder to Colab (or Google Drive), run `!pip install -r requirements.txt`, and open the notebook. Run it from the `notebooks/` folder so the relative paths work. *The Windows and Colab steps were written for you but not tested on those platforms.*

## 8. How to run

```
jupyter notebook                      # open notebooks/Final_Data_Science_Capstone.ipynb
```

Choose **Kernel → Restart & Run All**. A full run takes about two minutes. It re-creates the CSV copy in `data/raw/`, the processed data, the 17 charts, the model, `results/*` and verifies every quoted number. All random steps use `random_state = 42`.

To use the saved model on new data:

```python
import joblib, pandas as pd
bundle = joblib.load("models/best_model.joblib")
new = pd.DataFrame([{"age": 55, "sex_2": 0, "bmi": 31.0, "bp": 100, "s1": 190, "s2": 110, "s3": 40, "s4": 4.5, "s5": 5.0, "s6": 90}])
print(bundle["model"].predict(new[bundle["features"]]))   # illustrative values, not a real patient
```

(`sex_2` is 1 if the original sex code is 2, otherwise 0.)

## 9. Testing

```
python -m pytest -v
```

`tests/test_project_code.py` checks loading and validation, missing/duplicate/outlier detection, VIF, feature engineering boundaries, pipeline behaviour (missing input, no data leakage), metrics, bootstrap intervals, OLS, figure saving, and that the saved model reproduces the saved test predictions.

**Actual test status.** pytest could not be installed in the build environment. The 32 tests were executed with a small stand-in runner that supports the pytest features used (`raises`, `approx`, `fixture`, `tmp_path`): **32 passed, 0 failed**. *Real pytest has not been run;* please run `python -m pytest` yourself. Likewise the notebook was executed with a small custom executor (Jupyter could not be installed); a *Restart & Run All* in Jupyter on your computer is the recommended final check.

## 10. Limitations and future scope

* Small, single-source data with unknown selection; no external validation (the test R² interval is 0.39 to 0.67).
* Moderate predictive power: about half of the variation is unexplained; individual predictions can be 100 points off.
* Overlapping cholesterol measurements make individual coefficients unreliable; association is not causation.
* No Streamlit app or dashboard was built (not required for this assignment, and Streamlit could not be installed in the build environment). XGBoost and SHAP were also unavailable; scikit-learn Gradient Boosting and permutation importance were used instead.
* Future: external validation, richer data (repeat measurements, lifestyle, medication), interactions/splines, prediction intervals, fairness checks once the sex coding is documented, a simple risk dashboard.

## 11. Honesty notes

* Every number in the notebook, report and slides comes from the executed code (`results/key_results.json`).
* The data source page could not be opened from the build environment; provenance rests on the documentation shipped with scikit-learn.
* Word and PowerPoint files were checked by converting them to PDF and viewing the pages, not by opening them in Microsoft Office.
* No certificate or mentor approval is included or implied.

## 12. Uploading to GitHub

Nothing has been uploaded for you. Create an **empty** repository (no README, no `.gitignore`) named `Final_Data_Science_Capstone` on <https://github.com>, then:

```
cd Final_Data_Science_Capstone
git init
git add .
git commit -m "Add Final Data Science Capstone project"
git branch -M main
git remote add origin https://github.com/<your-username>/Final_Data_Science_Capstone.git
git push -u origin main
```

*Suggested repository description:* "Diabetes disease-progression prediction: regression, model comparison, error analysis and risk insights (Python, scikit-learn)."
*Suggested topics:* `data-science`, `machine-learning`, `regression`, `scikit-learn`, `pandas`, `jupyter-notebook`, `healthcare-analytics`, `internship-project`.

## 13. Remaining manual actions

1. Run the notebook once in Jupyter (*Restart & Run All*) and `python -m pytest` on your computer.
2. Read `reports/Viva_Preparation.docx` and be ready to explain every step in your own words.
3. Create the GitHub repository and push it (commands above); add its URL to the report.
4. Obtain any internship certificate or mentor approval from Yuva Intern yourself; none is included or implied here.
