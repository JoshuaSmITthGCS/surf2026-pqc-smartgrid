# SURF 2026 Weekly Progress Report - Week 1

**Reporting period:** May 19-21, 2026
**Researcher:** Joshua Smith
**Mentor:** Dr. Mohamed Baza
**Project:** Benchmarking post-quantum and homomorphic encryption for smart-grid communications under simulated quantum threats

## Email Draft

**Subject:** SURF 2026 Weekly Progress Report - Week 1

Dear Dr. Baza,

This is my Week 1 progress report for the SURF 2026 smart-grid cryptography benchmarking project.

## 1. Summary of Work Completed During the Week

This week I focused on setting up the project foundation and confirming that the baseline development environment is working.

Completed setup work:

- Created and organized the project repository structure.
- Confirmed Homebrew, Conda, the `surf26` environment, and the Jupyter kernel are available.
- Installed and validated the main Python dependencies needed for the project.
- Added the initial benchmark framework for collecting timing results and exporting CSV files.
- Added an AES classical encryption baseline for early validation.
- Added RSA helper code during setup, but RSA will not be treated as a Phase 1 comparison baseline.
- Added starter homomorphic encryption and quantum demonstration modules for future work.
- Added the smart-grid dataset to the project.
- Created the Week 1 validation notebook and a simple smoke-test script.

The main result from Week 1 is that the project now has a working baseline environment. The code can import the required packages, run basic cryptography checks, and export benchmark results in a consistent CSV format.

## 2. Tasks and Goals Planned for the Following Week

Next week I plan to move from setup into the first real homomorphic-encryption benchmark work.

Planned tasks:

- Prepare a short explanation of three homomorphic encryption techniques.
- Focus on BFV, CKKS, and one third candidate such as BGV or TFHE.
- Decide which two HE techniques should be implemented first.
- Use AES-GCM as the one classical encryption baseline for comparison.
- Start improving BFV and CKKS benchmarks around the real smart-grid dataset.
- Confirm the target publication direction and preferred HE baseline scope.

## 3. Challenges Encountered and Proposed Solutions

The main challenge this week was making sure the environment and project structure were stable before starting algorithm implementation. Some dependencies, especially TenSEAL and Qiskit Aer, can be sensitive to Python versions and platform setup.

My solution was to validate the environment early and add a smoke-test script that can quickly confirm whether the project still imports and runs correctly after changes.

Another challenge is keeping the comparison fair. RSA is classical public-key encryption, but it does not support encrypted computation, so it is not a good Phase 1 baseline against homomorphic encryption. I plan to use AES-GCM as the single classical encryption baseline because it represents conventional fast encryption, while BFV and CKKS represent encrypted computation.

Raspberry Pi testing may be useful later, but the main priority for the paper should be reproducible workstation and virtual/simulated benchmark results. I plan to keep Raspberry Pi testing as an optional extension after the core benchmark suite is stable.

Best,
Joshua Smith
SURF 2026 Researcher
College of Charleston Computer Science Department
