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

The runner can also use the SGCC electricity-theft archive
(``archive (2)/data.csv``) or a derived feature dataframe (``df.csv``):

    python scripts/run_he_baseline_comparison.py --dataset sgcc --meters 50 --row 975
    python scripts/run_he_baseline_comparison.py --dataset df --row 0

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

DEFAULT_SGCC_PATH = PROJECT_ROOT / "archive (2)"
DEFAULT_DF_PATH = PROJECT_ROOT / "df.csv"


def _load_london_readings(args, console):
    """Return (integer_readings, float_readings) from the London dataset, or None."""

    if not args.london_path:
        return None

    from src.smartgrid import london_meters

    root = Path(args.london_path)
    if not root.exists():
        console.print(
            f"[yellow]London dataset not found at {root} -- using built-in "
            "sample vectors. Place the extracted dataset there (or pass "
            "--london-path) to benchmark on real meters.[/yellow]"
        )
        return None

    blocks = tuple(int(b) for b in args.blocks.split(",") if b.strip())
    try:
        matrix = london_meters.build_meter_matrix(
            root,
            blocks=blocks,
            max_meters=args.meters,
        )
    except (FileNotFoundError, ValueError) as exc:
        console.print(
            f"[yellow]Could not load London dataset ({exc}) -- using built-in "
            "sample vectors.[/yellow]"
        )
        return None

    summary = london_meters.summarize_meter_matrix(matrix, root=root, blocks=blocks)
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


def _load_sgcc_readings(args, console):
    """Return readings from the SGCC electricity-theft archive, or None."""

    from src.smartgrid import electricity_theft

    root = Path(args.sgcc_path)
    if not root.exists():
        console.print(
            f"[yellow]SGCC archive not found at {root} -- using built-in "
            "sample vectors. Place the extracted archive there (or pass "
            "--sgcc-path) to benchmark on the SGCC data.[/yellow]"
        )
        return None

    try:
        matrix = electricity_theft.build_sgcc_meter_matrix(
            root,
            max_meters=args.meters,
        )
    except (FileNotFoundError, ValueError) as exc:
        console.print(
            f"[yellow]Could not load SGCC archive ({exc}) -- using built-in "
            "sample vectors.[/yellow]"
        )
        return None

    summary = electricity_theft.summarize_matrix(
        matrix,
        source=str(root),
        notes="SGCC electricity-theft wide daily customer readings",
    )
    console.print(
        f"[cyan]SGCC electricity-theft archive[/cyan]: {summary.meters} "
        f"customers x {summary.timesteps} daily readings "
        f"({summary.start_timestamp} .. {summary.end_timestamp})"
    )
    row = args.row % len(matrix)
    float_readings = electricity_theft.readings_at(matrix, row=row)
    integer_readings = electricity_theft.integer_readings_at(matrix, row=row)
    console.print(
        f"[cyan]Daily customer vector @ row {args.row} "
        f"({matrix.index[row]})[/cyan]: {len(float_readings)} live customers, "
        f"total {sum(float_readings):.3f} kWh"
    )
    return integer_readings, float_readings


def _load_df_readings(args, console):
    """Return readings from the local derived df.csv feature matrix, or None."""

    from src.smartgrid import electricity_theft

    path = Path(args.df_path)
    if not path.exists():
        console.print(
            f"[yellow]Derived df.csv not found at {path} -- using built-in "
            "sample vectors. Place the CSV there (or pass --df-path).[/yellow]"
        )
        return None

    try:
        matrix = electricity_theft.build_df_feature_matrix(
            path,
            max_features=args.meters,
            electricity_only=not args.df_all_numeric,
        )
    except (FileNotFoundError, ValueError) as exc:
        console.print(
            f"[yellow]Could not load derived dataframe ({exc}) -- using built-in "
            "sample vectors.[/yellow]"
        )
        return None

    summary = electricity_theft.summarize_matrix(
        matrix,
        source=str(path),
        notes="derived hourly electricity feature matrix",
    )
    console.print(
        f"[cyan]Derived df.csv feature matrix[/cyan]: {summary.meters} "
        f"features x {summary.timesteps} rows "
        f"({summary.start_timestamp} .. {summary.end_timestamp})"
    )
    row = args.row % len(matrix)
    float_readings = electricity_theft.readings_at(matrix, row=row)
    integer_readings = electricity_theft.integer_readings_at(matrix, row=row)
    console.print(
        f"[cyan]Feature vector @ row {args.row}[/cyan]: "
        f"{len(float_readings)} live features, total {sum(float_readings):.3f}"
    )
    return integer_readings, float_readings


def _load_dataset_readings(args, console):
    """Dispatch to the selected real-data loader."""

    if args.dataset == "london":
        return _load_london_readings(args, console)
    if args.dataset == "sgcc":
        return _load_sgcc_readings(args, console)
    if args.dataset == "df":
        return _load_df_readings(args, console)
    raise ValueError(f"Unsupported dataset: {args.dataset}")


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


def _export_name(args, scheme: str) -> str:
    """Return a scheme export filename, tagging non-London datasets."""

    tag = args.output_tag
    if tag is None:
        tag = "" if args.dataset == "london" else args.dataset
    if tag:
        return f"he_comparison_{tag}_{scheme}.csv"
    return f"he_comparison_{scheme}.csv"


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
        default=str(PROJECT_ROOT / "data" / "smart-meters-in-london"),
        help=(
            "Path to the Smart Meters in London dataset. Defaults to "
            "data/smart-meters-in-london; if that folder is absent the runner "
            "falls back to built-in sample vectors. Pass an empty string to "
            "force the built-in vectors."
        ),
    )
    parser.add_argument(
        "--dataset",
        choices=("london", "sgcc", "df"),
        default="london",
        help=(
            "Real-data source to use: london (Smart Meters in London), sgcc "
            "(archive (2)/data.csv), or df (derived df.csv feature matrix)."
        ),
    )
    parser.add_argument(
        "--sgcc-path",
        type=str,
        default=str(DEFAULT_SGCC_PATH),
        help="Path to the SGCC electricity-theft archive directory or data.csv.",
    )
    parser.add_argument(
        "--df-path",
        type=str,
        default=str(DEFAULT_DF_PATH),
        help="Path to the derived df.csv feature dataset.",
    )
    parser.add_argument(
        "--df-all-numeric",
        action="store_true",
        help="Use all numeric df.csv columns instead of electricity-only columns.",
    )
    parser.add_argument(
        "--output-tag",
        type=str,
        default=None,
        help=(
            "Tag inserted into output filenames. Defaults to the dataset name "
            "for sgcc/df and no tag for london."
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

    readings = _load_dataset_readings(args, console)
    integer_readings = float_readings = None
    paillier_kwargs: dict = {}
    bfv_kwargs: dict = {}
    ckks_kwargs: dict = {}
    if readings is not None:
        integer_readings, float_readings = readings
        paillier_kwargs["sample_values"] = tuple(integer_readings)
        bfv_kwargs["sample_values"] = tuple(integer_readings)
        ckks_kwargs["sample_values"] = tuple(float_readings)

    console.rule("[bold]Paillier (PHE) baseline")
    records = paillier_scheme.benchmark_paillier_baseline(
        runner,
        trials=trials,
        keygen_trials=keygen_trials,
        export_path=_export_name(args, "paillier"),
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
            export_path=_export_name(args, "bfv"),
            **bfv_kwargs,
        )
        console.rule("[bold]CKKS (approximate real-valued analytics)")
        records += ckks_scheme.benchmark_ckks_schemes(
            runner,
            trials=trials,
            export_path=_export_name(args, "ckks"),
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
