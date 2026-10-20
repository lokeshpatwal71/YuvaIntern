# Objectives Checklist and Submission Checklist

## A. Internship objectives -> where they are satisfied

| # | Objective | Where it is satisfied |
|---|---|---|
| 1 | Select a reliable real-world dataset and understand its business context | Notebook Sections 4 and 5; `data/README.md`; report Section 3 |
| 2 | Explore structure, data types, distributions, missing values, duplicates, relationships | Notebook Sections 8 and 9; `ra.assess_quality()`; `outputs/tables/missing_values_before_cleaning.csv`; report Sections 3 and 5 |
| 3 | Clean and preprocess the data appropriately | Notebook Section 10 (7 audited steps); `src/analysis.py` (`step_...` functions); `outputs/tables/cleaning_audit.csv`; report Section 5 |
| 4 | EDA using Pandas, NumPy and statistical techniques | Notebook Sections 11 and 12; `src/analysis.py` (`compute_results`); report Section 6 |
| 5 | Meaningful visualizations with Matplotlib and Seaborn | Notebook Section 13 (13 charts); `outputs/figures/`; report Section 7 |
| 6 | Present findings, interpretations, conclusions, recommendations in a notebook and report | Notebook Sections 14-17; `Real_World_Dataset_Analysis_Report.docx/.pdf` (after `build_report.py`) |

Other requirements: environment setup (`requirements.txt`, README, `docs/Beginner_Guide.md`); reproducibility (`python src/analysis.py`, `tests/test_pipeline.py`); limitations (Notebook Section 16, report Section 10).

## B. Final submission checklist

**Before running**
- [ ] Python installed, virtual environment created and active, `pip install -r requirements.txt` finished
- [ ] I opened the Kaggle dataset page, confirmed it loads and read the License field
- [ ] `Global_Superstore2.csv` is saved in `data/` (or `DATA_PATH` is set)
- [ ] `python tests/test_pipeline.py` ends with `ALL TESTS PASSED`

**Running**
- [ ] Notebook: Kernel > Restart & Run All finished with no red errors; notebook saved (outputs visible)
- [ ] `outputs/figures` has 13 PNG files; `outputs/summary.json` exists
- [ ] `python src/build_report.py` created the report; I opened and read all of it
- [ ] The report no longer contains `[PENDING EXECUTION]`
- [ ] I replaced `[SUBMISSION DATE]` (`SUBMISSION_DATE` in `src/build_report.py`) and rebuilt the report
- [ ] I rewrote the conclusion in my own words and checked every finding against the tables

**Understanding**
- [ ] I can explain every notebook section and every cleaning step
- [ ] I read `docs/Viva_Questions.md` twice and added my real numbers to the answers
- [ ] I can explain the limitations (association is not causation; insights were drafted from results)

**GitHub**
- [ ] The repository is public, has a clear name and description
- [ ] The dataset file is **not** uploaded (license not verified)
- [ ] The notebook (with outputs), README, `src`, `outputs` and the report are uploaded

**Honesty**
- [ ] I did not claim the internship is verified or completed by YuvaIntern; I only submit this project
