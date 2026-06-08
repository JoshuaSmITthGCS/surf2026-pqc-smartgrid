# Codex Setup Instructions: Connect the Dataset and Start the CLI

Paste the block below to Codex (or another coding agent) inside VS Code, with the
`surf2026-pqc-smartgrid` folder open. It connects the project to the Smart Meters
in London dataset and starts the HE benchmark CLI. Commands assume macOS/Linux;
on Windows use the PowerShell notes where given.

---

## Task for Codex

You are working in the repository `surf2026-pqc-smartgrid`. Connect the project
to the Smart Meters in London dataset and start the benchmark CLI. Do the
following, in order, and stop and report if any step fails.

### 1. Use the correct branch

```bash
git checkout claude/gifted-cerf-bkk9a2
git pull origin claude/gifted-cerf-bkk9a2
```

### 2. Activate the environment and install dependencies

```bash
conda activate surf26
pip install -r requirements.txt
pip install gmpy2   # makes Paillier much faster; optional but recommended
```

If `conda` is not available, use the project virtualenv instead:

```bash
python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### 3. Connect the dataset

The benchmark runner reads the dataset from `data/smart-meters-in-london/` by
default. Put the data there using ONE of these options.

**Option A — I already extracted the Kaggle zip (folder named `archive (1)`):**

```bash
# from the repo root; quote the name because it contains a space
mv "archive (1)" data/smart-meters-in-london
```

**Option B — download it with kagglehub (needs a Kaggle API token):**

1. Create a token at kaggle.com -> Account -> "Create New Token". Save the
   downloaded `kaggle.json` to `~/.kaggle/kaggle.json` (on Windows:
   `%USERPROFILE%\.kaggle\kaggle.json`), then `chmod 600 ~/.kaggle/kaggle.json`.
2. Let the bootstrap CLI download it automatically in step 4, or do it manually:

   ```bash
   python -c "import kagglehub; print(kagglehub.dataset_download('jeanmidev/smart-meters-in-london'))"
   ```

Verify the data is connected (this folder is gitignored on purpose and must NOT
be committed):

```bash
ls data/smart-meters-in-london
# expect: informations_households.csv, halfhourly_dataset/, daily_dataset/, ...
```

### 4. Start the CLI

Preferred — the one-command bootstrap (pull, download if missing, then run). Do
a fast smoke run first:

```bash
python scripts/setup_and_run.py --skip-pull --quick --meters 20 --blocks 0
```

If that prints `Encrypted aggregation (Paillier): decrypted N Wh == expected N Wh
[OK]`, run the full benchmark:

```bash
python scripts/setup_and_run.py --skip-pull --meters 50 --blocks 0,1 --trials 50
```

Equivalent direct call without the bootstrap wrapper:

```bash
python scripts/run_he_baseline_comparison.py --meters 50 --blocks 0,1 --trials 50
```

### 5. Report results

- Confirm the run finished with `Done. <N> records exported under .../benchmarks/results/workstation`.
- List the generated CSVs: `ls benchmarks/results/workstation/he_comparison_*.csv`.
- Do NOT commit the dataset or the generated CSVs (both are gitignored).

### Success criteria

- The dataset is present at `data/smart-meters-in-london/`.
- The CLI runs Paillier (always) plus BFV and CKKS (when TenSEAL is installed).
- The encrypted multi-meter aggregation check prints `[OK]`.

### If something fails

- `ModuleNotFoundError: phe` / `kagglehub` -> rerun step 2 in the active env.
- `London dataset not found ... using built-in sample vectors` -> the folder in
  step 3 is missing or misnamed; fix the path.
- Kaggle 403/auth error -> the `~/.kaggle/kaggle.json` token is missing or
  unreadable; redo step 3 Option B.1.
- BFV/CKKS skipped with "TenSEAL not installed" -> `pip install tenseal==0.3.16`
  (it is in `requirements.txt`).
