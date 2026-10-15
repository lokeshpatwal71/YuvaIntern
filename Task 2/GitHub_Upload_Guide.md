# Uploading the Project to GitHub (Step by Step)

## A. Before you start
1. Create a free account at https://github.com if you do not have one.
2. Install Git for Windows from https://git-scm.com/download/win (keep the default options).
3. Open CMD or PowerShell and tell Git who you are (one time only):
```
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```
Use the same email as your GitHub account.

## B. Choose a good repository name and description
A good name is short, lowercase, uses hyphens instead of spaces and says what the project is.

* Name: `hands-on-data-lab`  (or `hands-on-data-lab-supermarket-analysis`)
* Description:
  `Hands-on data analysis project using Python, Jupyter, pandas, Matplotlib and Seaborn: data cleaning, EDA, visualization and statistics (Yuva Intern internship)`
* Visibility: **Public** (so the evaluator can open it)
* Topics (optional): `python`, `data-analysis`, `pandas`, `jupyter-notebook`, `eda`, `data-visualization`

## C. Create the empty repository on GitHub
1. Click **+** (top right) > **New repository**.
2. Fill in the name and description from Section B and choose **Public**.
3. **Do NOT tick** "Add a README", "Add .gitignore" or "Choose a license". The project already has them, and ticking them causes conflicts.
4. Click **Create repository**. Keep this page open; you need the repository link.

## D. Upload using Git commands
Open CMD or PowerShell **inside the project folder** (the folder that contains `data`, `notebooks`, `src`):
```
cd %USERPROFILE%\Desktop\Hands-On-Data-Lab
```

| Command | What it does (simple words) |
|---|---|
| `git init` | Turns this folder into a Git repository (creates a hidden `.git` folder that tracks changes) |
| `git add .` | Selects **all** files in the folder to be saved in the next snapshot (files listed in `.gitignore` are skipped). The dot means "everything here" |
| `git status` | Shows which files are selected. Use it to check that `venv` is not in the list |
| `git commit -m "Initial commit: Hands-On Data Lab project"` | Takes the snapshot (a "commit") with a short message describing it |
| `git branch -M main` | Names the main line of work `main` (GitHub's default name) |
| `git remote add origin https://github.com/YOUR-USERNAME/hands-on-data-lab.git` | Tells Git the address of your GitHub repository. `origin` is just a nickname for it. Copy the real link from the GitHub page |
| `git push -u origin main` | Sends your commits to GitHub. `-u` remembers the connection so next time `git push` is enough |

Run them in this order:
```
git init
git add .
git status
git commit -m "Initial commit: Hands-On Data Lab project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/hands-on-data-lab.git
git push -u origin main
```
**Login:** GitHub no longer accepts your account password for `git push`. A browser window usually opens for you to sign in (Git Credential Manager). If it asks for a password in the terminal, create a **Personal Access Token** (GitHub > Settings > Developer settings > Personal access tokens) and paste it instead.

After the push, refresh your repository page. You should see all folders and the README with its charts.

## E. Alternative without Git (browser upload)
1. Open your new repository > **Add file > Upload files**.
2. Drag the **contents** of the project folder (not the outer folder) into the page. Folders are kept.
3. Type a commit message and click **Commit changes**.
(The browser can handle up to about 100 files at a time, which is enough for this project. The `.gitignore` file is hidden in Windows; turn on "Hidden items" in File Explorer to see and upload it.)

## F. What to upload and what to exclude
**Upload:**
* `data/` (the dataset and its README)
* `notebooks/Hands_On_Data_Lab.ipynb`
* `src/` (both Python files)
* `visualizations/` (the 8 PNG charts)
* `report/` (Markdown and Word report)
* `docs/`
* `README.md`, `requirements.txt`, `.gitignore`

**Do not upload (the `.gitignore` already excludes them):**
* `venv/` or `.venv/`: your virtual environment (large and not needed; others recreate it with `requirements.txt`)
* `__pycache__/` and `*.pyc`: temporary Python files
* `.ipynb_checkpoints/`: Jupyter autosave copies
* `.vscode/`, `.DS_Store`, `Thumbs.db`: editor/system files

## G. Updating the repository later
After editing any file (for example, fixing a typo in the README):
```
git add .
git commit -m "Add my name and details"
git push
```

## H. Final check on GitHub
* The README shows the title, tables and images correctly.
* Click `notebooks/Hands_On_Data_Lab.ipynb`: GitHub displays it with outputs and charts.
* The `Author` section has your real name.
