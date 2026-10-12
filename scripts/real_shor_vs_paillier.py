"""Genuine Shor order-finding attack against a real (toy-scale) Paillier key.

Unlike ``src/quantum/shor_attack.py`` (an educational surrogate that is handed
the true order), this script:

1. Generates a real ``phe`` Paillier keypair -- but at a modulus far below the
   library's real-world security floor (``n_length=8``, i.e. an 8-bit modulus
   such as 143 = 11 x 13), because factoring an actual 2048/3072-bit Paillier
   modulus this way needs ~4,000+ logical qubits -- a statevector of roughly
   2**4000 amplitudes that no classical simulator (and no quantum computer
   that exists today) can hold. See ``CLAUDE.md``'s research guardrails: do
   not overclaim this as a practical attack on real-world key sizes.
2. Encrypts a real reading pulled from ``data/smart_grid_dataset.csv`` with
   the real public key (``public_key.encrypt(...)``) -- a genuine ciphertext,
   not a synthetic one.
3. Runs ``factor_modulus_via_quantum_order`` to find the modulus's factors
   from quantum measurement alone (no classical shortcut supplies the order).
4. Reconstructs the private key purely from the recovered factors
   (``PaillierPrivateKey(public_key, p, q)``) and decrypts the real
   ciphertext with it, confirming the recovered plaintext matches the
   legitimate owner's decryption.

Run with: ``python scripts/real_shor_vs_paillier.py``
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
from phe import paillier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.quantum.shor_real_order_finding import factor_modulus_via_quantum_order

DATASET_PATH = PROJECT_ROOT / "data" / "smart_grid_dataset.csv"
TOY_N_LENGTH_BITS = 8  # deliberately far below phe's real-world floor (see module docstring)


def load_real_reading(modulus: int) -> int:
    """Pull one real Power Consumption (kW) reading, reduced to fit the toy modulus.

    ``phe``'s signed-integer encoding only accepts plaintexts within
    roughly +/- n/3, so the real reading is scaled (x100, to keep two decimal
    digits of real precision) and reduced into that safe range -- it stays a
    real dataset value, just scaled down to fit the toy key's tiny plaintext
    space.
    """

    frame = pd.read_csv(DATASET_PATH, nrows=20)
    raw_kw = float(frame["Power Consumption (kW)"].max())
    safe_bound = max(2, modulus // 4)
    return int(round(raw_kw * 100)) % safe_bound


def main() -> None:
    public_key, private_key = paillier.generate_paillier_keypair(n_length=TOY_N_LENGTH_BITS)
    modulus = public_key.n
    print(f"Real (toy-scale) Paillier modulus n = {modulus} (owner's p={private_key.p}, q={private_key.q})")

    reading = load_real_reading(modulus)
    print(f"Real smart-grid reading (scaled, reduced mod n): {reading}")

    ciphertext = public_key.encrypt(reading)
    print(f"Real Paillier ciphertext (int): {ciphertext.ciphertext(be_secure=False)}")

    owner_decrypted = private_key.decrypt(ciphertext)
    print(f"Owner's own decryption (ground truth): {owner_decrypted}")

    print("\nRunning genuine quantum order-finding attack (no order supplied as input)...")
    start = time.perf_counter()
    result = factor_modulus_via_quantum_order(
        modulus,
        bases=(2, 3, 5, 7, 11, 13),
        counting_qubits=14,
        shots=2048,
    )
    elapsed = time.perf_counter() - start

    if not result.factors:
        print(f"Attack FAILED to factor n={modulus} after {elapsed:.2f}s.")
        return

    p, q = result.factors
    print(
        f"Attack recovered factors p={p}, q={q} via base={result.base}, "
        f"measured order={result.measured_order}, "
        f"{result.work_qubits} work + {result.counting_qubits} counting qubits, "
        f"circuit depth={result.circuit_depth}, {elapsed:.2f}s"
    )

    forged_private_key = paillier.PaillierPrivateKey(public_key, p, q)
    attacker_decrypted = forged_private_key.decrypt(ciphertext)
    print(f"Attacker's reconstructed-key decryption: {attacker_decrypted}")

    assert attacker_decrypted == owner_decrypted == reading
    print("\nSUCCESS: real encrypted smart-grid reading decrypted via quantum-recovered factors.")


if __name__ == "__main__":
    main()
