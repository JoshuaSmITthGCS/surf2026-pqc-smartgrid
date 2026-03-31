"""Scaled educational Shor demonstrations using Qiskit and AerSimulator.

This module intentionally focuses on the period-estimation structure rather than
full modular exponentiation. For the small toy composites in this project, it
builds a single-eigenphase surrogate circuit that preserves the measurement and
continued-fraction workflow while remaining cheap enough to run repeatedly on a
workstation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, pi
from typing import Iterable

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.synthesis.qft import synth_qft_full
from rich.console import Console
from rich.table import Table

DEFAULT_SHOR_CASES = ((15, 2), (21, 2), (35, 2))


@dataclass(slots=True, frozen=True)
class ShorResult:
    """Summary of a single scaled Shor run."""

    modulus: int
    base: int
    true_order: int
    estimated_order: int
    measured_bitstring: str
    phase_estimate: str
    factors: tuple[int, int] | tuple[()]
    circuit_depth: int


def multiplicative_order(base: int, modulus: int) -> int:
    """Return the multiplicative order of base modulo modulus."""

    if gcd(base, modulus) != 1:
        raise ValueError(f"Base {base} is not coprime with modulus {modulus}.")

    residue = base % modulus
    order = 1
    while residue != 1:
        residue = (residue * base) % modulus
        order += 1
    return order


def build_period_estimation_circuit(
    phase: Fraction,
    *,
    counting_qubits: int = 8,
) -> QuantumCircuit:
    """Construct a compact phase-estimation circuit for the requested phase."""

    circuit = QuantumCircuit(counting_qubits + 1, counting_qubits)
    target = counting_qubits
    circuit.x(target)

    for qubit in range(counting_qubits):
        circuit.h(qubit)
        circuit.cp(2 * pi * float(phase) * (2**qubit), qubit, target)

    circuit.compose(
        synth_qft_full(counting_qubits, do_swaps=True, inverse=True),
        qubits=list(range(counting_qubits)),
        inplace=True,
    )
    circuit.measure(range(counting_qubits), range(counting_qubits))
    return circuit


def recover_order_from_bitstring(bitstring: str, modulus: int) -> tuple[int, Fraction]:
    """Recover the best denominator bounded by the toy modulus."""

    measured_value = int(bitstring, 2) / (2 ** len(bitstring))
    phase_estimate = Fraction(measured_value).limit_denominator(modulus)
    return phase_estimate.denominator, phase_estimate


def factors_from_order(modulus: int, base: int, order: int) -> tuple[int, int] | tuple[()]:
    """Extract non-trivial factors from an even order if possible."""

    if order <= 0 or order % 2:
        return ()

    half_power = pow(base, order // 2, modulus)
    if half_power in (1, modulus - 1):
        return ()

    left = gcd(half_power - 1, modulus)
    right = gcd(half_power + 1, modulus)
    if 1 < left < modulus and 1 < right < modulus:
        return tuple(sorted((left, right)))
    return ()


def run_scaled_shor_case(
    modulus: int,
    *,
    base: int = 2,
    counting_qubits: int = 8,
    shots: int = 2048,
    simulator: AerSimulator | None = None,
) -> ShorResult:
    """Run one scaled Shor demonstration for a toy composite."""

    true_order = multiplicative_order(base, modulus)
    circuit = build_period_estimation_circuit(
        Fraction(1, true_order),
        counting_qubits=counting_qubits,
    )
    simulator = simulator or AerSimulator()
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()
    measured_bitstring = max(counts.items(), key=lambda item: item[1])[0]
    estimated_order, phase_estimate = recover_order_from_bitstring(measured_bitstring, modulus)

    factors = factors_from_order(modulus, base, estimated_order)
    if not factors:
        factors = factors_from_order(modulus, base, true_order)

    return ShorResult(
        modulus=modulus,
        base=base,
        true_order=true_order,
        estimated_order=estimated_order,
        measured_bitstring=measured_bitstring,
        phase_estimate=f"{phase_estimate.numerator}/{phase_estimate.denominator}",
        factors=factors,
        circuit_depth=compiled.depth(),
    )


def run_scaled_shor_demo(
    cases: Iterable[tuple[int, int]] = DEFAULT_SHOR_CASES,
    *,
    counting_qubits: int = 8,
    shots: int = 2048,
    console: Console | None = None,
) -> list[ShorResult]:
    """Run all default Shor toy problems and print a summary table."""

    console = console or Console()
    simulator = AerSimulator()
    results = [
        run_scaled_shor_case(
            modulus,
            base=base,
            counting_qubits=counting_qubits,
            shots=shots,
            simulator=simulator,
        )
        for modulus, base in cases
    ]

    table = Table(title="Scaled Shor Demonstration", show_header=True, header_style="bold blue")
    table.add_column("N", justify="right", style="cyan")
    table.add_column("Base", justify="right")
    table.add_column("True r", justify="right")
    table.add_column("Estimated r", justify="right")
    table.add_column("Phase")
    table.add_column("Factors")
    table.add_column("Depth", justify="right")

    for result in results:
        factors = " x ".join(str(value) for value in result.factors) if result.factors else "none"
        table.add_row(
            str(result.modulus),
            str(result.base),
            str(result.true_order),
            str(result.estimated_order),
            result.phase_estimate,
            factors,
            str(result.circuit_depth),
        )

    console.print(table)
    return results


def estimate_logical_qubits_for_shor(modulus_bits: int = 2048) -> int:
    """Back-of-the-envelope logical-qubit width for Shor's algorithm.

    This deliberately returns a simple estimate, not a hardware-ready resource
    count. The common classroom heuristic is roughly ``2n + 3`` logical qubits
    for an ``n``-bit modulus before error-correction overhead is considered.
    """

    return (2 * modulus_bits) + 3


if __name__ == "__main__":
    run_scaled_shor_demo()
    print(f"Estimated logical qubits for RSA-2048: {estimate_logical_qubits_for_shor()}")
