# SURF 2026 Smart-Grid Crypto Benchmark Repository

This repository collects benchmark code for a SURF 2026 research project on
secure smart-grid communications. The current codebase measures classical
cryptography, homomorphic encryption, and small educational quantum-security
demonstrations using a shared timing and CSV export harness.

## Project Context

- Researcher: Joshua Smith
- Mentor: Dr. Mohamed Baza
- Institution: College of Charleston
- Program: SURF 2026, May 19-July 24, 2026
- Intended publication direction: IEEE SmartGridComm / IEEE CNS-style research

## What This Repository Is Today

The repository name includes `pqc`, but the checked-in implementation is not
yet a full post-quantum cryptography benchmark suite.

What is implemented now:

- Classical baselines with PyCryptodome:
  - AES-CBC
  - AES-GCM
  - RSA-OAEP with SHA-256
- Homomorphic encryption schemes:
  - Paillier (PHE) with `phe`, the additively-homomorphic comparison baseline
  - BFV for integer vectors with TenSEAL
  - CKKS for approximate floating-point vectors with TenSEAL
- Educational quantum-risk demonstrations with Qiskit:
  - Grover search on toy key spaces
  - Scaled Shor-style period estimation for small composite numbers
- A reusable benchmark harness that exports consistent CSV rows
- A real smart-grid telemetry CSV under `data/`
- Smart-grid workload helpers that turn telemetry rows into reproducible
  benchmark payload bytes
- A Week 1 validation notebook and smoke-test script for AES/RSA sanity checks

Current Phase 1 research focus:

- Run a head-to-head comparison of homomorphic encryption schemes against the
  Paillier (PHE) baseline. This follows Dr. Baza's Meeting 2 feedback: the
  comparison baseline must be a homomorphic scheme (the classic smart-metering
  prior art), not RSA.
- Use Paillier (PHE) as the single comparison baseline. It is additively
  homomorphic (unlimited adds, zero ciphertext-ciphertext multiplies) and rests
  on the DCR assumption, which is broken by Shor's algorithm.
- Use BFV for exact integer smart-grid aggregation.
- Use CKKS for approximate real-valued telemetry analytics.
- Plan BGV (depth >= 2 demand-response pipeline) as the Week 3-4 third scheme.
- Keep AES-GCM and RSA as context-only references; they are not the active
  comparison baseline for encrypted computation.

What is not yet implemented:

- NIST PQC algorithms such as ML-KEM, ML-DSA, Falcon, or SPHINCS+
- A full smart-grid simulator or network stack
- Automated tests or CI workflows

In other words, the "smart-grid" aspect is currently represented by realistic
payload sizes, real telemetry-derived payload bytes, and encrypted aggregation
patterns, not by a full end-to-end grid application.

## Research Goal

The goal of the project is to compare security-relevant cryptographic choices
for smart-grid-like workloads along dimensions such as:

- latency
- variability across repeated trials
- behavior on workstation-class versus edge-class hardware
- practical tradeoffs between classical cryptography, homomorphic processing,
  and long-term quantum security discussions

The benchmark harness is designed so the same experiment structure can be run
on a workstation now and a Raspberry Pi later.

## Technical Stack

- Benchmarking and analysis:
  - Python
  - Rich
  - NumPy
  - pandas
  - psutil
- Classical cryptography:
  - PyCryptodome
- Homomorphic encryption:
  - TenSEAL
- Quantum simulation:
  - Qiskit
  - Qiskit Aer
- Notebook and plotting support:
  - JupyterLab
  - Matplotlib
  - Plotly
  - OpenPyXL

## Repository Tour

```text
surf2026-pqc-smartgrid/
├── benchmarks/
│   ├── __init__.py
│   ├── runner.py
│   └── results/
│       ├── pi/
│       │   └── .gitkeep
│       └── workstation/
│           └── .gitkeep
├── data/
│   ├── .gitkeep
│   └── smart_grid_dataset.csv
├── docs/
│   ├── .gitkeep
│   ├── SUMMER_PLAN.md
│   └── WEEK1_VALIDATION.md
├── notebooks/
│   ├── .gitkeep
│   └── week1_validation.ipynb
├── src/
│   ├── __init__.py
│   ├── classical/
│   │   ├── __init__.py
│   │   ├── aes_baseline.py
│   │   └── rsa_baseline.py
│   ├── fhe/
│   │   ├── __init__.py
│   │   ├── paillier_scheme.py
│   │   ├── bfv_scheme.py
│   │   └── ckks_scheme.py
│   ├── quantum/
│       ├── __init__.py
│       ├── grover_attack.py
│       └── shor_attack.py
│   └── smartgrid/
│       ├── __init__.py
│       ├── london_meters.py
│       └── workloads.py
├── scripts/
│   ├── convert_to_obsidian.py
│   ├── run_he_baseline_comparison.py
│   ├── setup_and_run.py
│   └── week1_smoke_test.py
├── requirements.txt
└── README.md
```

### Directory-by-directory

`benchmarks/`
- Contains the common timing and export infrastructure.
- `runner.py` is the core benchmark harness used across classical and FHE code.

`benchmarks/results/workstation/`
- Default output directory for locally generated benchmark CSV files.
- Intended for workstation-class runs.

`benchmarks/results/pi/`
- Reserved for Raspberry Pi or other edge-device benchmark outputs.

`src/classical/`
- Baseline implementations for AES and RSA.
- These are the main "conventional crypto" references for later comparisons.

`src/fhe/`
- Homomorphic encryption helpers and benchmark wrappers.
- `paillier_scheme.py` is the additively-homomorphic Paillier (PHE) baseline and
  depends only on `phe`; it imports without TenSEAL so it can run on
  constrained, TenSEAL-free environments.
- `bfv_scheme.py` and `ckks_scheme.py` are TenSEAL-backed and load only when
  TenSEAL is installed.
- Includes both small smart-grid-style demos and benchmark wrappers.

`src/quantum/`
- Educational quantum demonstrations.
- These are not practical attacks on production RSA or AES. They are toy models
  intended for explanation, comparison, and discussion.

`src/smartgrid/`
- Real dataset loading, quality summaries, and deterministic payload builders.
- `workloads.py` validates the single-feed telemetry CSV (`smart_grid_dataset.csv`)
  and converts rows into exact-size byte payloads for reproducible AES/RSA
  benchmarks.
- `london_meters.py` loads the multi-household Smart Meters in London dataset
  (half-hourly per-meter kWh) into a `timestamp x meter` matrix and produces
  per-meter reading vectors (scaled integers for Paillier/BFV, floats for CKKS)
  for the encrypted-aggregation use case. It is independent of `workloads.py`.

`notebooks/`
- Contains `week1_validation.ipynb`, a small notebook that validates the real
  dataset, runs AES/RSA baseline checks, and summarizes results with pandas.

`data/`
- Contains `smart_grid_dataset.csv`, the real telemetry dataset used to derive
  Week 1 benchmark payloads.

`docs/`
- Reserved for project plans, validation notes, figures, writeups, and exported
  analysis products.

`scripts/`
- Contains reusable command-line helpers, including `week1_smoke_test.py` for a
  quick import, dataset, and RSA-2048 benchmark check.

## Architecture and Execution Flow

Most benchmarkable code in the repository follows the same pattern:

1. A module defines small helper functions for encrypt, decrypt, or toy quantum
   operations.
2. A `benchmark_*` wrapper builds representative inputs and callable closures.
   Classical wrappers can optionally receive a `payload_factory` so real
   telemetry bytes are used instead of random bytes.
3. `BenchmarkRunner` measures repeated execution time in milliseconds.
4. The runner summarizes the samples into mean, median, standard deviation, and
   p95 latency.
5. Results are appended to a CSV file using a single shared schema.

This structure keeps measurement logic centralized while leaving algorithm code
small and readable.

## Benchmark Harness

`benchmarks/runner.py` is the backbone of the repository.

It provides:

- `BenchmarkRunner`
  - creates the output directory if needed
  - collects machine metadata once per run
  - times callables with configurable trial count and warmup
  - computes summary statistics
  - displays results in a Rich table
  - exports rows to CSV
- `BenchmarkRecord`
  - a normalized row object used by all benchmark modules
- `DeviceMetadata`
  - a small structure used to collapse hostname, OS, CPU, and RAM into the
    single `device` column stored in CSV outputs

### Shared CSV schema

Every benchmark export uses the same columns:

| Column | Meaning |
| --- | --- |
| `scheme` | High-level family such as `Paillier`, `AES`, `RSA`, `BFV`, or `CKKS` |
| `mode` | Variant or parameter label such as `PHE-2048`, `CBC`, `GCM`, `OAEP-SHA256`, `poly-4096`, or `balanced-8192` |
| `key_size` | Key size or analogous parameter, such as AES key bits or polynomial modulus degree |
| `payload_bytes` | Approximate plaintext payload size represented by the benchmark |
| `device` | Hostname and machine metadata captured at runtime |
| `operation` | Operation name such as `encrypt`, `decrypt`, `add`, or `multiply` |
| `mean_ms` | Mean runtime in milliseconds |
| `median_ms` | Median runtime in milliseconds |
| `std_ms` | Sample standard deviation in milliseconds |
| `p95_ms` | 95th percentile runtime in milliseconds |
| `timestamp` | UTC timestamp for the exported record |

### Result-file behavior

- Relative export paths are resolved inside `benchmarks/results/workstation/` by
  default.
- CSV rows are appended, not overwritten.
- The header row is written automatically the first time a file is created.
- Generated `*.csv` files are gitignored. Only the `.gitkeep` files under the
  results directories are tracked.

## Module Guide

### Classical Baselines

#### `src/classical/aes_baseline.py`

This module provides AES helpers and a benchmark wrapper for symmetric crypto.

Key characteristics:

- supports `CBC` and `GCM`
- default key sizes: `128`, `256`
- default payload sizes: `64`, `512`, `1024`, `65536` bytes
- benchmarks both `encrypt` and `decrypt`
- uses PKCS7 padding for CBC
- normalizes CBC and GCM outputs through a shared `AESCiphertext` dataclass

This is the most direct "fast baseline" in the repository and is useful when
contrasting classical symmetric performance against heavier techniques.

#### `src/classical/rsa_baseline.py`

This module provides RSA-OAEP timing for asymmetric baseline comparison.

Key characteristics:

- supports RSA key sizes `2048` and `4096`
- uses OAEP with SHA-256
- default payload sizes: `64`, `128`, `256` bytes
- benchmarks both `encrypt` and `decrypt`
- explicitly skips payloads that exceed the OAEP plaintext limit for a given
  modulus

The OAEP size check is important because it prevents invalid benchmark rows
from being recorded for unsupported payload/key combinations.

### Homomorphic Encryption

#### `src/fhe/paillier_scheme.py`

This module provides the Paillier (PHE) baseline, the head-to-head comparison
point for the BFV and CKKS experiments per Dr. Baza's Meeting 2 feedback.

Key characteristics:

- uses the pure-Python `phe` library (no TenSEAL dependency)
- default key sizes: `2048`, `3072`
- benchmarks `keygen`, `encrypt`, `decrypt`, `add` (ciphertext + ciphertext),
  and `mul_plain` (ciphertext * plaintext scalar)
- `keygen` is timed with its own smaller trial count because it dominates cost
- includes `encrypted_sum_demo()` for encrypted meter-reading aggregation
- includes `ciphertext_expansion()` to report ciphertext size and the
  ciphertext/plaintext expansion ratio (the Meeting 2 communication metric)

Paillier supports unlimited homomorphic additions but no ciphertext-ciphertext
multiplication, and encrypts one value per ciphertext (no SIMD batching). Its
DCR hardness is broken by Shor, which is the deliberate contrast with the
RLWE-based BFV/CKKS/BGV schemes. It should not be described as post-quantum
secure.

#### `src/fhe/bfv_scheme.py`

This module contains BFV utilities for integer-valued workloads that resemble
batched smart-meter readings.

Key characteristics:

- uses TenSEAL BFV vectors
- default polynomial modulus degrees: `4096`, `8192`, `16384`
- default plaintext modulus: `1032193`
- default sample vector: eight integers
- benchmarks `encrypt`, `decrypt`, `add`, and `multiply`
- includes `encrypted_sum_demo()` for an end-to-end encrypted aggregation

Because BFV operates on exact integer arithmetic, it fits the idea of secure
aggregation over count-like or reading-like values.

#### `src/fhe/ckks_scheme.py`

This module contains CKKS utilities for approximate floating-point workloads
such as voltage or sensor readings.

Key characteristics:

- defines named parameter sets through `CKKSConfig`
- default configs:
  - `balanced-8192`
  - `high-depth-16384`
- default sample vector: six floating-point values
- benchmarks `encrypt`, `decrypt`, `add`, and `multiply`
- includes `encrypted_average_demo()` for simple approximate aggregation

Because CKKS is approximate, it is better suited than BFV for real-valued
telemetry where exact integer semantics are not required.

### Quantum Demonstrations

#### `src/quantum/grover_attack.py`

This module demonstrates Grover search on toy marked states.

What it does:

- builds a Grover circuit for a target bitstring
- estimates the near-optimal iteration count
- runs the circuit with AerSimulator
- compares Grover query count to expected classical brute-force queries
- includes a helper that reports the common "AES security is effectively halved
  under Grover" rule of thumb

What it does not do:

- attack production AES implementations
- model realistic fault-tolerant resource overhead

#### `src/quantum/shor_attack.py`

This module demonstrates a scaled Shor-style workflow for toy composite numbers.

What it does:

- computes multiplicative order classically for tiny composites
- builds a compact phase-estimation-style circuit around that order
- estimates the order from measurement results
- attempts factor recovery from the order
- exposes a rough logical-qubit estimate for RSA-2048

What it does not do:

- implement full modular exponentiation for large RSA moduli
- perform practical cryptanalysis on RSA-2048
- estimate full hardware-ready fault-tolerant resources

This file should be read as an educational companion to the cryptography
benchmarks, not as evidence of near-term RSA break capability.

## Notebook

### `notebooks/week1_validation.ipynb`

This notebook is a small validation workflow, not a full analysis suite.

It currently:

- adds the project root to `sys.path`
- instantiates `BenchmarkRunner` for the workstation results directory
- runs RSA validation with reduced trial counts
- runs AES validation with reduced trial counts
- converts the resulting `BenchmarkRecord` objects into a pandas DataFrame
- summarizes the results by scheme and operation

At the moment, the notebook covers AES and RSA only. BFV, CKKS, Grover, and
Shor are currently exercised through module functions rather than notebook
analysis.

## Setup

The repository uses pinned dependencies listed in `requirements.txt`.

Recommended environment:

- Python 3.11
- a local virtual environment or Conda environment

Example setup with `venv`:

```bash
cd ~/Documents/surf2026-pqc-smartgrid
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Example setup with Conda:

```bash
conda create -n surf26 python=3.11
conda activate surf26
pip install -r requirements.txt
```

Notes:

- `tenseal` and `qiskit-aer` can be the most environment-sensitive packages.
- Apple Silicon users may need a Python build and wheel combination compatible
  with those dependencies.

## Running The Code

All commands below assume you are in the repository root.

### One-command setup and run

`scripts/setup_and_run.py` pulls the latest code for the working branch from
origin, downloads the Smart Meters in London dataset into
`data/smart-meters-in-london` (via `kagglehub`, if not already present), and
starts the HE baseline comparison on it:

```bash
python scripts/setup_and_run.py            # pull, download, full run
python scripts/setup_and_run.py --quick    # fast smoke run
python scripts/setup_and_run.py --install --meters 50 --blocks 0,1
```

It needs a Kaggle API token at `~/.kaggle/kaggle.json` for the download step.
Use `--skip-pull` / `--skip-download` to bypass either stage, and `--install` to
`pip install -r requirements.txt` first. The `--quick`, `--trials`, `--meters`,
`--blocks`, and `--row` flags are forwarded to the comparison runner.

### Open the notebook

```bash
cd ~/Documents/surf2026-pqc-smartgrid
source .venv/bin/activate
jupyter lab
```

### Run the Week 1 smoke test

```bash
python scripts/week1_smoke_test.py
```

### Quick AES benchmark

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.classical.aes_baseline import benchmark_aes_baselines

runner = BenchmarkRunner()
benchmark_aes_baselines(
    runner,
    trials=10,
    payload_sizes=(64, 512),
    key_sizes=(128,),
    export_path="quick_aes_check.csv",
)
PY
```

### Quick RSA benchmark

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.classical.rsa_baseline import benchmark_rsa_baselines

runner = BenchmarkRunner()
benchmark_rsa_baselines(
    runner,
    trials=10,
    payload_sizes=(64, 128),
    key_sizes=(2048,),
    export_path="quick_rsa_check.csv",
)
PY
```

### Quick BFV benchmark

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.fhe.bfv_scheme import benchmark_bfv_schemes

runner = BenchmarkRunner()
benchmark_bfv_schemes(
    runner,
    trials=3,
    poly_degrees=(4096,),
    export_path="quick_bfv_check.csv",
)
PY
```

### Quick CKKS benchmark

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.fhe.ckks_scheme import benchmark_ckks_schemes, DEFAULT_CKKS_CONFIGS

runner = BenchmarkRunner()
benchmark_ckks_schemes(
    runner,
    trials=3,
    configs=(DEFAULT_CKKS_CONFIGS[0],),
    export_path="quick_ckks_check.csv",
)
PY
```

### Run the Phase 1 HE baseline comparison

This is the single command for the Phase 1 experiment. It always benchmarks the
Paillier (PHE) baseline, and automatically adds BFV and CKKS when TenSEAL is
installed. Results are exported under `benchmarks/results/workstation/`.

```bash
# Fast smoke run (small trial counts)
python scripts/run_he_baseline_comparison.py --quick

# Full run
python scripts/run_he_baseline_comparison.py --trials 50
```

To drive the readings from the real multi-household **Smart Meters in London**
dataset (`jeanmidev/smart-meters-in-london`), place the extracted dataset at
`data/smart-meters-in-london/`. The runner uses that location automatically (it
is the default `--london-path`), so the commands above then benchmark on real
meters with no extra flags. If the folder is absent, the runner falls back to
small built-in sample vectors.

Download it either by extracting the Kaggle zip into that folder, e.g.:

```bash
# after extracting the Kaggle download (default name "archive (1)")
mv "archive (1)" data/smart-meters-in-london
```

or with `kagglehub` (needs a Kaggle API token at `~/.kaggle/kaggle.json`):

```python
import kagglehub
path = kagglehub.dataset_download("jeanmidev/smart-meters-in-london")
print("Path to dataset files:", path)  # then point --london-path at this
```

The raw dataset is hundreds of MB and is gitignored on purpose -- it stays
local and is never committed. The runner builds a `timestamp x meter` matrix,
feeds a real per-meter reading vector into Paillier/BFV (scaled integer Wh) and
CKKS (kWh floats), and runs an encrypted multi-meter aggregation correctness
check. Control the slice with `--meters`, `--blocks`, and `--row`:

```bash
python scripts/run_he_baseline_comparison.py --meters 20 --blocks 0
```

The runner also supports the newer local SGCC electricity-theft archive and the
derived `df.csv` feature dataframe:

```bash
# SGCC archive: 42,372 customers, daily electricity readings, theft labels.
# The raw file is local-only at archive (2)/data.csv and is too large for git.
python scripts/run_he_baseline_comparison.py \
  --dataset sgcc \
  --sgcc-path "archive (2)" \
  --meters 50 \
  --row 944 \
  --trials 50

# Derived df.csv: hourly building-energy electricity feature vector.
python scripts/run_he_baseline_comparison.py \
  --dataset df \
  --df-path df.csv \
  --row 0 \
  --trials 50
```

For SGCC, the runner converts the wide `CONS_NO, FLAG, <date...>` layout into a
`date x customer` matrix. Row `944` corresponds to `2016-08-02` in chronological
order for the first 50 loaded customers and gives 50 live customer readings. For
`df.csv`, the default path uses the electricity columns only; pass
`--df-all-numeric` to include gas and other numeric features as well. Tagged
result CSVs are exported as `he_comparison_sgcc_*.csv` and
`he_comparison_df_*.csv`.

### Quick Paillier baseline benchmark

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.fhe.paillier_scheme import benchmark_paillier_baseline

runner = BenchmarkRunner()
benchmark_paillier_baseline(
    runner,
    trials=10,
    keygen_trials=2,
    key_sizes=(2048,),
    export_path="quick_paillier_check.csv",
)
PY
```

### Run the Grover demo

```bash
python -m src.quantum.grover_attack
```

### Run the scaled Shor demo

```bash
python -m src.quantum.shor_attack
```

## Results Management

Results are intended to live under `benchmarks/results/` and be separated by
device class.

Recommended convention:

- `benchmarks/results/workstation/` for laptop or desktop development runs
- `benchmarks/results/pi/` for Raspberry Pi or other edge-like runs

Generated result CSV files are ignored by Git, so you can create local benchmark
outputs without polluting repository history. The input dataset
`data/smart_grid_dataset.csv` is explicitly tracked. If you later need
publication artifacts in version control, place curated summaries or figures in
`docs/` instead of committing raw benchmark dumps.

## Methodology Notes and Caveats

- RSA measurements use OAEP with SHA-256, not PKCS#1 v1.5.
- AES-CBC includes padding overhead; AES-GCM includes authentication overhead.
- BFV and CKKS timings include TenSEAL vector operations and therefore reflect
  the chosen parameter sets, not some scheme-independent FHE cost.
- The smart-grid framing in this repository currently comes from a real
  telemetry CSV, telemetry-derived payloads, representative payload sizes, and
  encrypted aggregation patterns, not from a simulated utility network.
- The Shor and Grover modules are pedagogical. They should not be presented as
  practical attacks on production cryptosystems.
- No automated test suite is present yet, so validation is currently driven by
  notebook checks and direct benchmark runs.

## Suggested Next Steps

If the project is meant to become a fuller PQC benchmark repository, the next
natural additions would be:

- NIST PQC KEM/signature baselines
- committed analysis notebooks or plots under `docs/`
- automated smoke tests for imports and short benchmark runs
- a clearer smart-grid workload generator for telemetry and control-message
  traces

## Acknowledgement

This research was supported by the College of Charleston Office of Undergraduate
Research and Creative Activities under SURF Grant #12 for the SURF 2026 program.
