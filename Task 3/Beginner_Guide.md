# Beginner Guide: Run, Understand and Explain the Project

*(English with Hindi hints where useful. / Jahan zaroori ho wahan Hindi mein bhi samjhaya hai.)*

## Part 1. Step-by-step execution guide

**Step 1: Install Python** (python.org/downloads; tick "Add python.exe to PATH"). Check: `python --version`.

**Step 2: Open the project folder** in CMD/PowerShell: `cd path\to\Real-World-Dataset-Analysis`

**Step 3: Create and activate a virtual environment** (a private box of libraries for this project)
```
python -m venv venv
venv\Scripts\activate
```
`(venv)` should appear at the start of the line.

**Step 4: Install the libraries:** `pip install -r requirements.txt`

**Step 5: Download the dataset** (free Kaggle account needed) and put `Global_Superstore2.csv` in the `data` folder. Details: `data/README.md`.

**Step 6: Check the code works** (optional): `python tests/test_pipeline.py`. It must end with `ALL TESTS PASSED`.

**Step 7: Run the notebook:** `jupyter notebook` -> open `real_world_dataset_analysis.ipynb` -> **Kernel > Restart & Run All**. Wait until every cell finishes (a few minutes at most). Red error text means something failed; see Troubleshooting below. Press **Ctrl+S** to save with outputs.

**Step 8: Look at your results:** the `outputs` folder now has charts, tables and `summary.json`.

**Step 8b: Word version of the notebook (optional):** `python src/notebook_to_docx.py` creates `real_world_dataset_analysis.docx` containing the notebook text, code and the saved outputs. Run it only after the notebook has been executed and saved.

**Step 9: Build the report:** `python src/build_report.py`. Open the `.docx`, read it fully, add your own sentences in the conclusion, set the submission date (top of `src/build_report.py`, `SUBMISSION_DATE`), rebuild, and save as PDF if needed.

**Step 10: Upload to GitHub** (the data file stays out because of `.gitignore`).

*Hindi hint:* pehle dataset download karo, phir notebook "Run All" karo. Jab tak aap notebook nahi chalate, koi asli number nahi aata. Isliye report abhi "template" hai.

## Part 2. The libraries in simple words

| Library | What it is | Used here for |
|---|---|---|
| **Python** | the programming language | everything |
| **Pandas** | tables of data (DataFrame) like Excel inside Python | loading, cleaning, `groupby`, filtering |
| **NumPy** | fast maths on arrays of numbers | calculations behind Pandas, `np.where`, log scale |
| **SciPy** (`scipy.stats`) | statistical tests | Spearman correlation, Kruskal-Wallis, Mann-Whitney |
| **Matplotlib** | basic charts | bar, line, histogram, scatter |
| **Seaborn** | prettier statistical charts | heatmaps, box plots |
| **Jupyter Notebook** | document with code + results + text | the main deliverable |
| **python-docx** | writes Word files | `build_report.py` |

## Part 3. Important functions and code explained

| Function / idea (file `src/analysis.py`) | What it does | Why |
|---|---|---|
| `find_data_file()` | looks for the dataset in `data/` or uses the path you give; clear error if missing | no hidden manual steps |
| `read_dataset()` | reads CSV/Excel; tries utf-8, then latin2, then latin-1 | the Kaggle CSV is not UTF-8 |
| `standardise_columns()` | `Sub-Category` -> `sub_category` | easy, safe names in code |
| `check_schema()` | stops with a clear message if essential columns are missing | handles unexpected column names |
| `detect_date_format()` | tries several date formats, picks the one that parses most values | `05-02-2013` can be 5 Feb or 2 May; this avoids guessing |
| `assess_quality()` | counts missing, duplicates, impossible values | measure before you clean |
| `step_...()` functions + `AuditLog` | seven cleaning steps; each writes rows before/after to a log | "never silently change the data" |
| `iqr_bounds()` | IQR rule: outlier if below Q1-1.5xIQR or above Q3+1.5xIQR | find unusual values |
| `agg_table(df, by)` | sales, profit, margin and loss share for each group | the engine of most EDA tables |
| `compute_results()` | runs all analyses and returns KPIs `K`, tables `T`, tests `S` | one place for all numbers |
| `build_insights()` | writes observation / evidence / significance / recommendation from the numbers | no invented numbers |
| `plot_...()` functions | draw each chart | consistent, labelled charts |

**Key Pandas ideas used**
* `df.groupby("category")["profit"].sum()` : split into groups, calculate, combine ("category-wise total profit").
* `df[df["profit"] < 0]` : filter rows (loss-making lines).
* `pd.to_datetime(...)` : text -> real dates, so we can extract year and month.
* `pd.cut(...)` : put numbers into bands (discount bands such as 0%, 1-10%, ...).
* `df.duplicated()` / `drop_duplicates()` : find / remove identical rows.

**Key statistics ideas**
* **Margin** = profit / sales. Negative = loss.
* **Median vs mean:** with skewed data (a few very large values) the median is a better "typical" value.
* **IQR rule** finds outliers; we **keep** them if they are genuine (large orders, real losses).
* **Correlation** (-1 to +1) shows how two numbers move together; **it never proves cause and effect.**
* **Spearman** uses ranks (robust to outliers). **Kruskal-Wallis / Mann-Whitney** compare groups without assuming a normal distribution.
* **p-value:** small (below 0.05) means "unlikely to be pure chance", but look at the *size* of the difference too.

*Hindi hint:* correlation ka matlab "saath-saath badhna/ghatna" hai, "ek cheez doosri ka kaaran hai" nahi.

## Part 4. Troubleshooting

| Error | Meaning | Fix |
|---|---|---|
| `FileNotFoundError: No dataset file found` | dataset not in `data/` | download it (`data/README.md`) or set `DATA_PATH` |
| `KeyError: These essential columns were not found` | column names differ | read the message; rename columns or edit `REQUIRED_COLUMNS` |
| `ModuleNotFoundError: No module named 'pandas'` (or scipy, seaborn, docx) | libraries not installed / venv not active | `venv\Scripts\activate` then `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'analysis'` | notebook started from the wrong folder | run `jupyter notebook` inside the project folder |
| Strange characters in names | text encoding | harmless; numbers are not affected |
| `UnicodeDecodeError` | unusual encoding | add the correct encoding to `ENCODINGS` at the top of `src/analysis.py` |
| Notebook cell stays `[*]` | still running | wait; large charts take a few seconds |
| `PermissionError` when saving report | the .docx is open in Word | close it and run again |
| PDF not created | LibreOffice/Word not found | open `.docx` in Word, *Save As* PDF |
| Assertion error in the cleaning validation cell | a check failed on your data | read the message; it shows which rule failed |
