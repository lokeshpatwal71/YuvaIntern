# Viva Questions and Answers

Answers are in simple English. **Where you see [square brackets], replace the text with the real number from your own notebook output.** I did not type any result here because the real results appear only when you run the project on the real dataset. The two answers marked *(Edit to your real experience)* are suggestions.

**Q1. What is the aim of your project?**

I analysed a real-world retail dataset, the Global Superstore sales data, to find where sales and profit come from, where money is lost, how sales change over time and how discounts affect profit. Then I gave recommendations based on the evidence.

**Q2. Which dataset did you use and where is it from?**

I used the Global Superstore dataset from Kaggle (dataset name apoorvaappz/global-super-store-dataset). It is reported to have 51,290 rows and 24 columns. My notebook prints the exact size of the file I loaded: [your number of rows].

**Q3. Why did you choose this dataset?**

It has real business columns: dates, categories, markets, customers, sales, quantity, discount, profit and shipping cost. So I could do sales, profit, customer, product, regional and trend analysis, plus cleaning and statistics.

**Q4. Did you check the license of the dataset?**

I could not verify the license from outside Kaggle, so I told the reader to check the License field on the Kaggle page. Because of this I did not upload the data file to GitHub. I only upload the code and the instructions to download it.

**Q5. What is data analysis and what is EDA?**

Data analysis means finding useful information in data to support decisions. EDA, Exploratory Data Analysis, is the first step: we explore the data with summaries and charts to understand its structure, quality and patterns before drawing conclusions.

**Q6. What is Pandas?**

Pandas is a Python library for tables of data called DataFrames. I used it to load the file, clean it, filter rows, group data with groupby and calculate totals.

**Q7. What is NumPy?**

NumPy is a Python library for fast calculations on arrays of numbers. Pandas is built on it. I used it for things like np.where to calculate margin safely and the log scale for the sales histogram.

**Q8. What is the difference between Python and Pandas?**

Python is the programming language. Pandas is a library, a ready-made toolbox written in Python, that makes working with tables easy.

**Q9. What is Jupyter Notebook and why did you use it?**

It is a document where code, results, charts and explanations are together. It is ideal for analysis because anyone can run it step by step and see how each result was produced.

**Q10. Why did you use SciPy?**

SciPy has statistical tests. I used Spearman correlation, the Kruskal-Wallis test and the Mann-Whitney U test to study how discount and profit margin are related.

**Q11. What is a virtual environment?**

A separate folder with its own Python libraries for one project, so that library versions of different projects do not conflict. I created it with python -m venv venv.

**Q12. What is data cleaning and why is it needed?**

Data cleaning means fixing problems like duplicates, missing values, wrong data types and impossible values. Wrong data gives wrong answers, so cleaning is necessary before analysis.

**Q13. How did you make sure you did not change the original data?**

I kept the loaded data in df_raw and did all cleaning on a copy called df. At the end of the cleaning section the notebook compares df_raw with a saved snapshot using assert_frame_equal. If anything had changed, it would stop with an error.

**Q14. What is your audit log?**

Each cleaning step writes a line with rows before, rows after, rows affected and details. So every change is documented and nothing changes silently. It is saved in outputs/tables/cleaning_audit.csv.

**Q15. How did you handle missing values?**

Rows missing an essential value, like sales or profit, are dropped. Columns with less than 5% missing are filled: median for numbers and the word Unknown for text. Columns with 5% or more missing are not filled, because that would invent data; I keep them but do not use them. In my run: [numbers from your cleaning audit].

**Q16. How did you handle duplicates?**

I removed only rows that are identical in every column. Rows that differ only in Row ID are reported but kept, because the same product can legitimately appear twice in an order. Number removed in my run: [from your audit].

**Q17. How did you convert the date columns?**

The CSV stores dates as text. My function tries several formats and picks the one that parses the most values, because 05-02-2013 could be 5 February or 2 May. The notebook prints the format it detected. Then I created year, month and quarter columns.

**Q18. What is an outlier and how did you find outliers?**

An outlier is a value far from most values. I used the IQR rule: below Q1 minus 1.5 times IQR or above Q3 plus 1.5 times IQR. I looked at the extreme rows first.

**Q19. Did you remove the outliers? Why or why not?**

No, I flagged them but kept them. Big orders and heavy losses are real business events, not errors, and removing valid observations would distort totals. I also calculated how much they influence total profit (see the outlier sensitivity table).

**Q20. What invalid values did you check?**

Negative sales, zero or negative quantity, discount outside 0 to 1, negative shipping cost and ship date before order date. Rows with such values are removed and counted in the audit.

**Q21. What is profit margin?**

Profit divided by sales, usually shown as a percentage. It shows how much profit the business keeps from each unit of sales. A negative margin means a loss.

**Q22. What is the difference between mean and median? Which did you prefer?**

The mean is the average and the median is the middle value. My data is skewed, with a few very large values, so the mean is pulled up. For a typical value the median is better, so I report both.

**Q23. What is skewness?**

It measures whether a distribution is symmetric. Positive skewness means a long tail to the right. Sales and profit had skewness of [your values from Section 12], so I used non-parametric tests.

**Q24. What is correlation? Does it prove cause and effect?**

Correlation (-1 to +1) shows how two numbers move together. It does not prove cause and effect. For example, discount and profit margin may be negatively related, but product mix and costs also matter.

**Q25. Why did you use Spearman as well as Pearson?**

Pearson measures straight-line relationships and is sensitive to outliers. Spearman uses ranks, so it is more robust for skewed data with outliers.

**Q26. What do the Kruskal-Wallis and Mann-Whitney tests do?**

Kruskal-Wallis checks whether the profit margin differs between several discount bands. Mann-Whitney compares two groups: discounted and non-discounted order lines. Both do not assume a normal distribution.

**Q27. What is a p-value? Is a small p-value enough?**

A small p-value (below 0.05) means the difference is unlikely to be pure chance. With a large dataset p-values become tiny even for small effects, so I also look at the size of the difference, like the difference in medians.

**Q28. What is groupby?**

It splits the data into groups, calculates something for each group and combines the results. For example df.groupby('category')['profit'].sum() gives total profit for each category.

**Q29. What did you find about discounts and profit?**

My notebook shows the margin for each discount band and the Spearman correlation: [your result, e.g. margin in the highest band vs no discount]. I explain it as an association and not as proof that discounts cause the losses.

**Q30. Which category or market is best and which is worst?**

[Take this from Section 11.2 and 11.3 of your notebook: highest sales, highest profit, lowest margin.] I also checked whether the sales leader is the same as the profit leader.

**Q31. Did you find loss-making products or sub-categories?**

[From Section 11.5 and 11.8: number of loss-making products and sub-categories with negative total profit, and the worst product.] My recommendation is to review price, discount and cost for them.

**Q32. Is there seasonality in sales?**

I looked at monthly totals, the average by calendar month, a year-by-month heatmap and z-scores to find unusual months. [Your strongest and weakest months from Section 11.4.]

**Q33. Why did you use these chart types?**

Bar charts compare categories, line charts show trends over time, histograms show distributions, scatter plots and heatmaps show relationships, and box plots show outliers. I chose each chart for the question it answers.

**Q34. What is a heatmap and what did you use it for?**

A heatmap uses colours to show values in a table. I used it for the correlation matrix, for profit margin by market and category, and for sales by year and month.

**Q35. Are your findings written by you or generated automatically?**

The text of the findings is drafted by rules from the calculated results, so that no number is invented. I then checked every statement against the tables and rewrote the conclusion in my own words.

**Q36. How can someone reproduce your work?**

Download the dataset, install requirements.txt, run python src/analysis.py or run the notebook. A test script, python tests/test_pipeline.py, checks the code on a small synthetic file, which is not real data.

**Q37. What are the limitations of your analysis?**

It describes one dataset; it shows association, not causation; the exact definition of Profit and the currency are not documented in sources I could verify; outliers influence totals; and it is descriptive only, with no forecasting model.

**Q38. What was the biggest challenge? (Edit to your real experience)**

Possible answer: handling the date format and the non-UTF-8 encoding of the file, deciding what to do with outliers, and interpreting discount and profit without claiming cause and effect.

**Q39. What did you learn? (Edit to your real experience)**

Possible answer: the full workflow of an analysis, why cleaning must be documented, the difference between association and causation, and how to turn numbers into recommendations.

**Q40. How could the project be improved?**

Add forecasting, a customer segmentation model (clustering), an interactive dashboard in Power BI or Streamlit, and test discount policies with a controlled experiment.

