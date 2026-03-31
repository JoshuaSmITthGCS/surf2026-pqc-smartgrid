# Benchmarking Post-Quantum and Homomorphic Encryption for Secure Smart Grid Communications

**Researcher:** Joshua Smith  
**Mentor:** Dr. Mohamed Baza  
**Institution:** College of Charleston  
**Program:** SURF 2026, May 19-July 24, 2026  
**Target Venue:** IEEE SmartGridComm / IEEE Conference on Communications and Network Security

## Research Overview

This repository benchmarks classical cryptography, lattice-based homomorphic
encryption, and educational quantum attack models in a smart-grid setting.
The goal is to quantify latency, statistical variability, and resource tradeoffs
for workloads that resemble meter telemetry, control messages, and encrypted
aggregation on edge-like devices.

The codebase is organized so the same benchmark harness can be reused on the
primary workstation now and a Raspberry Pi 4 later. Every benchmark emits a
consistent CSV schema:

`scheme, mode, key_size, payload_bytes, device, operation, mean_ms, median_ms, std_ms, p95_ms, timestamp`

## Stack

- **Benchmark harness:** Python 3.11, Rich, NumPy, Pandas, psutil
- **Classical baselines:** PyCryptodome for RSA-OAEP and AES-CBC/AES-GCM
- **FHE:** TenSEAL for BFV and CKKS experiments
- **Quantum simulation:** Qiskit + AerSimulator for scaled Shor and Grover demos
- **Analysis:** JupyterLab, Matplotlib, Plotly, OpenPyXL

## Repository Layout

```text
surf2026-pqc-smartgrid/
├── benchmarks/
│   ├── __init__.py
│   ├── runner.py
│   └── results/
│       ├── pi/
│       └── workstation/
├── data/
├── docs/
├── notebooks/
│   └── week1_validation.ipynb
├── src/
│   ├── classical/
│   │   ├── aes_baseline.py
│   │   └── rsa_baseline.py
│   ├── fhe/
│   │   ├── bfv_scheme.py
│   │   └── ckks_scheme.py
│   └── quantum/
│       ├── grover_attack.py
│       └── shor_attack.py
├── requirements.txt
└── README.md
```

## Setup

```bash
conda activate surf26
pip install -r requirements.txt
```

## Quick Start

Run the Week 1 notebook in JupyterLab:

```bash
conda activate surf26
jupyter lab
```

Or run a quick CLI validation:

```bash
conda activate surf26
cd ~/Documents/surf2026-pqc-smartgrid
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.classical.rsa_baseline import benchmark_rsa_baselines

runner = BenchmarkRunner()
benchmark_rsa_baselines(runner, trials=10, payload_sizes=(64,), export_path="quick_rsa_check.csv")
PY
```

## Notes on Benchmark Design

- RSA uses OAEP with SHA-256. The implementation explicitly skips payload sizes
  that exceed the OAEP plaintext limit for a given modulus size.
- BFV and CKKS wrappers use small, publication-friendly helper functions so the
  benchmark path stays readable and reproducible.
- The Shor module is an educational, scaled model of period estimation rather
  than a full attack on real RSA parameters. It is intended for comparison and
  discussion, not for claims of practical cryptanalysis.

## Acknowledgement

This research was supported by the College of Charleston Office of Undergraduate
Research and Creative Activities, SURF Grant #12.
