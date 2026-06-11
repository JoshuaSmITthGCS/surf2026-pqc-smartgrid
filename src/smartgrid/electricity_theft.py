"""Helpers for the SGCC electricity-theft and derived dataframe datasets.

The SGCC archive is a wide smart-meter dataset: one row per customer, metadata
columns ``CONS_NO`` and ``FLAG``, then one column per daily consumption reading.
For homomorphic aggregation, we transpose a slice into a ``date x customer``
matrix so one row is a multi-meter vector.

The local ``df.csv`` file is a derived hourly building-energy/theft dataframe.
It is not a household smart-meter matrix, but its electricity load columns are
useful as a compact real-valued feature-vector workload.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

SGCC_CUSTOMER_COLUMN = "CONS_NO"
SGCC_FLAG_COLUMN = "FLAG"
DEFAULT_SGCC_FILENAME = "data.csv"
DEFAULT_WH_SCALE = 1000
DF_EXCLUDED_NUMERIC_COLUMNS = {"0"}


@dataclass(slots=True, frozen=True)
class WideMeterSummary:
    """Compact summary for a wide smart-meter or feature-vector matrix."""

    source: str
    meters: int
    timesteps: int
    start_timestamp: str
    end_timestamp: str
    missing_readings: int
    mean_reading: float
    max_reading: float
    notes: str = ""

    def to_row(self) -> dict[str, object]:
        row = asdict(self)
        for field, value in row.items():
            if isinstance(value, float):
                row[field] = round(value, 6)
        return row


def resolve_sgcc_data_file(path: str | Path) -> Path:
    """Return the SGCC ``data.csv`` file, accepting either a file or directory."""

    root = Path(path)
    if root.is_file():
        return root
    candidate = root / DEFAULT_SGCC_FILENAME
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"SGCC data.csv not found at {root}")


def _date_columns(columns: Iterable[str]) -> list[str]:
    return [
        column
        for column in columns
        if column not in {SGCC_CUSTOMER_COLUMN, SGCC_FLAG_COLUMN}
    ]


def build_sgcc_meter_matrix(
    path: str | Path,
    *,
    max_meters: int | None = None,
    max_timesteps: int | None = None,
) -> pd.DataFrame:
    """Build a ``date x customer`` matrix from the SGCC wide archive CSV."""

    data_file = resolve_sgcc_data_file(path)
    frame = pd.read_csv(data_file, nrows=max_meters)
    if SGCC_CUSTOMER_COLUMN not in frame.columns:
        raise ValueError(f"{SGCC_CUSTOMER_COLUMN} column missing from {data_file}")

    date_cols = _date_columns(frame.columns)
    if not date_cols:
        raise ValueError(f"No daily reading columns found in {data_file}")

    parsed_dates = pd.to_datetime(date_cols, errors="coerce")
    ordered = sorted(
        (
            (date, column)
            for date, column in zip(parsed_dates, date_cols, strict=True)
            if not pd.isna(date)
        ),
        key=lambda item: item[0],
    )
    if max_timesteps is not None:
        ordered = ordered[:max_timesteps]
    ordered_dates = [item[0] for item in ordered]
    ordered_cols = [item[1] for item in ordered]

    values = frame[ordered_cols].apply(pd.to_numeric, errors="coerce")
    matrix = values.T
    matrix.index = pd.DatetimeIndex(ordered_dates, name="date")
    matrix.columns = frame[SGCC_CUSTOMER_COLUMN].astype(str).tolist()
    return matrix


def build_df_feature_matrix(
    path: str | Path,
    *,
    max_features: int | None = None,
    max_timesteps: int | None = None,
    electricity_only: bool = True,
) -> pd.DataFrame:
    """Build a ``row x feature`` matrix from the local derived ``df.csv`` file."""

    data_file = Path(path)
    if not data_file.exists():
        raise FileNotFoundError(f"Derived dataframe CSV not found: {data_file}")

    frame = pd.read_csv(data_file, nrows=max_timesteps)
    numeric = frame.select_dtypes(include="number").copy()
    numeric = numeric.drop(
        columns=[col for col in numeric.columns if col in DF_EXCLUDED_NUMERIC_COLUMNS],
        errors="ignore",
    )
    if electricity_only:
        electricity_cols = [
            col for col in numeric.columns if "electricity" in col.lower()
        ]
        if electricity_cols:
            numeric = numeric[electricity_cols]
    if max_features is not None:
        numeric = numeric.iloc[:, :max_features]
    if numeric.empty:
        raise ValueError(f"No numeric feature columns found in {data_file}")
    return numeric


def summarize_matrix(matrix: pd.DataFrame, *, source: str, notes: str = "") -> WideMeterSummary:
    """Summarize a wide meter or feature matrix."""

    if matrix.empty:
        raise ValueError("Cannot summarize an empty matrix.")

    return WideMeterSummary(
        source=source,
        meters=int(matrix.shape[1]),
        timesteps=int(matrix.shape[0]),
        start_timestamp=str(matrix.index.min()),
        end_timestamp=str(matrix.index.max()),
        missing_readings=int(matrix.isna().sum().sum()),
        mean_reading=float(matrix.mean(skipna=True).mean()),
        max_reading=float(matrix.max(skipna=True).max()),
        notes=notes,
    )


def readings_at(matrix: pd.DataFrame, *, row: int = 0) -> list[float]:
    """Return the reading vector at one matrix row, dropping missing values."""

    if matrix.empty:
        raise ValueError("Matrix is empty.")
    series = matrix.iloc[row % len(matrix)].dropna()
    return [float(value) for value in series.tolist()]


def integer_readings_at(
    matrix: pd.DataFrame,
    *,
    row: int = 0,
    scale: int = DEFAULT_WH_SCALE,
) -> list[int]:
    """Return scaled integer readings for exact HE aggregation."""

    return [int(round(value * scale)) for value in readings_at(matrix, row=row)]


__all__ = [
    "DEFAULT_SGCC_FILENAME",
    "DEFAULT_WH_SCALE",
    "SGCC_CUSTOMER_COLUMN",
    "SGCC_FLAG_COLUMN",
    "WideMeterSummary",
    "build_df_feature_matrix",
    "build_sgcc_meter_matrix",
    "integer_readings_at",
    "readings_at",
    "resolve_sgcc_data_file",
    "summarize_matrix",
]
