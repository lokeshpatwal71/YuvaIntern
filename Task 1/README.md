# Data Science Fundamentals Assessment

Internship assessment project by **Lokesh Patwal** (Data Analyst Intern, Yuva Intern).

This repository contains the code, datasets and written report for a beginner-level
data science assessment. It covers Python basics, NumPy, pandas, statistics, data types,
data cleaning, exploratory data analysis (EDA) and visualization with Matplotlib and Seaborn.

## What is inside

| Folder / file | Description |
|---|---|
| `docs/Data_Science_Fundamentals_Assessment.docx` | The full assessment report (theory, 22-task practical, mini project) |
| `data/student_performance.csv` | Student dataset used in the practical assessment (123 rows, 10 columns) |
| `data/retail_sales.csv` | Retail sales dataset used in the mini project (305 rows, 9 columns) |
| `src/practical_assessment.py` | Solutions to the 22-task practical assessment |
| `src/mini_project_eda.py` | Mini project: EDA on retail sales data |
| `src/generate_data.py` | Script that regenerates both (synthetic) datasets |
| `examples/` | Small code examples for every concept in the report (01 to 07) |
| `figures/` | Charts created by the scripts |

## Setup

```bash
git clone https://github.com/<your-username>/data-science-fundamentals-assessment.git
cd data-science-fundamentals-assessment
python -m venv .venv
# Windows:  .venv\Scripts\activate      Mac/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## How to run

Run all commands from the repository root folder.

```bash
python src/practical_assessment.py
python src/mini_project_eda.py
python examples/01_python_fundamentals.py
```

To recreate the datasets: `python src/generate_data.py`

## Notes

- Both datasets are **synthetic** (created with fixed random seeds), so results are reproducible.
  They contain deliberate problems (missing values, duplicates, outliers, inconsistent text)
  to practise data cleaning.
- A chart window opens during `plt.show()`; close it to continue the script.

## Skills demonstrated

Python, NumPy, pandas, descriptive statistics, correlation, outlier detection, data cleaning,
encoding and scaling, EDA workflow, Matplotlib and Seaborn visualization, and clear
written reporting.

## License

MIT License. See `LICENSE`.
