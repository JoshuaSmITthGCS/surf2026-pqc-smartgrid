"""Homomorphic encryption helpers and benchmark wrappers.

The Paillier (PHE) baseline depends only on ``phe`` and is always available.
The TenSEAL-backed BFV and CKKS modules are imported lazily-tolerantly so that
Paillier-only environments (for example resource-constrained edge meters, or a
machine without TenSEAL installed) can still import this package and run the
baseline. When TenSEAL is missing, the BFV/CKKS names are simply absent.
"""

from .paillier_scheme import (
    benchmark_paillier_baseline,
    ciphertext_expansion,
    encrypted_sum_demo as paillier_encrypted_sum_demo,
)

__all__ = [
    "benchmark_paillier_baseline",
    "ciphertext_expansion",
    "paillier_encrypted_sum_demo",
]

try:  # BFV/CKKS require TenSEAL, which is optional in Paillier-only setups.
    from .bfv_scheme import benchmark_bfv_schemes, encrypted_sum_demo
    from .ckks_scheme import benchmark_ckks_schemes, encrypted_average_demo
except ImportError:  # pragma: no cover - exercised only without TenSEAL
    pass
else:
    __all__ += [
        "benchmark_bfv_schemes",
        "benchmark_ckks_schemes",
        "encrypted_average_demo",
        "encrypted_sum_demo",
    ]
