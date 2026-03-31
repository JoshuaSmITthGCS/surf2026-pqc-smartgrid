"""Homomorphic encryption helpers and benchmark wrappers."""

from .bfv_scheme import benchmark_bfv_schemes, encrypted_sum_demo
from .ckks_scheme import benchmark_ckks_schemes, encrypted_average_demo

__all__ = [
    "benchmark_bfv_schemes",
    "benchmark_ckks_schemes",
    "encrypted_average_demo",
    "encrypted_sum_demo",
]
