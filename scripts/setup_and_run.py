"""One-command bootstrap: pull latest code, download the dataset, run the suite.

This orchestrates the full Phase 1 workflow so you only run a single command:

    1. PULL   the latest code for the working branch from origin.
    2. DOWNLOAD the Smart Meters in London dataset (via kagglehub) into
       ``data/smart-meters-in-london`` if it is not already present.
    3. RUN    the HE baseline comparison (Paillier vs BFV vs CKKS) on it.

Examples:

    python scripts/setup_and_run.py                 # pull, download, full run
    python scripts/setup_and_run.py --quick         # fast smoke run
    python scripts/setup_and_run.py --skip-pull --meters 50 --blocks 0,1
    python scripts/setup_and_run.py --skip-pull --dataset sgcc --row 975
    python scripts/setup_and_run.py --install        # also pip install -r requirements.txt

Notes:
- A Kaggle API token at ``~/.kaggle/kaggle.json`` is required for the download
  step. If the dataset folder already exists, the download is skipped.
- Run this from an environment where the project dependencies are installed
  (for example the ``surf26`` conda env). Use ``--install`` to install them.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRANCH = "claude/gifted-cerf-bkk9a2"
KAGGLE_DATASET = "jeanmidev/smart-meters-in-london"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "smart-meters-in-london"
COMPARISON_SCRIPT = PROJECT_ROOT / "scripts" / "run_he_baseline_comparison.py"


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    """Run a command, echoing it, and raise on a non-zero exit."""

    print(f"\n$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def _run_with_retry(cmd: list[str], *, cwd: Path | None = None, attempts: int = 4) -> None:
    """Run a command, retrying with exponential backoff on failure (2,4,8,16s)."""

    for attempt in range(1, attempts + 1):
        try:
            _run(cmd, cwd=cwd)
            return
        except subprocess.CalledProcessError:
            if attempt == attempts:
                raise
            delay = 2**attempt
            print(f"  command failed (attempt {attempt}/{attempts}); retrying in {delay}s")
            time.sleep(delay)


def pull_branch(branch: str) -> None:
    """Fetch and fast-forward the working branch from origin, with retries."""

    print(f"==> Pulling latest code for '{branch}' from origin")
    _run_with_retry(["git", "fetch", "origin", branch], cwd=PROJECT_ROOT)
    # Switch to the branch (create a local tracking branch if needed).
    try:
        _run(["git", "checkout", branch], cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError:
        _run(["git", "checkout", "-b", branch, f"origin/{branch}"], cwd=PROJECT_ROOT)
    _run_with_retry(["git", "pull", "origin", branch], cwd=PROJECT_ROOT)


def install_requirements() -> None:
    """Install pinned dependencies into the active environment."""

    print("==> Installing requirements")
    _run([sys.executable, "-m", "pip", "install", "-r", str(PROJECT_ROOT / "requirements.txt")])


def ensure_dataset(data_dir: Path) -> Path:
    """Return a usable dataset root, downloading it via kagglehub if absent."""

    if data_dir.exists():
        print(f"==> Dataset already present at {data_dir} (skipping download)")
        return data_dir

    print(f"==> Downloading {KAGGLE_DATASET} via kagglehub")
    try:
        import kagglehub
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "kagglehub is not installed. Run with --install, or "
            "`pip install kagglehub`, then retry."
        ) from exc

    downloaded = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    print(f"    downloaded to {downloaded}")

    # Expose the download at the canonical default location via a symlink so the
    # runner finds it with no flags. Fall back to using the cache path directly.
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(downloaded, data_dir, target_is_directory=True)
        print(f"    linked {data_dir} -> {downloaded}")
        return data_dir
    except OSError as exc:
        print(f"    could not create symlink ({exc}); using the cache path directly")
        return downloaded


def run_comparison(dataset_root: Path, passthrough: list[str]) -> int:
    """Invoke the HE baseline comparison on the dataset."""

    print("==> Starting HE baseline comparison (Paillier vs BFV vs CKKS)")
    cmd = [
        sys.executable,
        str(COMPARISON_SCRIPT),
        "--london-path",
        str(dataset_root),
        *passthrough,
    ]
    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Branch to pull from origin.")
    parser.add_argument("--skip-pull", action="store_true", help="Do not pull from origin.")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Do not download the dataset; use the default location as-is.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="pip install -r requirements.txt before running.",
    )
    # Pass-through options forwarded to run_he_baseline_comparison.py.
    parser.add_argument("--quick", action="store_true", help="Fast smoke run.")
    parser.add_argument(
        "--dataset",
        choices=("london", "sgcc", "df"),
        help="Dataset source forwarded to the HE comparison runner.",
    )
    parser.add_argument("--sgcc-path", type=str, help="Path to SGCC archive or data.csv.")
    parser.add_argument("--df-path", type=str, help="Path to the derived df.csv.")
    parser.add_argument(
        "--df-all-numeric",
        action="store_true",
        help="Use all numeric df.csv columns instead of electricity-only columns.",
    )
    parser.add_argument("--output-tag", type=str, help="Tag for output CSV filenames.")
    parser.add_argument("--trials", type=int, help="Per-operation trial count.")
    parser.add_argument("--meters", type=int, help="Max household meters to use.")
    parser.add_argument("--blocks", type=str, help="Comma-separated block indices.")
    parser.add_argument("--row", type=int, help="Timestamp row index for the reading vector.")
    args = parser.parse_args()

    if not args.skip_pull:
        pull_branch(args.branch)
    if args.install:
        install_requirements()

    if args.skip_download:
        dataset_root = DEFAULT_DATA_DIR
    else:
        dataset_root = ensure_dataset(DEFAULT_DATA_DIR)

    passthrough: list[str] = []
    if args.quick:
        passthrough.append("--quick")
    if args.dataset is not None:
        passthrough += ["--dataset", args.dataset]
    if args.sgcc_path is not None:
        passthrough += ["--sgcc-path", args.sgcc_path]
    if args.df_path is not None:
        passthrough += ["--df-path", args.df_path]
    if args.df_all_numeric:
        passthrough.append("--df-all-numeric")
    if args.output_tag is not None:
        passthrough += ["--output-tag", args.output_tag]
    if args.trials is not None:
        passthrough += ["--trials", str(args.trials)]
    if args.meters is not None:
        passthrough += ["--meters", str(args.meters)]
    if args.blocks is not None:
        passthrough += ["--blocks", args.blocks]
    if args.row is not None:
        passthrough += ["--row", str(args.row)]

    return run_comparison(dataset_root, passthrough)


if __name__ == "__main__":
    raise SystemExit(main())
