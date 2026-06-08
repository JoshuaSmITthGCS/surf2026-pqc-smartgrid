"""Phase 1 HE baseline comparison runner.

Runs the head-to-head comparison defined in Meeting 2 with Dr. Baza:

    Paillier (PHE)  -- the comparison baseline (Q5)
    BFV             -- exact integer meter aggregation
    CKKS            -- approximate real-valued telemetry analytics

Paillier is always benchmarked. BFV and CKKS are benchmarked automatically when
TenSEAL is installed; if TenSEAL is missing the script reports that and runs the
Paillier baseline alone, so the experiment is runnable in any environment.

By default the benchmarks use small built-in sample vectors. Pass
``--london-path`` (the path returned by ``kagglehub.dataset_download(
"jeanmidev/smart-meters-in-london")``) to drive the readings from the real
Smart Meters in London multi-household dataset and run an encrypted multi-meter
aggregation correctness check.

Usage:

    python scripts/run_he_baseline_comparison.py
    python scripts/run_he_baseline_comparison.py --trials 50 --quick
    python scripts/run_he_baseline_comparison.py \
        --london-path ~/.cache/kagglehub/datasets/jeanmidev/smart-meters-in-london/versions/10 \
        --meters 20
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


def _load_london_readings(args, console):
    """Return (integer_readings, float_readings) from the London dataset, or None."""

    if not args.london_path:
        return None

    from src.smartgrid import london_meters

    blocks = tuple(int(b) for b in args.blocks.split(",") if b.strip())
    matrix = london_meters.build_meter_matrix(
        args.london_path,
        blocks=blocks,
        max_meters=args.meters,
    )
    summary = london_meters.summarize_meter_matrix(
        matrix, root=args.london_path, blocks=blocks
    )
    console.print(
        f"[cyan]Smart Meters in London[/cyan]: {summary.meters} meters x "
        f"{summary.timesteps} timesteps  (blocks {summary.blocks}, "
        f"{summary.start_timestamp} .. {summary.end_timestamp})"
    )
    float_readings = london_meters.readings_at(matrix, row=args.row)
    integer_readings = london_meters.integer_readings_at(matrix, row=args.row)
    console.print(
        f"[cyan]Per-meter vector @ row {args.row}[/cyan]: "
        f"{len(float_readings)} live meters, "
        f"total {sum(float_readings):.3f} kWh"
    )
    return integer_readings, float_readings


def _aggregation_check(console, integer_readings, float_readings) -> None:
    """Verify encrypted multi-meter aggregation matches the cleartext total."""

    demo = paillier_scheme.encrypted_sum_demo(integer_readings, key_bits=2048)
    status = "OK" if demo["decrypted_total"] == demo["expected_total"] else "MISMATCH"
    console.print(
        f"[bold]Encrypted aggregation (Paillier)[/bold]: decrypted "
        f"{demo['decrypted_total']} Wh == expected {demo['expected_total']} Wh "
        f"[{status}] across {demo['sample_count']} meters"
    )


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
    parser.add_argument(
        "--london-path",
        type=str,
        default=None,
        help=(
            "Path to the Smart Meters in London dataset (the path returned by "
            "kagglehub.dataset_download). Drives readings from real data."
        ),
    )
    parser.add_argument(
        "--blocks",
        type=str,
        default="0",
        help="Comma-separated half-hourly block indices to load (default: 0).",
    )
    parser.add_argument(
        "--meters",
        type=int,
        default=12,
        help="Max number of household meters to use from the dataset.",
    )
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help="Timestamp row index to take the per-meter reading vector from.",
    )
    args = parser.parse_args()

    trials = 5 if args.quick else args.trials
    keygen_trials = 1 if args.quick else args.keygen_trials

    console = Console()
    runner = BenchmarkRunner(
        results_dir=PROJECT_ROOT / "benchmarks" / "results" / "workstation",
        console=console,
    )

    london = _load_london_readings(args, console)
    integer_readings = float_readings = None
    paillier_kwargs: dict = {}
    bfv_kwargs: dict = {}
    ckks_kwargs: dict = {}
    if london is not None:
        integer_readings, float_readings = london
        paillier_kwargs["sample_values"] = tuple(integer_readings)
        bfv_kwargs["sample_values"] = tuple(integer_readings)
        ckks_kwargs["sample_values"] = tuple(float_readings)

    console.rule("[bold]Paillier (PHE) baseline")
    records = paillier_scheme.benchmark_paillier_baseline(
        runner,
        trials=trials,
        keygen_trials=keygen_trials,
        export_path="he_comparison_paillier.csv",
        **paillier_kwargs,
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
            **bfv_kwargs,
        )
        console.rule("[bold]CKKS (approximate real-valued analytics)")
        records += ckks_scheme.benchmark_ckks_schemes(
            runner,
            trials=trials,
            export_path="he_comparison_ckks.csv",
            **ckks_kwargs,
        )

    if integer_readings is not None:
        console.rule("[bold]Encrypted multi-meter aggregation check")
        _aggregation_check(console, integer_readings, float_readings)

    console.rule("[bold]Summary")
    console.print(_summary_table(records))
    console.print(
        f"[green]Done.[/green] {len(records)} records exported under "
        f"{runner.results_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
