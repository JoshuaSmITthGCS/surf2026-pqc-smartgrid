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
  `python scripts/run_he_baseline_comparison.py --dataset sgcc --sgcc-path "archive (2)" --meters 50 --row 944 --trials 50`
- SGCC result:
  - 50 customers x 1,034 daily readings
  - date: 2016-08-02
  - cleartext total: 1,153.960 kWh
  - encrypted aggregation check: 1,153,960 Wh decrypted == 1,153,960 Wh expected
  - status: OK across 50 customers
- df.csv command:
  `python scripts/run_he_baseline_comparison.py --dataset df --df-path df.csv --row 0 --trials 50`
- df.csv result:
  - 6 electricity features x 560,655 rows
  - row 0 feature-vector total: 38.401
  - encrypted aggregation check: 38,401 Wh decrypted == 38,401 Wh expected
  - status: OK across 6 features

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
