# Business Insights Register and Recommendations
## Analytics Report & Insights Documentation: Technology-Stock Performance Review, 1990 – 2022

## 1. How to read this document
Every row below is traceable to a calculation in `notebooks/analytics_report_insights.ipynb` and to a figure in `reports/figures/`.

* **Observed facts** come directly from the calculations.
* **Interpretations** are explanations supported by the analysis.
* **Hypotheses** need further investigation; the dataset (prices only) cannot show causes.
* **Recommendations** are expected directions to be tested. No financial return is promised or estimated.

## 2. Business insights register
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

## 3. Recommendations
These follow from the findings above. No financial return is promised; "expected direction" means what the evidence suggests, to be tested.

| ID | Supporting finding | Proposed action | Reason | Priority | Suggested owner | Expected direction of impact | KPI to measure success | Time horizon | Validation / experiment plan | Risks and assumptions |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | F2, F4 | Set a maximum weight for each holding, with lower caps for the highest-risk names (Xerox, Adobe, Amazon, Apple) | The four named holdings fell 54 %–76 % at their worst point, so large positions create large losses | **High** | Portfolio manager | Smaller worst-case losses | Portfolio maximum drawdown; share of total risk from the largest holding | Next committee meeting | Back-test several cap levels on this dataset and compare drawdown and CAGR | Caps may reduce gains; back-test uses past data only |
| R2 | F6 | Keep a diversified basket of all seven instead of concentrating in a few | Equal-weight basket volatility was about 31 % lower than the average single stock | **High** | Investment committee chair | Lower volatility without lowering growth below the single-stock average | Portfolio volatility; average pairwise correlation | Ongoing | Compare the basket with concentrated alternatives on out-of-sample months | The period favoured these companies; diversification weakens in crises |
| R3 | F5, F8 | Add a regular stress-test report using the three windows (dot-com, 2007–09, 2022) | Every holding fell in every window; extreme months cluster in crises | **High** | Risk manager | Earlier awareness of downside | Largest fall in each window per holding | Monthly / quarterly | Re-run the stress table whenever holdings change | Past crises may not resemble the next one |
| R4 | F1, F3 | Put Xerox on a formal watch list and review IBM; decide with company information, not prices alone | Both grew below the S&P 500 (IBM 6.1 %, Xerox −2.5 % vs 7.2 %) and Xerox combined high beta with a loss | **Medium** | Portfolio manager | Better use of capital if weak positions are reduced or explained | Return/risk versus S&P 500 over the next review | One quarter | Gather fundamentals (revenue, earnings, outlook) and compare with peers | Past weakness may not continue; price data cannot explain it |
| R5 | F4, F8 | Investigate the flagged unusual months (for example Xerox 2019/2020, IBM 2018) against company events | The data cannot explain company-specific extremes | **Medium** | Risk analyst | Clarifies which risks are company-specific | Share of flagged months explained by events | One quarter | Match each flagged month with earnings dates and corporate actions | Event data must be sourced separately |
| R6 | All | Improve the data: daily prices, dividends, trading volume, confirmed price adjustments, a wider set of companies | Current data cannot show causes and may be biased toward survivors | **Medium** | Data analyst | More reliable conclusions | Data coverage; change in findings after refresh | One to two months | Re-run this notebook on the richer data and compare findings | Additional data may cost money or need licences |

## 4. What the data does *not* show
* Why individual companies gained or lost value: there are no revenue, profit, volume, dividend or news data.
* Whether the results would hold for a different set of companies or a different period (survivorship bias, one period).
* Anything about the future. All statements describe 1990 – 2022 prices.
