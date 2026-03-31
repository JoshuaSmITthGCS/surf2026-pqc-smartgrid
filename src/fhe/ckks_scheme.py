"""CKKS scheme utilities and benchmark wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import tenseal as ts

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner


@dataclass(slots=True, frozen=True)
class CKKSConfig:
    """Named CKKS parameter set used in experiments."""

    name: str
    poly_modulus_degree: int
    coeff_mod_bit_sizes: tuple[int, ...]
    scale: int = 2**40


DEFAULT_CKKS_CONFIGS = (
    CKKSConfig(
        name="balanced-8192",
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=(60, 40, 40, 60),
    ),
    CKKSConfig(
        name="high-depth-16384",
        poly_modulus_degree=16384,
        coeff_mod_bit_sizes=(60, 40, 40, 40, 60),
    ),
)
DEFAULT_CKKS_SAMPLE_VALUES = (0.9821, 0.9974, 1.0012, 1.0068, 1.0121, 0.9896)


def create_ckks_context(config: CKKSConfig) -> ts.Context:
    """Create a CKKS context using the provided parameter set."""

    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=config.poly_modulus_degree,
        coeff_mod_bit_sizes=list(config.coeff_mod_bit_sizes),
    )
    context.global_scale = config.scale
    context.generate_galois_keys()
    context.generate_relin_keys()
    return context


def encrypt_floats(context: ts.Context, values: Iterable[float]) -> ts.CKKSVector:
    """Encrypt floating-point voltage readings."""

    return ts.ckks_vector(context, [float(value) for value in values])


def decrypt_floats(vector: ts.CKKSVector) -> list[float]:
    """Decrypt a CKKS vector back to Python floats."""

    return [float(value) for value in vector.decrypt()]


def approximate_add(left: ts.CKKSVector, right: ts.CKKSVector) -> ts.CKKSVector:
    """Add two CKKS vectors."""

    return left + right


def approximate_multiply(left: ts.CKKSVector, right: ts.CKKSVector) -> ts.CKKSVector:
    """Multiply two CKKS vectors.

    TenSEAL handles the rescale step internally for this common case, which keeps
    the helper concise and version-stable across the installed library build.
    """

    return left * right


def encrypted_average_demo(
    readings: Iterable[float],
    *,
    config: CKKSConfig = DEFAULT_CKKS_CONFIGS[0],
) -> dict[str, object]:
    """Compute an encrypted average of voltage readings."""

    reading_list = [float(value) for value in readings]
    context = create_ckks_context(config)

    accumulator = encrypt_floats(context, [0.0])
    for reading in reading_list:
        accumulator = approximate_add(accumulator, encrypt_floats(context, [reading]))

    encrypted_average = accumulator * (1.0 / len(reading_list))
    return {
        "config": config.name,
        "encrypted_average": encrypted_average,
        "decrypted_average": decrypt_floats(encrypted_average)[0],
        "sample_count": len(reading_list),
    }


def benchmark_ckks_schemes(
    runner: BenchmarkRunner | None = None,
    *,
    trials: int = 10,
    warmup: int = 1,
    configs: tuple[CKKSConfig, ...] = DEFAULT_CKKS_CONFIGS,
    sample_values: tuple[float, ...] = DEFAULT_CKKS_SAMPLE_VALUES,
    export_path: str | Path = "ckks_scheme.csv",
) -> list[BenchmarkRecord]:
    """Benchmark CKKS encrypt, decrypt, add, and multiply operations."""

    runner = runner or BenchmarkRunner()
    records: list[BenchmarkRecord] = []
    payload_bytes = len(sample_values) * 8

    for config in configs:
        context = create_ckks_context(config)
        encrypted_left = encrypt_floats(context, sample_values)
        encrypted_right = encrypt_floats(context, [value * 1.01 for value in sample_values])

        benchmarks = {
            "encrypt": lambda context=context, data=sample_values: encrypt_floats(context, data),
            "decrypt": lambda blob=encrypted_left: decrypt_floats(blob),
            "add": lambda left=encrypted_left, right=encrypted_right: approximate_add(left, right),
            "multiply": lambda left=encrypted_left, right=encrypted_right: approximate_multiply(left, right),
        }

        for operation, func in benchmarks.items():
            records.append(
                runner.benchmark(
                    func,
                    scheme="CKKS",
                    mode=config.name,
                    key_size=config.poly_modulus_degree,
                    payload_bytes=payload_bytes,
                    operation=operation,
                    trials=trials,
                    warmup=warmup,
                )
            )

    runner.export_records(records, export_path)
    return records


__all__ = [
    "CKKSConfig",
    "DEFAULT_CKKS_CONFIGS",
    "benchmark_ckks_schemes",
    "create_ckks_context",
    "decrypt_floats",
    "encrypt_floats",
    "encrypted_average_demo",
]
