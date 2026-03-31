# Benchmarking Post-Quantum and Homomorphic Encryption for Secure Smart Grid Communications

**Researcher:** Joshua Smith | **Mentor:** Dr. Mohamed Baza | **Institution:** College of Charleston
**Program:** SURF 2026 | **Duration:** May 19-July 24, 2026
**Target Venue:** IEEE SmartGridComm / IEEE Conference on Communications and Network Security

## Research Overview

This project benchmarks lattice-based Fully Homomorphic Encryption (FHE) schemes against classical
encryption baselines in the context of smart grid communications. It evaluates whether BFV and CKKS
schemes can operate within the latency and resource constraints of smart grid edge nodes under
simulated quantum attacks.

## Stack

- FHE: TenSEAL (Microsoft SEAL wrapper) for BFV and CKKS schemes
- Classical: PyCryptodome for RSA-2048/4096 and AES-128/256 baselines
- Quantum simulation: IBM Qiskit + Qiskit Aer
- Hardware targets: primary workstation + Raspberry Pi 4 edge node simulation

## Project Structure

```text
surf2026-pqc-smartgrid/
├── src/
│   ├── classical/
│   ├── fhe/
│   └── quantum/
├── benchmarks/
│   ├── runner.py
│   └── results/
│       ├── workstation/
│       └── pi/
├── data/
├── notebooks/
└── docs/
```

## Setup

```bash
conda activate surf26
pip install -r requirements.txt
```

## Acknowledgement

This research was supported by the College of Charleston Office of Undergraduate Research
and Creative Activities SURF Grant #12.
