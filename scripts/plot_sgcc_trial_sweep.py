"""Build SGCC HE trial-sweep charts and projection tables.

The sweep inputs are the CSV files produced by:

    python scripts/run_he_baseline_comparison.py \
        --dataset sgcc --sgcc-path "archive (2)" --meters 50 --row 944 \
        --trials 50 --output-tag sgcc_sweep_t50

and the matching 100, 150, 200, 250, and 300 trial runs.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "benchmarks" / "results" / "workstation"
TRIAL_FILE_RE = re.compile(r"he_comparison_sgcc_sweep_t(?P<trials>\d+)_(?P<scheme>\w+)\.csv")
TRIALS = (50, 100, 150, 200, 250, 300)
CALLS_PER_DAY = (1, 24, 48, 96, 144, 288, 1440)

SELECTED_LABELS = (
    "Paillier PHE-2048",
    "Paillier PHE-3072",
    "BFV poly-4096",
    "BFV poly-8192",
    "CKKS balanced-8192",
    "CKKS high-depth-16384",
)


def _label(row: pd.Series) -> str:
    return f"{row['scheme']} {row['mode']}"


def load_sweep(results_dir: Path) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for path in sorted(results_dir.glob("he_comparison_sgcc_sweep_t*_*.csv")):
        match = TRIAL_FILE_RE.fullmatch(path.name)
        if not match:
            continue
        frame = pd.read_csv(path)
        frame["trials"] = int(match.group("trials"))
        frame["source_file"] = path.name
        rows.append(frame)

    if not rows:
        raise FileNotFoundError(
            f"No SGCC sweep CSVs found under {results_dir}. Run the sweep first."
        )

    sweep = pd.concat(rows, ignore_index=True)
    sweep["label"] = sweep.apply(_label, axis=1)
    sweep["payload_readings"] = (sweep["payload_bytes"] / 8).clip(lower=1)
    sweep["mean_calls_per_second"] = 1000 / sweep["mean_ms"]
    sweep["p95_calls_per_second"] = 1000 / sweep["p95_ms"]
    return sweep.sort_values(["trials", "scheme", "mode", "operation"])


def write_summary_tables(sweep: pd.DataFrame, results_dir: Path) -> tuple[Path, Path, Path]:
    summary_path = results_dir / "he_comparison_sgcc_sweep_summary.csv"
    rates_path = results_dir / "he_comparison_sgcc_sweep_rates.csv"
    projection_path = results_dir / "he_comparison_sgcc_calls_per_day_projection.csv"

    sweep.to_csv(summary_path, index=False)

    rate_rows: list[dict[str, object]] = []
    for (scheme, mode, operation), group in sweep.groupby(["scheme", "mode", "operation"]):
        group = group.sort_values("trials")
        if len(group) < 2:
            continue
        first = group.iloc[0]
        last = group.iloc[-1]
        slope_mean = np.polyfit(group["trials"], group["mean_ms"], 1)[0]
        slope_p95 = np.polyfit(group["trials"], group["p95_ms"], 1)[0]
        mean_delta = last["mean_ms"] - first["mean_ms"]
        p95_delta = last["p95_ms"] - first["p95_ms"]
        rate_rows.append(
            {
                "scheme": scheme,
                "mode": mode,
                "operation": operation,
                "trial_min": int(first["trials"]),
                "trial_max": int(last["trials"]),
                "mean_ms_at_50": first["mean_ms"],
                "mean_ms_at_300": last["mean_ms"],
                "mean_delta_ms_50_to_300": mean_delta,
                "mean_pct_change_50_to_300": (mean_delta / first["mean_ms"]) * 100,
                "mean_slope_ms_per_trial": slope_mean,
                "mean_slope_ms_per_50_trials": slope_mean * 50,
                "p95_ms_at_50": first["p95_ms"],
                "p95_ms_at_300": last["p95_ms"],
                "p95_delta_ms_50_to_300": p95_delta,
                "p95_pct_change_50_to_300": (p95_delta / first["p95_ms"]) * 100,
                "p95_slope_ms_per_trial": slope_p95,
                "p95_slope_ms_per_50_trials": slope_p95 * 50,
            }
        )

    rates = pd.DataFrame(rate_rows).sort_values(["scheme", "mode", "operation"])
    rates.to_csv(rates_path, index=False)

    latest = sweep[(sweep["trials"] == max(TRIALS)) & (sweep["operation"].isin(["encrypt", "add"]))]
    projection_rows: list[dict[str, object]] = []
    for _, row in latest.iterrows():
        payload_readings = max(float(row["payload_readings"]), 1.0)
        for calls in CALLS_PER_DAY:
            projection_rows.append(
                {
                    "scheme": row["scheme"],
                    "mode": row["mode"],
                    "operation": row["operation"],
                    "calls_per_house_per_day": calls,
                    "payload_readings": payload_readings,
                    "mean_ms_per_payload": row["mean_ms"],
                    "mean_seconds_per_day_per_payload": calls * row["mean_ms"] / 1000,
                    "mean_seconds_per_day_amortized_per_reading": (
                        calls * row["mean_ms"] / payload_readings / 1000
                    ),
                    "calls_per_second_per_payload": row["mean_calls_per_second"],
                    "amortized_readings_per_second": row["mean_calls_per_second"] * payload_readings,
                }
            )
    projections = pd.DataFrame(projection_rows).sort_values(
        ["operation", "scheme", "mode", "calls_per_house_per_day"]
    )
    projections.to_csv(projection_path, index=False)
    return summary_path, rates_path, projection_path


def _selected(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame["label"].isin(SELECTED_LABELS)].copy()


def _plot_lines(
    frame: pd.DataFrame,
    *,
    value: str,
    operation: str,
    title: str,
    ylabel: str,
    path: Path,
    log_y: bool = True,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2), constrained_layout=True)
    data = _selected(frame[frame["operation"] == operation])
    for label, group in data.groupby("label", sort=False):
        group = group.sort_values("trials")
        ax.plot(group["trials"], group[value], marker="o", linewidth=2, label=label)

    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Trials per operation")
    ax.set_ylabel(ylabel)
    ax.set_xticks(TRIALS)
    if log_y:
        ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_multiply(frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2), constrained_layout=True)
    data = _selected(frame[frame["operation"].isin(["multiply", "mul_plain"])])
    for label, group in data.groupby("label", sort=False):
        group = group.sort_values("trials")
        line_label = label
        if group["operation"].iloc[0] == "mul_plain":
            line_label = f"{label} mul_plain"
        ax.plot(group["trials"], group["mean_ms"], marker="o", linewidth=2, label=line_label)

    ax.set_title("SGCC Trial Sweep: Multiplication-Like Cost", fontweight="bold")
    ax.set_xlabel("Trials per operation")
    ax.set_ylabel("Mean latency (ms, log scale)")
    ax.set_xticks(TRIALS)
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_300_bars(frame: pd.DataFrame, path: Path) -> None:
    latest = _selected(frame[frame["trials"] == max(TRIALS)])
    ops = ["encrypt", "decrypt", "add", "multiply"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    for ax, operation in zip(axes.ravel(), ops, strict=True):
        operation_frame = latest[latest["operation"] == operation].copy()
        if operation_frame.empty and operation == "multiply":
            operation_frame = latest[latest["operation"] == "mul_plain"].copy()
        operation_frame = operation_frame.sort_values("mean_ms")
        ax.barh(operation_frame["label"], operation_frame["mean_ms"], color="#2E86AB")
        ax.set_title(operation)
        ax.set_xlabel("Mean latency (ms)")
        ax.set_xscale("log")
        ax.grid(True, axis="x", which="both", alpha=0.25)
    fig.suptitle("SGCC 300-Trial Mean Latency by Operation", fontweight="bold")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_rate_heatmap(rates: pd.DataFrame, path: Path) -> None:
    ops = ["encrypt", "decrypt", "add", "multiply"]
    filtered = rates[
        rates.apply(lambda row: f"{row['scheme']} {row['mode']}" in SELECTED_LABELS, axis=1)
        & rates["operation"].isin(ops)
    ].copy()
    filtered["label"] = filtered["scheme"] + " " + filtered["mode"]
    pivot = filtered.pivot_table(
        index="label",
        columns="operation",
        values="mean_pct_change_50_to_300",
        aggfunc="mean",
    ).reindex(index=SELECTED_LABELS, columns=ops)

    fig, ax = plt.subplots(figsize=(10.5, 5.8), constrained_layout=True)
    values = pivot.to_numpy(dtype=float)
    limit = np.nanmax(np.abs(values))
    image = ax.imshow(values, cmap="coolwarm", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_title("Mean Latency Change From 50 to 300 Trials", fontweight="bold")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for row_idx in range(values.shape[0]):
        for col_idx in range(values.shape[1]):
            value = values[row_idx, col_idx]
            if np.isnan(value):
                text = "n/a"
            else:
                text = f"{value:+.1f}%"
            ax.text(col_idx, row_idx, text, ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="% change in mean latency")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_daily_projection(
    projections: pd.DataFrame,
    *,
    operation: str,
    value_column: str,
    title: str,
    ylabel: str,
    path: Path,
) -> None:
    data = projections[
        (projections["operation"] == operation)
        & projections.apply(lambda row: f"{row['scheme']} {row['mode']}" in SELECTED_LABELS, axis=1)
    ].copy()
    data["label"] = data["scheme"] + " " + data["mode"]

    fig, ax = plt.subplots(figsize=(11, 6.2), constrained_layout=True)
    for label, group in data.groupby("label", sort=False):
        group = group.sort_values("calls_per_house_per_day")
        ax.plot(
            group["calls_per_house_per_day"],
            group[value_column],
            marker="o",
            linewidth=2,
            label=label,
        )

    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Calls per house per day")
    ax.set_ylabel(ylabel)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(CALLS_PER_DAY, [str(value) for value in CALLS_PER_DAY])
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_throughput(frame: pd.DataFrame, path: Path) -> None:
    latest = _selected(frame[(frame["trials"] == max(TRIALS)) & (frame["operation"] == "encrypt")])
    latest = latest.sort_values("mean_calls_per_second")

    fig, ax = plt.subplots(figsize=(11, 6.2), constrained_layout=True)
    ax.barh(latest["label"], latest["mean_calls_per_second"], color="#4E937A")
    ax.set_title("SGCC 300-Trial Encryption Throughput", fontweight="bold")
    ax.set_xlabel("Payload encryptions per second (higher is better)")
    ax.set_xscale("log")
    ax.grid(True, axis="x", which="both", alpha=0.25)
    for index, value in enumerate(latest["mean_calls_per_second"]):
        ax.text(value, index, f" {value:.1f}/s", va="center", fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def build_plots(sweep: pd.DataFrame, rates: pd.DataFrame, projections: pd.DataFrame, plots_dir: Path) -> list[Path]:
    plots_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        plots_dir / "sgcc_trial_sweep_encrypt_mean.png",
        plots_dir / "sgcc_trial_sweep_encrypt_p95.png",
        plots_dir / "sgcc_trial_sweep_add_mean.png",
        plots_dir / "sgcc_trial_sweep_multiply_mean.png",
        plots_dir / "sgcc_300_trial_operation_bars.png",
        plots_dir / "sgcc_trial_sweep_rate_of_change_heatmap.png",
        plots_dir / "sgcc_calls_per_day_encrypt_per_payload.png",
        plots_dir / "sgcc_calls_per_day_add_per_payload.png",
        plots_dir / "sgcc_calls_per_day_encrypt_amortized.png",
        plots_dir / "sgcc_calls_per_day_add_amortized.png",
        plots_dir / "sgcc_encryption_throughput_300_trials.png",
    ]

    _plot_lines(
        sweep,
        value="mean_ms",
        operation="encrypt",
        title="SGCC Trial Sweep: Encryption Mean Latency",
        ylabel="Mean latency (ms, log scale)",
        path=paths[0],
    )
    _plot_lines(
        sweep,
        value="p95_ms",
        operation="encrypt",
        title="SGCC Trial Sweep: Encryption P95 Latency",
        ylabel="P95 latency (ms, log scale)",
        path=paths[1],
    )
    _plot_lines(
        sweep,
        value="mean_ms",
        operation="add",
        title="SGCC Trial Sweep: Homomorphic Addition Mean Latency",
        ylabel="Mean latency (ms, log scale)",
        path=paths[2],
    )
    _plot_multiply(sweep, paths[3])
    _plot_300_bars(sweep, paths[4])
    _plot_rate_heatmap(rates, paths[5])
    _plot_daily_projection(
        projections,
        operation="encrypt",
        value_column="mean_seconds_per_day_per_payload",
        title="Projected Daily Cost: Edge Encryption Per Payload",
        ylabel="Mean compute seconds/day per encrypted payload",
        path=paths[6],
    )
    _plot_daily_projection(
        projections,
        operation="add",
        value_column="mean_seconds_per_day_per_payload",
        title="Projected Daily Cost: Server Addition Per Payload",
        ylabel="Mean compute seconds/day per encrypted payload",
        path=paths[7],
    )
    _plot_daily_projection(
        projections,
        operation="encrypt",
        value_column="mean_seconds_per_day_amortized_per_reading",
        title="Projected Daily Cost: Edge Encryption Amortized Per Reading",
        ylabel="Mean compute seconds/day, amortized per reading",
        path=paths[8],
    )
    _plot_daily_projection(
        projections,
        operation="add",
        value_column="mean_seconds_per_day_amortized_per_reading",
        title="Projected Daily Cost: Server Addition Amortized Per Reading",
        ylabel="Mean compute seconds/day, amortized per reading",
        path=paths[9],
    )
    _plot_throughput(sweep, paths[10])
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory containing SGCC sweep CSVs.",
    )
    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR / "plots",
        help="Directory for generated PNG charts.",
    )
    args = parser.parse_args()

    sweep = load_sweep(args.results_dir)
    summary_path, rates_path, projection_path = write_summary_tables(sweep, args.results_dir)
    rates = pd.read_csv(rates_path)
    projections = pd.read_csv(projection_path)
    plot_paths = build_plots(sweep, rates, projections, args.plots_dir)

    print(f"Wrote {summary_path}")
    print(f"Wrote {rates_path}")
    print(f"Wrote {projection_path}")
    for path in plot_paths:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
