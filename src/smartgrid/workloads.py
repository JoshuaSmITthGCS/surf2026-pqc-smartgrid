"""Real smart-grid dataset loading and payload construction utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "smart_grid_dataset.csv"

TIMESTAMP_COLUMN = "Timestamp"
VOLTAGE_COLUMN = "Voltage (V)"
CURRENT_COLUMN = "Current (A)"
POWER_COLUMN = "Power Consumption (kW)"
REACTIVE_POWER_COLUMN = "Reactive Power (kVAR)"
POWER_FACTOR_COLUMN = "Power Factor"
SOLAR_POWER_COLUMN = "Solar Power (kW)"
WIND_POWER_COLUMN = "Wind Power (kW)"
GRID_SUPPLY_COLUMN = "Grid Supply (kW)"
VOLTAGE_FLUCTUATION_COLUMN = "Voltage Fluctuation (%)"
OVERLOAD_COLUMN = "Overload Condition"
TRANSFORMER_FAULT_COLUMN = "Transformer Fault"
TEMPERATURE_COLUMN = "Temperature (\N{DEGREE SIGN}C)"
HUMIDITY_COLUMN = "Humidity (%)"
PRICE_COLUMN = "Electricity Price (USD/kWh)"
PREDICTED_LOAD_COLUMN = "Predicted Load (kW)"

REQUIRED_COLUMNS = (
    TIMESTAMP_COLUMN,
    VOLTAGE_COLUMN,
    CURRENT_COLUMN,
    POWER_COLUMN,
    REACTIVE_POWER_COLUMN,
    POWER_FACTOR_COLUMN,
    SOLAR_POWER_COLUMN,
    WIND_POWER_COLUMN,
    GRID_SUPPLY_COLUMN,
    VOLTAGE_FLUCTUATION_COLUMN,
    OVERLOAD_COLUMN,
    TRANSFORMER_FAULT_COLUMN,
    TEMPERATURE_COLUMN,
    HUMIDITY_COLUMN,
    PRICE_COLUMN,
    PREDICTED_LOAD_COLUMN,
)


@dataclass(slots=True, frozen=True)
class SmartGridDatasetSummary:
    """Compact quality and range summary for the real telemetry CSV."""

    path: str
    rows: int
    columns: int
    start_timestamp: str
    end_timestamp: str
    interval_minutes: float
    missing_values: int
    duplicate_timestamps: int
    overload_count: int
    transformer_fault_count: int
    mean_voltage_v: float
    mean_current_a: float
    mean_power_kw: float
    max_power_kw: float
    mean_power_factor: float
    mean_price_usd_per_kwh: float
    mean_predicted_load_kw: float

    def to_row(self) -> dict[str, object]:
        """Return a display-friendly dict with stable rounding."""

        row = asdict(self)
        for field, value in row.items():
            if isinstance(value, float):
                row[field] = round(value, 6)
        return row


def load_smart_grid_dataset(path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load and validate the smart-grid telemetry dataset."""

    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Smart-grid dataset not found: {dataset_path}")

    frame = pd.read_csv(dataset_path, parse_dates=[TIMESTAMP_COLUMN])
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    return frame.sort_values(TIMESTAMP_COLUMN).reset_index(drop=True)


def summarize_smart_grid_dataset(
    frame: pd.DataFrame,
    *,
    path: str | Path = DEFAULT_DATASET_PATH,
) -> SmartGridDatasetSummary:
    """Summarize dataset coverage and basic data quality checks."""

    if frame.empty:
        raise ValueError("Cannot summarize an empty smart-grid dataset.")

    intervals = frame[TIMESTAMP_COLUMN].diff().dropna().dt.total_seconds().div(60)
    interval_minutes = float(intervals.mode().iloc[0]) if not intervals.empty else 0.0

    return SmartGridDatasetSummary(
        path=str(Path(path)),
        rows=int(len(frame)),
        columns=int(len(frame.columns)),
        start_timestamp=str(frame[TIMESTAMP_COLUMN].min()),
        end_timestamp=str(frame[TIMESTAMP_COLUMN].max()),
        interval_minutes=interval_minutes,
        missing_values=int(frame.isna().sum().sum()),
        duplicate_timestamps=int(frame[TIMESTAMP_COLUMN].duplicated().sum()),
        overload_count=int(frame[OVERLOAD_COLUMN].sum()),
        transformer_fault_count=int(frame[TRANSFORMER_FAULT_COLUMN].sum()),
        mean_voltage_v=float(frame[VOLTAGE_COLUMN].mean()),
        mean_current_a=float(frame[CURRENT_COLUMN].mean()),
        mean_power_kw=float(frame[POWER_COLUMN].mean()),
        max_power_kw=float(frame[POWER_COLUMN].max()),
        mean_power_factor=float(frame[POWER_FACTOR_COLUMN].mean()),
        mean_price_usd_per_kwh=float(frame[PRICE_COLUMN].mean()),
        mean_predicted_load_kw=float(frame[PREDICTED_LOAD_COLUMN].mean()),
    )


def _row_to_telemetry_dict(row: pd.Series) -> dict[str, object]:
    """Normalize one dataset row into compact JSON-safe telemetry fields."""

    timestamp = row[TIMESTAMP_COLUMN]
    if hasattr(timestamp, "isoformat"):
        timestamp_value = timestamp.isoformat()
    else:
        timestamp_value = str(timestamp)

    return {
        "timestamp": timestamp_value,
        "voltage_v": round(float(row[VOLTAGE_COLUMN]), 6),
        "current_a": round(float(row[CURRENT_COLUMN]), 6),
        "power_kw": round(float(row[POWER_COLUMN]), 6),
        "reactive_power_kvar": round(float(row[REACTIVE_POWER_COLUMN]), 6),
        "power_factor": round(float(row[POWER_FACTOR_COLUMN]), 6),
        "solar_kw": round(float(row[SOLAR_POWER_COLUMN]), 6),
        "wind_kw": round(float(row[WIND_POWER_COLUMN]), 6),
        "grid_supply_kw": round(float(row[GRID_SUPPLY_COLUMN]), 6),
        "voltage_fluctuation_pct": round(float(row[VOLTAGE_FLUCTUATION_COLUMN]), 6),
        "overload": int(row[OVERLOAD_COLUMN]),
        "transformer_fault": int(row[TRANSFORMER_FAULT_COLUMN]),
        "temperature_c": round(float(row[TEMPERATURE_COLUMN]), 6),
        "humidity_pct": round(float(row[HUMIDITY_COLUMN]), 6),
        "price_usd_per_kwh": round(float(row[PRICE_COLUMN]), 6),
        "predicted_load_kw": round(float(row[PREDICTED_LOAD_COLUMN]), 6),
    }


def payload_from_dataset(
    frame: pd.DataFrame,
    size_bytes: int,
    *,
    row_offset: int = 0,
) -> bytes:
    """Build an exact-size payload from real telemetry rows.

    Rows are serialized as compact JSON lines, concatenated, and truncated to the
    requested byte count. This keeps benchmark payloads reproducible while still
    deriving bytes from the real smart-grid dataset.
    """

    if size_bytes < 1:
        raise ValueError("size_bytes must be at least 1")
    if frame.empty:
        raise ValueError("Cannot build payloads from an empty dataset.")

    chunks: list[bytes] = []
    total_bytes = 0
    row_index = row_offset
    while total_bytes < size_bytes:
        row = frame.iloc[row_index % len(frame)]
        payload_line = json.dumps(
            _row_to_telemetry_dict(row),
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        payload_line += b"\n"
        chunks.append(payload_line)
        total_bytes += len(payload_line)
        row_index += 1

    return b"".join(chunks)[:size_bytes]


def build_payloads(
    frame: pd.DataFrame,
    payload_sizes: Iterable[int],
    *,
    row_offset: int = 0,
) -> dict[int, bytes]:
    """Return exact-size telemetry-derived payloads keyed by byte length."""

    return {
        int(size): payload_from_dataset(frame, int(size), row_offset=row_offset)
        for size in payload_sizes
    }


__all__ = [
    "DEFAULT_DATASET_PATH",
    "REQUIRED_COLUMNS",
    "SmartGridDatasetSummary",
    "build_payloads",
    "load_smart_grid_dataset",
    "payload_from_dataset",
    "summarize_smart_grid_dataset",
]
