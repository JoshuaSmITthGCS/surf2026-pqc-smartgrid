"""Loader and multi-meter workload helpers for the Smart Meters in London dataset.

Dataset: ``jeanmidev/smart-meters-in-london`` on Kaggle (the Low Carbon London /
UK Power Networks trial). Unlike ``data/smart_grid_dataset.csv`` -- a single
telemetry feed -- this dataset is a TRUE multi-household source: ~5,567 London
households with half-hourly kWh readings, tariff type (Standard vs. Time-of-Use),
and Acorn demographic groups. That makes it the dataset for the privacy-
preserving meter-AGGREGATION use case (sum across households at one interval)
and the demand-response pipeline described in the Meeting 2 slides.

This module is intentionally separate from ``workloads.py`` so the existing
single-feed Week 1 flow keeps working unchanged.

Expected layout (download with ``kagglehub.dataset_download(...)``)::

    <root>/informations_households.csv          LCLid, stdorToU, Acorn, Acorn_grouped, file
    <root>/.../halfhourly_dataset/block_0.csv    LCLid, tstp, energy(kWh/hh)
    ...                                          block_1.csv ... block_111.csv

Each household (``LCLid``) lives in exactly one block, so a single block holds a
few dozen meters -- enough for an aggregation demo. Load more blocks for a wider
multi-meter scenario. ``energy(kWh/hh)`` contains occasional ``Null`` strings,
which are coerced to ``NaN`` and dropped from reading vectors.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

LCLID_COLUMN = "LCLid"
TIMESTAMP_COLUMN = "tstp"
ENERGY_COLUMN = "energy(kWh/hh)"
HOUSEHOLD_INFO_FILENAME = "informations_households.csv"
# kWh -> Wh integer scale for exact-integer aggregation (Paillier / BFV / BGV).
DEFAULT_WH_SCALE = 1000


@dataclass(slots=True, frozen=True)
class LondonMeterSummary:
    """Compact summary of a loaded multi-meter slice."""

    root: str
    blocks: tuple[int, ...]
    meters: int
    timesteps: int
    start_timestamp: str
    end_timestamp: str
    missing_readings: int
    mean_kwh_per_hh: float
    max_kwh_per_hh: float

    def to_row(self) -> dict[str, object]:
        row = asdict(self)
        row["blocks"] = ",".join(str(b) for b in self.blocks)
        for field, value in row.items():
            if isinstance(value, float):
                row[field] = round(value, 6)
        return row


def resolve_dataset_root(path: str | Path) -> Path:
    """Return the dataset root, accepting the path returned by ``kagglehub``."""

    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"London dataset path not found: {root}")
    return root


def _find_block_files(root: Path) -> dict[int, Path]:
    """Map block index -> block CSV path, searching the nested layout robustly."""

    blocks: dict[int, Path] = {}
    for candidate in root.rglob("block_*.csv"):
        # Prefer half-hourly blocks; skip daily aggregates if both are present.
        if "daily" in candidate.parent.name.lower():
            continue
        stem = candidate.stem  # "block_7"
        try:
            index = int(stem.split("_", 1)[1])
        except (IndexError, ValueError):
            continue
        blocks.setdefault(index, candidate)
    if not blocks:
        raise FileNotFoundError(
            f"No half-hourly block_*.csv files found under {root}. "
            "Check that the Smart Meters in London dataset downloaded correctly."
        )
    return blocks


def load_household_info(path: str | Path) -> pd.DataFrame:
    """Load ``informations_households.csv`` (tariff type and Acorn groups)."""

    root = resolve_dataset_root(path)
    matches = list(root.rglob(HOUSEHOLD_INFO_FILENAME))
    if not matches:
        raise FileNotFoundError(
            f"{HOUSEHOLD_INFO_FILENAME} not found under {root}."
        )
    return pd.read_csv(matches[0])


def _load_block_frame(block_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(block_path)
    energy_col = (
        ENERGY_COLUMN
        if ENERGY_COLUMN in frame.columns
        else next(col for col in frame.columns if "energy" in col.lower())
    )
    frame = frame.rename(columns={energy_col: ENERGY_COLUMN})
    frame[ENERGY_COLUMN] = pd.to_numeric(frame[ENERGY_COLUMN], errors="coerce")
    frame[TIMESTAMP_COLUMN] = pd.to_datetime(frame[TIMESTAMP_COLUMN], errors="coerce")
    return frame[[LCLID_COLUMN, TIMESTAMP_COLUMN, ENERGY_COLUMN]].dropna(
        subset=[TIMESTAMP_COLUMN]
    )


def build_meter_matrix(
    path: str | Path,
    *,
    blocks: Iterable[int] = (0,),
    max_meters: int | None = None,
    max_timesteps: int | None = None,
) -> pd.DataFrame:
    """Build a ``timestamp x meter`` matrix of half-hourly kWh readings.

    Rows are timestamps; columns are household ``LCLid`` meters; values are kWh
    per half hour (``NaN`` where a reading was ``Null`` or absent). A single
    timestamp row is the per-meter vector to aggregate homomorphically.
    """

    root = resolve_dataset_root(path)
    available = _find_block_files(root)
    requested = list(blocks)
    missing = [b for b in requested if b not in available]
    if missing:
        raise ValueError(
            f"Requested blocks not found: {missing}. "
            f"Available blocks range 0..{max(available)}."
        )

    frames = [_load_block_frame(available[b]) for b in requested]
    long_frame = pd.concat(frames, ignore_index=True)

    matrix = long_frame.pivot_table(
        index=TIMESTAMP_COLUMN,
        columns=LCLID_COLUMN,
        values=ENERGY_COLUMN,
        aggfunc="mean",
    ).sort_index()

    if max_meters is not None:
        matrix = matrix.iloc[:, :max_meters]
    if max_timesteps is not None:
        matrix = matrix.iloc[:max_timesteps, :]
    return matrix


def summarize_meter_matrix(
    matrix: pd.DataFrame,
    *,
    root: str | Path,
    blocks: Iterable[int],
) -> LondonMeterSummary:
    """Summarize coverage and quality for a loaded meter matrix."""

    if matrix.empty:
        raise ValueError("Cannot summarize an empty meter matrix.")

    return LondonMeterSummary(
        root=str(Path(root)),
        blocks=tuple(int(b) for b in blocks),
        meters=int(matrix.shape[1]),
        timesteps=int(matrix.shape[0]),
        start_timestamp=str(matrix.index.min()),
        end_timestamp=str(matrix.index.max()),
        missing_readings=int(matrix.isna().sum().sum()),
        mean_kwh_per_hh=float(matrix.mean(skipna=True).mean()),
        max_kwh_per_hh=float(matrix.max(skipna=True).max()),
    )


def readings_at(matrix: pd.DataFrame, *, row: int = 0) -> list[float]:
    """Return the per-meter kWh vector at one timestamp, dropping missing meters.

    This is the CKKS-ready real-valued input for encrypted averaging.
    """

    if matrix.empty:
        raise ValueError("Meter matrix is empty.")
    series = matrix.iloc[row % len(matrix)].dropna()
    return [float(value) for value in series.tolist()]


def integer_readings_at(
    matrix: pd.DataFrame,
    *,
    row: int = 0,
    scale: int = DEFAULT_WH_SCALE,
) -> list[int]:
    """Return the per-meter reading vector as scaled integers (Wh by default).

    This is the Paillier / BFV / BGV-ready exact-integer input for encrypted
    aggregation. Values are kWh * ``scale`` rounded to the nearest integer.
    """

    return [int(round(value * scale)) for value in readings_at(matrix, row=row)]


__all__ = [
    "DEFAULT_WH_SCALE",
    "ENERGY_COLUMN",
    "HOUSEHOLD_INFO_FILENAME",
    "LCLID_COLUMN",
    "LondonMeterSummary",
    "TIMESTAMP_COLUMN",
    "build_meter_matrix",
    "integer_readings_at",
    "load_household_info",
    "readings_at",
    "resolve_dataset_root",
    "summarize_meter_matrix",
]
