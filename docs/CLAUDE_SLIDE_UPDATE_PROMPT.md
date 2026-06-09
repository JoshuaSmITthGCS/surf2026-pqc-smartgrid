# Prompt for Claude: Update Previous Slides With This Week's Results

Copy the fenced prompt below into Claude. Attach the previous PowerPoint deck
that was already made. If Claude cannot read the repo directly, also attach:

- `benchmarks/results/workstation/he_comparison_paillier.csv`
- `benchmarks/results/workstation/he_comparison_bfv.csv`
- `benchmarks/results/workstation/he_comparison_ckks.csv`
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
1. The project is now connected to a true multi-household smart-meter dataset:
   Smart Meters in London / Low Carbon London.
2. The dataset is local at:
   `data/smart-meters-in-london/`
3. The benchmark CLI ran successfully on a real 50-meter aggregation slice:
   `python scripts/setup_and_run.py --skip-pull --skip-download --meters 50 --blocks 0,1 --row 15055 --trials 50`
4. Dataset slice:
   - Blocks: 0 and 1
   - Matrix size: 50 meters x 39,247 timesteps
   - Time range: 2011-12-03 09:00:00 to 2014-02-28 00:00:00
   - Row used: 15055
   - Live meters at that row: 50
   - Aggregate cleartext total: 12.511 kWh
5. Correctness check passed:
   - Encrypted aggregation with Paillier decrypted to 12,511 Wh
   - Expected plaintext total was 12,511 Wh
   - Result: OK across 50 meters
6. Result CSVs were exported under:
   `benchmarks/results/workstation/`

Dataset correction for the old slide deck:
- The previous slide set had the dataset story wrong or incomplete. Fix that
  directly in the updated deck.
- The main dataset is NOT ETT transformer telemetry anymore, and it is NOT a
  generic customer-behavior / social-ads dataset.
- The main dataset is Smart Meters in London / Low Carbon London, which contains
  household-level electricity smart-meter readings.
- The local dataset includes:
  - `informations_households.csv`
  - `halfhourly_dataset/.../block_0.csv` through `block_111.csv`
  - `hhblock_dataset/.../block_0.csv` through `block_111.csv`
  - `daily_dataset/.../block_0.csv` through `block_111.csv`
  - weather, holiday, and ACORN demographic context files
- Household metadata:
  - 5,566 household rows
  - columns: `LCLid`, `stdorToU`, `Acorn`, `Acorn_grouped`, `file`
  - tariff split in this local copy: 4,443 standard tariff and 1,123
    time-of-use tariff households
- Half-hourly meter readings:
  - columns: `LCLid`, `tstp`, `energy(kWh/hh)`
  - `LCLid` is the household/meter identifier
  - `tstp` is the timestamp
  - `energy(kWh/hh)` is the electricity consumption reading in kWh per
    half-hour interval
- What the HE input means:
  - one timestamp row becomes a vector of many household meter readings
  - for Paillier and BFV, readings are scaled from kWh to Wh integers
  - for CKKS, readings can be treated as real-valued kWh inputs for approximate
    analytics
- Say plainly that ETT can still be mentioned as earlier background data for
  transformer/load forecasting, but it should not be presented as the main
  multi-household aggregation dataset.

Important implementation note:
- BFV needed a batching-parameter fix. The default BFV plain modulus was changed
  from `1032193` to `1146881` because batching requires
  `plain_modulus == 1 mod 2 * poly_modulus_degree`.
- `1146881 = 35 * 32768 + 1`, so it supports the default BFV degrees:
  4096, 8192, and 16384.
- Mention this as a small engineering fix, not as a major research result.

Use the latest full run only:
- The latest full run has `payload_bytes = 400`, which corresponds to 50 meter
  readings x 8 bytes.
- Ignore earlier smoke-test rows with `payload_bytes = 8` unless you mention
  them as a preliminary smoke test.

Key benchmark results from the latest full run:

Paillier baseline:
- PHE-2048:
  - keygen mean: 625.97 ms
  - encrypt mean: 136.99 ms
  - decrypt mean: 38.04 ms
  - homomorphic add mean: 0.059 ms
  - multiply by plaintext mean: 0.127 ms
- PHE-3072:
  - keygen mean: 2934.86 ms
  - encrypt mean: 439.92 ms
  - decrypt mean: 145.36 ms
  - homomorphic add mean: 0.690 ms
  - multiply by plaintext mean: 0.945 ms

BFV:
- poly-4096:
  - encrypt mean: 1.46 ms
  - decrypt mean: 0.24 ms
  - add mean: 0.026 ms
  - multiply mean: 2.24 ms
- poly-8192:
  - encrypt mean: 2.95 ms
  - decrypt mean: 0.96 ms
  - add mean: 0.068 ms
  - multiply mean: 9.85 ms
- poly-16384:
  - encrypt mean: 8.19 ms
  - decrypt mean: 3.16 ms
  - add mean: 0.288 ms
  - multiply mean: 49.85 ms

CKKS:
- balanced-8192:
  - encrypt mean: 3.41 ms
  - decrypt mean: 0.85 ms
  - add mean: 0.071 ms
  - multiply mean: 2.15 ms
- high-depth-16384:
  - encrypt mean: 6.89 ms
  - decrypt mean: 2.11 ms
  - add mean: 0.102 ms
  - multiply mean: 5.81 ms

Headline findings to include:
1. The project moved from simulated or single-source telemetry toward a real
   multi-household smart-meter workload.
2. The 50-meter encrypted aggregation path works end to end.
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
7. The next research step is to turn this into scenario-level smart-grid
   workloads and add analysis figures.

Required deck update:
- Keep the old deck's title, motivation, trust model, and scheme background if
  they are still accurate.
- Update any slide with the old or incorrect dataset story. Replace it with the
  corrected Smart Meters in London description above: 5,566 households, 112
  half-hourly block files, columns `LCLid`, `tstp`, and `energy(kWh/hh)`, and a
  50-meter same-timestamp aggregation vector for this week's run.
- Keep a short note that earlier ETT datasets are still useful for
  transformer/load forecasting context, but they are no longer the main
  aggregation dataset.
- Keep the baseline correction: Paillier is the HE baseline, not RSA. AES/RSA
  should be context only, not the main head-to-head baseline.

Suggested slide structure:
1. Title / project status
2. Previous motivation recap: why HE for smart-grid privacy
3. Updated dataset status: Smart Meters in London integrated
4. Workload this week: 50-meter encrypted aggregation
5. Correctness result: 12,511 Wh decrypted == 12,511 Wh expected
6. Benchmark setup: workstation, 50 meters, 50 trials, Paillier/BFV/CKKS
7. Main latency table: encrypt/decrypt/add/multiply by scheme
8. Finding 1: Paillier is the classic PHE baseline but costly to encrypt/keygen
9. Finding 2: BFV fits exact integer aggregation
10. Finding 3: CKKS fits approximate real-valued analytics
11. Engineering fix: BFV batching modulus corrected
12. Updated research status against summer plan
13. Next steps: scenario module, notebook, figures, Week 4 report
14. Mentor questions / decisions needed

For the main latency table, use a compact table with mean ms only. Include these
rows:
- Paillier PHE-2048: encrypt 136.99, decrypt 38.04, add 0.059, mul_plain 0.127
- Paillier PHE-3072: encrypt 439.92, decrypt 145.36, add 0.690, mul_plain 0.945
- BFV poly-4096: encrypt 1.46, decrypt 0.24, add 0.026, multiply 2.24
- BFV poly-8192: encrypt 2.95, decrypt 0.96, add 0.068, multiply 9.85
- BFV poly-16384: encrypt 8.19, decrypt 3.16, add 0.288, multiply 49.85
- CKKS balanced-8192: encrypt 3.41, decrypt 0.85, add 0.071, multiply 2.15
- CKKS high-depth-16384: encrypt 6.89, decrypt 2.11, add 0.102, multiply 5.81

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
