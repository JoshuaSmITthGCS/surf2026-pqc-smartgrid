# SURF 2026 Weekly Progress Report - Week 2

**Reporting period:** May 26-28, 2026
**Researcher:** Joshua Smith
**Mentor:** Dr. Mohamed Baza
**Project:** Benchmarking post-quantum and homomorphic encryption for smart-grid communications under simulated quantum threats

## Email Draft

**Subject:** SURF 2026 Weekly Progress Report - Week 2

Dear Dr. Baza,

This is my Week 2 progress report for the SURF 2026 smart-grid cryptography benchmarking project.

## 1. Summary of Work Completed During the Week

This week I expanded the initial research codebase beyond basic setup and validated the first baseline benchmark path. The repository now includes a reusable benchmark harness, an AES classical encryption baseline, starter BFV and CKKS homomorphic encryption modules, and educational Grover and scaled Shor quantum-security demonstrations. RSA helper code exists from setup, but it will not be treated as a Phase 1 comparison baseline.

I also integrated the real smart-grid telemetry dataset into the project under `data/smart_grid_dataset.csv`. I added dataset validation utilities that check required columns, timestamp coverage, missing values, duplicate timestamps, and basic telemetry statistics. The dataset currently contains 50,000 rows, 16 columns, 15-minute sampling intervals, no missing values, and no duplicate timestamps.

For baseline validation, I updated the Jupyter notebook so it loads the real dataset, builds exact-size telemetry-derived payloads, and runs quick encryption checks through the shared `BenchmarkRunner`. The active Phase 1 comparison will focus on AES-GCM as the classical encryption baseline versus BFV and CKKS as homomorphic encryption baselines.

Environment validation was completed for the local workstation. Homebrew, Miniconda, the `surf26` Conda environment, and the `SURF 2026 (surf26)` Jupyter kernel are present. The key packages `tenseal`, `Crypto`, `qiskit`, and `qiskit_aer` import successfully.

## 2. Tasks and Goals Planned for the Following Week

Next week, I plan to focus on selecting and implementing the first homomorphic encryption baselines. The main goal is to compare at least two HE techniques against one classical encryption baseline using the same benchmark schema.

Planned tasks:

- Present three HE techniques: BFV, CKKS, and BGV or TFHE.
- Decide which two HE techniques should be implemented first, likely BFV and CKKS.
- Confirm AES-GCM as the one classical encryption baseline.
- Improve `src/fhe/bfv_scheme.py` for encrypted integer aggregation over smart-grid data.
- Improve `src/fhe/ckks_scheme.py` for encrypted voltage/load averages over smart-grid data.
- Export first HE benchmark results to `benchmarks/results/workstation/`.
- Update documentation to reflect the HE-first baseline scope.
- Define the virtual or simulated edge benchmark strategy that will be used for the paper.

I would also like to confirm the target publication direction, either IEEE SmartGridComm or IEEE Conference on Communications and Network Security, and confirm whether the third HE technique should be implemented in code or discussed as a literature comparison.

## 3. Challenges Encountered and Proposed Solutions

One challenge was that generated benchmark CSV files and real input CSV files need different Git behavior. Benchmark result CSVs should remain ignored so repeated runs do not pollute the repository, but the real smart-grid dataset needs to be tracked. I addressed this by keeping the general `*.csv` ignore rule while explicitly allowing `data/smart_grid_dataset.csv`.

Another challenge is choosing the right classical baseline. RSA is not the right Phase 1 comparison because it does not support computation over encrypted data. AES-GCM is a better classical baseline because it represents fast conventional encryption for the same telemetry payloads, while BFV and CKKS measure the extra cost of encrypted computation.

A third challenge is dependency sensitivity for TenSEAL and Qiskit Aer. To reduce reproducibility issues, I validated imports inside the `surf26` environment and added a smoke-test script that can be run quickly after environment changes.

The main open challenge for next week is HE parameter selection. My proposed solution is to begin with TenSEAL-supported BFV and CKKS parameter sets, validate correctness on small smart-grid workloads, and then scale benchmark sizes carefully.

Raspberry Pi hardware testing may still be useful later, but I plan to treat it as an optional back-end extension rather than a blocker for the main research paper. The higher-priority path is to produce reproducible workstation and virtual/simulated benchmark results first, then add Raspberry Pi results as supplemental data if time and hardware availability allow.

Best,
Joshua Smith
SURF 2026 Researcher
College of Charleston Computer Science Department
