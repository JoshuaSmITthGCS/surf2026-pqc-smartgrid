# CLAUDE.md

This file gives Claude-style coding agents a compact working brief for this
repository.

## Project Summary

This repository benchmarks crypto-relevant building blocks for a SURF 2026
smart-grid research project.

Current checked-in scope:

- AES and RSA baselines in `src/classical/`
- BFV and CKKS experiments in `src/fhe/`
- educational Grover and scaled Shor demos in `src/quantum/`
- real telemetry dataset loading and payload construction in `src/smartgrid/`
- shared timing/export logic in `benchmarks/runner.py`
- one validation notebook in `notebooks/week1_validation.ipynb`
- one reusable smoke script in `scripts/week1_smoke_test.py`

Important: despite the repository name, there are no checked-in NIST PQC
implementations yet. Do not describe the current codebase as if ML-KEM,
ML-DSA, Falcon, or SPHINCS+ already exist here.

Current Phase 1 research scope:

- Compare homomorphic encryption techniques against one classical encryption
  baseline.
- Use AES-GCM as the classical encryption baseline unless the user or mentor
  changes that choice.
- Treat RSA as setup/reference code only for this phase; do not frame it as the
  main baseline against BFV or CKKS.
- Prioritize BFV and CKKS as the first two HE baselines.

## Key Files

- `benchmarks/runner.py`
  - canonical benchmark harness
  - owns CSV schema, device labeling, timing, and CSV export
- `src/classical/aes_baseline.py`
  - AES-CBC and AES-GCM helpers and benchmark wrapper
- `src/classical/rsa_baseline.py`
  - RSA-OAEP baseline and OAEP payload-size checks
- `src/fhe/bfv_scheme.py`
  - BFV helpers, encrypted sum demo, benchmark wrapper
- `src/fhe/ckks_scheme.py`
  - CKKS helpers, encrypted average demo, benchmark wrapper
- `src/quantum/grover_attack.py`
  - toy Grover search demos
- `src/quantum/shor_attack.py`
  - scaled educational Shor demos
- `src/smartgrid/workloads.py`
  - validates `data/smart_grid_dataset.csv`
  - summarizes dataset quality and coverage
  - builds exact-size telemetry-derived payload bytes for benchmarks
- `notebooks/week1_validation.ipynb`
  - dataset-aware AES and RSA validation notebook
- `scripts/week1_smoke_test.py`
  - import, dataset, and quick RSA-2048 benchmark smoke test

## Working Conventions

- Keep benchmark logic in Python modules, not inside notebooks.
- Use `BenchmarkRunner` for new measured code paths so CSV output stays
  consistent.
- Preserve the existing CSV schema unless there is a strong reason to change it.
- Generated CSV files belong under `benchmarks/results/` and are intentionally
  gitignored.
- The real input dataset belongs at `data/smart_grid_dataset.csv` and is
  explicitly unignored in `.gitignore`.
- Prefer adding small helper functions plus a `benchmark_*` wrapper rather than
  large monolithic scripts.
- Match the existing code style:
  - type hints
  - focused helper functions
  - dataclasses for structured results where useful
  - module-level defaults for benchmark parameters
  - `__all__` exports in package modules

## Research Guardrails

- Do not overclaim the quantum modules.
  - `grover_attack.py` is a toy search demonstration.
  - `shor_attack.py` is a scaled educational surrogate, not a practical RSA
    attack.
- Do not call BFV or CKKS "post-quantum replacements" for RSA/AES. They serve a
  different purpose.
- Do not use RSA as the active Phase 1 comparison baseline against homomorphic
  encryption; AES-GCM is the intended single classical baseline.
- Be explicit that the smart-grid framing is currently modeled through a real
  telemetry CSV, telemetry-derived payloads, payload sizes, and encrypted
  aggregation patterns, not a full simulator.
- If you add actual PQC algorithms later, document the algorithm family,
  library, parameter set, and why it belongs in the comparison.

## Common Commands

Set up:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run notebook:

```bash
jupyter lab
```

Run the Week 1 smoke test:

```bash
python scripts/week1_smoke_test.py
```

Quick AES or RSA validation:

```bash
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.classical.aes_baseline import benchmark_aes_baselines
from src.classical.rsa_baseline import benchmark_rsa_baselines

runner = BenchmarkRunner()
benchmark_aes_baselines(runner, trials=10, payload_sizes=(64,), key_sizes=(128,), export_path="claude_aes.csv")
benchmark_rsa_baselines(runner, trials=10, payload_sizes=(64,), key_sizes=(2048,), export_path="claude_rsa.csv")
PY
```

Run quantum demos:

```bash
python -m src.quantum.grover_attack
python -m src.quantum.shor_attack
```

## When Adding New Work

- If you add a new cryptosystem, place it in the closest existing package or a
  new focused package under `src/`.
- Expose a benchmark wrapper that returns `BenchmarkRecord` rows.
- Keep exports reproducible and easy to re-run with small trial counts.
- Update `README.md` when the repository scope materially changes.
- If the addition is the first real PQC implementation, also update this file so
  future agents stop assuming the project is still classical/FHE/quantum-demo
  only.
