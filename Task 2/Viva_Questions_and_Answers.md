# Viva Preparation: Questions and Answers

Answers are written in simple spoken English with the real numbers from this project. **Read them, then say them in your own words.** The two answers marked *(Edit this to your real experience)* are suggestions; change them to what you really experienced.

Before the viva, remember: the dataset is **synthetic**. Say this clearly if asked.

**Q1. What is data analysis?**

Data analysis means looking at data carefully to find useful information, like totals, averages, patterns and trends, so that people can make better decisions. In my project I analysed supermarket invoices to find which products, branches and times give the most revenue.

**Q2. Why did you choose this dataset?**

I chose a supermarket sales dataset because it is easy to understand and it has everything this internship needs: categories like branch and product line, numbers like price and quantity, dates and times, and some data-quality problems to clean. It lets me practise cleaning, grouping, filtering, correlation and different charts.

**Q3. Is your dataset real?**

No, and I want to be clear about that. The dataset is synthetic, which means a Python program generated it (src/generate_dataset.py). Its columns are modelled on a public Kaggle supermarket sales dataset, but the rows are not from a real shop. I did this so that the project is fully reproducible. So my findings describe this file and I do not claim them as facts about a real supermarket.

**Q4. Why did you add problems like duplicates and missing values?**

I added a few common data-entry problems on purpose: 12 blank ratings, 6 duplicate invoices and different spellings of the payment method. Real data is usually messy, so this gave the cleaning section real work. I have explained this openly in the README and data folder.

**Q5. What is Pandas?**

Pandas is a Python library for working with tables of data. Its main object is the DataFrame, which is like an Excel sheet inside Python. With it I loaded the CSV, cleaned the data, filtered rows, grouped by categories and calculated statistics.

**Q6. What is NumPy?**

NumPy is a Python library for fast numerical calculations on arrays of numbers. Pandas is built on top of it. In my project I used it for checks such as np.isclose to confirm that total equals cogs plus tax.

**Q7. What is Jupyter Notebook?**

Jupyter Notebook is an interactive document where I can write code, see the output and charts straight below it, and add explanations in text. It is perfect for data analysis because the whole story is in one place and can be run step by step.

**Q8. What is the difference between Python and Pandas?**

Python is the programming language. Pandas is a library, a ready-made toolbox written in Python, which adds powerful tools for tables of data. Without Pandas, I would have to write many lines of Python to do what Pandas does in one line.

**Q9. What is a DataFrame and a Series?**

A DataFrame is a two-dimensional table with rows and columns. A Series is a single column of a DataFrame. For example, df is my table of invoices and df['total'] is a Series of invoice totals.

**Q10. What is data cleaning and why is it needed?**

Data cleaning means fixing problems in the data, such as duplicates, missing values, wrong types and inconsistent text. It is needed because wrong data gives wrong answers. For example, my 6 duplicate invoices would have counted some revenue twice.

**Q11. What are missing values and how did you handle them?**

Missing values are blank cells where no data was recorded. In my data, 12 ratings were blank. Since it was only about 1% of rows, I did not delete the invoices. I filled the blanks with the median rating, which is 7.0.

**Q12. Why did you use the median and not the mean to fill the missing values?**

The median is the middle value and is not affected by extreme values, while the mean can be pulled by very high or low values. For ratings both are close, but the median is a safe, standard choice.

**Q13. What are duplicate records and how did you remove them?**

Duplicate records are the same row entered more than once. I found them with df.duplicated().sum(), which gave 6, and confirmed that the same Invoice IDs were repeated. I removed them with drop_duplicates(), which left 1000 unique invoices.

**Q14. What is EDA?**

EDA means Exploratory Data Analysis. It is the step where we explore the data by asking questions, calculating summaries and drawing charts to understand its structure and patterns before making conclusions. I answered 10 EDA questions in my notebook.

**Q15. What is correlation? Does it mean one thing causes the other?**

Correlation measures how two numbers move together, from -1 to +1. Positive means they rise together, negative means one rises while the other falls, and near zero means no relationship. But correlation does not prove causation. In my data the rating and total have correlation of only 0.03, so there is no relationship.

**Q16. What is the difference between mean and median? Which is better for your data?**

The mean is the average. The median is the middle value after sorting. In my data the mean invoice is Rs. 2,777 and the median is Rs. 2,277. The mean is higher because a few large invoices pull it up, so for a typical invoice the median is a better number.

**Q17. What are standard deviation, quartiles and IQR?**

Standard deviation shows how much values usually differ from the mean. Quartiles divide sorted data into four equal parts: Q1 is 25%, Q2 is the median and Q3 is 75%. IQR is Q3 minus Q1, the spread of the middle 50% of values. I used the IQR to detect outliers.

**Q18. What is an outlier and how did you detect it?**

An outlier is a value far away from most others. I used the IQR rule: anything above Q3 plus 1.5 times IQR is an outlier. About 25 invoices were above Rs. 8,250. I checked them and found they were genuine large purchases, so I kept them but noted that they raise the average.

**Q19. What is skewness? What is the skewness of your data?**

Skewness tells whether a distribution is symmetric or has a long tail on one side. My invoice totals have skewness of about 1.05, which is positive, so the data is right-skewed: many small invoices and a few very large ones.

**Q20. What is a histogram?**

A histogram shows the distribution of one numerical variable. Values are grouped into bins and the height of each bar shows how many values are in that bin. I used it for invoice totals and it showed the right-skewed shape.

**Q21. What is a scatter plot?**

A scatter plot shows the relationship between two numerical variables, with one dot for each record. I plotted rating against invoice total. The dots had no pattern, which shows there is no relationship.

**Q22. What is a box plot?**

A box plot shows the median, the middle 50% of values in the box, the whiskers for the normal range and dots for outliers. I used it to compare invoice totals of the three branches, and they looked similar.

**Q23. What is a heatmap?**

A heatmap uses colours to show values in a table. I used it for the correlation matrix: red for strong positive, blue for negative, and grey for almost zero. It lets me see all relationships in one picture.

**Q24. What is a pie chart and when should it be used?**

A pie chart shows how a whole is divided into parts. It works well when there are only a few parts. I used it for payment methods, which are three almost equal slices of about 34.5%, 33.0% and 32.5%.

**Q25. Why did you use Seaborn?**

Seaborn is built on Matplotlib and makes statistical charts like histograms with a density line, box plots, scatter plots with groups and heatmaps with just one line, and they look attractive by default. I still used Matplotlib for the basic charts and for saving files.

**Q26. Why is visualization important?**

People understand pictures faster than tables of numbers. A chart can show peaks, trends, skewed data and outliers immediately. It also helps to explain results to people who are not technical.

**Q27. What does groupby do?**

groupby splits the data into groups, calculates something for each group and puts the results together. For example, df.groupby('product_line')['total'].sum() gives the revenue of each product line.

**Q28. What does value_counts do?**

It counts how many times each value appears in a column. I used it to count invoices per product line and, importantly, to discover that the payment column had 8 different spellings for only 3 payment methods.

**Q29. Why did you convert the Date column to a datetime type?**

The date was stored as text, so Python could not sort it by date or extract the month or weekday. After pd.to_datetime with the format month/day/year, I could create month, weekday and weekend columns and draw the daily revenue line chart.

**Q30. Why did you drop the columns gross margin percentage and gross income?**

I checked them: gross margin percentage has the same value in every row, and gross income is exactly equal to the tax column. They add no new information, so they only make the analysis more confusing.

**Q31. Why is the correlation between total and unit price high? Is it a discovery?**

No, it is not a discovery. The invoice total is calculated as unit price times quantity plus tax, so total naturally moves with price (0.67) and quantity (0.64). It is built into the formula. The interesting finding is that price and quantity are not related to each other (-0.02).

**Q32. February has lower revenue than January and March. Does it mean sales fell?**

No. February has only 28 days. When I divide revenue by the number of days, the daily revenue is almost the same in all three months, around Rs. 31,000 per day. So there is no real decline.

**Q33. Which product line earns the most and why?**

Home and lifestyle earns the most, about Rs. 640,873, which is 23.1% of revenue. The number of invoices per product line is similar, so the reason is price: the average Home and lifestyle invoice is about Rs. 4,056 against Rs. 1,359 for Food and beverages.

**Q34. What are the main insights from your project?**

First, total revenue is about Rs. 27.8 lakh from 1000 invoices. Second, Home and lifestyle is the top product line. Third, Members spend about 19% more per invoice because they buy more items. Fourth, the busiest times are lunchtime, evenings and weekends, and weekends bring 38.1% of revenue. Fifth, ratings are unrelated to spending.

**Q35. What was the biggest challenge? (Edit this to your real experience)**

My biggest challenge was finding the hidden data problems. The payment column looked fine until I used value_counts and saw different spellings. I also had to be careful with the date format and with interpreting the mean for skewed data.

**Q36. What did you personally learn? (Edit this to your real experience)**

I learned the full workflow of an analysis: load, check, clean, explore, visualise and explain. I learned that cleaning is very important, that the median can be better than the mean, and that correlation is not causation.

**Q37. What is a virtual environment and why did you use it?**

A virtual environment is a separate folder with its own Python libraries for one project. It keeps the project's libraries separate from other projects, so versions do not conflict. I created it with python -m venv venv.

**Q38. What is requirements.txt?**

It is a text file that lists the libraries the project needs: numpy, pandas, matplotlib, seaborn, jupyter and notebook. Anyone can install them all with one command: pip install -r requirements.txt.

**Q39. Why did you not use machine learning?**

The internship objective is data manipulation, visualization and basic analysis, so I kept the project focused on that. Machine learning, like predicting invoice totals, is mentioned only as future scope.

**Q40. How does your script find the data file from any folder?**

In analysis.py I use pathlib: Path(__file__).resolve().parent.parent gives the project folder, and I build the path to data/dataset.csv from that. So the script works no matter where I run it from.

**Q41. What is Git and GitHub?**

Git is a version control tool that tracks changes in files. GitHub is a website that stores Git repositories online so that I can share my project. I uploaded my project there with git init, add, commit, branch, remote and push.

**Q42. How could you improve this project?**

I could use a larger, real dataset, add a prediction model, forecast daily revenue, build an interactive dashboard with Streamlit or Power BI, and run statistical tests such as a t-test for Members versus Normal customers.
