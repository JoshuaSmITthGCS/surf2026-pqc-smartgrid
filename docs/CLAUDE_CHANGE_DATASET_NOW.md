# Claude Prompt: Change The Dataset Story Now

Copy the block below into Claude when you want it to update the existing
PowerPoint deck's dataset slides without reworking the whole deck.

```text
Update my existing SURF 2026 smart-grid homomorphic-encryption slide deck so the
dataset information is current and correct.

Do not keep the old dataset story. Replace it with this:

CURRENT MAIN DATASET
- The current main dataset is the SGCC electricity-theft detection archive from
  State Grid Corporation of China.
- Local file: `archive (2)/data.csv`
- Source paper: "Wide and Deep Convolutional Neural Networks for
  Electricity-Theft Detection to Secure Smart Grids"
- It contains 42,372 electricity customers.
- The README describes 1,035 days from 2014-01-01 to 2016-10-31; this local CSV
  exposes 1,034 dated reading columns.
- Columns:
  - `CONS_NO` = customer ID
  - `FLAG` = theft label
  - date columns = daily electricity consumption readings
- Label counts in this local copy:
  - 38,757 normal customers
  - 3,615 theft-flagged customers

SECONDARY / DERIVED DATASET
- The current secondary derived dataframe is `df.csv`.
- It has 560,655 rows.
- For the current HE benchmark, it uses these electricity feature columns:
  - `Electricity:Facility [kW](Hourly)`
  - `Fans:Electricity [kW](Hourly)`
  - `Cooling:Electricity [kW](Hourly)`
  - `Heating:Electricity [kW](Hourly)`
  - `InteriorLights:Electricity [kW](Hourly)`
  - `InteriorEquipment:Electricity [kW](Hourly)`
- It also includes class/theft labels, but the current HE benchmark uses the
  numeric electricity feature vector, not the labels.

WHAT TO REMOVE OR DEMOTE
- Do not present ETT transformer telemetry as the current main dataset.
- Do not present Customer_Behaviour / Social Network Ads as smart-grid telemetry.
- Smart Meters in London can be mentioned only as previous validation work, not
  the current mentor-requested dataset.

HOW THE HE INPUT IS FORMED
- SGCC: one date row becomes a vector of customer daily consumption readings.
- `df.csv`: one dataframe row becomes a compact electricity feature vector.
- Paillier and BFV use scaled integer values.
- CKKS uses real-valued approximate analytics inputs.

LATEST RUNS TO REPORT
- SGCC command:
  `python scripts/run_he_baseline_comparison.py --dataset sgcc --sgcc-path "archive (2)" --meters 50 --row 944 --trials 50 --output-tag sgcc_latest`
- SGCC result:
  - 50 customers x 1,034 daily readings
  - date: 2016-08-02
  - cleartext total: 1,153.960 kWh
  - encrypted aggregation check: 1,153,960 Wh decrypted == 1,153,960 Wh expected
  - status: OK across 50 customers
- df.csv command:
  `python scripts/run_he_baseline_comparison.py --dataset df --df-path df.csv --row 0 --trials 50 --output-tag df_latest`
- df.csv result:
  - 6 electricity features x 560,655 rows
  - row 0 feature-vector total: 38.401
  - encrypted aggregation check: 38,401 Wh decrypted == 38,401 Wh expected
  - status: OK across 6 features

PASTEABLE HE BENCHMARK RESULTS
Use this exact block in the slides or speaker notes.

SGCC rerun summary:
- Dataset: SGCC electricity-theft archive (`archive (2)/data.csv`)
- Slice: 50 customers, row 944, date 2016-08-02
- Input vector: 50 daily customer electricity readings
- Cleartext aggregate: 1,153.960 kWh
- Encrypted aggregation check: 1,153,960 Wh decrypted == 1,153,960 Wh expected
- Status: OK across 50 customers
- Trials: 50 per operation
- Result CSVs:
  - `benchmarks/results/workstation/he_comparison_sgcc_latest_paillier.csv`
  - `benchmarks/results/workstation/he_comparison_sgcc_latest_bfv.csv`
  - `benchmarks/results/workstation/he_comparison_sgcc_latest_ckks.csv`

SGCC latency results, mean ms and p95 ms:

| Scheme | Mode | Operation | Payload bytes | Mean ms | P95 ms |
|---|---|---:|---:|---:|---:|
| Paillier | PHE-2048 | keygen | 8 | 1511.662 | 3192.929 |
| Paillier | PHE-2048 | encrypt | 8 | 125.842 | 131.191 |
| Paillier | PHE-2048 | decrypt | 8 | 33.223 | 35.077 |
| Paillier | PHE-2048 | add | 8 | 0.057 | 0.064 |
| Paillier | PHE-2048 | mul_plain | 8 | 0.112 | 0.130 |
| Paillier | PHE-3072 | keygen | 8 | 4321.254 | 7814.305 |
| Paillier | PHE-3072 | encrypt | 8 | 389.610 | 406.008 |
| Paillier | PHE-3072 | decrypt | 8 | 108.438 | 114.158 |
| Paillier | PHE-3072 | add | 8 | 0.128 | 0.138 |
| Paillier | PHE-3072 | mul_plain | 8 | 0.225 | 0.247 |
| BFV | poly-4096 | encrypt | 400 | 0.824 | 0.956 |
| BFV | poly-4096 | decrypt | 400 | 0.201 | 0.218 |
| BFV | poly-4096 | add | 400 | 0.022 | 0.024 |
| BFV | poly-4096 | multiply | 400 | 2.243 | 2.375 |
| BFV | poly-8192 | encrypt | 400 | 2.168 | 2.372 |
| BFV | poly-8192 | decrypt | 400 | 0.717 | 0.824 |
| BFV | poly-8192 | add | 400 | 0.070 | 0.108 |
| BFV | poly-8192 | multiply | 400 | 9.045 | 9.414 |
| BFV | poly-16384 | encrypt | 400 | 7.724 | 10.574 |
| BFV | poly-16384 | decrypt | 400 | 3.101 | 3.728 |
| BFV | poly-16384 | add | 400 | 0.304 | 0.464 |
| BFV | poly-16384 | multiply | 400 | 44.963 | 47.675 |
| CKKS | balanced-8192 | encrypt | 400 | 2.568 | 2.756 |
| CKKS | balanced-8192 | decrypt | 400 | 0.709 | 0.795 |
| CKKS | balanced-8192 | add | 400 | 0.036 | 0.040 |
| CKKS | balanced-8192 | multiply | 400 | 1.956 | 2.399 |
| CKKS | high-depth-16384 | encrypt | 400 | 6.215 | 6.478 |
| CKKS | high-depth-16384 | decrypt | 400 | 2.094 | 2.249 |
| CKKS | high-depth-16384 | add | 400 | 0.110 | 0.160 |
| CKKS | high-depth-16384 | multiply | 400 | 6.383 | 7.568 |

df.csv rerun summary:
- Dataset: derived `df.csv`
- Slice: row 0, 6 electricity feature columns
- Input vector: 6 hourly electricity features
- Feature-vector total: 38.401
- Encrypted aggregation check: 38,401 Wh decrypted == 38,401 Wh expected
- Status: OK across 6 features
- Trials: 50 per operation
- Result CSVs:
  - `benchmarks/results/workstation/he_comparison_df_latest_paillier.csv`
  - `benchmarks/results/workstation/he_comparison_df_latest_bfv.csv`
  - `benchmarks/results/workstation/he_comparison_df_latest_ckks.csv`

df.csv latency results, mean ms and p95 ms:

| Scheme | Mode | Operation | Payload bytes | Mean ms | P95 ms |
|---|---|---:|---:|---:|---:|
| Paillier | PHE-2048 | keygen | 8 | 1856.422 | 3637.890 |
| Paillier | PHE-2048 | encrypt | 8 | 123.702 | 125.702 |
| Paillier | PHE-2048 | decrypt | 8 | 33.152 | 33.710 |
| Paillier | PHE-2048 | add | 8 | 0.055 | 0.056 |
| Paillier | PHE-2048 | mul_plain | 8 | 0.108 | 0.126 |
| Paillier | PHE-3072 | keygen | 8 | 1884.925 | 2345.783 |
| Paillier | PHE-3072 | encrypt | 8 | 451.847 | 722.864 |
| Paillier | PHE-3072 | decrypt | 8 | 116.604 | 163.277 |
| Paillier | PHE-3072 | add | 8 | 0.117 | 0.119 |
| Paillier | PHE-3072 | mul_plain | 8 | 0.224 | 0.248 |
| BFV | poly-4096 | encrypt | 48 | 0.972 | 1.519 |
| BFV | poly-4096 | decrypt | 48 | 0.235 | 0.445 |
| BFV | poly-4096 | add | 48 | 0.029 | 0.057 |
| BFV | poly-4096 | multiply | 48 | 2.375 | 2.684 |
| BFV | poly-8192 | encrypt | 48 | 2.190 | 2.364 |
| BFV | poly-8192 | decrypt | 48 | 0.750 | 0.856 |
| BFV | poly-8192 | add | 48 | 0.066 | 0.070 |
| BFV | poly-8192 | multiply | 48 | 9.279 | 9.735 |
| BFV | poly-16384 | encrypt | 48 | 6.959 | 7.688 |
| BFV | poly-16384 | decrypt | 48 | 2.938 | 3.446 |
| BFV | poly-16384 | add | 48 | 0.304 | 0.342 |
| BFV | poly-16384 | multiply | 48 | 44.148 | 48.860 |
| CKKS | balanced-8192 | encrypt | 48 | 2.646 | 3.121 |
| CKKS | balanced-8192 | decrypt | 48 | 0.720 | 0.828 |
| CKKS | balanced-8192 | add | 48 | 0.040 | 0.042 |
| CKKS | balanced-8192 | multiply | 48 | 1.906 | 2.233 |
| CKKS | high-depth-16384 | encrypt | 48 | 6.320 | 6.705 |
| CKKS | high-depth-16384 | decrypt | 48 | 2.079 | 2.242 |
| CKKS | high-depth-16384 | add | 48 | 0.101 | 0.125 |
| CKKS | high-depth-16384 | multiply | 48 | 5.864 | 6.461 |

Short slide takeaway:
- Both reruns passed the encrypted aggregation correctness check.
- Paillier remains the classic additive HE baseline, but its encryption and
  key-generation costs are far higher than BFV/CKKS.
- BFV gives exact integer aggregation and very fast homomorphic addition.
- CKKS is best for approximate real-valued electricity analytics.
- Multiplication remains the expensive operation, especially for BFV at larger
  polynomial degrees.

SLIDE CHANGES TO MAKE
1. Replace the old dataset slide with a new slide titled:
   "Current Dataset: SGCC Electricity-Theft Archive"
2. Add a small secondary-data note for `df.csv`.
3. Add one slide or callout explaining how a row becomes an HE input vector.
4. Update result slides to say the latest run used SGCC, not the older dataset.
5. Keep the old HE motivation, trust model, and Paillier/BFV/CKKS comparison if
   those slides are still accurate.

Do not overclaim. Be clear that:
- SGCC is the main current smart-grid dataset.
- `df.csv` is a derived feature-vector workload.
- Smart Meters in London was useful earlier, but it is no longer the current
  dataset for this slide update.
```
