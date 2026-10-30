# Executive Summary
## Analytics Report & Insights Documentation: Technology-Stock Performance Review, 1990 – 2022

**Prepared by:** Lokesh Patwal (Data Analyst Intern, Yuva Intern) · **Date:** 28 October 2026

> *Educational exercise on historical prices. It is not investment advice, and past performance does not predict future results. The investment club and stakeholders are assumed for the exercise.*

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

### Key metrics at a glance (common window, September 2004 – June 2022)

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

*Total return and CAGR are changes in price. Volatility is the annualised standard deviation of monthly returns. Beta and correlation are measured against the S&P 500. All figures are calculated from the dataset by the notebook `notebooks/analytics_report_insights.ipynb`.*

For the full evidence, charts and methods see `final_analytics_report.md`; for the findings and recommendations tables see `business_insights.md`.
