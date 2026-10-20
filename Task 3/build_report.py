"""
build_report.py - creates the project report (Word + PDF) from the REAL results.

How to use (after you have run the notebook or `python src/analysis.py`):
    python src/build_report.py                 # writes Real_World_Dataset_Analysis_Report.docx (+ .pdf if possible)
    python src/build_report.py --template      # writes a report TEMPLATE with "[PENDING EXECUTION]" placeholders

It reads outputs/summary.json and outputs/figures/*.png, which are produced by the analysis.
Nothing is typed in by hand: every number in the report comes from your data file.
If outputs/summary.json does not exist yet, the template version is created automatically.

PDF: created with LibreOffice (if installed) or docx2pdf (if installed). Otherwise open the .docx in
Microsoft Word and use File > Save As > PDF.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------- edit these details ----------------
STUDENT = "Lokesh Patwal"
COURSE = "B.Tech, 3rd Year"
COLLEGE = "Invertis University"
INTERNSHIP = "YuvaIntern"
PERIOD = "October 01, 2026 to November 26, 2026"
SUBMISSION_DATE = "[SUBMISSION DATE]"
# -----------------------------------------------------

TITLE = "Real-World Dataset Analysis Project"
DATASET_URL = "https://www.kaggle.com/datasets/apoorvaappz/global-super-store-dataset"
NAVY, BLUE, GREY = RGBColor(0x1F, 0x38, 0x64), RGBColor(0x2E, 0x75, 0xB6), RGBColor(0x59, 0x59, 0x59)
PENDING = "[PENDING EXECUTION]"


# ============================ small Word helpers ============================
def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def add_field(paragraph, instruction):
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, instruction), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
        run._r.append(el)
    return run


def style_document(doc):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = Cm(2.3); sec.bottom_margin = Cm(2.0)
    normal = doc.styles["Normal"]; normal.font.name = "Calibri"; normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.paragraph_format.space_after = Pt(6); normal.paragraph_format.line_spacing = 1.12
    for name, size, color in (("Heading 1", 18, NAVY), ("Heading 2", 14, BLUE), ("Heading 3", 12, NAVY)):
        st = doc.styles[name]; st.font.name = "Calibri"; st.font.size = Pt(size); st.font.bold = True; st.font.color.rgb = color
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        st.paragraph_format.space_before = Pt(16 if name == "Heading 1" else 10); st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True


def header_footer(doc):
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True            # no header/footer on the cover page
    hp = sec.header.paragraphs[0]; hp.text = ""
    r = hp.add_run(f"{TITLE}"); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = NAVY
    r = hp.add_run(f"\t\t{INTERNSHIP} Internship Report"); r.font.size = Pt(9); r.font.color.rgb = GREY
    fp = sec.footer.paragraphs[0]; fp.text = ""
    r = fp.add_run(f"{STUDENT}  |  {COLLEGE}\t\tPage "); r.font.size = Pt(9); r.font.color.rgb = GREY
    pr = add_field(fp, "PAGE"); pr.font.size = Pt(9); pr.font.color.rgb = GREY


def para(doc, text="", bold=False, italic=False, size=None, color=None, align=None, space_after=None):
    p = doc.add_paragraph()
    parts = text.split("**")
    for i, chunk in enumerate(parts):
        if not chunk:
            continue
        r = p.add_run(chunk); r.bold = bold or (i % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
    if align: p.alignment = align
    if space_after is not None: p.paragraph_format.space_after = Pt(space_after)
    return p


def bullets(doc, items, style="List Bullet"):
    for t in items:
        p = doc.add_paragraph(style=style)
        parts = t.split("**")
        for i, chunk in enumerate(parts):
            if chunk:
                r = p.add_run(chunk); r.bold = (i % 2 == 1)
        p.paragraph_format.space_after = Pt(2)


def table(doc, header, rows, widths_cm=None, font=9):
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; shade(c, "1F3864")
        r = c.paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(font); r.font.color.rgb = RGBColor(255, 255, 255)
    trPr = t.rows[0]._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trPr.append(h)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(font)
            if ri % 2: shade(cells[i], "F2F6FB")
    if widths_cm:
        t.autofit = False
        for row in t.rows:
            for i, w in enumerate(widths_cm):
                row.cells[i].width = Cm(w)
    for row in t.rows:
        for c in row.cells:
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def note_box(doc, title, text, fill="FDF1E7"):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; c = t.rows[0].cells[0]; shade(c, fill); c.text = ""
    r = c.paragraphs[0].add_run(title + " "); r.bold = True
    c.paragraphs[0].add_run(text)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def n0(x):
    return f"{x:,.0f}"


# ============================ report content ============================
def build(summary: dict | None, figures_dir: Path, out_docx: Path):
    real = summary is not None
    K = summary["kpis"] if real else {}
    P = lambda key, fmt="{:,.0f}": (fmt.format(K[key]) if real and key in K else PENDING)

    doc = Document(); style_document(doc); header_footer(doc)

    # ---------- cover page ----------
    for _ in range(3): doc.add_paragraph()
    para(doc, "INTERNSHIP PROJECT REPORT", bold=True, size=13, color=BLUE, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, TITLE, bold=True, size=30, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    para(doc, "Analysis of the Global Superstore Sales Dataset", size=15, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "Python | Jupyter Notebook | Pandas | NumPy | SciPy | Matplotlib | Seaborn", size=11, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3): doc.add_paragraph()
    t = doc.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for a, b in (("Submitted by:", STUDENT), ("Course / Year:", COURSE), ("College / University:", COLLEGE),
                 ("Internship Provider:", INTERNSHIP), ("Internship Period:", PERIOD), ("Date of Submission:", SUBMISSION_DATE)):
        cells = t.add_row().cells
        r = cells[0].paragraphs[0].add_run(a); r.bold = True; r.font.size = Pt(12); r.font.color.rgb = NAVY
        r = cells[1].paragraphs[0].add_run(b); r.bold = True; r.font.size = Pt(12)
        cells[0].width, cells[1].width = Cm(5.5), Cm(9.5)
    if not real:
        for _ in range(2): doc.add_paragraph()
        note_box(doc, "REPORT TEMPLATE - RESULTS PENDING EXECUTION.",
                 "The structure, methodology and explanations are final. Every place marked " + PENDING + " is filled automatically with the real numbers, "
                 "tables and charts when you run the notebook (or python src/analysis.py) and then python src/build_report.py.")
    doc.add_page_break()

    # ---------- contents ----------
    doc.add_heading("Contents", level=1)
    sections = ["Project Title and Summary", "Objectives and Problem Statement", "Dataset Source and Description", "Methodology",
                "Data Cleaning Procedures", "Exploratory Data Analysis Results", "Charts and Interpretations",
                "Key Findings and Evidence", "Business Recommendations", "Limitations", "Conclusion", "References"]
    for i, s in enumerate(sections, 1):
        para(doc, f"{i}.  {s}", space_after=3)
    doc.add_page_break()

    # ---------- 1 ----------
    doc.add_heading("1. Project Title and Summary", level=1)
    para(doc, f"**{TITLE}** is an internship project completed through {INTERNSHIP}. It analyses a real-world retail dataset, the Global Superstore Sales dataset, "
              "to find where sales and profit come from, where money is lost, how sales change over time and how discounts affect profitability. "
              "The work covers dataset selection, environment setup, data exploration, cleaning, exploratory data analysis (EDA), statistical analysis, "
              "visualization and business recommendations, using Python, Pandas, NumPy, SciPy, Matplotlib and Seaborn in a Jupyter Notebook.")
    if real:
        para(doc, f"**Summary of results:** the analysed data covers {K['date_min']} to {K['date_max']} with {n0(K['n_orders'])} orders ({n0(K['n_lines'])} order lines). "
                  f"Total sales are {n0(K['total_sales'])} and total profit is {n0(K['total_profit'])}, a profit margin of {K['profit_margin_pct']:.1f}%. "
                  f"{K['loss_line_pct']:.1f}% of order lines are loss-making.")
    else:
        para(doc, f"**Summary of results:** {PENDING}")

    # ---------- 2 ----------
    doc.add_heading("2. Objectives and Problem Statement", level=1)
    doc.add_heading("Problem statement", level=2)
    para(doc, "Using the order data of a global retailer, which categories, sub-categories, products, markets and customers generate the most sales and profit, "
              "how do sales change over time, and how do discounts affect profitability? The answers should lead to practical, evidence-based recommendations.")
    doc.add_heading("Objectives", level=2)
    bullets(doc, ["Select a reliable real-world dataset and understand its business context.",
                  "Explore the dataset structure, data types, distributions, missing values, duplicates and relationships.",
                  "Clean and preprocess the data appropriately and document every change.",
                  "Perform exploratory data analysis (EDA) using Pandas, NumPy and statistical techniques.",
                  "Create meaningful visualizations using Matplotlib and Seaborn.",
                  "Present findings, interpretations, conclusions and recommendations in a professional notebook and report."], "List Number")

    # ---------- 3 ----------
    doc.add_heading("3. Dataset Source and Description", level=1)
    table(doc, ["Item", "Details"], [
        ["Dataset", "Global Superstore (file Global_Superstore2.csv; Excel version in the same download)"],
        ["Source", f"Kaggle, dataset apoorvaappz/global-super-store-dataset ({DATASET_URL})"],
        ["Documented size", "51,290 rows x 24 columns (as reported by published notebooks that use this file)"],
        ["Size in this analysis", (f"{n0(summary['rows_raw'])} raw rows; {n0(summary['rows_clean'])} rows after cleaning; file: {summary['source_file']}" if real else PENDING)],
        ["License", "Not verified from outside Kaggle; check the License field on the Kaggle page. The data file is therefore not redistributed in the project repository."],
        ["Business context", "Order lines of a global retailer selling products in several categories to customers in many countries and markets."],
    ], [4, 12.4])
    para(doc, "**Important columns:** Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Segment, Country, Market, Region, Category, Sub-Category, Product Name, "
              "Sales, Quantity, Discount, Profit, Shipping Cost and Order Priority. Column meanings follow the public dataset descriptions. "
              "The dataset is suitable because it contains dates, categories, numerical measures and several business dimensions (product, market, customer, shipping), "
              "and has enough records for meaningful analysis.")

    # ---------- 4 ----------
    doc.add_heading("4. Methodology", level=1)
    bullets(doc, ["**Environment:** Python, a virtual environment, Jupyter Notebook, Pandas, NumPy, SciPy, Matplotlib and Seaborn (requirements.txt).",
                  "**Loading:** the file is read with automatic text-encoding detection; column names are standardised; a schema check reports missing columns.",
                  "**Exploration:** head/tail, shape, data types, descriptive statistics, missing values and percentages, duplicates, unique values, category counts, skewness and date inspection.",
                  "**Quality assessment:** missing values, duplicates, impossible values (negative sales, zero quantity, discount outside 0-1, shipping before ordering) and outliers by the IQR rule.",
                  "**Cleaning:** seven documented steps on a copy of the data; the original is never modified; an audit log records the rows affected by each step.",
                  "**EDA:** KPIs, sales and profit by category, sub-category, market, region, time, product, customer and segment, discount analysis and loss-making items.",
                  "**Statistics:** descriptive statistics, skewness and kurtosis, Pearson and Spearman correlation, Kruskal-Wallis and Mann-Whitney tests (non-parametric, because the data is skewed).",
                  "**Visualization:** 13 charts with titles, labelled axes and interpretations.",
                  "**Reproducibility:** one command (python src/analysis.py) repeats the whole analysis; automated checks are in tests/test_pipeline.py."])

    # ---------- 5 ----------
    doc.add_heading("5. Data Cleaning Procedures", level=1)
    if real:
        audit = summary["cleaning_audit"]
        table(doc, ["Step", "Description", "Rows before", "Rows after", "Rows removed", "Details"],
              [[a["step"], a["description"], n0(a["rows_before"]), n0(a["rows_after"]), n0(a["rows_removed"]), a["details"]] for a in audit],
              [1.0, 4.0, 1.9, 1.9, 1.9, 5.7], font=8)
        q = summary["quality"]
        para(doc, f"**Quality findings before cleaning:** exact duplicate rows: {q['exact_duplicates']}; rows identical except Row ID: {q['duplicates_ignoring_row_id']}. "
                  "Impossible-value counts: " + ", ".join(f"{k} = {v}" for k, v in q["invalid_values"].items()) + ".")
        para(doc, "**Decisions:** exact duplicates and impossible records were removed; small amounts of missing data were filled (median for numbers, 'Unknown' for text); "
                  "columns with 5% or more missing values were kept but not used; outliers were flagged and **kept** because they are genuine large orders or heavy losses. "
                  f"Rows: {n0(summary['rows_raw'])} before cleaning, {n0(summary['rows_clean'])} after.")
    else:
        table(doc, ["Step", "Description", "Rows before", "Rows after", "Rows removed", "Details"],
              [[i, d, PENDING, PENDING, PENDING, PENDING] for i, d in enumerate(
                  ["Strip spaces from text columns", "Convert data types (dates, numbers); check discount scale", "Handle missing values",
                   "Remove exact duplicate rows", "Remove impossible values", "Create new columns", "Flag outliers (IQR rule) - kept in data"], 1)],
              [1.0, 4.4, 1.9, 1.9, 1.9, 5.3], font=8)
        para(doc, "**Decisions (design of the cleaning, final):** exact duplicates and impossible records are removed; small amounts of missing data are filled (median for numbers, 'Unknown' for text); "
                  "columns with 5% or more missing values are kept but not used; outliers are flagged and kept because they are genuine business events. The original data is preserved.")

    # ---------- 6 ----------
    doc.add_heading("6. Exploratory Data Analysis Results", level=1)
    if real:
        table(doc, ["Key figure", "Value"], [
            ["Period", f"{K['date_min']} to {K['date_max']}"], ["Orders / order lines", f"{n0(K['n_orders'])} / {n0(K['n_lines'])}"],
            ["Customers", n0(K["n_customers"]) if "n_customers" in K else "n/a"],
            ["Total sales", n0(K["total_sales"])], ["Total profit", n0(K["total_profit"])], ["Profit margin", f"{K['profit_margin_pct']:.2f}%"],
            ["Average / median order value", f"{n0(K['avg_order_value'])} / {n0(K['median_order_value'])}"],
            ["Average discount", f"{K['avg_discount_pct']:.1f}%"], ["Loss-making order lines", f"{n0(K['loss_lines'])} ({K['loss_line_pct']:.1f}%)"],
        ], [6, 10.4])
        prev = summary["tables_preview"]
        for key, label in (("category", "Sales and profit by category"), ("market", "Sales and profit by market"),
                           ("year", "Sales and profit by year"), ("discount_band", "Profit margin by discount band")):
            if key in prev and prev[key]:
                doc.add_heading(label, level=2)
                rows = prev[key]; idx = [c for c in rows[0] if c not in ("sales", "profit", "profit_margin_pct", "lines", "orders", "quantity", "avg_discount", "loss_lines",
                                                                       "loss_line_pct", "sales_growth_pct", "profit_growth_pct", "median_margin", "avg_order_value")][0]
                table(doc, [idx.replace("_", " ").title(), "Sales", "Profit", "Margin %", "Loss-making lines %"],
                      [[r[idx], n0(r["sales"]), n0(r["profit"]), f"{r['profit_margin_pct']:.1f}", f"{r['loss_line_pct']:.1f}"] for r in rows], [4.4, 3.2, 3.2, 2.6, 3.0])
        st = summary["stats"]
        doc.add_heading("Statistical tests", level=2)
        rows = []
        for name, v in st.items():
            if name == "outlier_sensitivity": continue
            main = {k: val for k, val in v.items() if k in ("rho", "H", "U", "p_value")}
            rows.append([name.replace("_", " "), ", ".join(f"{k} = {val:.3g}" for k, val in main.items())])
        if rows: table(doc, ["Test", "Result"], rows, [7, 9.4])
    else:
        table(doc, ["Key figure", "Value"], [[k, PENDING] for k in
              ["Period", "Orders / order lines", "Customers", "Total sales", "Total profit", "Profit margin", "Average / median order value", "Average discount", "Loss-making order lines"]], [6, 10.4])
        para(doc, f"Tables of sales and profit by category, market, year and discount band, and the results of the statistical tests (Spearman, Kruskal-Wallis, Mann-Whitney): {PENDING}")

    # ---------- 7 ----------
    doc.add_heading("7. Charts and Interpretations", level=1)
    if real and summary["figures"]:
        for i, f in enumerate(summary["figures"], 1):
            path = figures_dir / f["file"]
            if path.exists():
                doc.add_picture(str(path), width=Cm(14.5)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            para(doc, f"Figure {i}: {f['title']}", italic=True, size=9.5, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
            para(doc, "**Interpretation:** " + f["interpretation"])
    else:
        para(doc, f"Thirteen charts are inserted here after execution ({PENDING}): sales and profit by category; profit by sub-category; sales and profit by market; "
                  "profit-margin heatmap; distributions of sales and profit; monthly trend; yearly sales by category; discount versus profit; profit box plot; "
                  "correlation heatmap; top and bottom products; shipping analysis; year-month sales heatmap. Each chart is followed by a written interpretation.")

    # ---------- 8 ----------
    doc.add_heading("8. Key Findings and Evidence", level=1)
    if real:
        for i, ins in enumerate(summary["insights"], 1):
            doc.add_heading(f"Finding {i}: {ins['title']}", level=3)
            bullets(doc, [f"**Observation:** {ins['observation']}", f"**Evidence:** {ins['evidence']}",
                          f"**Business significance:** {ins['significance']}", f"**Recommendation:** {ins['recommendation']}"])
    else:
        para(doc, f"Ten findings are generated from the results ({PENDING}). Each finding has four parts: **observation**, **numerical evidence**, "
                  "**business significance** and **recommendation**. Topics: overall performance; category; sub-category and loss-makers; market/region; trend and seasonality; "
                  "top and loss-making products; customers and segments; discount versus profit; shipping; outliers.")

    # ---------- 9 ----------
    doc.add_heading("9. Business Recommendations", level=1)
    if real:
        bullets(doc, [f"**{ins['title']}:** {ins['recommendation']}" for ins in summary["insights"]], "List Number")
    else:
        para(doc, f"Recommendations derived from each finding: {PENDING}")

    # ---------- 10-12 ----------
    doc.add_heading("10. Limitations", level=1)
    bullets(doc, ["**Association, not causation:** correlations and group differences describe the data; they do not prove cause and effect.",
                  "**Single dataset:** the results describe this file and may not hold for other periods, companies or countries.",
                  "**Unknown definitions:** the exact meaning of Profit and the currency are not documented in the sources that could be verified.",
                  "**Outliers kept:** extreme orders influence totals and averages; medians and non-parametric tests were used to reduce the effect.",
                  "**Unused columns:** columns with many missing values (for example postal code, if affected) were not used.",
                  "**Descriptive only:** no forecasting or machine-learning model was built.",
                  "**Drafted insights:** the finding text is generated by rules from the results and was reviewed by the student."])
    doc.add_heading("11. Conclusion", level=1)
    if real:
        para(doc, f"The project analysed {n0(K['n_orders'])} orders from {K['date_min']} to {K['date_max']} after documented cleaning ({n0(summary['rows_raw'])} raw rows, "
                  f"{n0(summary['rows_clean'])} after cleaning). Total sales were {n0(K['total_sales'])} and total profit {n0(K['total_profit'])} (margin {K['profit_margin_pct']:.1f}%). "
                  "The analysis identified the categories, markets and products that drive profit, the areas that lose money, the seasonal pattern of sales and the relationship between "
                  "discount level and profit margin, and turned them into recommendations. Python, Pandas, NumPy, SciPy, Matplotlib and Seaborn made the analysis reproducible.")
        para(doc, "(Add a paragraph in your own words about what you learned.)", italic=True, color=GREY)
    else:
        para(doc, f"Conclusion based on the real results: {PENDING}")
    doc.add_heading("12. References", level=1)
    bullets(doc, [f"Kaggle dataset: Global Superstore, apoorvaappz/global-super-store-dataset. {DATASET_URL}",
                  "The pandas development team. pandas documentation. https://pandas.pydata.org/docs/",
                  "NumPy Developers. NumPy documentation. https://numpy.org/doc/",
                  "SciPy Developers. SciPy documentation (scipy.stats). https://docs.scipy.org/doc/scipy/",
                  "Matplotlib Development Team. Matplotlib documentation. https://matplotlib.org/stable/",
                  "Waskom, M. L. seaborn: statistical data visualization. https://seaborn.pydata.org/",
                  "Project Jupyter. Jupyter Notebook documentation. https://jupyter-notebook.readthedocs.io/"], "List Number")
    out_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_docx)
    return out_docx


def convert_to_pdf(docx_path: Path) -> Path | None:
    """Try LibreOffice, then docx2pdf. Returns the PDF path or None."""
    for exe in ("soffice", "libreoffice"):
        found = shutil.which(exe)
        if found:
            try:
                subprocess.run([found, "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent), str(docx_path)],
                               check=True, capture_output=True, timeout=180)
                pdf = docx_path.with_suffix(".pdf")
                if pdf.exists():
                    return pdf
            except Exception:
                pass
    try:
        from docx2pdf import convert            # works on Windows/Mac with Microsoft Word installed
        convert(str(docx_path), str(docx_path.with_suffix(".pdf")))
        return docx_path.with_suffix(".pdf")
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the project report (DOCX + PDF) from the real results")
    ap.add_argument("--summary", default=str(PROJECT_ROOT / "outputs" / "summary.json"))
    ap.add_argument("--out-dir", default=str(PROJECT_ROOT))
    ap.add_argument("--template", action="store_true", help="build the template with [PENDING EXECUTION] placeholders")
    args = ap.parse_args(argv)
    summary_path = Path(args.summary)
    summary = None
    if not args.template and summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    elif not args.template:
        print(f"NOTE: {summary_path} not found - building the TEMPLATE. Run the notebook or 'python src/analysis.py' first for the real report.")
    out = build(summary, summary_path.parent / "figures", Path(args.out_dir) / "Real_World_Dataset_Analysis_Report.docx")
    print("Created:", out, "(real results)" if summary else "(TEMPLATE - results pending)")
    pdf = convert_to_pdf(out)
    print("Created:", pdf) if pdf else print("PDF not created automatically. Open the .docx in Word and use File > Save As > PDF.")


if __name__ == "__main__":
    main()
