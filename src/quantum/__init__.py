"""Quantum attack simulations for SURF 2026."""

from .grover_attack import effective_aes_security_bits, run_grover_demos
from .shor_attack import estimate_logical_qubits_for_shor, run_scaled_shor_demo

__all__ = [
    "effective_aes_security_bits",
    "estimate_logical_qubits_for_shor",
    "run_grover_demos",
    "run_scaled_shor_demo",
]
