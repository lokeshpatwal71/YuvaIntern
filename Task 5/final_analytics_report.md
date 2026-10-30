# Analytics Report & Insights Documentation
## Final Analytics Report: Technology-Stock Performance Review, 1990 – 2022

| | |
|---|---|
| **Project title** | Analytics Report & Insights Documentation |
| **Programme** | Yuva Intern |
| **Student name** | Lokesh Patwal |
| **Internship / role** | Data Analyst Intern |
| **Roll / enrolment number** | [YOUR ENROLMENT NUMBER] |
| **Institution and branch** | [YOUR COLLEGE, B.Tech BRANCH] |
| **Internship period** | 01 October 2026 to 26 November 2026 |
| **Mentor** | [MENTOR NAME] |
| **Repository** | [GITHUB URL after you upload it] |
| **Date of submission** | 28 October 2026 |

*Placeholders in square brackets must be filled in by the student. No mentor approval or certificate is stated or implied by this document.*

> **Educational notice.** This is a data-analysis exercise on historical prices. It is not investment advice. The investment club and its stakeholders are *assumed* for the exercise.


## 1. Executive summary

**Business problem.** An (assumed) technology-focused investment club asked which of its seven long-held technology shares created value, at what risk, and whether holding them together reduces risk.

**Data.** Real monthly Yahoo Finance prices from January 1990 to June 2022 (390 months after cleaning) for IBM, Apple, Microsoft, Xerox, Amazon, Alphabet and Adobe, plus the S&P 500 and NASDAQ Composite. Dell is in the file but has only 70 months of history. Comparisons use a common window of 17.75 years (September 2004 – June 2022).

**Key metrics (common window).** Apple CAGR 35.9 %, Amazon 25.0 %, Alphabet 22.1 %, Adobe 16.4 %, Microsoft 16.3 %, IBM 6.1 %, Xerox −2.5 %, against 7.2 % (S&P 500) and 10.5 % (NASDAQ). Annual volatility ranged from 20.9 % to 36.3 % for the holdings, against 14.7 % for the S&P 500.

**Major findings.**
1. Growth was concentrated in Apple, Amazon and Alphabet; IBM and Xerox did not beat the market.
2. Growth came with risk: six of seven holdings fell further than the S&P 500 at their worst point (Xerox −75.5 %, Adobe −65.1 %).
3. Every holding fell in every market-stress window tested; no holding was a safe haven.
4. Market movements explain only 24 %–46 % of each holding's monthly changes, so company-specific risk is large.
5. An equal-weight basket had about 31 % lower volatility than the average single stock, but still fell 48.7 % at its worst.

**Overall conclusion.** Holding all seven reduced risk without lowering growth below the single-stock average, but position sizes, stress testing and a review of the weakest holdings (Xerox, IBM) are the main decisions the data point to.

**Important limitations.** Prices only (no financials); survivorship bias; unclear price adjustments; monthly data; a partial final month; findings describe the past and do not prove causes or predict the future.

## 2. Business background and problem statement

### 2.1 Business background
A small technology-focused investment club (an *assumed* organisation used for this exercise) holds shares in seven long-established technology companies: **IBM, Apple, Microsoft, Xerox, Amazon, Alphabet (Google) and Adobe**. Once a year its investment committee reviews how each holding has performed and how risky it has been, compared with the broad market (the **S&P 500** index) and the technology-heavy **NASDAQ Composite** index. Dell is also in the dataset but has only a short price history.

### 2.2 Problem statement
The committee has price histories but no consolidated analysis. It needs to know **which holdings created value, how much risk was taken to get it, how the holdings behave when markets fall, and whether holding all seven together reduces risk**, so it can decide where to keep, review or limit its positions.

## 3. Business objectives and analytical questions

### 3.1 Business objectives
1. Measure the growth and risk of each holding on a fair, comparable basis.
2. Understand how closely each holding follows the market and how it behaved in past market downturns.
3. Check whether combining the holdings lowers risk.
4. Identify unusual months that deserve investigation.
5. Turn the evidence into prioritised, testable recommendations.

### 3.2 Stakeholders (assumed, for this exercise)
| Stakeholder | What they need from the report |
|---|---|
| Investment committee chair | A one-page summary and clear recommendations |
| Portfolio manager | Return, risk and ranking of each holding |
| Risk manager | Drawdowns, stress behaviour, extreme months |

### 3.3 Key business questions
| ID | Business question |
|---|---|
| Q1 | Which holdings created the most value, and how does that compare with the market indices? |
| Q2 | How risky was each holding (volatility, largest falls, spread of monthly returns)? |
| Q3 | Which holdings delivered the most growth for the risk taken? |
| Q4 | How strongly does each holding follow the market (beta, correlation)? |
| Q5 | How did the holdings behave in past market-stress periods? |
| Q6 | Does holding all seven together reduce risk? |
| Q7 | How consistent were returns from year to year? |
| Q8 | Which months were unusual, and when did they happen? |

### 3.4 Reporting requirements: question → metric → visual → decision
| Question | Metrics needed | Visual / table | Decision it supports |
|---|---|---|---|
| Q1 | Total return, CAGR | Fig 1, Fig 2, KPI tables | Which holdings stay as core positions |
| Q2 | Annualised volatility, maximum drawdown, monthly-return spread | Fig 4, Fig 5, Fig 6 | How large each position should be |
| Q3 | Return-to-risk ratio | Fig 3 | How to rank holdings for allocation |
| Q4 | Beta, correlation with S&P 500 | Fig 7, Fig 8 | How much market exposure the club carries |
| Q5 | Largest fall inside defined stress windows | Fig 9 | Whether risk limits and stress tests are needed |
| Q6 | Average pairwise correlation, equal-weight basket volatility and drawdown | Fig 10, Fig 12 | Whether to keep a diversified basket |
| Q7 | Calendar-year returns, share of positive years | Fig 11 | What return consistency to expect |
| Q8 | Months more than 3 standard deviations from a stock's own average | Outlier table | Which events to investigate |

## 4. Dataset source and description

| Item | Detail |
|---|---|
| **Name** | `Stocks.csv` – monthly stock prices |
| **Original source** | Yahoo Finance, <https://finance.yahoo.com> (stated in the first line of the file) |
| **How it is accessed** | The file is part of Matplotlib's `sample_data` folder (`matplotlib.cbook.get_sample_data("Stocks.csv")`). It is read from the installed Matplotlib package: no download, account or API key is needed. |
| **Publisher / usage conditions** | Prices come from Yahoo Finance; Matplotlib distributes the file with its documentation examples. Yahoo's own terms govern reuse of its data, so this repository **does not copy the raw file**; it reads it from Matplotlib at run time. |
| **Size and period** | 524 rows × 11 columns, 1990-01-01 to 2022-06-28 (details in Section 6) |
| **Columns** | `Date` plus ten price columns (data dictionary below) |
| **Business context** | Long-run price history of well-known technology companies and two US stock-market indices |
| **Why it was chosen** | It is real data from a recognised source, is available without internet access or credentials, has a long period (over 32 years), and supports return, risk, market-relationship, stress-period and diversification analysis |
| **Limitations and biases** | Prices only (no revenue, profit, volume, dividends or company information); the companies are today's well-known names (survivorship bias); monthly frequency; the file does not state whether prices are adjusted. See Section 14. |

> **Why not a sales dataset?** The working environment for this project could not reach most public data sites (for example data portals and the UCI repository), and no retail or sales dataset with clear reuse terms was available offline. Rather than invent data, the project uses this real dataset. If a sales dataset is preferred, the same workflow (business questions → KPIs → charts → insights → recommendations) applies.

**Data dictionary**

| Column | Meaning | Type | Unit |
|---|---|---|---|
| `Date` | Date of the monthly observation (normally the first day of the month) | text → date | – |
| `IBM`, `AAPL`, `MSFT`, `XRX`, `AMZN`, `DELL`, `GOOGL`, `ADBE` | Monthly price of IBM, Apple, Microsoft, Xerox, Amazon, Dell, Alphabet (Google Class A), Adobe | decimal | Assumed US dollars per share (not stated in the file) |
| `^GSPC` | S&P 500 index level | decimal | Index points |
| `^IXIC` | NASDAQ Composite index level | decimal | Index points |

## 5. Methodology and tools

**Workflow.** Business problem → business questions → dataset selection → data-quality checks → cleaning → KPI definition → analysis → visualisation → findings → insights → executive summary → recommendations.

1. **Business understanding first.** The problem, stakeholders (assumed), eight questions and the question → metric → chart → decision mapping (Section 3.4) are placed before any result in both the notebook and this report.
2. **Dataset selection.** A real dataset from a recognised source was needed, available without credentials. Most public data sites could not be reached from the working environment and no retail or sales dataset was available offline; none was invented (see Section 4).
3. **Reusable code.** Loading, cleaning, KPI and chart functions are in `src/` and are covered by automated tests in `tests/test_analysis.py`.
4. **Reproducible notebook.** `notebooks/analytics_report_insights.ipynb` runs top to bottom. Its last cell re-calculates every number quoted in the notebook text (139 numbers) and stops with an error if any differ.
5. **Interpretation rules.** Observed facts, interpretations and hypotheses are kept apart. Association is never presented as causation.

| Tool | Version used when the notebook was executed | Purpose |
|---|---|---|
| Python | 3.13 | language |
| pandas | 3.0.5 | tables, cleaning, KPIs |
| NumPy | 2.5.3 | numerical calculations |
| Matplotlib / Seaborn | 3.11.2 / 0.13.2 | charts |
| SciPy | 1.18.1 | rank correlation (Spearman) in the stress analysis |
| Jupyter notebook format (`.ipynb`) | – | interactive, documented analysis |

*The notebook was executed with a custom Python runner, not the Jupyter application (Jupyter could not be installed in the build environment). Re-running it in Jupyter is a recommended manual check.*


## 6. Data-quality assessment

Checks were run on the raw file exactly as stored.

| Check | Result |
|---|---|
| Rows | 524 |
| Columns | 11 |
| First date | 1990-01-01 |
| Last date | 2022-06-28 |
| Dates in increasing order | True |
| Rows with no price at all | 133 |
| Exact duplicate rows | 0 |
| Duplicate dates | 0 |
| Extra rows in an already-seen month | 1 |
| Prices that are zero or negative | 0 |
| Missing price cells (all columns) | 1915 |

**Missing values by column (raw file)**

| Column | Missing cells | Share |
|---|---|---|
| IBM | 133 | 25.4% |
| AAPL | 133 | 25.4% |
| MSFT | 133 | 25.4% |
| XRX | 133 | 25.4% |
| AMZN | 222 | 42.4% |
| DELL | 453 | 86.5% |
| GOOGL | 309 | 59.0% |
| ADBE | 133 | 25.4% |
| ^GSPC | 133 | 25.4% |
| ^IXIC | 133 | 25.4% |

**Check 1 – rows without any price.** The table above shows 133 missing values in *every* column, which suggests the same rows are empty across all columns. A second check confirmed it.

**Interpretation.** 133 rows (25.4 % of the file) contain a date but no price in any column. They all fall in February, May, August or November, roughly once per quarter, on days other than the 1st. They are placeholder rows, not months with missing data, and carry no information. They are removed in the cleaning step. This is a fact established by the code above; why Yahoo's export contains them is not documented in the file.

**Interpretation.** After the empty rows are ignored, Amazon, Alphabet and Dell still have missing values, but only *before* their first price (Amazon from June 1997, Alphabet from September 2004, Dell from September 2016). These gaps are real: the company had no price in the file yet. They are **not filled in**, because inventing prices would distort returns. Dell has only 70 months of prices once the duplicate June 2022 row is removed, so it is not compared with the longer histories.

**Interpretation.** There are no exact duplicate rows and no repeated dates. However, June 2022 appears twice (dated 2022-06-01 and 2022-06-28) and all ten prices are identical. The second row is a duplicate of the same month, and it also shows that the June 2022 value is a price **as of 28 June 2022**, so June 2022 is a partial month. The duplicate row is removed, and the partial month is kept and noted as a limitation.

**Interpretation.** Every price is above zero, so percentage returns can be calculated. The wide ranges (for example Alphabet's maximum above 2,900 and Apple's minimum of 0.10) are consistent with long histories, and with prices that have been adjusted for share splits. The file does not say which adjustments were made; this is documented as an assumption in Section 14.

**Check – are the fields suitable for the planned KPIs?**

| KPI group | Fields needed | Available? |
|---|---|---|
| Total return, CAGR, volatility, drawdown, beta, correlation | Monthly price per ticker | Yes |
| Calendar-year returns | December price of each year | Yes |
| Revenue, profit, margin, trading volume, dividend yield | Company financials, volume, dividends | **No – not in the file, so none of these are calculated** |

## 7. Data cleaning and preprocessing

Cleaning steps, each justified by a finding in Section 6:
1. Convert `Date` to a real date.
2. Remove the 133 rows with no price.
3. Keep only the first row of each calendar month (removes the duplicate June 2022 row).
4. Use the month as the table index. Remaining missing values (before a company's first price) are left as missing.

The raw data are never modified; the cleaned table is a new object.

**Before and after**

| Measure | Before cleaning | After cleaning |
|---|---|---|
| Rows | 524 | 390 |
| Rows with no price | 133 | 0 |
| Repeated-month rows | 1 | 0 |
| Missing price cells | 1915 | 585 |
| First date | 1990-01-01 | 1990-01-01 |
| Last date | 2022-06-28 | 2022-06-01 |

**Interpretation.** The file shrinks from 524 rows to 390, which is exactly 32 years and 6 months of monthly data (January 1990 to June 2022). The 585 remaining missing cells are all the "before first listing" gaps shown above (Amazon 89, Alphabet 176, Dell 320).

**Comparable-period decision.** Companies enter the data at different dates, so comparing a 1990 start with a 2004 start would be unfair. The analysis therefore uses two views:
* **Full history** – each series over its own available months (shows long-run behaviour).
* **Common window** – the same months for all seven holdings and both indices, from the month Alphabet first has a price. All rankings and risk comparisons use this window.

Dell is shown in the full-history KPI table for completeness, and excluded from the common-window comparison.

## 8. KPI definitions and results

| KPI | Business purpose | Exact formula | Columns needed | Limitation |
|---|---|---|---|---|
| **Total return** | How much value grew over the period | last price ÷ first price − 1 | monthly price | Ignores dividends unless prices are adjusted |
| **CAGR** | Average yearly growth rate that is comparable between different lengths of history | (last ÷ first) ^ (1 ÷ years) − 1, where years = number of monthly returns ÷ 12 | monthly price | Hides the ups and downs on the way |
| **Annualised volatility** | How much returns fluctuate (risk) | standard deviation of monthly returns × √12 | monthly returns | Treats ups and downs alike |
| **Maximum drawdown** | Worst fall from a previous high (what an investor could have experienced) | min over time of (price ÷ highest price so far − 1) | monthly price | Based on month-end prices, so daily falls would be deeper |
| **Return-to-risk ratio** | Growth per unit of risk | CAGR ÷ annualised volatility (risk-free rate assumed 0) | CAGR, volatility | Simplified Sharpe-style ratio; a 0 % risk-free rate is an assumption |
| **Beta** | Sensitivity to the market | covariance(stock, S&P 500) ÷ variance(S&P 500), monthly returns | monthly returns | Describes association in the past, not a cause |
| **Correlation** | Strength of the linear link between two return series | Pearson correlation of monthly returns | monthly returns | Only linear relationships |
| **Share of positive months / years** | Consistency | months (years) with return > 0 ÷ all months (years) | returns | Ignores size of gains and losses |

All KPIs are in percentages or ratios, so no currency is needed. A *monthly return* is `price(t) ÷ price(t−1) − 1`. These formulas are implemented in `src/kpi_analysis.py` and tested in `tests/test_analysis.py`.

### 8.1 KPI results: common window (September 2004 – June 2022, same months for every series)

| Series | From | Months | Total return | CAGR | Volatility | Return / risk | Max drawdown | Beta | Corr. with S&P | Positive months |
|---|---|---|---|---|---|---|---|---|---|---|
| IBM | 2004-09 | 214 | 183.7% | 6.1% | 20.9% | 0.29 | -37.2% | 0.82 | 0.58 | 54.0% |
| AAPL | 2004-09 | 214 | 23,130.3% | 35.9% | 33.1% | 1.09 | -56.9% | 1.25 | 0.56 | 61.5% |
| MSFT | 2004-09 | 214 | 1,358.5% | 16.3% | 22.8% | 0.72 | -55.2% | 0.99 | 0.64 | 62.4% |
| XRX | 2004-09 | 214 | -36.1% | -2.5% | 35.2% | -0.07 | -75.5% | 1.57 | 0.66 | 51.2% |
| AMZN | 2004-09 | 214 | 5,157.0% | 25.0% | 36.3% | 0.69 | -54.2% | 1.20 | 0.49 | 59.2% |
| GOOGL | 2004-09 | 214 | 3,353.6% | 22.1% | 30.1% | 0.73 | -58.6% | 1.08 | 0.53 | 60.6% |
| ADBE | 2004-09 | 214 | 1,379.2% | 16.4% | 29.5% | 0.56 | -65.1% | 1.36 | 0.68 | 63.8% |
| S&P 500 | 2004-09 | 214 | 242.9% | 7.2% | 14.7% | 0.49 | -52.6% | 1.00 | 1.00 | 64.8% |
| NASDAQ | 2004-09 | 214 | 489.5% | 10.5% | 17.5% | 0.60 | -51.8% | 1.12 | 0.94 | 61.0% |

### 8.2 KPI results: each series over its own full history

| Series | From | Months | Total return | CAGR | Volatility | Return / risk | Max drawdown | Beta | Corr. with S&P | Positive months |
|---|---|---|---|---|---|---|---|---|---|---|
| IBM | 1990-01 | 390 | 1,193.1% | 8.2% | 26.5% | 0.31 | -62.8% | 1.00 | 0.55 | 53.2% |
| AAPL | 1990-01 | 390 | 56,573.4% | 21.6% | 42.4% | 0.51 | -79.6% | 1.28 | 0.44 | 56.8% |
| MSFT | 1990-01 | 390 | 63,423.0% | 22.0% | 30.4% | 0.73 | -66.9% | 1.22 | 0.59 | 62.0% |
| XRX | 1990-01 | 390 | 41.2% | 1.1% | 41.1% | 0.03 | -92.1% | 1.58 | 0.56 | 54.5% |
| AMZN | 1997-06 | 301 | 139,230.3% | 33.6% | 58.8% | 0.57 | -93.1% | 1.77 | 0.47 | 59.0% |
| DELL | 2016-09 | 70 | 267.4% | 25.4% | 29.0% | 0.88 | -41.3% | 0.84 | 0.46 | 66.7% |
| GOOGL | 2004-09 | 214 | 3,353.6% | 22.1% | 30.1% | 0.73 | -58.6% | 1.08 | 0.53 | 60.6% |
| ADBE | 1990-01 | 390 | 26,413.0% | 18.8% | 44.7% | 0.42 | -75.3% | 1.45 | 0.48 | 59.4% |
| S&P 500 | 1990-01 | 390 | 1,061.3% | 7.9% | 14.7% | 0.54 | -52.6% | 1.00 | 1.00 | 64.0% |
| NASDAQ | 1990-01 | 390 | 2,589.2% | 10.7% | 21.6% | 0.49 | -75.0% | 1.25 | 0.85 | 61.2% |

**How to read these tables.** Use the *common window* table to compare holdings with each other, because every row covers exactly the same months. Use the *full history* table to see long-run behaviour (for example Microsoft or Apple since 1990). Dell appears only in the full-history table.

## 9. Detailed analysis and visualisations

Each subsection gives the business question, the method, the result (chart and table) and an interpretation that separates **observed facts** from **interpretations** and **hypotheses**.

### 9.1 Q1. Which holdings created the most value compared with the market?

**Method:** CAGR and total return, over each series' full history (Fig 1) and over the common window (Fig 2, value of 100 invested in September 2004).

![Fig 1. CAGR of each series over its own available history](figures/fig01_cagr_full_history.png)

*Figure 1. CAGR of each series over its own available history*

![Fig 2. Growth of 100 invested in September 2004 (log scale)](figures/fig02_growth_of_100_common_window.png)

*Figure 2. Growth of 100 invested in September 2004 (log scale)*

**Value of 100 invested in September 2004, by June 2022**

| Series | Value of 100 in June 2022 |
|---|---|
| AAPL | 23,230 |
| AMZN | 5,257 |
| GOOGL | 3,454 |
| ADBE | 1,479 |
| MSFT | 1,459 |
| NASDAQ | 589 |
| S&P 500 | 343 |
| IBM | 284 |
| XRX | 64 |


**Observed facts (common window, 17.75 years).**
* Apple grew fastest (CAGR **35.9 %**), then Amazon (**25.0 %**) and Alphabet (**22.1 %**). Adobe (**16.4 %**) and Microsoft (**16.3 %**) were almost equal. IBM grew **6.1 %** a year, below the S&P 500 (**7.2 %**). Xerox lost value (**−2.5 %** a year; a 100 investment fell to about **64**).
* Five of the seven holdings grew faster than the NASDAQ Composite (**10.5 %**).
* Over the full history, Microsoft (**22.0 %**), Apple (**21.6 %**) and Adobe (**18.8 %**) grew far faster than the S&P 500 (**7.9 %**) and NASDAQ (**10.7 %**); IBM (**8.2 %**) was close to the S&P 500; Xerox managed **1.1 %**. Amazon has grown **33.6 %** a year since June 1997.

**Interpretation.** Growth was very unequal. Three holdings (Apple, Amazon, Alphabet) account for the largest gains; two (IBM, Xerox) did not beat the broad market.

**Limitations.** These companies are well-known names that exist today, so the set is likely to look better than a random selection of 1990 technology companies (survivorship bias). If the file's stock prices are adjusted for dividends but the index levels are not, the stocks have a small built-in advantage over the indices. The causes of each company's performance are not in this dataset.

### 9.2 Q2. How risky was each holding?

**Method:** annualised volatility, maximum drawdown (Fig 4), and the spread of monthly returns (Fig 5 box plot, Fig 6 histograms). Fig 3 plots growth against volatility.

![Fig 3. Growth against risk, common window](figures/fig03_risk_vs_return.png)

*Figure 3. Growth against risk, common window*

![Fig 4. Fall from previous high, common window](figures/fig04_drawdowns.png)

*Figure 4. Fall from previous high, common window*

![Fig 5. Spread of monthly returns](figures/fig05_monthly_return_boxplot.png)

*Figure 5. Spread of monthly returns*

![Fig 6. Distribution of monthly returns](figures/fig06_monthly_return_histograms.png)

*Figure 6. Distribution of monthly returns*

**Largest fall, common window**

| Series | Max drawdown | Peak month | Trough month |
|---|---|---|---|
| IBM | -37.2% | 2013-03 | 2016-01 |
| AAPL | -56.9% | 2007-12 | 2008-12 |
| MSFT | -55.2% | 2007-10 | 2009-02 |
| XRX | -75.5% | 2007-05 | 2009-03 |
| AMZN | -54.2% | 2007-09 | 2008-11 |
| GOOGL | -58.6% | 2007-10 | 2008-11 |
| ADBE | -65.1% | 2007-10 | 2009-02 |
| S&P 500 | -52.6% | 2007-10 | 2009-02 |
| NASDAQ | -51.8% | 2007-10 | 2009-02 |

**Largest fall over each series' full history**

| Series | Max drawdown | Peak month | Trough month |
|---|---|---|---|
| IBM | -62.8% | 1991-02 | 1993-09 |
| AAPL | -79.6% | 1991-03 | 1997-12 |
| MSFT | -66.9% | 1999-12 | 2009-02 |
| XRX | -92.1% | 1999-01 | 2000-12 |
| AMZN | -93.1% | 1999-03 | 2001-09 |
| GOOGL | -58.6% | 2007-10 | 2008-11 |
| ADBE | -75.3% | 2000-09 | 2002-09 |
| S&P 500 | -52.6% | 2007-10 | 2009-02 |
| NASDAQ | -75.0% | 2000-02 | 2002-09 |


**Observed facts.**
* Volatility (common window): S&P 500 **14.7 %**, NASDAQ **17.5 %**; the holdings ranged from **20.9 %** (IBM) to **36.3 %** (Amazon). Xerox (**35.2 %**) and Apple (**33.1 %**) were also high.
* Largest falls (common window): Xerox **−75.5 %**, Adobe **−65.1 %**, Alphabet **−58.6 %**, Apple **−56.9 %**, Microsoft **−55.2 %**, Amazon **−54.2 %**, against **−52.6 %** for the S&P 500. IBM's largest fall (**−37.2 %**) was the smallest. Six of the seven holdings fell further than the S&P 500 at their worst point.
* Six holdings reached their peak in 2007 and their low between November 2008 and March 2009. IBM's largest fall was a different, slower episode (March 2013 to January 2016).
* Over the full history, Amazon fell **93.1 %** (March 1999 to September 2001) and Xerox **92.1 %** (January 1999 to December 2000) before the data show any recovery.
* Box plot and histograms: all holdings have a positive median monthly return, but their monthly returns are much more spread out than the indices', with long tails on both sides.

**Interpretation.** High growth and high risk came together. Apple's, Amazon's and Alphabet's gains required living through falls of more than half their value. This is a statement about past prices; it does not explain *why* the falls happened.

**Limitation.** Drawdowns use month-end prices; daily prices would show deeper short-lived falls.

### 9.3 Q3. Which holdings delivered the most growth for the risk taken?

**Method:** return-to-risk ratio = CAGR ÷ annualised volatility (risk-free rate assumed 0). Fig 3 above shows the same information: points high and to the left are better.


**Return-to-risk ratio (CAGR ÷ volatility), common window**

| Series | Return / risk |
|---|---|
| AAPL | 1.09 |
| GOOGL | 0.73 |
| MSFT | 0.72 |
| AMZN | 0.69 |
| NASDAQ | 0.60 |
| ADBE | 0.56 |
| S&P 500 | 0.49 |
| IBM | 0.29 |
| XRX | -0.07 |


**Observed facts.** Apple had the best ratio (**1.09**), followed by Alphabet (**0.73**), Microsoft (**0.72**) and Amazon (**0.69**). NASDAQ scored **0.60**, Adobe **0.56**, the S&P 500 **0.49**, IBM **0.29** and Xerox **−0.07**.

**Interpretation.** Taking more volatility did not guarantee a better outcome: Xerox was among the most volatile holdings but grew negatively. Amazon's very high growth came with the highest volatility, so its ratio is below Alphabet's and Microsoft's. Apple stands out because its growth was much larger than its risk. The ratio uses a 0 % risk-free rate, so absolute values are simplified; the *ranking* is what matters here.

### 9.4 Q4. How strongly does each holding follow the market?

**Method:** beta against the S&P 500 (Fig 7) and a scatter of each holding's monthly return against the market's monthly return, with a fitted line whose slope is the beta (Fig 8).

![Fig 7. Beta versus the S&P 500](figures/fig07_beta_vs_market.png)

*Figure 7. Beta versus the S&P 500*

![Fig 8. Monthly return of each series against the S&P 500](figures/fig08_beta_scatter.png)

*Figure 8. Monthly return of each series against the S&P 500*

**Beta and correlation with the S&P 500**

| Holding | Beta | Correlation with S&P 500 | Share explained (corr²) |
|---|---|---|---|
| IBM | 0.82 | 0.58 | 0.34 |
| AAPL | 1.25 | 0.56 | 0.31 |
| MSFT | 0.99 | 0.64 | 0.41 |
| XRX | 1.57 | 0.66 | 0.43 |
| AMZN | 1.20 | 0.49 | 0.24 |
| GOOGL | 1.08 | 0.53 | 0.28 |
| ADBE | 1.36 | 0.68 | 0.46 |


**Observed facts.** Beta ranged from **0.82** (IBM) and **0.99** (Microsoft) up to **1.36** (Adobe) and **1.57** (Xerox); Apple **1.25**, Amazon **1.20**, Alphabet **1.08**. Correlations with the S&P 500 were between **0.49** (Amazon) and **0.68** (Adobe). Squared, this means the market explains roughly **24 %** (Amazon) to **46 %** (Adobe) of each holding's monthly movement.

**Interpretation.** Most holdings amplify market moves (beta above 1); only IBM and, marginally, Microsoft were at or below the market. Because the market explains less than half of each holding's movement, a large part of the risk is specific to the company. Xerox had the highest beta and still lost value, so high market sensitivity was not rewarded in this sample.

**Limitation.** Beta and correlation describe how returns moved together in the past; they do not show that the market *causes* a company's movements.

### 9.5 Q5. How did the holdings behave in past market-stress periods?

**Method:** three stress windows were fixed *in advance*, chosen as well-known market episodes, not selected after seeing the results: dot-com (Jan 2000 – Dec 2002), financial crisis (Oct 2007 – Mar 2009) and the early-2022 slide (Dec 2021 – Jun 2022). For each window the table shows the **largest fall from a high reached inside that window**. Alphabet did not yet have a price in the first window.

![Fig 9. Largest fall inside each stress window](figures/fig09_stress_windows.png)

*Figure 9. Largest fall inside each stress window*

**Largest fall inside each stress window**

| Series | Dot-com (2000-01 to 2002-12) | Financial crisis (2007-10 to 2009-03) | Early-2022 slide (2021-12 to 2022-06) |
|---|---|---|---|
| IBM | -55.3% | -36.5% | -8.3% |
| AAPL | -78.9% | -56.9% | -22.4% |
| MSFT | -59.2% | -55.2% | -23.4% |
| XRX | -82.5% | -73.4% | -28.5% |
| AMZN | -91.3% | -53.9% | -35.6% |
| GOOGL | n/a (no price yet) | -58.6% | -22.7% |
| ADBE | -75.3% | -65.1% | -35.5% |
| S&P 500 | -46.3% | -52.6% | -19.8% |
| NASDAQ | -75.0% | -51.8% | -28.5% |

**Does a higher beta go with a deeper fall?** (descriptive: only 6–7 holdings)

| Window | Holdings used | Spearman ρ (beta vs size of fall) | p-value |
|---|---|---|---|
| Dot-com | 6 | 0.60 | 0.208 |
| Financial crisis | 7 | 0.82 | 0.023 |
| Early 2022 | 7 | 0.54 | 0.215 |


**Observed facts.**
* Every holding and both indices fell in every window.
* Dot-com window: Amazon **−91.3 %**, Xerox **−82.5 %**, Apple **−78.9 %**, Adobe **−75.3 %**, Microsoft **−59.2 %**, IBM **−55.3 %**, against **−46.3 %** for the S&P 500 and **−75.0 %** for NASDAQ.
* Financial-crisis window: falls ranged from **−36.5 %** (IBM) to **−73.4 %** (Xerox); S&P 500 **−52.6 %**.
* Early 2022: S&P 500 **−19.8 %**; Amazon **−35.6 %**, Adobe **−35.5 %**, Xerox **−28.5 %**, Microsoft **−23.4 %**, Alphabet **−22.7 %**, Apple **−22.4 %**, IBM **−8.3 %**. (The window ends in June 2022, a partial month.)
* In the financial-crisis window, holdings with a higher beta fell further (Spearman ρ = **0.82**, p = **0.023**, 7 holdings). In the dot-com and 2022 windows the relationship was in the same direction but weaker and not statistically clear (ρ = **0.60**, p = **0.208** and ρ = **0.54**, p = **0.215**).

**Interpretation.** None of the holdings protected the club in a market-wide fall; the least affected (IBM) still lost more than a third of its value in the financial-crisis window. A higher beta was *associated* with deeper falls, which fits the idea that beta gives a rough warning of stress behaviour, but with so few holdings this is only a hypothesis to test further.

### 9.6 Q6. Does holding all seven together reduce risk?

**Method:** correlation matrix of monthly returns (Fig 10); a hypothetical **equal-weight basket** that holds the seven stocks in equal parts and is rebalanced monthly (Fig 12). The basket ignores trading costs and taxes.

![Fig 10. Correlation of monthly returns](figures/fig10_correlation_heatmap.png)

*Figure 10. Correlation of monthly returns*

![Fig 12. Equal-weight basket versus the indices (growth of 100, log scale)](figures/fig12_equal_weight_basket.png)

*Figure 12. Equal-weight basket versus the indices (growth of 100, log scale)*

**Diversification results** (volatility, CAGR and drawdown as fractions, e.g. 0.204 = 20.4 %)

| Measure | Result |
|---|---|
| Average pairwise correlation (all months) | 0.386 |
| Average pairwise correlation (financial-crisis window) | 0.465 |
| Months in the crisis window | 18 |
| Average volatility of the 7 single stocks | 0.297 |
| Volatility of the equal-weight basket | 0.204 |
| Basket volatility is lower by (share) | 0.312 |
| Basket CAGR | 0.193 |
| Basket maximum drawdown | -0.487 |
| S&P 500 maximum drawdown | -0.526 |
| Basket return / risk | 0.944 |


**Observed facts.** The seven holdings are only moderately correlated with each other (average pairwise correlation **0.39**; lowest pairs Xerox–Amazon **0.25**, IBM–Alphabet **0.28**, Xerox–Alphabet **0.30**). The equal-weight basket had volatility of **20.4 %**, which is about **31 %** lower than the **29.7 %** average volatility of the seven single stocks. Its CAGR was **19.3 %**, a little above the simple average of the seven single-stock CAGRs (**17.0 %**); its largest fall was **−48.7 %** (S&P 500: **−52.6 %**) and its return-to-risk ratio **0.94**. In the 18 months of the financial-crisis window the average pairwise correlation rose to **0.47**.

**Interpretation.** Combining the seven reduced volatility noticeably without lowering growth below the single-stock average, which supports keeping a basket rather than concentrating in a few names. But the basket still lost almost half its value at its worst point, so diversification *within* technology shares did not remove the risk of a large fall. The higher correlation in the crisis window is consistent with diversification weakening when markets fall, but 18 months is a small sample.

**Limitations.** The basket is hypothetical (monthly rebalancing, no costs or taxes) and is measured over a period in which these particular companies did well.

### 9.7 Q7. How consistent were returns from year to year?

**Method:** calendar-year return = December price ÷ previous December price − 1, for full years only (Fig 11). The partial year 2022 is excluded.

![Fig 11. Calendar-year returns, 1991 – 2021 (full years only)](figures/fig11_calendar_year_returns.png)

*Figure 11. Calendar-year returns, 1991 – 2021 (full years only)*

**Consistency of calendar-year returns**

| Series | Full years | Positive years | Share positive | Best year | Worst year |
|---|---|---|---|---|---|
| IBM | 31 | 19 | 61.3% | 1998 (+77.5%) | 1992 (-40.0%) |
| AAPL | 31 | 22 | 71.0% | 1998 (+211.9%) | 2000 (-71.1%) |
| MSFT | 31 | 24 | 77.4% | 1991 (+121.8%) | 2000 (-62.8%) |
| XRX | 31 | 19 | 61.3% | 2001 (+127.2%) | 2000 (-78.7%) |
| AMZN | 24 | 17 | 70.8% | 1998 (+966.4%) | 2000 (-79.6%) |
| GOOGL | 17 | 13 | 76.5% | 2005 (+115.2%) | 2008 (-55.5%) |
| ADBE | 31 | 24 | 77.4% | 1999 (+188.6%) | 1992 (-51.6%) |
| S&P 500 | 31 | 23 | 74.2% | 1995 (+34.1%) | 2008 (-38.5%) |
| NASDAQ | 31 | 24 | 77.4% | 1999 (+85.6%) | 2008 (-40.5%) |


**Observed facts.** Microsoft and Adobe finished higher in **24 of 31** years (**77.4 %**), Alphabet in **13 of 17** (**76.5 %**), Apple in **22 of 31** (**71.0 %**), Amazon in **17 of 24** (**70.8 %**), IBM and Xerox in **19 of 31** (**61.3 %**). The S&P 500 was up in **23 of 31** years (**74.2 %**). The worst single years were Amazon **−79.6 %** (2000), Xerox **−78.7 %** (2000) and Apple **−71.1 %** (2000); the best was Amazon's **+966 %** in 1998.

**Interpretation.** Even the strongest holdings lost money in roughly one year in four, and the worst years were severe and clustered around 2000 and 2008 (see Fig 11). The holdings were not more reliable year to year than the S&P 500 (Microsoft and Adobe only slightly better); their advantage came from larger gains in good years. Different holdings have different numbers of full years, so shares are not perfectly comparable.

### 9.8 Q8. Which months were unusual, and when?

**Method:** a month is flagged if its return is more than 3 standard deviations away from that series' own average monthly return (z-score), over the common window.


**21 unusual months** (return more than 3 standard deviations from the series' own average, common window)

| Series | Month | Return | z-score |
|---|---|---|---|
| GOOGL | 2004-10 | +47.1% | +5.2 |
| AMZN | 2007-04 | +54.1% | +4.9 |
| XRX | 2019-01 | +44.6% | +4.4 |
| S&P 500 | 2008-10 | -16.9% | -4.1 |
| XRX | 2020-03 | -41.2% | -4.1 |
| IBM | 2018-10 | -23.7% | -4.0 |
| ADBE | 2008-10 | -32.5% | -4.0 |
| AAPL | 2008-09 | -33.0% | -3.8 |
| NASDAQ | 2008-10 | -17.7% | -3.7 |
| AAPL | 2008-01 | -31.7% | -3.6 |
| MSFT | 2007-10 | +24.9% | +3.6 |
| IBM | 2008-10 | -20.5% | -3.5 |
| XRX | 2009-04 | +35.4% | +3.4 |
| AAPL | 2004-10 | +35.2% | +3.4 |
| ADBE | 2006-05 | -27.0% | -3.4 |
| GOOGL | 2008-04 | +30.4% | +3.3 |
| AMZN | 2005-07 | +36.4% | +3.2 |
| AMZN | 2006-07 | -30.5% | -3.1 |
| ADBE | 2009-03 | +28.1% | +3.1 |
| S&P 500 | 2020-03 | -12.5% | -3.1 |
| ADBE | 2009-04 | +27.9% | +3.1 |


**Observed facts.** **21** of **1,917** monthly returns (**1.1 %**) were beyond ±3 standard deviations. **10** of the 21 fall in 2008–2009 (7 in 2008, 3 in 2009), including October 2008, when IBM, Adobe, the S&P 500 and NASDAQ were all flagged. The largest were Alphabet **+47.1 %** (October 2004, its second month in the data), Amazon **+54.1 %** (April 2007), Xerox **+44.6 %** (January 2019) and **−41.2 %** (March 2020), and IBM **−23.7 %** (October 2018).

**Interpretation.** Extreme months cluster in the financial crisis, which supports stress testing. The isolated company-specific extremes (for example Xerox in 2019 and 2020, IBM in 2018) are **hypotheses to investigate**: the dataset contains no information about earnings releases, corporate actions or news, so it cannot explain them.

## 10. Key findings

*Observed facts* come directly from the calculations above. *Interpretations* are explanations supported by the analysis. *Hypotheses* need further investigation. No causes are claimed where the data cannot show them.

| ID | Business question | Finding (observed) | Numerical evidence | Source | Interpretation / potential business impact | Confidence or limitation | Suggested follow-up |
|---|---|---|---|---|---|---|---|
| F1 | Q1 | Growth was very unequal across holdings | Common-window CAGR: Apple 35.9 %, Amazon 25.0 %, Alphabet 22.1 % … IBM 6.1 %, Xerox −2.5 %; S&P 500 7.2 % | Fig 1, 2; KPI table | Three holdings produced most of the gain; two did not beat the market. Allocation to winners and laggards matters more than owning the sector. | Survivorship bias; possible adjusted-price advantage over indices | Compare with a wider list of tech companies |
| F2 | Q2 | Higher growth came with higher risk; 6 of 7 holdings fell further than the S&P 500 at their worst point | Max drawdown: Xerox −75.5 %, Adobe −65.1 % … IBM −37.2 %; S&P 500 −52.6 %. Amazon −93.1 % over full history | Fig 3, 4, 5, 6 | Large positions in these holdings expose the club to falls of more than half their value. Position sizing is a decision, not a detail. | Month-end prices understate daily falls | Test position-size caps (see R1) |
| F3 | Q3 | Return per unit of risk differed widely | Return/risk: Apple 1.09, Alphabet 0.73, Microsoft 0.72, Amazon 0.69 … IBM 0.29, Xerox −0.07; S&P 500 0.49 | Fig 3 | Taking more volatility was not automatically rewarded (Xerox). Apple earned most per unit of risk. | 0 % risk-free rate assumed; one period | Re-test with another period |
| F4 | Q4 | Most holdings amplify market moves, but market explains < half of their movement | Beta 0.82 (IBM) to 1.57 (Xerox); correlation 0.49–0.68; market explains 24 %–46 % | Fig 7, 8 | Much of the risk is company-specific, so monitoring individual companies matters. | Association, not causation | Add company-level data (earnings, news) |
| F5 | Q5 | No holding protected the club in market-wide falls; higher beta went with deeper falls in the 2007–09 crisis | Crisis-window falls −36.5 % to −73.4 %; Spearman ρ = 0.82 (p = 0.023, 7 holdings) | Fig 9 | Stress losses of more than a third should be expected in a major downturn. | Only 7 holdings; weaker in other windows (hypothesis) | Add more companies and windows |
| F6 | Q6 | Combining the seven lowered volatility by about 31 % | Basket volatility 20.4 % vs 29.7 % average single stock; basket drawdown −48.7 %; avg. correlation 0.39 (0.47 in crisis window) | Fig 10, 12 | Keeping a basket reduces risk, but a sector-wide fall still cost almost half the value. | Hypothetical basket; no costs; favourable period | Test adding assets outside the dataset |
| F7 | Q7 | Even strong holdings lost money in about one year in four | Positive years: Microsoft/Adobe 77.4 %, Alphabet 76.5 %, S&P 500 74.2 %, IBM/Xerox 61.3 % | Fig 11 | Expect losing years; do not assume steady annual gains. | Different numbers of full years | – |
| F8 | Q8 | Extreme months cluster in the financial crisis | 21 of 1,917 months beyond ±3 SD; 10 in 2008–09 | Outlier table | Supports regular stress testing. Isolated company extremes (Xerox 2019/2020, IBM 2018) need explanation. | Causes are **not** in the data (hypotheses) | Match flagged months to company events |

## 11. Business insights and potential impact

What the data **shows**, what it **suggests** and what still has to be **investigated** (all figures are those in Section 9 and the findings table):

| Theme | Observed fact (from the data) | Interpretation (supported by the analysis) | Hypothesis / needs investigation |
|---|---|---|---|
| Value creation | Growth was very unequal: Apple, Amazon and Alphabet grew fastest, IBM and Xerox did not beat the S&P 500 (F1) | Choosing and sizing holdings matters more than simply owning the sector | Why the laggards lagged (needs company fundamentals) |
| Risk | Higher growth came with higher volatility and deeper falls; six of seven holdings fell further than the S&P 500 at their worst point (F2, F3) | Large positions in high-growth holdings expose the club to very large losses | Whether position-size caps would reduce losses without giving up much growth (to be back-tested) |
| Market link | Beta ranged 0.82 – 1.57; the market explained only 24 % – 46 % of monthly movement (F4) | A large part of each holding's risk is company-specific | Which company events drive that specific risk |
| Stress behaviour | Every holding fell in every stress window; higher beta went with deeper falls in 2007 – 09 (F5) | No holding was a safe haven; beta is a rough warning sign | Whether the beta–fall link holds with more companies |
| Diversification | The equal-weight basket had about 31 % lower volatility than the average single stock but still fell 48.7 % (F6) | Keeping a basket lowers risk but does not remove sector-wide losses | Whether adding non-technology assets would lower the worst fall |
| Consistency | Even strong holdings lost money in about one year in four (F7) | Do not assume steady annual gains | – |
| Unusual months | 21 of 1,917 months were extreme; 10 fell in 2008 – 09 (F8) | Stress testing is justified | What explained the isolated company extremes |

**Potential business impact.** The evidence points to three decisions for the committee: how large each position should be, whether to track stress losses regularly, and which weak holdings to review. The size of any benefit cannot be quantified from this dataset, so none is claimed.


## 12. Actionable recommendations

These follow from the findings above. No financial return is promised; "expected direction" means what the evidence suggests, to be tested.

| ID | Supporting finding | Proposed action | Reason | Priority | Suggested owner | Expected direction of impact | KPI to measure success | Time horizon | Validation / experiment plan | Risks and assumptions |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | F2, F4 | Set a maximum weight for each holding, with lower caps for the highest-risk names (Xerox, Adobe, Amazon, Apple) | The four named holdings fell 54 %–76 % at their worst point, so large positions create large losses | **High** | Portfolio manager | Smaller worst-case losses | Portfolio maximum drawdown; share of total risk from the largest holding | Next committee meeting | Back-test several cap levels on this dataset and compare drawdown and CAGR | Caps may reduce gains; back-test uses past data only |
| R2 | F6 | Keep a diversified basket of all seven instead of concentrating in a few | Equal-weight basket volatility was about 31 % lower than the average single stock | **High** | Investment committee chair | Lower volatility without lowering growth below the single-stock average | Portfolio volatility; average pairwise correlation | Ongoing | Compare the basket with concentrated alternatives on out-of-sample months | The period favoured these companies; diversification weakens in crises |
| R3 | F5, F8 | Add a regular stress-test report using the three windows (dot-com, 2007–09, 2022) | Every holding fell in every window; extreme months cluster in crises | **High** | Risk manager | Earlier awareness of downside | Largest fall in each window per holding | Monthly / quarterly | Re-run the stress table whenever holdings change | Past crises may not resemble the next one |
| R4 | F1, F3 | Put Xerox on a formal watch list and review IBM; decide with company information, not prices alone | Both grew below the S&P 500 (IBM 6.1 %, Xerox −2.5 % vs 7.2 %) and Xerox combined high beta with a loss | **Medium** | Portfolio manager | Better use of capital if weak positions are reduced or explained | Return/risk versus S&P 500 over the next review | One quarter | Gather fundamentals (revenue, earnings, outlook) and compare with peers | Past weakness may not continue; price data cannot explain it |
| R5 | F4, F8 | Investigate the flagged unusual months (for example Xerox 2019/2020, IBM 2018) against company events | The data cannot explain company-specific extremes | **Medium** | Risk analyst | Clarifies which risks are company-specific | Share of flagged months explained by events | One quarter | Match each flagged month with earnings dates and corporate actions | Event data must be sourced separately |
| R6 | All | Improve the data: daily prices, dividends, trading volume, confirmed price adjustments, a wider set of companies | Current data cannot show causes and may be biased toward survivors | **Medium** | Data analyst | More reliable conclusions | Data coverage; change in findings after refresh | One to two months | Re-run this notebook on the richer data and compare findings | Additional data may cost money or need licences |

## 13. Conclusions

* Between 2004 and 2022 the seven holdings differed greatly: Apple, Amazon and Alphabet delivered the largest growth, IBM and Xerox did not beat the market.
* Higher growth came with higher volatility and deeper falls; no holding protected against market-wide declines.
* A diversified basket of all seven lowered volatility by about 31 % compared with the average single stock, yet still suffered a fall of nearly half its value.
* The most decision-relevant actions are position-size limits, stress-test reporting and a fundamentals review of the weakest holdings.

## 14. Limitations and future work

1. **Only prices.** There is no revenue, profit, volume, dividend or company news, so causes cannot be identified and no profit-based KPIs are calculated.
2. **Survivorship and selection bias.** The companies are well-known firms that still exist; results are likely better than a random 1990 technology selection.
3. **Unclear adjustments.** The file does not state whether prices are adjusted for splits and dividends. Very low early prices (for example Apple at about 0.24 in 1990) suggest adjusted stock prices, while index levels are price-only, so stocks may have a small built-in advantage over the indices. Currency is assumed to be US dollars.
4. **Monthly data.** Daily prices would show deeper short-term falls and more extreme days.
5. **Partial final month.** The June 2022 value is as of 28 June 2022.
6. **Short and uneven histories.** Alphabet starts in 2004 and Dell in 2016; Dell is excluded from comparisons.
7. **Small samples.** Seven holdings and three stress windows; the statistical tests are descriptive.
8. **Association, not causation**, and the analysis describes the past, not the future.
9. **Assumed stakeholders and organisation**; the data are not from a real investment club.


**Future work.** Daily data; dividends and fundamentals; more companies (including ones that were delisted); more stress windows; testing the recommendations by back-test.

## 15. References

1. Yahoo Finance. Historical price data. <https://finance.yahoo.com> (source named in `Stocks.csv`).
2. Matplotlib development team. `matplotlib.cbook.get_sample_data` and the `sample_data` folder, <https://matplotlib.org>.
3. McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*.
4. Harris, C. R., et al. (2020). Array programming with NumPy. *Nature*, 585, 357–362.
5. Virtanen, P., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261–272.
6. Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90–95.
7. Waskom, M. L. (2021). seaborn: statistical data visualization. *Journal of Open Source Software*, 6(60), 3021.

## Appendix A. Objective-to-evidence matrix

| Official objective | Evidence | Where | Verified |
|---|---|---|---|
| 1. Define business objectives | Business background, problem statement, objectives, assumed stakeholders, eight questions, question → metric → chart → decision mapping | Sections 2 and 3; notebook Section 2 | Yes: content checked against the questions answered in Section 9 |
| 2. Analyse data and identify findings | Data-quality checks, cleaning, 8 KPIs, eight analyses, eight findings | Sections 6 – 10; notebook Sections 6 – 10 | Yes: notebook executed without errors; 139 quoted numbers re-calculated by code |
| 3. Create meaningful visualisations | 12 charts and supporting tables generated from the data | Section 9; `reports/figures/` | Yes: all 12 files exist and were viewed |
| 4. Generate business insights | Findings table with interpretation, impact and limitations; insights table separating facts, interpretations and hypotheses | Sections 10 and 11; `reports/business_insights.md` | Yes |
| 5. Prepare an executive summary | One-page summary written after the analysis | Section 1; `reports/executive_summary.md` | Yes: numbers match the notebook |
| 6. Provide actionable recommendations | Six prioritised recommendations with owner, KPI, time horizon, validation plan and risks | Section 12; `reports/business_insights.md` | Yes: each is linked to findings F1 – F8 |

