# Prompt for "regular Claude" — add benchmark RESULTS to the deck

## Step 0 (you do this first, in the repo) — generate the results CSV
The `benchmarks/results/` folders are empty placeholders; numbers are generated
on demand and gitignored. Produce a CSV before running the prompt:

```bash
source .venv/bin/activate
python - <<'PY'
from benchmarks.runner import BenchmarkRunner
from src.classical.aes_baseline import benchmark_aes_baselines
from src.fhe.bfv_scheme import benchmark_bfv_schemes
from src.fhe.ckks_scheme import benchmark_ckks_schemes

runner = BenchmarkRunner(results_dir="benchmarks/results/workstation")
# All three write to the SAME csv so every row shares one schema. Small trials = quick first pass.
benchmark_aes_baselines(runner, trials=50, payload_sizes=(64, 256), key_sizes=(128,), export_path="results_all.csv")
benchmark_bfv_schemes(runner, trials=20, export_path="results_all.csv")
benchmark_ckks_schemes(runner, trials=20, export_path="results_all.csv")
PY
```

Then attach `benchmarks/results/workstation/results_all.csv` to Claude with the
prompt below.

---

```
You are adding a benchmark-RESULTS section to my existing SURF 2026 deck,
"Homomorphic Encryption for Smart-Grid Privacy." I am attaching a results CSV
from my benchmark harness. Build the results slides FROM THE DATA — do not
invent numbers; if the CSV is missing an operation or scheme, say so on the
slide instead of fabricating.

CSV SCHEMA (one row per measured operation):
  scheme, mode, key_size, payload_bytes, device, operation,
  mean_ms, median_ms, std_ms, p95_ms, timestamp
- scheme: e.g. AES, BFV, CKKS, (Paillier later)
- operation: encrypt, decrypt, add, multiply (HE), or encrypt/decrypt (AES)
- *_ms: latency in milliseconds; p95_ms is the tail
- device: the machine label all rows share
- payload_bytes / key_size: the sweep dimensions

DELIVERABLE
1. A short matplotlib script (saved as scripts/plot_results.py) that reads the
   CSV and writes PNGs to an images/ folder:
     a) Grouped bar chart: mean_ms per operation (x), bars grouped by scheme —
        log y-axis (HE is orders of magnitude slower than AES).
     b) Latency vs payload_bytes line chart for the encrypt operation, one line
        per scheme.
     c) A small "tail" chart: p95_ms vs mean_ms per scheme/operation (shows
        variance), OR error bars (std_ms) on chart (a).
   Use one color per scheme, readable fonts (>=12pt), titled axes, and a legend.
   Pull the device label from the CSV and put it in each figure caption.
2. New slides appended to the deck. Either (preferred) extend my existing
   python-pptx builder scripts/build_meeting_deck.py by adding the slides below
   before the "Next Two Weeks" slide, or generate a standalone results add-on
   .pptx I can merge. Keep the same dark theme (NAVY background, ACCENT cyan,
   WHITE text) and add speaker notes to every slide.

SLIDES TO ADD
A. "Benchmark Results — Setup": device/CPU/RAM label from the CSV, schemes and
   operations measured, trial count, payload sizes, and that latency is reported
   as mean / median / std / p95 (ms). One line on methodology: same
   BenchmarkRunner harness and CSV schema across all schemes.
B. "Per-Operation Latency": embed chart (a). 3-4 speaker-note bullets reading the
   actual numbers off the CSV (e.g. "BFV encrypt = X ms vs AES encrypt = Y ms,
   a Z-times gap").
C. "Cost of HE Operations": embed chart (b) and/or a results table of the key
   rows (scheme, operation, mean_ms, p95_ms). Highlight that multiply +
   relinearization dominate, and that approximate CKKS vs exact BFV trade off.
D. "What This Means for Meter Reading": interpret results against the use case —
   is per-meter encrypt latency acceptable for a meter sending one reading per
   15 min? Is aggregation latency reasonable at the cloud? Tie back to the
   communication-overhead point (ciphertext size) if the CSV has payload info.

RULES
- Read every number from the CSV; quote them in speaker notes so I can say them
  out loud. Round to sensible precision (e.g. 2-3 sig figs).
- If Paillier rows aren't in the CSV yet, add a placeholder bullet "Paillier
  baseline pending" rather than guessing.
- If a chart would be misleading on a linear axis (AES ~microseconds vs HE
  ~milliseconds), use a log scale and say so in the caption.
- Output: the matplotlib script, the updated build_meeting_deck.py (or add-on),
  and the regenerated .pptx.
```

---

## Notes for you (Joshua)
- I checked `benchmarks/results/` — only `.gitkeep` files, so there is **no data to
  chart yet**. Run Step 0 first; the wrapper names/imports are already correct for
  this repo (`benchmark_bfv_schemes`, `benchmark_ckks_schemes`,
  `benchmark_aes_baselines`). BFV/CKKS sweep `poly_degrees`/`configs` internally,
  so no payload-size arg is needed for them.
- The prompt forces Claude to read real numbers off the CSV and refuse to
  fabricate — important so your deck stays honest in front of Dr. Baza.
- It reuses your existing theme + `scripts/build_meeting_deck.py` so the results
  slides match the rest of the deck.
