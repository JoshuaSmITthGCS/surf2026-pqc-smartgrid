# Prompt for "regular Claude" — build the meeting PPTX

Copy everything inside the fenced block below into Claude (claude.ai).
**Also attach these files** when you paste it:
- `HE_SmartGrid_Background_Deck.pdf` (the existing deck)
- `ETTh1.csv`, `ETTh2.csv`, `ETTm1.csv`
- `Customer_Behaviour.csv`

---

```
You are helping me prepare a PowerPoint (.pptx) for a research meeting TOMORROW
with my mentor, Dr. Mohamed Baza, for a SURF 2026 project at the College of
Charleston titled "Homomorphic Encryption (HE) for Smart-Grid Privacy."

DELIVERABLE
Produce a polished, presenter-ready .pptx file (use python-pptx; give me the
code AND the generated file). 14–18 slides, clean and readable, dark or
professional theme, one idea per slide, short bullets, and SPEAKER NOTES on
every content slide that I can read out loud. Title slide should credit:
Researcher: Joshua Smith · Mentor: Dr. Mohamed Baza · SURF 2026, College of
Charleston · Target venue: IEEE SmartGridComm / CNS.

CONTEXT — WHAT EXISTS ALREADY (from the attached background deck and repo)
- Goal: benchmark HE schemes for privacy-preserving computation on smart-grid
  telemetry.
- Three RLWE schemes are in scope: BFV (exact integers, TenSEAL), CKKS
  (approximate reals, TenSEAL), BGV (exact integers, leveled, needs Microsoft
  SEAL binding).
- Current pairings in the old deck: demand aggregation -> BFV; anomaly
  detection -> CKKS.
- Harness: a shared BenchmarkRunner with a fixed CSV schema; payloads derived
  from real telemetry; metrics = per-operation latency (mean/median/std/p95).
- The OLD deck used AES-GCM as the classical baseline and RSA as reference.
  IMPORTANT CHANGE BELOW.

THIS MEETING MUST DIRECTLY ANSWER MY MENTOR'S QUESTIONS. Build the deck around
these six points and make each its own slide (or two):

1) DEMAND RESPONSE + HE — how and why is HE useful here?
   - Demand response (DR) = the utility/aggregator sends signals so customers
     shift or curtail load at peak times, and must compute aggregate available
     flexibility, total load reduction achieved, and per-customer incentives.
   - Why HE: the aggregator can compute the AGGREGATE response (sum of curtailed
     kW across many homes), check it against a target, forecast load, and settle
     incentive payments WITHOUT seeing any individual household's consumption or
     which appliances were curtailed (that data leaks occupancy/behavior).
   - HE enables: encrypted summation of per-home reductions, encrypted weighted
     aggregation, encrypted comparison to a target/threshold, and fair
     incentive/settlement computation on encrypted contributions.
   - DR is a MULTI-STEP pipeline (baseline -> deviation -> incentive ->
     settlement), so it needs multiplicative depth: this is the strongest motive
     for a LEVELED scheme (BGV/BFV), with CKKS for real-valued forecasting.
   - Value isn't only privacy: it enables third-party/cloud aggregators,
     regulatory compliance (GDPR/CCPA), customer trust, and verifiable fair
     settlement.

2) METER READING + HE — why useful? privacy only? what is the INPUT DATA?
   - Smart-meter reads (kWh per interval) are sent to the utility for billing and
     grid operations. Fine-grained reads reveal occupancy, appliances, behavior.
   - HE is useful for MORE than privacy:
       (a) privacy of fine-grained consumption,
       (b) aggregation for grid load-balancing WITHOUT a trusted aggregator,
       (c) safe OUTSOURCING of storage/compute to an untrusted cloud,
       (d) time-of-use / tariff billing computed over encrypted reads,
       (e) reduced utility liability — it never holds raw data,
       (f) verifiable aggregation.
   - INPUT DATA for the HE technique = per-meter consumption readings per time
     interval. In the attached ETT datasets, treat the load columns
     (HUFL/HULL/MUFL/MULL/LUFL/LULL) as the meter "readings," and OT (oil
     temperature) as a feature for the anomaly use case. Encode integers
     (scaled kWh, e.g. Wh as ints) for BFV/BGV; encode real values directly for
     CKKS. State the encoding explicitly on the slide.

3) WHAT METRICS COMPARE THE HE TECHNIQUES, AND WHO IMPLEMENTS WHAT?
   - Computation time: key generation, encrypt, decrypt, homomorphic add,
     homomorphic multiply, relinearization/rescale, AND end-to-end aggregation
     latency vs number of meters.
   - Communication overhead: ciphertext size and ciphertext EXPANSION RATIO
     (bytes transmitted per reading), key sizes (public key, relin keys, Galois
     keys), and total bytes per aggregation round.
   - Also: memory/storage footprint; supported multiplicative depth / noise
     budget; accuracy/error (for CKKS approximate vs plaintext); scalability vs
     poly_modulus_degree and vs meter count.
   - WHO IMPLEMENTS (trust model slide):
       * Smart meter (resource-constrained): runs ENCRYPTION and transmits
         ciphertext under a shared/utility public key. Its compute budget is
         tight, so encryption cost and ciphertext size matter most here.
       * Utility / cloud / aggregator (untrusted for raw data): performs the
         HOMOMORPHIC computation (sum/average/statistics) on ciphertext.
       * Key holder (utility or a separate authority): performs DECRYPTION of the
         final aggregate only.
     Make a simple diagram: Meters --(encrypt)--> Aggregator/Cloud
     --(homomorphic compute)--> Utility/key-holder --(decrypt aggregate)-->.

4) WHICH APPLICATION TO IMPLEMENT FIRST?
   - Recommendation: START WITH METER READING / DEMAND AGGREGATION using BFV
     (exact integer summation), because (a) it is the simplest correct circuit
     (additions only, low depth), (b) BFV is already running in TenSEAL, and
     (c) it gives a clean first benchmark milestone. Then add CKKS for encrypted
     averages/statistics, and BGV later for the deeper demand-response pipeline.
   - Put a concrete next-two-weeks plan on a slide.

5) BASELINE MUST BE ANOTHER HE TECHNIQUE, NOT RSA.
   - Per mentor feedback, the head-to-head baseline should be an HE scheme, not
     RSA and not framed around AES.
   - Use PAILLIER (additively homomorphic / partially homomorphic encryption) as
     the baseline for the encrypted-aggregation / meter-reading use case — it is
     the classic prior-generation smart-metering HE baseline (cf. Erkin &
     Tsudik, ACNS 2012). Compare Paillier (PHE) against the RLWE schemes
     BFV / BGV / CKKS on the metrics above.
   - Also include intra-RLWE comparisons (BFV vs BGV vs CKKS).
   - Demote AES-GCM/RSA to a one-line "context only" mention; do NOT present them
     as the comparison baseline.

6) DATASETS — be honest and show a clear status.
   - ETTh1 & ETTh2 (hourly) and ETTm1 (15-min) are real "Electricity Transformer
     Temperature" datasets: 6 load features + oil temperature, single
     transformer. Good for load-aggregation and transformer-anomaly framing, but
     it is ONE transformer, not many households — so multi-meter aggregation has
     to be SIMULATED (e.g., treat columns / time-windows / resampled segments as
     separate meters). Say this plainly.
   - Customer_Behaviour.csv is actually the well-known "Social Network Ads"
     dataset (User ID, Gender, Age, EstimatedSalary, Purchased). It is NOT
     smart-grid telemetry. Flag this as mislabeled; at most it could serve as a
     toy encrypted-classification demo, not as grid data.
   - ACTION ITEMS slide: keep searching for a true multi-HOUSEHOLD smart-meter
     dataset. Candidates to name: UMass Smart*, Pecan Street/Dataport, UK-DALE,
     CER Irish Smart Metering, Low Carbon London. And: follow up by emailing
     bluhmja@g.cofc.edu, and ask "adawa" for Adam's email to request a dataset.

SLIDE OUTLINE (adapt as needed)
1. Title
2. Agenda / what this meeting answers (list the 6 questions)
3. Recap: why HE for smart grids (1 slide)
4. Use case A — Meter reading: why HE, beyond privacy, + input data
5. Use case B — Demand response: how & why HE, multi-step pipeline
6. The actors & trust model (meter vs aggregator vs key-holder) + data-flow diagram
7. Evaluation metrics: computation time
8. Evaluation metrics: communication overhead (+ ciphertext expansion)
9. Who implements what (responsibilities mapped to the metrics)
10. Baseline change: Paillier (PHE) as the HE baseline, not RSA — why
11. Scheme comparison table: Paillier vs BFV vs CKKS vs BGV (data type, exact vs
    approx, noise mgmt, additive vs leveled, library, best-fit use case)
12. Where I start: BFV meter-reading/aggregation first — rationale
13. Datasets: what we have (ETT) + honest gaps + Customer_Behaviour caveat
14. Dataset action items (search + email bluhmja@g.cofc.edu + ask for Adam)
15. Two-week plan / milestones
16. Open questions for the mentor

STYLE
- Concise bullets (max ~6 per slide, short phrases not sentences).
- Put the detailed explanations in the SPEAKER NOTES so the slides stay clean.
- Include the comparison table as a real PowerPoint table.
- Keep claims accurate: BGV needs Microsoft SEAL (TenSEAL lacks BGV); CKKS is
  approximate; don't overclaim. No quantum-attack claims in this deck.
- End with 3–5 concrete questions to ask the mentor.

Now generate the python-pptx code and the .pptx file.
```

---

## Why this prompt is shaped this way (for your own reference)

It forces regular Claude to answer **all six** mentor questions explicitly, fixes
the **baseline** to Paillier (an HE scheme, per her feedback — not RSA/AES),
gives the **honest dataset story** (ETT is real but single-transformer;
Customer_Behaviour is mislabeled), and recommends **BFV meter-reading/aggregation
as the first implementation**. It also bakes in the trust model (who encrypts vs
who computes vs who decrypts) and a full metrics list (compute time +
communication/ciphertext-expansion).
