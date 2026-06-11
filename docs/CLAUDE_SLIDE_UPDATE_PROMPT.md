# Prompt for Claude: Update Previous Slides With This Week's Results

Copy the fenced prompt below into Claude. Attach the previous PowerPoint deck
that was already made. If Claude cannot read the repo directly, also attach:

- `benchmarks/results/workstation/he_comparison_paillier.csv`
- `benchmarks/results/workstation/he_comparison_bfv.csv`
- `benchmarks/results/workstation/he_comparison_ckks.csv`
- `benchmarks/results/workstation/he_comparison_sgcc_paillier.csv`
- `benchmarks/results/workstation/he_comparison_sgcc_bfv.csv`
- `benchmarks/results/workstation/he_comparison_sgcc_ckks.csv`
- `benchmarks/results/workstation/he_comparison_df_paillier.csv`
- `benchmarks/results/workstation/he_comparison_df_bfv.csv`
- `benchmarks/results/workstation/he_comparison_df_ckks.csv`
- `docs/HE_BASELINE_MEETING_NOTES.md`
- `docs/SUMMER_PLAN.md`

```text
You are helping me update my existing SURF 2026 smart-grid homomorphic
encryption slide deck for my mentor, Dr. Mohamed Baza.

Goal:
Combine my previous slides with this week's new implementation and benchmark
results. Keep the deck polished and presenter-ready. Do not start from scratch
unless necessary. Preserve the useful previous slides, then add/update slides
with the new dataset, run results, findings, and next steps.

Project:
- SURF 2026, College of Charleston
- Researcher: Joshua Smith
- Mentor: Dr. Mohamed Baza
- Topic: Homomorphic Encryption for Smart-Grid Privacy
- Current focus: compare Paillier (PHE baseline), BFV, and CKKS on real smart
  meter aggregation workloads.

What changed this week:
1. The mentor wants the deck to use the new local archive and the new `df.csv`,
   not the older incorrect dataset slide.
2. The new archive is the SGCC electricity-theft detection dataset:
   `archive (2)/data.csv`
3. The new derived dataframe is:
   `df.csv`
4. The benchmark runner now supports both:
   - `--dataset sgcc` for `archive (2)/data.csv`
   - `--dataset df` for the derived `df.csv` feature matrix
5. Both were run successfully and exported tagged result CSVs under:
   `benchmarks/results/workstation/`

Dataset correction for the old slide deck:
- The previous slide set had the dataset story wrong or incomplete. Fix that
  directly in the updated deck.
- The main dataset for the new slides is NOT ETT transformer telemetry anymore,
  and it is NOT the old Customer_Behaviour / social-ads dataset.
- The main dataset is the SGCC electricity-theft archive from State Grid
  Corporation of China:
  - local path: `archive (2)/data.csv`
  - source paper: "Wide and Deep Convolutional Neural Networks for
    Electricity-Theft Detection to Secure Smart Grids"
  - 42,372 electricity customers
  - README says 1,035 days from 2014-01-01 to 2016-10-31; this local CSV exposes
    1,034 dated reading columns
  - columns: `CONS_NO`, `FLAG`, then daily date columns
  - `CONS_NO` is customer ID
  - `FLAG` is theft label, with this local copy containing 38,757 normal
    customers and 3,615 theft-flagged customers
  - date columns are daily electricity consumption readings
- The derived `df.csv` is a separate feature dataframe:
  - local path: `df.csv`
  - 560,655 rows
  - electricity feature columns used by default:
    `Electricity:Facility [kW](Hourly)`,
    `Fans:Electricity [kW](Hourly)`,
    `Cooling:Electricity [kW](Hourly)`,
    `Heating:Electricity [kW](Hourly)`,
    `InteriorLights:Electricity [kW](Hourly)`,
    `InteriorEquipment:Electricity [kW](Hourly)`
  - also includes class/theft labels, but the current HE benchmark uses the
    numeric electricity feature vector, not the classifier labels
- What the HE input means:
  - SGCC: one date row becomes a vector of customer daily consumption readings
  - `df.csv`: one dataframe row becomes a compact electricity feature vector
  - for Paillier and BFV, values are scaled to integers
  - for CKKS, values are used as real-valued approximate analytics inputs
- Smart Meters in London can be mentioned only as a previous validation dataset;
  the newest slide update should center SGCC archive + `df.csv`.

Important implementation note:
- BFV needed a batching-parameter fix. The default BFV plain modulus was changed
  from `1032193` to `1146881` because batching requires
  `plain_modulus == 1 mod 2 * poly_modulus_degree`.
- `1146881 = 35 * 32768 + 1`, so it supports the default BFV degrees:
  4096, 8192, and 16384.
- Mention this as a small engineering fix, not as a major research result.

Use these latest runs:
- SGCC command:
  `python scripts/run_he_baseline_comparison.py --dataset sgcc --sgcc-path "archive (2)" --meters 50 --row 944 --trials 50`
- SGCC slice:
  - 50 customers x 1,034 daily readings
  - date row: 944
  - date: 2016-08-02
  - live customers: 50
  - aggregate cleartext total: 1,153.960 kWh
  - encrypted aggregation check: 1,153,960 Wh decrypted == 1,153,960 Wh expected
    [OK] across 50 customers
- df.csv command:
  `python scripts/run_he_baseline_comparison.py --dataset df --df-path df.csv --row 0 --trials 50`
- df.csv slice:
  - 6 electricity features x 560,655 rows
  - row: 0
  - feature-vector total: 38.401
  - encrypted aggregation check: 38,401 Wh decrypted == 38,401 Wh expected [OK]
    across 6 features

Key SGCC benchmark results from the latest full run:

Paillier baseline:
- PHE-2048:
  - keygen mean: 375.31 ms
  - encrypt mean: 128.05 ms
  - decrypt mean: 32.97 ms
  - homomorphic add mean: 0.056 ms
  - multiply by plaintext mean: 0.116 ms
- PHE-3072:
  - keygen mean: 3231.57 ms
  - encrypt mean: 397.08 ms
  - decrypt mean: 108.78 ms
  - homomorphic add mean: 0.110 ms
  - multiply by plaintext mean: 0.223 ms

BFV:
- poly-4096:
  - encrypt mean: 0.90 ms
  - decrypt mean: 0.23 ms
  - add mean: 0.024 ms
  - multiply mean: 2.27 ms
- poly-8192:
  - encrypt mean: 2.34 ms
  - decrypt mean: 0.84 ms
  - add mean: 0.066 ms
  - multiply mean: 9.25 ms
- poly-16384:
  - encrypt mean: 7.40 ms
  - decrypt mean: 3.45 ms
  - add mean: 0.266 ms
  - multiply mean: 44.03 ms

CKKS:
- balanced-8192:
  - encrypt mean: 2.68 ms
  - decrypt mean: 0.74 ms
  - add mean: 0.040 ms
  - multiply mean: 1.91 ms
- high-depth-16384:
  - encrypt mean: 6.35 ms
  - decrypt mean: 2.13 ms
  - add mean: 0.098 ms
  - multiply mean: 5.92 ms

Also mention the `df.csv` run briefly:
- It validates that the same runner can benchmark the derived feature dataframe.
- It uses only 6 electricity features, so payload is 48 bytes instead of 400.
- Correctness passed, but it is a feature-vector workload rather than the main
  multi-customer aggregation dataset.

Headline findings to include:
1. The project moved from the older incorrect dataset framing to the SGCC
   electricity-theft archive plus the derived `df.csv`.
2. The SGCC 50-customer encrypted aggregation path works end to end.
3. Paillier is useful as a classic additively homomorphic baseline, but its
   encryption and key generation costs are much higher than BFV/CKKS in this
   run.
4. BFV is the best fit for exact integer meter aggregation:
   - exact Wh totals
   - very fast homomorphic addition
   - latency increases with larger polynomial degrees, especially multiplication
5. CKKS is the best fit for approximate real-valued analytics:
   - averages, forecasting-style features, and load statistics
   - approximate results require later error analysis
6. Multiplication is the expensive operation, especially for BFV at high
   polynomial degree.
7. The next research step is to use SGCC labels (`FLAG`) for scenario-level
   theft/anomaly workloads and add analysis figures.

Required deck update:
- Keep the old deck's title, motivation, trust model, and scheme background if
  they are still accurate.
- Update any slide with the old or incorrect dataset story. Replace it with the
  corrected SGCC archive + `df.csv` description above.
- Keep a short note that Smart Meters in London and ETT were earlier validation
  or background datasets, but SGCC + `df.csv` are the current mentor-requested
  datasets for this slide update.
- Keep the baseline correction: Paillier is the HE baseline, not RSA. AES/RSA
  should be context only, not the main head-to-head baseline.

Suggested slide structure:
1. Title / project status
2. Previous motivation recap: why HE for smart-grid privacy
3. Dataset correction: SGCC archive + df.csv, replacing old dataset slide
4. Workload this week: SGCC 50-customer encrypted aggregation
5. Correctness result: 1,153,960 Wh decrypted == 1,153,960 Wh expected
6. Benchmark setup: workstation, 50 SGCC customers, 50 trials, Paillier/BFV/CKKS
7. Main latency table: encrypt/decrypt/add/multiply by scheme
8. Finding 1: Paillier is the classic PHE baseline but costly to encrypt/keygen
9. Finding 2: BFV fits exact integer aggregation
10. Finding 3: CKKS fits approximate real-valued analytics
11. Engineering fix: BFV batching modulus corrected
12. Updated research status against summer plan
13. Next steps: use SGCC `FLAG` labels for theft/anomaly scenarios, notebook,
    figures, Week 4 report
14. Mentor questions / decisions needed

For the main latency table, use a compact table with mean ms only. Include these
rows:
- Paillier PHE-2048: encrypt 128.05, decrypt 32.97, add 0.056, mul_plain 0.116
- Paillier PHE-3072: encrypt 397.08, decrypt 108.78, add 0.110, mul_plain 0.223
- BFV poly-4096: encrypt 0.90, decrypt 0.23, add 0.024, multiply 2.27
- BFV poly-8192: encrypt 2.34, decrypt 0.84, add 0.066, multiply 9.25
- BFV poly-16384: encrypt 7.40, decrypt 3.45, add 0.266, multiply 44.03
- CKKS balanced-8192: encrypt 2.68, decrypt 0.74, add 0.040, multiply 1.91
- CKKS high-depth-16384: encrypt 6.35, decrypt 2.13, add 0.098, multiply 5.92

Speaker notes:
- Add speaker notes to every new or modified slide.
- Notes should explain what I should say out loud in plain language.
- Keep slide bullets short; put details in notes.

Style:
- Use the same visual style as the previous deck if possible.
- Make the new result slides visually distinct but consistent.
- Use clear headings like "This Week's Result" and "What This Means".
- Do not overcrowd slides. Split tables if needed.
- Prefer one key takeaway per slide.

Final deliverable:
- Return an updated `.pptx`.
- Also summarize which slides were changed or added.
- If generating with python-pptx, provide the script too.
```
