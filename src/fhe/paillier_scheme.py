"""Paillier (PHE) baseline utilities and reproducible benchmark wrappers.

Per Dr. Baza's feedback (Meeting 2, Q5), the head-to-head comparison baseline
for the homomorphic-encryption study is the Paillier partially-homomorphic
encryption (PHE) scheme, **not** RSA. Paillier is the classic prior-generation
smart-metering aggregation scheme (Erkin & Tsudik, ACNS 2012): it supports an
unlimited number of homomorphic additions but zero homomorphic multiplications
of two ciphertexts, and it encrypts a single value per ciphertext (no batching).

This module mirrors the structure of ``bfv_scheme.py`` and ``ckks_scheme.py`` so
the three schemes can be benchmarked side by side with the shared
``BenchmarkRunner``. AES-GCM and RSA remain in the repository as context-only
references, not as the active comparison baseline for this phase.

Hardness note: Paillier security rests on the Decisional Composite Residuosity
(DCR) assumption, which is broken by Shor's algorithm. This is the deliberate
contrast with the RLWE-based schemes (BFV/CKKS/BGV) that the project compares
against -- do not describe Paillier as post-quantum secure.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from phe import paillier

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner

DEFAULT_PAILLIER_KEY_SIZES = (2048, 3072)
# Integer meter readings (e.g. Wh, scaled) used for encrypted aggregation demos.
DEFAULT_PAILLIER_SAMPLE_VALUES = (12, 15, 16, 19, 18, 17, 14, 13)
# A single Paillier ciphertext carries one value; an int64-style reading is 8 B.
SINGLE_VALUE_PAYLOAD_BYTES = 8


@dataclass(slots=True, frozen=True)
class PaillierExpansion:
    """Ciphertext expansion summary for one Paillier key size.

    A Paillier ciphertext is an integer modulo ``n**2``, so its serialized size
    is roughly ``key_bits / 4`` bytes regardless of the small plaintext value.
    This is the communication-overhead metric called out in Meeting 2, Q8.
    """

    key_bits: int
    plaintext_bytes: int
    ciphertext_bytes: int
    expansion_ratio: float


def generate_paillier_keypair(
    key_bits: int,
) -> tuple[paillier.PaillierPublicKey, paillier.PaillierPrivateKey]:
    """Generate a Paillier keypair for the requested modulus size."""

    if key_bits < 1024:
        raise ValueError(f"Unsafe Paillier key size: {key_bits} (use >= 1024)")
    return paillier.generate_paillier_keypair(n_length=key_bits)


def encrypt_value(
    public_key: paillier.PaillierPublicKey,
    value: float | int,
) -> paillier.EncryptedNumber:
    """Encrypt a single meter reading (one value per ciphertext)."""

    return public_key.encrypt(value)


def encrypt_values(
    public_key: paillier.PaillierPublicKey,
    values: Iterable[float | int],
) -> list[paillier.EncryptedNumber]:
    """Encrypt a batch of readings as one ciphertext per value (no batching)."""

    return [public_key.encrypt(value) for value in values]


def decrypt_value(
    private_key: paillier.PaillierPrivateKey,
    ciphertext: paillier.EncryptedNumber,
) -> float | int:
    """Decrypt a single Paillier ciphertext."""

    return private_key.decrypt(ciphertext)


def decrypt_values(
    private_key: paillier.PaillierPrivateKey,
    ciphertexts: Iterable[paillier.EncryptedNumber],
) -> list[float | int]:
    """Decrypt a list of Paillier ciphertexts."""

    return [private_key.decrypt(ciphertext) for ciphertext in ciphertexts]


def homomorphic_add(
    left: paillier.EncryptedNumber,
    right: paillier.EncryptedNumber,
) -> paillier.EncryptedNumber:
    """Add two encrypted values -- the core smart-grid aggregation operation."""

    return left + right


def add_plaintext(
    ciphertext: paillier.EncryptedNumber,
    scalar: float | int,
) -> paillier.EncryptedNumber:
    """Add a public plaintext constant to an encrypted value."""

    return ciphertext + scalar


def multiply_plaintext(
    ciphertext: paillier.EncryptedNumber,
    scalar: float | int,
) -> paillier.EncryptedNumber:
    """Multiply an encrypted value by a public plaintext scalar.

    Paillier supports multiplication by a *plaintext* scalar (used for weighted
    aggregation), but it cannot multiply two ciphertexts together.
    """

    return ciphertext * scalar


def ciphertext_expansion(key_bits: int) -> PaillierExpansion:
    """Report Paillier ciphertext size and expansion ratio for a key size."""

    public_key, _ = generate_paillier_keypair(key_bits)
    ciphertext = public_key.encrypt(0)
    ciphertext_bytes = (ciphertext.ciphertext(be_secure=False).bit_length() + 7) // 8
    return PaillierExpansion(
        key_bits=key_bits,
        plaintext_bytes=SINGLE_VALUE_PAYLOAD_BYTES,
        ciphertext_bytes=ciphertext_bytes,
        expansion_ratio=ciphertext_bytes / SINGLE_VALUE_PAYLOAD_BYTES,
    )


def encrypted_sum_demo(
    readings: Iterable[int],
    *,
    key_bits: int = 2048,
) -> dict[str, object]:
    """Compute an encrypted meter-reading sum without decrypting intermediates.

    This is the Paillier-supported smart-grid use case: a substation or cloud
    aggregator sums per-household encrypted readings and only the final total is
    decrypted by the utility key holder.
    """

    reading_list = [int(value) for value in readings]
    public_key, private_key = generate_paillier_keypair(key_bits)

    accumulator = public_key.encrypt(0)
    for reading in reading_list:
        accumulator = homomorphic_add(accumulator, public_key.encrypt(reading))

    return {
        "key_bits": key_bits,
        "encrypted_total": accumulator,
        "decrypted_total": decrypt_value(private_key, accumulator),
        "expected_total": sum(reading_list),
        "sample_count": len(reading_list),
    }


def benchmark_paillier_baseline(
    runner: BenchmarkRunner | None = None,
    *,
    trials: int = 25,
    keygen_trials: int = 3,
    warmup: int = 1,
    key_sizes: tuple[int, ...] = DEFAULT_PAILLIER_KEY_SIZES,
    sample_values: tuple[int, ...] = DEFAULT_PAILLIER_SAMPLE_VALUES,
    export_path: str | Path = "paillier_baseline.csv",
) -> list[BenchmarkRecord]:
    """Benchmark the Paillier PHE baseline: keygen, encrypt, decrypt, and adds.

    Operations map to the Meeting 2 metrics (Q4/Q7): ``keygen`` is a one-time
    session cost, ``encrypt`` is the per-meter edge cost (the binding constraint
    for the smart meter), ``decrypt`` is the aggregate cost at the utility,
    ``add`` is the core homomorphic aggregation operation, and ``mul_plain`` is
    multiplication by a public scalar for weighted aggregation. Key generation
    is timed with its own ``keygen_trials`` count because it is far slower than
    the per-operation costs, especially at larger modulus sizes.
    """

    runner = runner or BenchmarkRunner()
    records: list[BenchmarkRecord] = []
    first_reading = int(sample_values[0])
    second_reading = int(sample_values[1]) if len(sample_values) > 1 else first_reading

    for key_bits in key_sizes:
        mode = f"PHE-{key_bits}"

        records.append(
            runner.benchmark(
                lambda bits=key_bits: generate_paillier_keypair(bits),
                scheme="Paillier",
                mode=mode,
                key_size=key_bits,
                payload_bytes=SINGLE_VALUE_PAYLOAD_BYTES,
                operation="keygen",
                trials=keygen_trials,
                warmup=0,
            )
        )

        public_key, private_key = generate_paillier_keypair(key_bits)
        encrypted_left = encrypt_value(public_key, first_reading)
        encrypted_right = encrypt_value(public_key, second_reading)

        benchmarks = {
            "encrypt": lambda key=public_key, value=first_reading: encrypt_value(key, value),
            "decrypt": lambda key=private_key, blob=encrypted_left: decrypt_value(key, blob),
            "add": lambda left=encrypted_left, right=encrypted_right: homomorphic_add(left, right),
            "mul_plain": lambda blob=encrypted_left: multiply_plaintext(blob, 3),
        }

        for operation, func in benchmarks.items():
            records.append(
                runner.benchmark(
                    func,
                    scheme="Paillier",
                    mode=mode,
                    key_size=key_bits,
                    payload_bytes=SINGLE_VALUE_PAYLOAD_BYTES,
                    operation=operation,
                    trials=trials,
                    warmup=warmup,
                )
            )

    runner.export_records(records, export_path)
    return records


def _main() -> None:
    """Run a quick Paillier baseline benchmark and print expansion ratios."""

    runner = BenchmarkRunner()
    benchmark_paillier_baseline(runner, trials=15, keygen_trials=3)
    for key_bits in DEFAULT_PAILLIER_KEY_SIZES:
        expansion = ciphertext_expansion(key_bits)
        runner.console.print(
            f"[green]Paillier-{key_bits}[/green]: ciphertext "
            f"{expansion.ciphertext_bytes} B, expansion "
            f"{expansion.expansion_ratio:.0f}x over {expansion.plaintext_bytes} B"
        )


__all__ = [
    "DEFAULT_PAILLIER_KEY_SIZES",
    "DEFAULT_PAILLIER_SAMPLE_VALUES",
    "PaillierExpansion",
    "SINGLE_VALUE_PAYLOAD_BYTES",
    "add_plaintext",
    "benchmark_paillier_baseline",
    "ciphertext_expansion",
    "decrypt_value",
    "decrypt_values",
    "encrypt_value",
    "encrypt_values",
    "encrypted_sum_demo",
    "generate_paillier_keypair",
    "homomorphic_add",
    "multiply_plaintext",
]


if __name__ == "__main__":
    _main()
