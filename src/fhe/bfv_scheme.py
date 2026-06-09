"""BFV scheme utilities and reproducible benchmark wrappers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import tenseal as ts

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner

DEFAULT_BFV_POLY_DEGREES = (4096, 8192, 16384)
# Batching requires plain_modulus == 1 mod 2 * poly_modulus_degree.
# 1146881 = 35 * 32768 + 1, so it supports all default BFV degrees.
DEFAULT_BFV_PLAIN_MODULUS = 1146881
DEFAULT_BFV_SAMPLE_VALUES = (12, 15, 16, 19, 18, 17, 14, 13)


def create_bfv_context(
    poly_modulus_degree: int,
    *,
    plain_modulus: int = DEFAULT_BFV_PLAIN_MODULUS,
) -> ts.Context:
    """Create a BFV context with keys required for addition and multiplication."""

    context = ts.context(
        ts.SCHEME_TYPE.BFV,
        poly_modulus_degree=poly_modulus_degree,
        plain_modulus=plain_modulus,
    )
    context.generate_galois_keys()
    context.generate_relin_keys()
    return context


def encrypt_integers(context: ts.Context, values: Iterable[int]) -> ts.BFVVector:
    """Encrypt a batch of integer smart-meter readings."""

    return ts.bfv_vector(context, list(values))


def decrypt_integers(vector: ts.BFVVector) -> list[int]:
    """Decrypt a BFV vector back to Python integers."""

    return [int(value) for value in vector.decrypt()]


def homomorphic_add(left: ts.BFVVector, right: ts.BFVVector) -> ts.BFVVector:
    """Add two encrypted BFV vectors element-wise."""

    return left + right


def homomorphic_multiply(left: ts.BFVVector, right: ts.BFVVector) -> ts.BFVVector:
    """Multiply two encrypted BFV vectors element-wise."""

    return left * right


def encrypted_sum_demo(
    readings: Iterable[int],
    *,
    poly_modulus_degree: int = 8192,
    plain_modulus: int = DEFAULT_BFV_PLAIN_MODULUS,
) -> dict[str, object]:
    """Compute an encrypted sum without decrypting intermediate state."""

    reading_list = [int(value) for value in readings]
    context = create_bfv_context(
        poly_modulus_degree,
        plain_modulus=plain_modulus,
    )

    accumulator = encrypt_integers(context, [0])
    for reading in reading_list:
        accumulator = homomorphic_add(accumulator, encrypt_integers(context, [reading]))

    return {
        "poly_modulus_degree": poly_modulus_degree,
        "encrypted_total": accumulator,
        "decrypted_total": decrypt_integers(accumulator)[0],
        "sample_count": len(reading_list),
    }


def benchmark_bfv_schemes(
    runner: BenchmarkRunner | None = None,
    *,
    trials: int = 10,
    warmup: int = 1,
    poly_degrees: tuple[int, ...] = DEFAULT_BFV_POLY_DEGREES,
    sample_values: tuple[int, ...] = DEFAULT_BFV_SAMPLE_VALUES,
    export_path: str | Path = "bfv_scheme.csv",
) -> list[BenchmarkRecord]:
    """Benchmark BFV encryption, decryption, addition, and multiplication."""

    runner = runner or BenchmarkRunner()
    records: list[BenchmarkRecord] = []
    payload_bytes = len(sample_values) * 8

    for degree in poly_degrees:
        context = create_bfv_context(degree)
        encrypted_left = encrypt_integers(context, sample_values)
        encrypted_right = encrypt_integers(context, [value + 1 for value in sample_values])

        benchmarks = {
            "encrypt": lambda context=context, data=sample_values: encrypt_integers(context, data),
            "decrypt": lambda blob=encrypted_left: decrypt_integers(blob),
            "add": lambda left=encrypted_left, right=encrypted_right: homomorphic_add(left, right),
            "multiply": lambda left=encrypted_left, right=encrypted_right: homomorphic_multiply(left, right),
        }

        for operation, func in benchmarks.items():
            records.append(
                runner.benchmark(
                    func,
                    scheme="BFV",
                    mode=f"poly-{degree}",
                    key_size=degree,
                    payload_bytes=payload_bytes,
                    operation=operation,
                    trials=trials,
                    warmup=warmup,
                )
            )

    runner.export_records(records, export_path)
    return records


__all__ = [
    "DEFAULT_BFV_POLY_DEGREES",
    "DEFAULT_BFV_PLAIN_MODULUS",
    "benchmark_bfv_schemes",
    "create_bfv_context",
    "decrypt_integers",
    "encrypt_integers",
    "encrypted_sum_demo",
    "homomorphic_add",
    "homomorphic_multiply",
]
