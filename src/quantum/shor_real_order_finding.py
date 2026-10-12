"""Genuine (non-surrogate) Shor order-finding against a real Paillier modulus.

``shor_attack.py`` intentionally builds a phase-estimation surrogate that is
handed the true order as input (see its module docstring and the research
guardrails in ``CLAUDE.md``): it demonstrates the measurement/continued-fraction
workflow without ever computing modular exponentiation on the quantum register.

This module instead builds the actual controlled modular-multiplication
unitaries ``|x> -> |a^(2^j) * x mod N>`` for a real small modulus ``N`` and
finds the multiplicative order of ``a`` from measurement alone -- nothing about
the order is given to the circuit. It is still a *toy-scale* attack: ``N`` must
stay small enough (tens of bits) that a classical simulator can hold the
corresponding statevector, which is why it is only ever run against a Paillier
key far below the library's real-world security floor (>=1024 bits). Factoring
an actual 2048/3072-bit Paillier modulus this way would need on the order of
4,000+ logical qubits (``estimate_logical_qubits_for_shor``) -- a state space of
roughly 2**4000 amplitudes, which no simulator, and no quantum computer that
exists today, can hold.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, gcd, log2
from typing import Iterable

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit.synthesis.qft import synth_qft_full
from qiskit_aer import AerSimulator

__all__ = [
    "OrderFindingResult",
    "modmul_permutation_matrix",
    "build_order_finding_circuit",
    "find_order_quantum",
    "factor_modulus_via_quantum_order",
]


@dataclass(slots=True, frozen=True)
class OrderFindingResult:
    """Outcome of one genuine quantum order-finding attempt."""

    modulus: int
    base: int
    work_qubits: int
    counting_qubits: int
    shots: int
    measured_order: int | None
    factors: tuple[int, int] | tuple[()]
    circuit_depth: int


def modmul_permutation_matrix(a_pow: int, modulus: int, num_qubits: int) -> np.ndarray:
    """Build the permutation matrix for ``|x> -> |a_pow * x mod modulus>``.

    Values ``x >= modulus`` (padding up to the register's power-of-two
    dimension) are left fixed, so the operator stays unitary on the full
    register while only ever acting on the real residues ``0..modulus-1``.
    """

    dim = 2**num_qubits
    if modulus > dim:
        raise ValueError(f"{num_qubits} work qubits cannot hold modulus {modulus}.")
    if gcd(a_pow, modulus) != 1:
        raise ValueError(f"{a_pow} is not invertible mod {modulus}.")

    matrix = np.zeros((dim, dim))
    for x in range(dim):
        target = (a_pow * x) % modulus if x < modulus else x
        matrix[target, x] = 1.0
    return matrix


def controlled_modmul_matrix(a_pow: int, modulus: int, num_qubits: int) -> np.ndarray:
    """Block-diagonal matrix for a single-qubit-controlled modular multiply.

    Built directly as one dense unitary (identity block when the control is
    |0>, the permutation block from :func:`modmul_permutation_matrix` when the
    control is |1>) instead of going through Qiskit's generic ``.control()``
    synthesis, which otherwise triggers an expensive general multi-qubit
    unitary-synthesis pass during transpilation for an 8+ qubit target.
    """

    identity = np.eye(2**num_qubits)
    permutation = modmul_permutation_matrix(a_pow, modulus, num_qubits)
    return np.block(
        [
            [identity, np.zeros_like(identity)],
            [np.zeros_like(permutation), permutation],
        ]
    )


def build_order_finding_circuit(
    base: int,
    modulus: int,
    *,
    work_qubits: int,
    counting_qubits: int,
) -> QuantumCircuit:
    """Build the real controlled-modular-exponentiation phase-estimation circuit.

    Each controlled unitary ``U_j`` implements multiplication by
    ``base**(2**j) mod modulus`` on the work register; the exponent is reduced
    classically (as any circuit synthesis must), but the quantum register is
    genuinely put into superposition and the modular arithmetic is performed by
    the unitary itself, not supplied as a precomputed phase.
    """

    if gcd(base, modulus) != 1:
        raise ValueError(f"Base {base} is not coprime with modulus {modulus}.")

    circuit = QuantumCircuit(counting_qubits + work_qubits, counting_qubits)
    counting = list(range(counting_qubits))
    work = list(range(counting_qubits, counting_qubits + work_qubits))

    circuit.x(work[0])  # work register starts at |1>
    circuit.h(counting)

    for j, control in enumerate(counting):
        power = pow(base, 2**j, modulus)
        gate = UnitaryGate(
            controlled_modmul_matrix(power, modulus, work_qubits),
            label=f"cU_{{{base}^{{2^{j}}} mod {modulus}}}",
            check_input=False,  # provably a permutation matrix -- skip the O(dim^3) unitarity check
        )
        circuit.append(gate, [control, *work])

    circuit.compose(
        synth_qft_full(counting_qubits, do_swaps=True, inverse=True),
        qubits=counting,
        inplace=True,
    )
    circuit.measure(counting, counting)
    return circuit


def _order_from_measurement(measured_bitstring: str, modulus: int, base: int) -> int | None:
    """Recover the true order from one phase measurement via continued fractions."""

    counting_qubits = len(measured_bitstring)
    measured_value = int(measured_bitstring, 2) / (2**counting_qubits)
    candidate = Fraction(measured_value).limit_denominator(modulus).denominator
    if candidate == 0:
        return None

    for multiple in range(1, modulus + 1):
        order = candidate * multiple
        if order == 0 or order > modulus:
            break
        if pow(base, order, modulus) == 1:
            return order
    return None


def find_order_quantum(
    base: int,
    modulus: int,
    *,
    work_qubits: int | None = None,
    counting_qubits: int | None = None,
    shots: int = 2048,
    simulator: AerSimulator | None = None,
) -> tuple[int | None, int]:
    """Run the real circuit and recover the order of ``base`` mod ``modulus``.

    Returns ``(order_or_None, circuit_depth)``. The order is derived purely
    from measured counts; no classical shortcut supplies it.
    """

    work_qubits = work_qubits or ceil(log2(modulus))
    counting_qubits = counting_qubits or max(2 * work_qubits, 8)

    circuit = build_order_finding_circuit(
        base,
        modulus,
        work_qubits=work_qubits,
        counting_qubits=counting_qubits,
    )
    simulator = simulator or AerSimulator()
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()

    for bitstring, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        order = _order_from_measurement(bitstring, modulus, base)
        if order is not None:
            return order, compiled.depth()
    return None, compiled.depth()


def factor_modulus_via_quantum_order(
    modulus: int,
    *,
    bases: Iterable[int] | None = None,
    work_qubits: int | None = None,
    counting_qubits: int | None = None,
    shots: int = 2048,
) -> OrderFindingResult:
    """Attack a real (toy-scale) modulus end-to-end using genuine order-finding.

    Tries each candidate base until an even order with a non-trivial
    ``gcd(base**(order/2) +/- 1, modulus)`` yields the factorization -- the
    textbook post-processing step of Shor's algorithm.
    """

    work_qubits = work_qubits or ceil(log2(modulus))
    counting_qubits = counting_qubits or max(2 * work_qubits, 8)
    simulator = AerSimulator()
    bases = bases if bases is not None else range(2, modulus)

    last_depth = 0
    for base in bases:
        if gcd(base, modulus) != 1:
            continue
        order, depth = find_order_quantum(
            base,
            modulus,
            work_qubits=work_qubits,
            counting_qubits=counting_qubits,
            shots=shots,
            simulator=simulator,
        )
        last_depth = depth
        if order is None or order % 2:
            continue

        half_power = pow(base, order // 2, modulus)
        if half_power in (1, modulus - 1):
            continue

        left = gcd(half_power - 1, modulus)
        right = gcd(half_power + 1, modulus)
        if 1 < left < modulus and 1 < right < modulus:
            return OrderFindingResult(
                modulus=modulus,
                base=base,
                work_qubits=work_qubits,
                counting_qubits=counting_qubits,
                shots=shots,
                measured_order=order,
                factors=tuple(sorted((left, right))),
                circuit_depth=depth,
            )

    return OrderFindingResult(
        modulus=modulus,
        base=-1,
        work_qubits=work_qubits,
        counting_qubits=counting_qubits,
        shots=shots,
        measured_order=None,
        factors=(),
        circuit_depth=last_depth,
    )
