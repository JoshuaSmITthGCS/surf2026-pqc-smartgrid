# SURF 2026: 10-Week Research Checklist

**Program Duration:** May 19-July 24, 2026
**Researcher:** Joshua Smith
**Mentor:** Dr. Mohamed Baza
**Goal:** Build a reproducible benchmark suite comparing homomorphic encryption techniques against one classical encryption baseline for smart-grid telemetry, then extend toward PQC if time allows.

## Status Legend

- `[x]` completed or already worked on
- `[ ]` not started or still open
- Items marked `partial` have been started but need follow-up before they count as finished

## Last Updated

- [x] May 19, 2026: Updated this plan into a living checklist.
- [x] May 19, 2026: Added real smart-grid dataset validation, telemetry-derived payloads, Week 1 notebook updates, and the Week 1 smoke test.
- [x] May 19, 2026: Moved Raspberry Pi hardware benchmarking to an optional back-end stretch goal and made virtual/simulated benchmark validation the primary paper path.
- [x] May 21, 2026: Refocused Phase 1 on homomorphic encryption techniques compared against one classical encryption baseline, AES-GCM.

---

## Week 1: May 19-23 - Onboarding, Environment, and Baseline Validation

### Objectives

- [x] Set up the development repository and baseline benchmark structure.
- [x] Validate local Python environment and required packages.
- [x] Integrate the real smart-grid dataset for Week 1 validation.
- [x] Run workstation sanity checks for the baseline code.
- [ ] Meet with Dr. Baza to finalize research scope and publication target.
- [ ] Present three homomorphic encryption techniques for the first research phase.
- [ ] Choose two homomorphic encryption techniques for initial baselines.
- [ ] Confirm AES-GCM as the one classical encryption baseline.
- [ ] Define the virtual benchmark strategy for the paper.

### Tasks

- [x] Confirm Homebrew is installed.
- [x] Confirm Miniconda/Conda is installed.
- [x] Confirm `surf26` Conda environment exists.
- [x] Confirm `SURF 2026 (surf26)` Jupyter kernel exists.
- [x] Validate imports for `tenseal`, `Crypto`, `qiskit`, and `qiskit_aer`.
- [x] Create or verify project structure under `~/Documents/surf2026-pqc-smartgrid`.
- [x] Implement reusable `BenchmarkRunner` with CSV export and Rich tables.
- [x] Implement AES-CBC and AES-GCM baseline helpers.
- [x] Implement RSA-OAEP helper code, now treated as nonessential for Phase 1.
- [x] Implement BFV helper functions and encrypted sum demo.
- [x] Implement CKKS helper functions and encrypted average demo.
- [x] Implement toy Grover and scaled Shor demonstrations.
- [x] Add the real dataset at `data/smart_grid_dataset.csv`.
- [x] Add smart-grid workload helpers in `src/smartgrid/workloads.py`.
- [x] Update AES/RSA benchmark wrappers to accept telemetry-derived payloads.
- [x] Update `notebooks/week1_validation.ipynb` to validate the dataset and run early AES/RSA checks.
- [x] Add `scripts/week1_smoke_test.py`.
- [x] Add `docs/WEEK1_VALIDATION.md`.
- [x] Run Week 1 notebook execution check.
- [x] Run Week 1 smoke test.
- [x] Create Week 1 progress report draft.
- [ ] Kickoff meeting: align on publication target, likely IEEE SmartGridComm or IEEE CNS.
- [ ] Prepare meeting notes for three HE techniques:
  - [ ] BFV for exact integer aggregation.
  - [ ] CKKS for approximate real-valued telemetry.
  - [ ] BGV or TFHE as the third candidate technique.
- [ ] Decide first two HE baselines, likely BFV and CKKS.
- [ ] Decide which one classical encryption baseline to keep, likely AES-GCM.
- [ ] Decide which virtual or simulated edge conditions should be included in the paper.

### Deliverables

- [x] Working repo with benchmark harness and starter implementations.
- [x] Dataset validation notes.
- [x] Week 1 validation notebook.
- [x] Week 1 smoke test script.
- [x] Week 1 progress report draft.
- [ ] Mentor-approved research scope decisions.
- [ ] Meeting-ready comparison notes for three HE techniques.
- [ ] Phase 1 baseline decision: two HE techniques plus one classical encryption baseline.
- [ ] Virtual benchmark methodology notes for the paper.

---

## Week 2: May 26-30 - Select and Implement HE Baselines

### Objectives

- [ ] Build a solid understanding of three homomorphic encryption techniques.
- [ ] Select at least two HE techniques for Phase 1 baselines.
- [ ] Use one classical encryption baseline, AES-GCM, as the conventional reference.
- [ ] Follow existing `BenchmarkRunner` patterns.

### Tasks

- [ ] Prepare meeting summary for BFV, CKKS, and BGV or TFHE.
- [ ] Explain which smart-grid workload each HE technique fits best.
- [ ] Confirm AES-GCM as the one classical encryption baseline.
- [ ] Improve `src/fhe/bfv_scheme.py` for dataset-derived integer aggregation.
- [ ] Improve `src/fhe/ckks_scheme.py` for dataset-derived voltage/load averages.
- [ ] Add benchmark runs comparing AES-GCM, BFV, and CKKS on comparable telemetry workloads.
- [ ] Validate BFV encrypted sum round trips.
- [ ] Validate CKKS encrypted average accuracy and error.
- [ ] Export HE baseline results to `benchmarks/results/workstation/`.
- [ ] Document why RSA is not part of Phase 1 comparison.
- [ ] Write Week 2 progress report by Thursday.

### Deliverables

- [ ] Meeting-ready explanation of three HE techniques.
- [ ] Phase 1 implementation decision: BFV and CKKS unless mentor chooses otherwise.
- [ ] AES-GCM classical baseline decision.
- [ ] First HE benchmark CSVs.
- [ ] BFV and CKKS validation notes.
- [ ] Code review notes from mentor.

---

## Week 3: June 2-6 - HE Workloads and Third-Technique Decision

### Objectives

- [ ] Turn BFV and CKKS into smart-grid-specific benchmark workloads.
- [ ] Decide whether to implement the third HE technique or keep it as a literature comparison.

### Tasks

- [ ] Create smart-grid BFV workload for encrypted integer aggregation.
- [ ] Create smart-grid CKKS workload for encrypted real-valued averaging.
- [ ] Compare AES-GCM encryption/decryption cost against HE encrypt, decrypt, add, and multiply costs.
- [ ] Measure CKKS approximation error for voltage/load averages.
- [ ] Measure BFV exactness for integer aggregation.
- [ ] Research implementation feasibility for BGV or TFHE.
- [ ] Decide whether BGV or TFHE should be implemented in code.
- [ ] Update README to reflect the HE-first Phase 1 scope.
- [ ] Write Week 3 progress report by Thursday.

### Deliverables

- [ ] Smart-grid HE workload module or notebook.
- [ ] AES-GCM vs BFV vs CKKS benchmark table.
- [ ] Recommendation on the third HE technique.
- [ ] Updated documentation.

---

## Week 4: June 9-13 - Smart-Grid Workload Integration

### Objectives

- [x] Add real smart-grid data to the repository.
- [x] Start realistic payload generation from telemetry rows.
- [ ] Build scenario-level smart-grid workloads.

### Tasks

- [x] Add real smart-grid dataset or comparable telemetry data under `data/`.
- [x] Create `src/smartgrid/__init__.py`.
- [x] Create smart-grid workload utilities for loading, validation, and payload construction.
- [x] Update AES/RSA benchmark wrappers to use real-data payload distributions.
- [ ] Create `src/smartgrid/scenarios.py`.
- [ ] Scenario 1: meter reading aggregation with BFV.
- [ ] Scenario 2: encrypted voltage/load average with CKKS.
- [ ] Scenario 3: AES-GCM reference encryption for the same telemetry payloads.
- [ ] Add notebook: `notebooks/week4_smart_grid_workloads.ipynb`.
- [ ] Write Week 4 progress report by Thursday.

### Deliverables

- [x] Real smart-grid data in `data/`.
- [x] Dataset validation and payload helper module.
- [ ] Scenario definitions.
- [ ] Smart-grid workload analysis notebook.

---

## Week 5: June 16-20 - Virtual Benchmarking and Simulated Edge Profiles

### Objectives

- [ ] Run the full benchmark suite on the primary workstation.
- [ ] Create paper-ready virtual or simulated edge comparison results.
- [ ] Identify performance bottlenecks without depending on hardware availability.

### Tasks

- [ ] Run AES baseline benchmarks with selected final trial counts.
- [ ] Run BFV benchmarks with selected final trial counts.
- [ ] Run CKKS benchmarks with selected final trial counts.
- [ ] Run BFV scenario checks.
- [ ] Run CKKS scenario checks.
- [ ] Export workstation results to `benchmarks/results/workstation/`.
- [ ] Define one or more simulated edge profiles for the paper.
- [ ] Record system metadata, memory pressure, and CPU load during benchmark runs.
- [ ] Document any library issues or performance anomalies.
- [ ] Create `notebooks/week5_virtual_benchmarking.ipynb`.
- [ ] Write Week 5 progress report by Thursday.

### Deliverables

- [ ] Complete workstation benchmark dataset.
- [ ] Virtual or simulated edge benchmark notes.
- [ ] Paper-ready comparison notebook.
- [ ] Documented bottlenecks and anomalies.

---

## Week 6: June 23-27 - Analysis and Visualization

### Objectives

- [ ] Analyze results across all implemented schemes.
- [ ] Generate publication-quality figures.

### Tasks

- [ ] Create `notebooks/full_analysis.ipynb`.
- [ ] Load all workstation CSV results.
- [ ] Load virtual or simulated edge comparison results if available.
- [ ] Compute mean, median, p95, and variance summaries.
- [ ] Compare AES-GCM, BFV, and CKKS costs.
- [ ] Compare workstation and virtual/simulated edge profiles.
- [ ] Analyze payload-size scaling.
- [ ] Generate latency comparison figure.
- [ ] Generate device comparison figure.
- [ ] Generate payload scaling figure.
- [ ] Generate ciphertext/signature overhead table.
- [ ] Generate smart-grid scenario latency figure.
- [ ] Export figures to `docs/figures/` as PNG and PDF.
- [ ] Create summary statistics table.
- [ ] Write Week 6 progress report by Thursday.

### Deliverables

- [ ] Complete analysis notebook.
- [ ] 5-7 publication-ready figures.
- [ ] Summary statistics CSV or table.

---

## Week 7: June 30-July 4 - Quantum Security Discussion

### Objectives

- [x] Implement toy Grover demonstration.
- [x] Implement scaled Shor demonstration.
- [x] Include AES security reduction helper under Grover.
- [x] Include RSA-2048 logical-qubit estimate helper for Shor.
- [ ] Write the formal quantum threat model discussion.

### Tasks

- [x] Add AES-128 and AES-256 effective security estimate under Grover.
- [x] Add rough RSA-2048 logical-qubit estimate.
- [ ] Expand RSA-2048/RSA-4096 vulnerability timeline discussion.
- [ ] Add references to NIST and recent quantum-computing resource estimates.
- [ ] Create `docs/quantum_threat_model.md`.
- [ ] Explain why smart grids need long-term security.
- [ ] Add quantum context to `notebooks/full_analysis.ipynb`.
- [ ] Dry run quantum demos for presentation.
- [ ] Write Week 7 progress report by Thursday.

### Deliverables

- [x] Working quantum demo modules.
- [ ] Quantum threat model document.
- [ ] Security comparison table for RSA, AES, and PQC.

---

## Week 8: July 7-11 - Testing and Reproducibility

### Objectives

- [ ] Add automated tests.
- [ ] Make the benchmark suite reproducible.
- [ ] Prepare the code for public release.

### Tasks

- [ ] Create `tests/__init__.py`.
- [ ] Create `tests/test_classical.py`.
- [ ] Add AES round-trip tests.
- [ ] Add RSA round-trip tests.
- [ ] Create `tests/test_pqc.py`.
- [ ] Add ML-KEM encapsulation/decapsulation tests.
- [ ] Add ML-DSA or Falcon sign/verify tests.
- [ ] Create `tests/test_fhe.py`.
- [ ] Add BFV smoke test.
- [ ] Add CKKS smoke test.
- [ ] Create `tests/test_benchmarks.py`.
- [ ] Validate `BenchmarkRunner` output schema.
- [ ] Add `pytest` to `requirements.txt`.
- [ ] Create GitHub Actions workflow if time allows.
- [ ] Run final full benchmark suite with selected parameters.
- [ ] Document reproduction steps in README.
- [ ] Write Week 8 progress report by Thursday.

### Deliverables

- [ ] Automated test suite.
- [ ] Reproducibility checklist.
- [ ] Optional CI workflow.

---

## Week 9: July 14-18 - Paper Writing Draft

### Objectives

- [ ] Write the first complete conference-paper draft.
- [ ] Target IEEE SmartGridComm or IEEE CNS style.

### Tasks

- [ ] Create `docs/paper_draft.md` or LaTeX draft.
- [ ] Write abstract.
- [ ] Write introduction.
- [ ] Write background section.
- [ ] Write methodology section.
- [ ] Write results section.
- [ ] Write discussion section.
- [ ] Write related work section.
- [ ] Write conclusion.
- [ ] Insert figures and tables.
- [ ] Add 20-30 relevant citations.
- [ ] Share draft with Dr. Baza for feedback.
- [ ] Write Week 9 progress report by Thursday.

### Deliverables

- [ ] Complete 6-8 page draft.
- [ ] Bibliography with 20-30 citations.
- [ ] Draft shared with mentor.

---

## Week 10: July 21-24 - Final Deliverables and Presentation

### Objectives

- [ ] Finalize research materials.
- [ ] Prepare final SURF presentation.
- [ ] Submit final SURF deliverables.

### Tasks

- [ ] Monday, July 21: revise paper based on mentor feedback.
- [ ] Tuesday, July 22: create final presentation slides.
- [ ] Add motivation slides.
- [ ] Add methodology slides.
- [ ] Add results slides with figures.
- [ ] Add discussion slides.
- [ ] Add conclusion slide.
- [ ] Add optional short demo.
- [ ] Wednesday, July 23: practice presentation.
- [ ] Thursday, July 24: deliver final SURF presentation.
- [ ] Polish README for public release.
- [ ] Archive final benchmark results.
- [ ] Create `docs/FINAL_REPORT.md`.
- [ ] Push final code to GitHub if public.
- [ ] Submit required SURF program materials.
- [ ] Write final weekly progress report by Thursday.

### Deliverables

- [ ] Revised paper draft.
- [ ] Final presentation slides.
- [ ] Delivered final presentation.
- [ ] Polished repository.
- [ ] SURF final report.

---

## Weekly Thursday Progress Report Checklist

Every Thursday by email:

- [x] Week 1 report draft created.
- [ ] Week 1 report emailed.
- [ ] Week 2 report emailed.
- [ ] Week 3 report emailed.
- [ ] Week 4 report emailed.
- [ ] Week 5 report emailed.
- [ ] Week 6 report emailed.
- [ ] Week 7 report emailed.
- [ ] Week 8 report emailed.
- [ ] Week 9 report emailed.
- [ ] Week 10 report emailed.

Each report should include:

- [ ] Summary of work completed during the week.
- [ ] Tasks and goals planned for the following week.
- [ ] Challenges encountered and proposed solutions.

## Weekly Maintenance Checklist

Complete each week after the Thursday report:

- [ ] Update this checklist with completed, partial, and blocked items.
- [ ] Commit code and documentation changes to Git.
- [ ] Export or archive latest benchmark results.
- [ ] Identify blockers for the next week.
- [ ] Confirm next meeting agenda with Dr. Baza.

---

## Contingency Planning

### If Ahead of Schedule

- [ ] Add additional PQC algorithms such as SPHINCS+ or Falcon-1024.
- [ ] Implement network latency simulation.
- [ ] Add Raspberry Pi hardware benchmarking as an optional back-end extension.
- [ ] Add Raspberry Pi power or energy measurements if hardware testing happens.
- [ ] Run benchmarks on additional edge devices if hardware is available.
- [ ] Start conference-paper submission process early.

### If Behind Schedule

Priority order:

1. [ ] BFV and CKKS implementation and benchmarks.
2. [ ] AES-GCM classical baseline comparison.
3. [x] Smart-grid dataset and payload integration.
4. [ ] Virtual benchmark comparison.
5. [ ] Full analysis and figures.
6. [ ] Paper draft.
7. [ ] Third HE technique implementation, if time permits.
8. [ ] PQC extension, if time permits after HE baselines.
9. [ ] Automated tests, if time permits.
10. [ ] Raspberry Pi hardware comparison, if time and hardware allow.
11. [x] Quantum demos implemented; documentation still needed.

### Known Risks

- [ ] HE parameter-selection complexity. Proposed response: start with TenSEAL-supported BFV and CKKS presets and document every parameter set.
- [ ] Raspberry Pi availability or performance limits. Proposed response: treat hardware tests as optional and prioritize reproducible virtual benchmarks for the paper.
- [x] Dataset availability risk reduced by adding `data/smart_grid_dataset.csv`.
- [ ] Paper timeline pressure. Proposed response: use SURF report as the first structured paper draft.

---

## Success Metrics By July 24

- [ ] At least two HE techniques benchmarked.
- [ ] One classical encryption baseline benchmarked, likely AES-GCM.
- [ ] AES-GCM vs BFV vs CKKS comparison.
- [ ] Workstation and virtual/simulated edge benchmark results.
- [ ] 5-7 publication-quality figures.
- [ ] 6-8 page paper draft.
- [ ] Reproducible codebase with documentation.
- [ ] Final presentation delivered.
- [ ] Paper ready for IEEE SmartGridComm or IEEE CNS submission planning.

## Optional Hardware Back-End Goal

Raspberry Pi testing is useful, but it is not required for the primary paper path. It should be attempted after the core virtual/workstation experiments, PQC implementation, analysis, and figures are stable.

- [ ] Set up Raspberry Pi 4 with matching Python environment.
- [ ] Transfer codebase to Raspberry Pi.
- [ ] Run a reduced benchmark suite on Raspberry Pi.
- [ ] Export hardware results to `benchmarks/results/pi/`.
- [ ] Compare Raspberry Pi results against workstation and virtual/simulated edge profiles.
- [ ] Add Raspberry Pi results as an appendix, supplemental figure, or future-work section if the hardware run is completed.

## Post-SURF Optional Goals

- [ ] August: submit paper to selected conference or preprint server.
- [ ] September-October: address reviewer or mentor feedback.
- [ ] November: present at conference if accepted.
- [ ] Spring 2027: consider journal extension.
