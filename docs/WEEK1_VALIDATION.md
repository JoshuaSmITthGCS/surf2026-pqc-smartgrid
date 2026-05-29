# Week 1 Validation Notes

## Dataset Inspection

- Input file: `data/smart_grid_dataset.csv`
- Rows: 50,000
- Columns: 16
- Date range: 2024-01-01 00:00:00 to 2025-06-04 19:45:00
- Sampling interval: 15 minutes
- Missing values: 0
- Duplicate timestamps: 0
- Overload rows: 4,956
- Transformer fault rows: 1,460

Selected observed ranges:

| Field | Mean | Min | Max |
| --- | ---: | ---: | ---: |
| Voltage (V) | 229.997896 | 207.671981 | 252.395421 |
| Current (A) | 27.482627 | 5.001239 | 49.999642 |
| Power Consumption (kW) | 6.320811 | 1.089178 | 12.103199 |
| Power Factor | 0.899997 | 0.800001 | 0.999997 |
| Grid Supply (kW) | 0.047198 | 0.000000 | 10.766046 |
| Electricity Price (USD/kWh) | 0.299095 | 0.100002 | 0.499996 |
| Predicted Load (kW) | 6.320693 | 1.043487 | 12.483253 |

## Week 1 Smoke Path

The Week 1 validation path uses the real dataset through
`src.smartgrid.workloads`. RSA was included as an early environment and
encryption sanity check, but it is not the recommended Phase 1 research
baseline against homomorphic encryption.

1. Load and validate the telemetry CSV.
2. Summarize timestamp coverage and data quality.
3. Build exact-size byte payloads from compact JSON telemetry rows.
4. Run early AES and RSA checks through `BenchmarkRunner`.
5. Export generated benchmark result CSV files under
   `benchmarks/results/workstation/`.

For the Phase 1 research comparison, use AES-GCM as the single classical
encryption baseline and compare it against BFV and CKKS homomorphic encryption
workloads.

Reusable command:

```bash
python scripts/week1_smoke_test.py
```
