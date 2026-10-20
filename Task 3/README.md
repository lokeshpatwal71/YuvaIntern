# Real-World Dataset Analysis Project

Internship project (YuvaIntern): analyse a real-world retail dataset, the **Global Superstore Sales** dataset, and present findings, visualizations, conclusions and business recommendations in a Jupyter Notebook and a report.

**Author:** Lokesh Patwal, B.Tech, Invertis University

---

## Please read first: what is finished and what you must run

| Item | Status |
|---|---|
| Notebook, analysis code, report builder, documentation | Complete |
| Code correctness | Tested on a small **synthetic** test file (`python tests/test_pipeline.py` passes; all 64 notebook cells ran without errors) |
| **Results on the real dataset** | **Pending execution.** I could not download the dataset from my environment, so no real result is typed anywhere. All numbers appear when **you** run the notebook on the real file |
| Report | `Real_World_Dataset_Analysis_Report.docx/.pdf` in this repository is a **template** marked `[PENDING EXECUTION]`. Running `python src/build_report.py` replaces it with the real report |
| Word version of the notebook | `real_world_dataset_analysis.docx` contains the notebook's explanations and code. Tables and charts are added when you run `python src/notebook_to_docx.py` **after** running and saving the notebook |

The test file is **not real data** and must never be used for your report.

## Project overview
The project follows a complete data-analysis workflow: load the dataset, assess its quality, clean it (keeping the original unchanged, with an audit log), explore it (EDA) with Pandas/NumPy/SciPy, create 13 charts with Matplotlib and Seaborn, and turn the results into findings, recommendations and limitations.

## Dataset source and download instructions
* **Global Superstore** on Kaggle: `apoorvaappz/global-super-store-dataset` (reported size 51,290 rows x 24 columns). Page: https://www.kaggle.com/datasets/apoorvaappz/global-super-store-dataset
* The license is **not verified**, so the data file is **not** included here (it is in `.gitignore`).
* Download steps (manual and Kaggle command line) are in [`data/README.md`](data/README.md). Save the file as `data/Global_Superstore2.csv`.

## Installation and setup (Windows CMD / PowerShell)
```
cd path\to\Real-World-Dataset-Analysis
python --version
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
(PowerShell: if activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.)

## How to run
**1. The notebook (main deliverable)**
```
jupyter notebook
```
Open `real_world_dataset_analysis.ipynb` and choose **Kernel > Restart & Run All**. Then **save the notebook** (Ctrl+S) so that its outputs are stored before you upload it.

**2. The script (same analysis, one command)**
```
python src/analysis.py
```
or with an explicit path: `python src/analysis.py --data "C:\path\to\Global_Superstore2.csv"`

**3. The report (after step 1 or 2)**
```
python src/build_report.py
```
This creates `Real_World_Dataset_Analysis_Report.docx` and, if LibreOffice or Microsoft Word is available, the `.pdf`. Otherwise open the `.docx` in Word and use *File > Save As > PDF*.

**3b. The notebook as a Word file (for portals that accept only .docx)**
```
python src/notebook_to_docx.py
```
Run this **after** the notebook has been executed and saved (Ctrl+S). It creates `real_world_dataset_analysis.docx` with the explanations, the code and the saved tables and charts.

**4. Automated checks (optional)**
```
python tests/test_pipeline.py
```

## Project structure
```
Real-World-Dataset-Analysis/
├── README.md                                  this file
├── requirements.txt                           libraries needed
├── real_world_dataset_analysis.ipynb          main notebook (18 sections)
├── real_world_dataset_analysis.docx           the same notebook as a Word document
├── Real_World_Dataset_Analysis_Report.docx    report (template until you run the analysis)
├── Real_World_Dataset_Analysis_Report.pdf     PDF of the report
├── data/
│   ├── README.md                              source, license note, download instructions
│   └── .gitkeep
├── outputs/                                   charts, tables and summary.json are created here
│   └── .gitkeep
├── src/
│   ├── analysis.py                            full analysis pipeline (also used by the notebook)
│   ├── build_report.py                        builds the report from the real results
│   └── notebook_to_docx.py                    converts the notebook into a Word document
├── tests/
│   ├── make_fixture.py                        creates a SYNTHETIC test file (not real data)
│   └── test_pipeline.py                       automated checks
└── docs/
    ├── Beginner_Guide.md                      step-by-step guide, libraries, code explained, troubleshooting
    ├── Viva_Questions.md                      30+ viva questions with answers
    ├── Presentation_Outline.md                12-slide outline
    └── Objectives_Checklist.md                objective -> file/section mapping, submission checklist
```

## Main analytical tasks
1. Data loading with automatic encoding and column-name handling; schema check
2. Exploration: head/tail, shape, dtypes, descriptive statistics, missing %, duplicates, unique values, category counts, skewness, date inspection
3. Data-quality assessment (missing, duplicates, impossible values, IQR outliers)
4. Cleaning in 7 audited steps (original data preserved)
5. EDA: total sales and profit, orders and customers, category / sub-category / market / region, yearly and monthly trends, top and loss-making products, customers and segments, discount versus profit, shipping
6. Statistics: skewness, correlation (Pearson and Spearman), Kruskal-Wallis, Mann-Whitney, outlier sensitivity
7. 13 visualizations, key findings with evidence, recommendations, limitations, conclusion

## How to interpret the outputs
After running, the `outputs` folder contains:
* `figures/` : 13 PNG charts. Each chart has a written interpretation in the notebook and the report.
* `tables/` : CSV files of every table (for example `category.csv`, `discount_band.csv`) plus `cleaning_audit.csv` (what each cleaning step changed).
* `summary.json` : all key numbers, test results and findings; the report builder reads this file.

Reading tips: a **profit margin** is profit divided by sales; **negative profit** means a loss; a **correlation** near 0 means no straight-line relationship and **never proves cause and effect**; a tiny **p-value** shows a difference is unlikely to be chance, but always check the size of the difference too.

## Technologies used
Python | Jupyter Notebook | Pandas | NumPy | SciPy | Matplotlib | Seaborn | python-docx

## Troubleshooting
| Problem | Solution |
|---|---|
| `No dataset file found in the 'data' folder` | Download the dataset (see `data/README.md`) or pass `--data` / set `DATA_PATH` |
| `These essential columns were not found` | Your file has different column names; the message lists the columns found. Rename them or edit `REQUIRED_COLUMNS` in `src/analysis.py` |
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt` |
| Garbled letters in city or customer names | Encoding issue, cosmetic only; the code already tries utf-8, latin2 and latin-1 |
| PDF is not created | Open the `.docx` in Word and save as PDF |
| Notebook cannot find `analysis` | Start Jupyter from the project folder (`jupyter notebook`) |

More help: [`docs/Beginner_Guide.md`](docs/Beginner_Guide.md).

## Limitations
Results describe one dataset and show association, not causation; the meaning of *Profit* and the currency are not documented in sources I could verify; the finding texts are drafted automatically from the results and must be reviewed by you before submission.
