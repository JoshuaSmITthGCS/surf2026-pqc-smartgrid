"""Reusable benchmark harness for SURF 2026 experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
import csv
import gc
import platform
import socket
import statistics
import time

import numpy as np
import psutil
from rich.console import Console
from rich.table import Table

CSV_FIELDS = (
    "scheme",
    "mode",
    "key_size",
    "payload_bytes",
    "device",
    "operation",
    "mean_ms",
    "median_ms",
    "std_ms",
    "p95_ms",
    "timestamp",
)


@dataclass(slots=True, frozen=True)
class DeviceMetadata:
    """Structured device metadata collected once per benchmark session."""

    hostname: str
    system: str
    release: str
    machine: str
    processor: str
    ram_gb: float
    cpu_physical: int | None
    cpu_logical: int

    def as_label(self) -> str:
        """Collapse structured metadata into the single CSV device field."""

        processor = self.processor or self.machine
        return (
            f"{self.hostname} | {self.system} {self.release} | {processor} | "
            f"RAM {self.ram_gb:.1f} GB | CPU {self.cpu_logical} logical"
        )


@dataclass(slots=True, frozen=True)
class BenchmarkRecord:
    """Single benchmark result row."""

    scheme: str
    mode: str
    key_size: int
    payload_bytes: int
    device: str
    operation: str
    mean_ms: float
    median_ms: float
    std_ms: float
    p95_ms: float
    timestamp: str

    def to_row(self) -> dict[str, Any]:
        """Return a CSV-compatible row dict."""

        row = asdict(self)
        for field in ("mean_ms", "median_ms", "std_ms", "p95_ms"):
            row[field] = round(row[field], 6)
        return row


class BenchmarkRunner:
    """Time callables, summarize latency statistics, and export results."""

    def __init__(
        self,
        results_dir: str | Path = "benchmarks/results/workstation",
        *,
        console: Console | None = None,
        device_label: str | None = None,
    ) -> None:
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.console = console or Console()
        self.device_metadata = self._collect_device_metadata()
        self.device_label = device_label or self.device_metadata.as_label()

    @staticmethod
    def _collect_device_metadata() -> DeviceMetadata:
        uname = platform.uname()
        return DeviceMetadata(
            hostname=socket.gethostname(),
            system=uname.system,
            release=uname.release,
            machine=uname.machine,
            processor=platform.processor() or uname.processor or uname.machine,
            ram_gb=psutil.virtual_memory().total / (1024**3),
            cpu_physical=psutil.cpu_count(logical=False),
            cpu_logical=psutil.cpu_count(logical=True) or 0,
        )

    @staticmethod
    def _summarize(durations_ms: Sequence[float]) -> tuple[float, float, float, float]:
        if not durations_ms:
            raise ValueError("At least one duration sample is required.")

        mean_ms = statistics.mean(durations_ms)
        median_ms = statistics.median(durations_ms)
        std_ms = statistics.stdev(durations_ms) if len(durations_ms) > 1 else 0.0
        p95_ms = float(np.percentile(np.asarray(durations_ms, dtype=float), 95))
        return mean_ms, median_ms, std_ms, p95_ms

    def time_callable(
        self,
        func: Callable[[], Any],
        *,
        trials: int = 1000,
        warmup: int = 3,
        collect_garbage: bool = False,
    ) -> list[float]:
        """Measure latency in milliseconds for a no-argument callable."""

        if trials < 1:
            raise ValueError("trials must be at least 1")
        if warmup < 0:
            raise ValueError("warmup cannot be negative")

        for _ in range(warmup):
            func()

        timings_ms: list[float] = []
        for _ in range(trials):
            if collect_garbage:
                gc.collect()
            start_ns = time.perf_counter_ns()
            func()
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            timings_ms.append(elapsed_ms)

        return timings_ms

    def benchmark(
        self,
        func: Callable[[], Any],
        *,
        scheme: str,
        mode: str,
        key_size: int,
        payload_bytes: int,
        operation: str,
        trials: int = 1000,
        warmup: int = 3,
        export_path: str | Path | None = None,
        collect_garbage: bool = False,
    ) -> BenchmarkRecord:
        """Time a callable and return a summarized record."""

        durations_ms = self.time_callable(
            func,
            trials=trials,
            warmup=warmup,
            collect_garbage=collect_garbage,
        )
        mean_ms, median_ms, std_ms, p95_ms = self._summarize(durations_ms)

        record = BenchmarkRecord(
            scheme=scheme,
            mode=mode,
            key_size=key_size,
            payload_bytes=payload_bytes,
            device=self.device_label,
            operation=operation,
            mean_ms=mean_ms,
            median_ms=median_ms,
            std_ms=std_ms,
            p95_ms=p95_ms,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

        self.display_records([record], title=f"{scheme} {operation} benchmark")
        if export_path is not None:
            self.export_records([record], export_path)
        return record

    def display_records(
        self,
        records: Iterable[BenchmarkRecord],
        *,
        title: str = "Benchmark Results",
    ) -> None:
        """Render records to the terminal with Rich."""

        table = Table(title=title, show_header=True, header_style="bold blue")
        table.add_column("Scheme", style="cyan")
        table.add_column("Mode", style="magenta")
        table.add_column("Key", justify="right")
        table.add_column("Payload", justify="right")
        table.add_column("Op")
        table.add_column("Mean ms", justify="right")
        table.add_column("Median ms", justify="right")
        table.add_column("Std ms", justify="right")
        table.add_column("P95 ms", justify="right")

        for record in records:
            table.add_row(
                record.scheme,
                record.mode,
                str(record.key_size),
                str(record.payload_bytes),
                record.operation,
                f"{record.mean_ms:.4f}",
                f"{record.median_ms:.4f}",
                f"{record.std_ms:.4f}",
                f"{record.p95_ms:.4f}",
            )

        self.console.print(table)

    def export_records(
        self,
        records: Sequence[BenchmarkRecord],
        export_path: str | Path,
    ) -> Path:
        """Append benchmark records to CSV."""

        path = Path(export_path)
        if not path.is_absolute():
            path = self.results_dir / path
        path.parent.mkdir(parents=True, exist_ok=True)

        write_header = not path.exists()
        with path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            if write_header:
                writer.writeheader()
            for record in records:
                writer.writerow(record.to_row())

        return path


__all__ = [
    "BenchmarkRecord",
    "BenchmarkRunner",
    "CSV_FIELDS",
    "DeviceMetadata",
]
