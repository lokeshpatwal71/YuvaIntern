# Analytics Report & Insights Documentation

**Technology-Stock Performance Review, 1990 – 2022** — a complete business-analytics workflow on real monthly price data: business problem → business questions → dataset → data-quality checks → KPIs → analysis → visualisations → findings → insights → executive summary → recommendations → final report.

> **Built for:** Yuva Intern — *Analytics Report & Insights Documentation* ("Develop professional data analysis and reporting skills").
> **Author:** Lokesh Patwal · **Role:** Data Analyst Intern · **Internship period:** 01 October 2026 – 26 November 2026 · **Institution:** [YOUR COLLEGE] · **Mentor:** [MENTOR NAME]
> *(Replace the bracketed placeholders with your own details.)*

> **Educational notice.** This is a data-analysis exercise on historical prices. It is not investment advice. The investment club and its stakeholders are *assumed* for the exercise.

---

## Official objectives

1. **Define business objectives** – understand the business problem, reporting requirements, key questions and stakeholder expectations.
2. **Analyse data and identify findings** – trends, patterns, relationships, performance indicators and areas needing attention.
3. **Create meaningful visualisations** – clear charts and tables that communicate the findings.
4. **Generate business insights** – interpret what the results mean, their potential impact and the factors involved.
5. **Prepare an executive summary** – concise, stakeholder-friendly.
6. **Provide actionable recommendations** – practical, data-driven actions with priorities and next steps.

The evidence for each objective is in the [objective-to-evidence matrix](#objective-to-evidence-matrix).

## Business problem and dataset

**Problem (assumed scenario).** A small technology-focused investment club holds seven long-established technology shares (IBM, Apple, Microsoft, Xerox, Amazon, Alphabet, Adobe). Its committee wants to know which holdings created value, at what risk, how they behave when markets fall, and whether holding all seven together reduces risk. Eight business questions (Q1 – Q8) are defined in the notebook before any result is shown.

**Dataset.** `Stocks.csv` – monthly stock prices from Yahoo Finance, 524 rows × 11 columns (January 1990 – June 2022): seven holdings, Dell, the S&P 500 and the NASDAQ Composite. It is shipped inside Matplotlib's `sample_data` folder, so it needs no download, account or API key.

**Why not a sales dataset?** Most public data sites could not be reached from the environment where this project was built, and no retail or sales dataset was available offline. Nothing was invented; a real dataset was used. The same workflow applies to a sales dataset.

## Tools and technologies

| Tool | Purpose |
|---|---|
| Python 3 | language |
| pandas, NumPy | data handling, cleaning, KPI calculations |
| Matplotlib, Seaborn | charts |
| SciPy | Spearman rank correlation in the stress analysis |
| Jupyter notebook | the documented, reproducible analysis |
| pytest | automated tests |

## Repository structure

```
analytics-report-insights/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── processed/
│       ├── clean_monthly_prices.csv          cleaned monthly prices (390 months)
│       └── monthly_returns_common_window.csv monthly returns, Sep 2004 – Jun 2022
├── notebooks/
│   └── analytics_report_insights.ipynb       the complete, executed analysis
├── src/
│   ├── data_loader.py                        load the raw file, save CSVs
│   ├── data_cleaning.py                      quality checks and cleaning
│   ├── kpi_analysis.py                       KPI formulas
│   └── visualization.py                      chart functions
├── reports/
│   ├── executive_summary.md
│   ├── business_insights.md                  findings register + recommendations
│   ├── final_analytics_report.md
│   └── figures/                              12 charts (PNG)
└── tests/
    └── test_analysis.py
```

There is no `data/raw/` folder: the raw file is **not copied** into this repository (Yahoo's terms govern reuse of its data). It is read from the installed Matplotlib package at run time.

## Installation (Windows)

1. Install Python 3.10 or newer from <https://www.python.org/downloads/> and tick **Add Python to PATH**.
2. Open Command Prompt in the project folder and run:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Check that your Matplotlib contains the dataset:

```
python -c "from matplotlib.cbook import get_sample_data; print(get_sample_data('Stocks.csv', asfileobj=False))"
```

It should print a file path. If it raises an error, run `pip install --upgrade matplotlib`.

**Google Colab:** upload the project folder (or clone your GitHub repository), run `!pip install -r requirements.txt` in the first cell, and open the notebook. Colab already has most libraries.

> **Honesty note.** Everything was executed only with Python 3.13, numpy 2.5.3, pandas 3.0.5, matplotlib 3.11.2, seaborn 0.13.2 and scipy 1.18.1 on Linux. The Windows and Colab steps above were **not** tested on those systems.

## How to run

**Notebook:** `jupyter notebook`, open `notebooks/analytics_report_insights.ipynb`, then *Kernel → Restart & Run All*. The notebook:

* reads the raw data and shows the quality checks,
* writes the processed CSVs to `data/processed/`,
* regenerates all 12 charts into `reports/figures/`,
* ends with a cell that re-calculates every number quoted in the text and stops with an error if any differs.

So running the notebook **is** how the processed data and charts are regenerated.

**Tests:**

```
python -m pytest
```

## Main findings (calculated from the data)

Common window: September 2004 – June 2022 (214 months, 17.75 years). Dell has only 70 months of history and is excluded from comparisons.

| Finding | Evidence |
|---|---|
| Growth was very unequal | CAGR: Apple 35.9 %, Amazon 25.0 %, Alphabet 22.1 %, Adobe 16.4 %, Microsoft 16.3 %, IBM 6.1 %, Xerox −2.5 %; S&P 500 7.2 %, NASDAQ 10.5 % |
| Higher growth came with higher risk | Six of seven holdings fell further than the S&P 500 (−52.6 %) at their worst point; Xerox −75.5 %, Adobe −65.1 % |
| No holding was a safe haven | Every holding fell in every stress window tested (dot-com, 2007 – 09, early 2022) |
| Much of the risk is company-specific | The market explains only 24 % – 46 % of each holding's monthly movement |
| Diversification helped, but not enough | An equal-weight basket had about 31 % lower volatility than the average single stock, yet still fell 48.7 % at its worst |
| Extreme months cluster in crises | 21 of 1,917 monthly returns beyond ±3 standard deviations; 10 in 2008 – 09 |

Six prioritised recommendations (position-size caps, keeping a diversified basket, a regular stress-test report, a watch list for Xerox and IBM, investigating unusual months, improving the data) are in `reports/business_insights.md`. They are expected directions to be tested; **no financial return is promised**. Findings describe the past, show association not causation, and do not predict the future.

## Testing status (what was and was not run)

| Check | Status |
|---|---|
| Notebook, top to bottom | **Executed, 29 code cells, 0 errors**, using a custom Python runner (Jupyter could not be installed in the build environment). Please run *Restart & Run All* once in Jupyter. |
| Quoted numbers in the notebook text | **139 numbers re-calculated by the last notebook cell – all match** |
| `tests/test_analysis.py` (31 tests) | **All 31 passed** when run with a small stand-in test runner (pytest could not be installed there). **Real pytest has not been run**; please run `python -m pytest` yourself. |
| Charts | All 12 files exist and were viewed |
| Windows / Colab setup | **Not tested** |

## Dataset attribution and conditions

* **Dataset:** `Stocks.csv`, monthly prices. The first line of the file names its source: Yahoo Finance, <https://finance.yahoo.com>.
* **Distributed with:** Matplotlib (`matplotlib/mpl-data/sample_data/Stocks.csv`), <https://matplotlib.org>.
* **Conditions:** Yahoo Finance's own terms govern reuse of its data, so the raw file is not redistributed here. The code and text in this repository are the student's own work. No licence file has been added; add one (for example MIT) if you want others to reuse your code, and do not apply it to the dataset.

## Limitations

Prices only (no revenue, profit, volume, dividends or news), so causes cannot be identified; survivorship bias (well-known companies that still exist); the file does not say whether prices are adjusted; monthly data; June 2022 is a partial month; small samples (seven holdings, three stress windows); the club and stakeholders are assumed. See Section 14 of the final report.

**Future scope:** daily prices, dividends and fundamentals, more companies (including delisted ones), more stress windows, and a back-test of the recommendations. A retail or sales dataset could be analysed with the same workflow.

## Objective-to-evidence matrix

| Objective | Evidence (file and section) | Verified |
|---|---|---|
| 1. Define business objectives | Notebook Section 2; final report Sections 2 – 3 (background, problem, objectives, assumed stakeholders, Q1 – Q8, question → metric → chart → decision table) | ✅ content checked against the analyses |
| 2. Analyse data and identify findings | Notebook Sections 6 – 10; final report Sections 6 – 10; `src/` | ✅ notebook executed; 139 numbers re-calculated; 31 tests passed (stand-in runner) |
| 3. Create meaningful visualisations | `reports/figures/fig01 … fig12` (12 charts); final report Section 9 | ✅ files exist and were viewed |
| 4. Generate business insights | Notebook Section 10; final report Sections 10 – 11; `reports/business_insights.md` | ✅ |
| 5. Prepare an executive summary | `reports/executive_summary.md`; final report Section 1; notebook Section 11 | ✅ numbers match the notebook |
| 6. Provide actionable recommendations | `reports/business_insights.md` Section 3; final report Section 12; notebook Section 12 | ✅ each linked to findings F1 – F8 |
| Public GitHub repository | – | ⏳ **not done**; see below |

## Uploading to GitHub and submitting

Nothing has been uploaded for you. Create an **empty** repository named `analytics-report-insights` on <https://github.com> (no README, no `.gitignore`), then:

```
cd analytics-report-insights
git init
git add .
git commit -m "Add Analytics Report & Insights project"
git branch -M main
git remote add origin https://github.com/<your-username>/analytics-report-insights.git
git push -u origin main
```

Or, in the browser: *Add file → Upload files*, drag the **contents** of the project folder (keep the folder structure), and commit.

For the Yuva Intern submission, use the report file (Word version supplied separately), the written description requested by the form, and the repository link once it exists. Obtain any certificate or mentor approval from Yuva Intern yourself; none is included or implied here.

## Remaining manual actions

1. Open the notebook in Jupyter and run *Restart & Run All*; run `python -m pytest`.
2. Fill in the placeholders ([YOUR COLLEGE], [MENTOR NAME], enrolment number, repository URL) in `README.md` and `reports/final_analytics_report.md`.
3. Create the GitHub repository and push it.
4. Submit on the Yuva Intern platform.
