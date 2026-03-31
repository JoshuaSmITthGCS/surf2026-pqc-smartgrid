"""Grover search demonstrations for toy key spaces."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from rich.console import Console
from rich.table import Table

DEFAULT_GROVER_CASES = (
    (4, "1011"),
    (8, "11001010"),
)


@dataclass(slots=True, frozen=True)
class GroverResult:
    """Summary of a Grover search run."""

    key_bits: int
    target_state: str
    measured_state: str
    iterations: int
    success_probability: float
    classical_expected_queries: float
    grover_query_estimate: int
    circuit_depth: int


def classical_bruteforce_queries(key_bits: int) -> float:
    """Expected classical brute-force queries for a uniformly random key."""

    return 2 ** (key_bits - 1)


def grover_iterations(key_bits: int) -> int:
    """Near-optimal Grover iteration count for one marked state."""

    return max(1, round((math.pi / 4) * math.sqrt(2**key_bits)))


def effective_aes_security_bits(key_bits: int) -> int:
    """Return the commonly cited AES security level under Grover's algorithm."""

    return key_bits // 2


def _apply_phase_oracle(circuit: QuantumCircuit, target_state: str) -> None:
    zero_positions = [index for index, bit in enumerate(reversed(target_state)) if bit == "0"]

    for qubit in zero_positions:
        circuit.x(qubit)

    last_qubit = circuit.num_qubits - 1
    circuit.h(last_qubit)
    circuit.mcx(list(range(last_qubit)), last_qubit)
    circuit.h(last_qubit)

    for qubit in zero_positions:
        circuit.x(qubit)


def _apply_diffuser(circuit: QuantumCircuit) -> None:
    last_qubit = circuit.num_qubits - 1
    circuit.h(range(circuit.num_qubits))
    circuit.x(range(circuit.num_qubits))
    circuit.h(last_qubit)
    circuit.mcx(list(range(last_qubit)), last_qubit)
    circuit.h(last_qubit)
    circuit.x(range(circuit.num_qubits))
    circuit.h(range(circuit.num_qubits))


def build_grover_circuit(target_state: str, *, iterations: int | None = None) -> QuantumCircuit:
    """Construct a Grover circuit for the requested marked state."""

    key_bits = len(target_state)
    if key_bits < 2:
        raise ValueError("Grover demonstrations require at least 2 qubits.")

    iteration_count = iterations if iterations is not None else grover_iterations(key_bits)
    circuit = QuantumCircuit(key_bits, key_bits)
    circuit.h(range(key_bits))

    for _ in range(iteration_count):
        _apply_phase_oracle(circuit, target_state)
        _apply_diffuser(circuit)

    circuit.measure(range(key_bits), range(key_bits))
    return circuit


def run_grover_search(
    target_state: str,
    *,
    shots: int = 2048,
    simulator: AerSimulator | None = None,
) -> GroverResult:
    """Run a Grover search and summarize the observed speedup."""

    key_bits = len(target_state)
    iterations = grover_iterations(key_bits)
    circuit = build_grover_circuit(target_state, iterations=iterations)
    simulator = simulator or AerSimulator()
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()
    measured_state, measured_count = max(counts.items(), key=lambda item: item[1])

    return GroverResult(
        key_bits=key_bits,
        target_state=target_state,
        measured_state=measured_state,
        iterations=iterations,
        success_probability=measured_count / shots,
        classical_expected_queries=classical_bruteforce_queries(key_bits),
        grover_query_estimate=iterations,
        circuit_depth=compiled.depth(),
    )


def run_grover_demos(
    cases: Iterable[tuple[int, str]] = DEFAULT_GROVER_CASES,
    *,
    shots: int = 2048,
    console: Console | None = None,
) -> list[GroverResult]:
    """Run the default Grover demonstrations and print a summary table."""

    console = console or Console()
    simulator = AerSimulator()
    results = [run_grover_search(target, shots=shots, simulator=simulator) for _, target in cases]

    table = Table(title="Grover Search Demonstration", show_header=True, header_style="bold blue")
    table.add_column("Bits", justify="right", style="cyan")
    table.add_column("Target")
    table.add_column("Measured")
    table.add_column("Iterations", justify="right")
    table.add_column("Success", justify="right")
    table.add_column("Classical Avg Queries", justify="right")
    table.add_column("Grover Queries", justify="right")
    table.add_column("Depth", justify="right")

    for result in results:
        table.add_row(
            str(result.key_bits),
            result.target_state,
            result.measured_state,
            str(result.iterations),
            f"{result.success_probability:.3f}",
            f"{result.classical_expected_queries:.1f}",
            str(result.grover_query_estimate),
            str(result.circuit_depth),
        )

    console.print(table)
    console.print(
        "Effective AES security under Grover: "
        f"AES-128 -> {effective_aes_security_bits(128)} bits, "
        f"AES-256 -> {effective_aes_security_bits(256)} bits."
    )
    return results


if __name__ == "__main__":
    run_grover_demos()
