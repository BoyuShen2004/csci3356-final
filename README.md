# CSCI 3356 Final Project

This guide walks you through setting up the **perch** conda environment and running the Django application.

## Prerequisites

- [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system.

---

## 1. Set up the conda environment

From the project root (`csci3356-final`), create a new conda environment named **perch** with Python 3.9:

```bash
conda create -n perch python=3.9 -y
```

Activate the environment:

```bash
conda activate perch
```

You should see `(perch)` in your terminal prompt when the environment is active.

---

## 2. Install dependencies

With the **perch** environment activated, install the project requirements:

```bash
pip install -r requirements.txt
```

This installs the packages listed in `requirements.txt` (including Django) into the perch environment.

---

## 3. Launch the Django app

1. Change into the Django project directory:

   ```bash
   cd perch
   ```

2. Start the development server:

   ```bash
   python manage.py runserver
   ```

3. Open a browser and go to:

   **http://127.0.0.1:8000/**

To stop the server, press `Ctrl+C` in the terminal.

---

## 4. After local changes: clean and push to GitHub

Before you commit and push, remove the local SQLite database file so it is not tracked:

```bash
rm -f perch/db.sqlite3
```

If `db.sqlite3` was already tracked in git, also run:

```bash
git rm --cached perch/db.sqlite3
```

Then push your work using your own branch (do **not** push directly to `main`):

```bash
git checkout -b your-branch-name
git add .
git commit -m "Describe your changes"
git push -u origin your-branch-name
```

After pushing, open a Pull Request from your branch to the original repository's `main` branch.

---

## Quick reference

| Step              | Command                                      |
|-------------------|----------------------------------------------|
| Create environment| `conda create -n perch python=3.9 -y`       |
| Activate          | `conda activate perch`                       |
| Install deps      | `pip install -r requirements.txt`            |
| Run app           | `cd perch` then `python manage.py runserver` |

---

## Deactivating the environment

When you're done working, leave the conda environment with:

```bash
conda deactivate
```
