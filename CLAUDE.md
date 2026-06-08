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

- Compare homomorphic encryption schemes head-to-head against the Paillier (PHE)
  baseline. Per Dr. Baza's Meeting 2 feedback (see the
  `SURF2026_Meeting_Baza_2` slides and `docs/HE_BASELINE_MEETING_NOTES.md`), the
  comparison baseline must be a homomorphic scheme, not RSA.
- Use Paillier (PHE), via the `phe` library, as the single comparison baseline.
  It is the classic prior-generation smart-metering aggregation scheme
  (additively homomorphic, DCR hardness, broken by Shor).
- Prioritize BFV and CKKS as the first two RLWE HE schemes; plan BGV
  (`python-seal`/OpenFHE) as the Week 3-4 third scheme for the depth >= 2
  demand-response pipeline.
- Treat AES-GCM and RSA as context-only references for this phase; do not frame
  either as the active comparison baseline against the HE schemes.

## Key Files

- `benchmarks/runner.py`
  - canonical benchmark harness
  - owns CSV schema, device labeling, timing, and CSV export
- `src/classical/aes_baseline.py`
  - AES-CBC and AES-GCM helpers and benchmark wrapper
- `src/classical/rsa_baseline.py`
  - RSA-OAEP baseline and OAEP payload-size checks
- `src/fhe/paillier_scheme.py`
  - Paillier (PHE) baseline: keygen/encrypt/decrypt/add/mul_plain helpers,
    encrypted meter-sum demo, ciphertext-expansion helper, benchmark wrapper
  - depends only on `phe`; the `src/fhe` package imports it without TenSEAL
- `src/fhe/bfv_scheme.py`
  - BFV helpers, encrypted sum demo, benchmark wrapper
- `src/fhe/ckks_scheme.py`
  - CKKS helpers, encrypted average demo, benchmark wrapper
- `src/quantum/grover_attack.py`
  - toy Grover search demos
- `src/quantum/shor_attack.py`
  - scaled educational Shor demos
- `src/smartgrid/workloads.py`
  - validates `data/smart_grid_dataset.csv` (single-feed telemetry)
  - summarizes dataset quality and coverage
  - builds exact-size telemetry-derived payload bytes for benchmarks
- `src/smartgrid/london_meters.py`
  - loads the multi-household Smart Meters in London dataset
    (`jeanmidev/smart-meters-in-london`, half-hourly per-meter kWh)
  - builds a `timestamp x meter` matrix and per-meter reading vectors
    (scaled integers for Paillier/BFV, floats for CKKS)
  - independent of `workloads.py`; used by the HE comparison runner via
    `--london-path`
- `notebooks/week1_validation.ipynb`
  - dataset-aware AES and RSA validation notebook
- `scripts/week1_smoke_test.py`
  - import, dataset, and quick RSA-2048 benchmark smoke test
- `scripts/run_he_baseline_comparison.py`
  - one-command Phase 1 runner: always benchmarks the Paillier baseline, adds
    BFV and CKKS automatically when TenSEAL is installed

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
- The active Phase 1 comparison baseline is Paillier (PHE). Do not use RSA or
  AES-GCM as the head-to-head baseline against the HE schemes; they are
  context-only references now.
- Do not describe Paillier as post-quantum secure. Its DCR hardness is broken by
  Shor; that contrast with the RLWE schemes (BFV/CKKS/BGV) is a key point.
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

Run the Phase 1 HE baseline comparison (Paillier baseline; adds BFV/CKKS when
TenSEAL is installed):

```bash
python scripts/run_he_baseline_comparison.py --quick
python scripts/run_he_baseline_comparison.py --trials 50
```

One-command bootstrap (pull from origin, download the Smart Meters in London
dataset via kagglehub, then run the comparison):

```bash
python scripts/setup_and_run.py --quick
python scripts/setup_and_run.py --install --meters 50 --blocks 0,1
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
