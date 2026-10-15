# Environment Setup on Windows (CMD / PowerShell)

Every command below can be copied and pasted. Open **Command Prompt** (press the Windows key, type `cmd`, Enter) or **PowerShell**.

## Step 1: Check whether Python is installed
```
python --version
```
* If you see something like `Python 3.12.x` (3.10 or newer is fine), go to Step 3.
* If you see "Python was not found" or "not recognized", try `py --version`. If that also fails, install Python (Step 2).

## Step 2: Install Python (only if needed)
1. Open https://www.python.org/downloads/ and download the latest Python 3 installer for Windows.
2. Run it. **Tick the box "Add python.exe to PATH"** on the first screen, then click **Install Now**.
3. Close the old terminal, open a new one and check again:
```
python --version
pip --version
```

## Step 3: Go to the project folder
Extract the project ZIP (for example to your Desktop) and move into the folder:
```
cd %USERPROFILE%\Desktop\Hands-On-Data-Lab
```
(In PowerShell use `cd $HOME\Desktop\Hands-On-Data-Lab`.) Check that you are in the right place:
```
dir
```
You should see `data`, `notebooks`, `src`, `README.md` and `requirements.txt`.

## Step 4: Create a virtual environment
A virtual environment is a private box of Python libraries for this project only, so it does not disturb other projects.
```
python -m venv venv
```

## Step 5: Activate the virtual environment
Command Prompt (CMD):
```
venv\Scripts\activate
```
PowerShell:
```
venv\Scripts\Activate.ps1
```
If PowerShell shows a "running scripts is disabled" error, run this once and activate again:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
When it works, `(venv)` appears at the start of the line.

## Step 6: Install the required libraries
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
This installs pandas, NumPy, Matplotlib, Seaborn, Jupyter and Notebook. It can take a few minutes.

## Step 7: Check Jupyter Notebook (installed by the step above)
```
jupyter --version
```
If this says "not recognized", install it directly:
```
pip install jupyter notebook
```

## Step 8: Launch Jupyter Notebook
Run this from the project folder (the one that contains `notebooks`):
```
jupyter notebook
```
Your browser opens automatically. If it does not, copy the `http://localhost:8888/...` link shown in the terminal into your browser. Keep the terminal window open while you work.

## Step 9: Open and run the notebook
1. In the browser, click the folder **notebooks**, then click **Hands_On_Data_Lab.ipynb**.
2. Click the menu **Kernel > Restart Kernel and Run All Cells** (in newer versions: **Run > Run All Cells**). Or run cell by cell with **Shift + Enter**.
3. The charts are saved automatically into the `visualizations` folder.
4. Press **Ctrl + S** to save. To stop Jupyter, press **Ctrl + C** twice in the terminal.

## Step 10 (optional): Run the Python script
```
python src/analysis.py
```
It prints the results in the terminal and saves 8 charts in `visualizations`.

## Common problems
| Problem | Solution |
|---|---|
| `python` is not recognized | Reinstall Python and tick "Add python.exe to PATH", or use `py` instead of `python` |
| `ModuleNotFoundError: No module named 'pandas'` | The virtual environment is not active (no `(venv)`), or libraries are not installed. Run Step 5 and Step 6 |
| `FileNotFoundError: dataset.csv not found` | Open the notebook from inside the `notebooks` folder of the project (do not move the notebook elsewhere) |
| PowerShell blocks `Activate.ps1` | Use the `Set-ExecutionPolicy` line in Step 5, or use CMD instead |
| Browser does not open | Copy the `http://localhost:8888` link from the terminal |
| Charts do not appear | Run the cell again; make sure the cell that imports the libraries (Section 5) was run first |
