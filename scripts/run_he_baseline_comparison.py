"""Phase 1 HE baseline comparison runner.

Runs the head-to-head comparison defined in Meeting 2 with Dr. Baza:

    Paillier (PHE)  -- the comparison baseline (Q5)
    BFV             -- exact integer meter aggregation
    CKKS            -- approximate real-valued telemetry analytics

Paillier is always benchmarked. BFV and CKKS are benchmarked automatically when
TenSEAL is installed; if TenSEAL is missing the script reports that and runs the
Paillier baseline alone, so the experiment is runnable in any environment.

Usage:

    python scripts/run_he_baseline_comparison.py
    python scripts/run_he_baseline_comparison.py --trials 50 --quick
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner
from src.fhe import paillier_scheme


def _try_import_tenseal_modules():
    """Return (bfv_scheme, ckks_scheme) if TenSEAL is importable, else None."""

    try:
        import tenseal  # noqa: F401
    except ImportError:
        return None

    from src.fhe import bfv_scheme, ckks_scheme

    return bfv_scheme, ckks_scheme


def _summary_table(records: list[BenchmarkRecord]) -> Table:
    table = Table(
        title="Phase 1 HE Baseline Comparison",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("Scheme", style="cyan")
    table.add_column("Mode", style="magenta")
    table.add_column("Operation")
    table.add_column("Mean ms", justify="right")
    table.add_column("P95 ms", justify="right")
    for record in records:
        table.add_row(
            record.scheme,
            record.mode,
            record.operation,
            f"{record.mean_ms:.4f}",
            f"{record.p95_ms:.4f}",
        )
    return table


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=25, help="Per-operation trial count.")
    parser.add_argument(
        "--keygen-trials",
        type=int,
        default=3,
        help="Trial count for the slower key-generation step.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use small trial counts for a fast smoke run.",
    )
    args = parser.parse_args()

    trials = 5 if args.quick else args.trials
    keygen_trials = 1 if args.quick else args.keygen_trials

    console = Console()
    runner = BenchmarkRunner(
        results_dir=PROJECT_ROOT / "benchmarks" / "results" / "workstation",
        console=console,
    )

    console.rule("[bold]Paillier (PHE) baseline")
    records = paillier_scheme.benchmark_paillier_baseline(
        runner,
        trials=trials,
        keygen_trials=keygen_trials,
        export_path="he_comparison_paillier.csv",
    )
    for key_bits in paillier_scheme.DEFAULT_PAILLIER_KEY_SIZES:
        expansion = paillier_scheme.ciphertext_expansion(key_bits)
        console.print(
            f"[green]Paillier-{key_bits}[/green] ciphertext "
            f"{expansion.ciphertext_bytes} B  "
            f"(expansion {expansion.expansion_ratio:.0f}x over "
            f"{expansion.plaintext_bytes} B plaintext)"
        )

    tenseal_modules = _try_import_tenseal_modules()
    if tenseal_modules is None:
        console.print(
            "[yellow]TenSEAL not installed -- skipping BFV and CKKS. "
            "Install requirements.txt to run the full comparison.[/yellow]"
        )
    else:
        bfv_scheme, ckks_scheme = tenseal_modules
        console.rule("[bold]BFV (exact integer aggregation)")
        records += bfv_scheme.benchmark_bfv_schemes(
            runner,
            trials=trials,
            export_path="he_comparison_bfv.csv",
        )
        console.rule("[bold]CKKS (approximate real-valued analytics)")
        records += ckks_scheme.benchmark_ckks_schemes(
            runner,
            trials=trials,
            export_path="he_comparison_ckks.csv",
        )

    console.rule("[bold]Summary")
    console.print(_summary_table(records))
    console.print(
        f"[green]Done.[/green] {len(records)} records exported under "
        f"{runner.results_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
