"""Week 1 validation smoke test for the SURF 2026 benchmark repository."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

from benchmarks.runner import BenchmarkRunner
from src.classical import aes_baseline, rsa_baseline
from src.fhe import bfv_scheme, ckks_scheme
from src.quantum import grover_attack, shor_attack
from src.smartgrid import workloads


def _status_table(rows: list[tuple[str, str]]) -> Table:
    table = Table(title="SURF 2026 Week 1 Smoke Test", show_header=True, header_style="bold blue")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    for check, status in rows:
        table.add_row(check, status)
    return table


def main() -> int:
    console = Console()
    status_rows: list[tuple[str, str]] = [
        ("module imports", "ok"),
        ("AES module", aes_baseline.__name__),
        ("RSA module", rsa_baseline.__name__),
        ("BFV module", bfv_scheme.__name__),
        ("CKKS module", ckks_scheme.__name__),
        ("Grover module", grover_attack.__name__),
        ("Shor module", shor_attack.__name__),
    ]

    dataset = workloads.load_smart_grid_dataset()
    summary = workloads.summarize_smart_grid_dataset(dataset)
    status_rows.extend(
        [
            ("dataset rows", str(summary.rows)),
            ("dataset interval", f"{summary.interval_minutes:g} minutes"),
            ("dataset missing values", str(summary.missing_values)),
        ]
    )

    payload = workloads.payload_from_dataset(dataset, 64)
    keypair = rsa_baseline.generate_rsa_keypair(2048)
    ciphertext = rsa_baseline.encrypt_rsa(keypair.publickey(), payload)
    decrypted = rsa_baseline.decrypt_rsa(keypair, ciphertext)
    if decrypted != payload:
        raise RuntimeError("RSA-2048 round trip failed for telemetry-derived payload.")
    status_rows.append(("RSA-2048 round trip", "ok"))

    runner = BenchmarkRunner(results_dir=PROJECT_ROOT / "benchmarks" / "results" / "workstation")
    record = runner.benchmark(
        lambda: rsa_baseline.encrypt_rsa(keypair.publickey(), payload),
        scheme="RSA",
        mode="OAEP-SHA256",
        key_size=2048,
        payload_bytes=len(payload),
        operation="encrypt",
        trials=10,
        warmup=2,
        export_path="week1_smoke_rsa.csv",
    )
    status_rows.append(("RSA-2048 10-trial mean", f"{record.mean_ms:.4f} ms"))
    status_rows.append(("Grover AES-128 effective bits", str(grover_attack.effective_aes_security_bits(128))))
    status_rows.append(("Shor RSA-2048 logical qubit estimate", str(shor_attack.estimate_logical_qubits_for_shor())))

    console.print(_status_table(status_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
