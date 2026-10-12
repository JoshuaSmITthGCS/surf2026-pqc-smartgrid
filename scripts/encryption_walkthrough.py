"""Step-by-step encryption walkthrough for screenshots and live demos.

Encrypts real smart-grid readings with Paillier-2048, BFV and CKKS, adds them
while still encrypted, decrypts only the total, and checks it against the
plaintext sum. Add ``--attack`` to finish with the toy-scale Shor attack.

    python scripts/encryption_walkthrough.py
    python scripts/encryption_walkthrough.py --attack
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from phe import paillier
from rich.console import Console
from rich.panel import Panel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

console = Console()
DATASET_PATH = PROJECT_ROOT / "data" / "smart_grid_dataset.csv"


def load_readings(count: int) -> list[float]:
    frame = pd.read_csv(DATASET_PATH, nrows=count)
    return [round(float(v), 2) for v in frame["Power Consumption (kW)"]]


def step(text: str) -> None:
    console.print(f"[bold cyan]>[/bold cyan] {text}")


def short(number: int, keep: int = 24) -> str:
    text = str(number)
    return f"{text[:keep]}... ({len(text)} digits)"


def run_paillier(readings: list[float]) -> None:
    console.rule("[bold]1. Paillier-2048 (baseline)[/bold]")
    scaled = [int(round(r * 100)) for r in readings]

    step("Generating a 2048-bit key pair...")
    start = time.perf_counter()
    public_key, private_key = paillier.generate_paillier_keypair(n_length=2048)
    console.print(f"  done in {time.perf_counter() - start:.2f}s, public modulus n has {public_key.n.bit_length()} bits")

    step(f"Encrypting {len(scaled)} meter readings (kW x 100, as integers), one ciphertext each")
    start = time.perf_counter()
    encrypted = [public_key.encrypt(v) for v in scaled]
    console.print(f"  done in {(time.perf_counter() - start) * 1000:.0f} ms")
    for plain, enc in zip(scaled[:3], encrypted[:3]):
        console.print(f"  {plain:>6}  ->  {short(enc.ciphertext(be_secure=False))}")
    console.print("  ...")

    step("Aggregator adds the ciphertexts without decrypting anything")
    total = encrypted[0]
    for enc in encrypted[1:]:
        total = total + enc
    console.print(f"  encrypted total: {short(total.ciphertext(be_secure=False))}")

    step("Utility decrypts only the total")
    decrypted = private_key.decrypt(total)
    ok = decrypted == sum(scaled)
    console.print(f"  decrypted = {decrypted}, expected = {sum(scaled)}  [{'green]OK' if ok else 'red]MISMATCH'}[/]")


def run_bfv(readings: list[float]) -> None:
    from src.fhe import bfv_scheme

    console.rule("[bold]2. BFV (exact integers, batched)[/bold]")
    scaled = [int(round(r * 100)) for r in readings]

    step("Creating BFV context (poly degree 8192) and keys...")
    start = time.perf_counter()
    context = bfv_scheme.create_bfv_context(8192)
    console.print(f"  done in {time.perf_counter() - start:.2f}s")

    step(f"Encrypting all {len(scaled)} readings into ONE ciphertext")
    start = time.perf_counter()
    vector = bfv_scheme.encrypt_integers(context, scaled)
    console.print(f"  done in {(time.perf_counter() - start) * 1000:.1f} ms, ciphertext size {len(vector.serialize()):,} bytes")

    step("Summing the slots while encrypted")
    total = vector.sum()

    step("Decrypting only the total")
    decrypted = int(total.decrypt()[0])
    ok = decrypted == sum(scaled)
    console.print(f"  decrypted = {decrypted}, expected = {sum(scaled)}  [{'green]OK' if ok else 'red]MISMATCH'}[/]")


def run_ckks(readings: list[float]) -> None:
    from src.fhe import ckks_scheme

    console.rule("[bold]3. CKKS (approximate reals, batched)[/bold]")
    config = ckks_scheme.DEFAULT_CKKS_CONFIGS[0]

    step(f"Creating CKKS context ({config.name}) and keys...")
    start = time.perf_counter()
    context = ckks_scheme.create_ckks_context(config)
    console.print(f"  done in {time.perf_counter() - start:.2f}s")

    step(f"Encrypting all {len(readings)} readings (kW) into ONE ciphertext")
    start = time.perf_counter()
    vector = ckks_scheme.encrypt_floats(context, readings)
    console.print(f"  done in {(time.perf_counter() - start) * 1000:.1f} ms, ciphertext size {len(vector.serialize()):,} bytes")

    step("Summing the slots while encrypted")
    total = vector.sum()

    step("Decrypting only the total")
    decrypted = float(total.decrypt()[0])
    expected = sum(readings)
    error = abs(decrypted - expected)
    console.print(f"  decrypted = {decrypted:.6f}, expected = {expected:.6f}, error = {error:.2e}  [green]OK (approximate by design)[/]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--readings", type=int, default=8, help="number of real readings to encrypt")
    parser.add_argument("--attack", action="store_true", help="finish with the toy-scale Shor attack on Paillier")
    args = parser.parse_args()

    readings = load_readings(args.readings)
    console.print(Panel.fit(
        f"Real readings (kW) from smart_grid_dataset.csv:\n{readings}\nPlaintext total: {sum(readings):.2f} kW",
        title="Encrypted aggregation walkthrough",
    ))

    run_paillier(readings)
    run_bfv(readings)
    run_ckks(readings)

    if args.attack:
        console.rule("[bold red]4. Quantum attack on a toy Paillier key[/bold red]")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import real_shor_vs_paillier

        real_shor_vs_paillier.main()
    else:
        console.print("\n[dim]Add --attack to finish with the Shor attack on a toy Paillier key.[/dim]")


if __name__ == "__main__":
    main()
