# BUILD.md: Fill the LS-STAR template in PowerPoint Online

Instructions for Claude in the browser. Edit the **already-open** copy of
"Student Template - Copy.pptx" in PowerPoint for the web. Do not create a new
file, do not touch the original template, and do not share or publish anything.

The audience is technical. The full spoken script is in `TALK_SCRIPT.md`; the
Speaker notes below are the short versions for each slide's Notes pane.

## Ground rules

1. Keep the template's own theme, fonts, colors, and layouts. Reuse its layouts
   (Title, Title and Content, Two Content, Section, Title Only) instead of
   drawing new frames. Delete template slides and sample text you do not use.
2. Target **10 slides** (about 12 minutes, 1 to 2 minutes of Q&A after).
3. One message per slide. Slide text stays short: titles about 40 characters or
   fewer, body text 18 pt or larger, captions 12 pt or larger.
4. Put the "Speaker notes" blocks below into each slide's Notes pane, not on the
   slide.
5. **Do not invent or round any number.** Use only the numbers written here.
   Anything in `[BRACKETS]` is for Joshua to confirm, so leave it highlighted
   and tell him at the end.
6. **Do not claim BFV or CKKS passed the 50-customer sum check.** That check ran
   through Paillier only (see slide 4).
7. If an instruction cannot be done in PowerPoint for the web, use the fallback
   given, and list what you changed at the end.

## Facts you may use (all measured or computed from the project repo)

Headline timings come from `he_comparison_sgcc_latest_*.csv` (50 trials). The
repeat check comes from `he_comparison_sgcc_sweep_*.csv` (50 to 300 trials).

| Item | Value |
|---|---|
| Presenter | Joshua Smith, College of Charleston, Computer Science, Honors College |
| Program | SURF 2026, Mentor Dr. Mohamed Baza |
| Event | 2026 LS-STAR Research Banquet, Wed 10/14, RITA 101 |
| Working title | `[Computing on Encrypted Smart-Grid Data]` (Joshua to confirm with Dr. Vulava) |
| Dataset | SGCC electricity-theft data, 42,372 customers (38,757 normal, 3,615 theft-flagged), daily readings 2014-01-01 to 2016-10-31 |
| Aggregation slice | 50 customers, date 2016-08-02, total 1,153,960 Wh |
| Sum check scope | Paillier-2048 only: decrypted total equals the plaintext total |
| Encrypt, Paillier-2048 | 125.8 ms |
| Encrypt, BFV (degree 8192) | 2.2 ms |
| Encrypt, CKKS (degree 8192) | 2.6 ms |
| Decrypt, Paillier-2048 | 33.2 ms |
| Decrypt, BFV / CKKS (8192) | 0.72 ms / 0.71 ms |
| Speedup, BFV vs Paillier | 58x encrypt, 46x decrypt |
| Repeat at 300 trials | Paillier 125.7 ms, BFV 2.2 ms, ratio about 57x encrypt |
| Noisy runs | 300-trial Paillier decrypt mean 40 ms (p95 67 ms); one 250-trial Paillier encrypt run at 177 ms (std 84) |
| Encrypt, Paillier-3072 | 389.6 ms |
| Encrypt, BFV (degree 16384) | 7.7 ms |
| Multiply | BFV 2.2 ms (4096), 9.0 ms (8192), 45.0 ms (16384); CKKS balanced-8192 2.0 ms; Paillier cannot multiply ciphertexts |
| Add | Paillier 0.057 ms, BFV (8192) 0.070 ms, CKKS (8192) 0.036 ms |
| Paillier, 50 readings | about 6.3 s (50 x 125.8 ms, computed, not separately measured) |
| BFV, 50 readings | 2.2 ms in one batched ciphertext (400-byte payload; 8,192 slots available, 50 used) |
| Day projection (288 encrypts) | Paillier-2048 about 36 s; BFV-8192 about 0.64 s for 288 payloads of 50 readings. Projection from the 300-trial means, not a measurement |
| Parameters | Paillier n = 2048 bits (about 112-bit classical). BFV degree 8192, plaintext modulus 1,146,881, SEAL default coefficient modulus. CKKS degree 8192, coeff bits 60/40/40/60, scale 2^40 |
| Known BFV issue | Plaintext modulus 1,146,881 is below the 1,153,960 total, so the full sum would wrap. Needs a larger modulus or new scaling |
| Stack | Paillier: Python `phe` 1.5.0. BFV and CKKS: TenSEAL 0.3.16 (C++ SEAL). `gmpy2` is not in requirements.txt `[Joshua to confirm whether it is installed]` |
| Hardware / trials | Apple-silicon MacBook Pro, 16 GB RAM, 10 logical cores; 50 trials headline, repeats at 100 to 300 |
| Shor attack target | Real `phe` Paillier key, n = 667 = 23 x 29 (10-bit) |
| Shor attack method | Qiskit Aer simulator, 10 work + 10 counting qubits (20 total), 2,048 shots |
| Shor attack outcome | Measured order 308, factors 23 and 29, circuit depth 31, 155 s |
| Decryption check | Key rebuilt from factors decrypted the ciphertext to 136; owner's decryption was 136 |
| Earlier run | 8-bit key n = 187, 62 s |
| Success rate | Not measured; worked on the first base in both runs |
| Real-key estimate | 2048-bit modulus needs about 4,099 logical qubits (2n+3 textbook heuristic) |
| Published estimates | Gidney 2025, arXiv:2505.15917, under 1 million noisy qubits, under a week; Gidney and Ekera 2021, Quantum 5, 433, about 20 million noisy qubits `[Joshua to verify both before presenting]` |

## Slides

### Slide 1: Title (Title layout)
- Title: `[Computing on Encrypted Smart-Grid Data]`
- Subtitle: Benchmarking Paillier, BFV and CKKS, and testing the quantum threat with a real Shor attack
- Name line: Joshua Smith | College of Charleston | Computer Science | Honors College
- Second line: SURF 2026 | Mentor: Dr. Mohamed Baza
- Small tag: 2026 LS-STAR Research Banquet
- Notes: About 50 seconds. Thank Dr. Vulava and LS-STAR, name Dr. Baza. Three questions: does homomorphic aggregation work on smart-meter data, is it worth it against a homomorphic baseline, can it run on meter-class hardware. I answer the first two and say where the third stands.

### Slide 2: "Private readings, useful totals" (Title Only + 3 shapes)
- Draw three rounded boxes left to right joined by arrows:
  1. Smart meters: Encrypt each reading under a public key
  2. Aggregator: Adds ciphertexts, sees no readings
  3. Utility: Holds the secret key, decrypts only the total
- Below, three bullets:
  - Readings reveal when people are home, asleep, or away
  - Threat model: honest-but-curious aggregator
  - Out of scope: malicious aggregator, sum integrity, utility-aggregator collusion
- Notes: About 1.5 minutes. The utility needs sums and averages, and individual readings leak household behavior. Obscurity fails once data is copied and logged. The design works only if the utility never sees individual ciphertexts, because it holds the secret key. Collusion, malicious aggregators, integrity and threshold or multi-key variants are future work.

### Slide 3: "Three schemes, one classical baseline" (Three Content, or 3 cards)
| Card | Lines |
|---|---|
| Paillier | Baseline (PHE) / Additive only, one value per ciphertext / n = 2048 bits (about 112-bit classical) / Hardness: factoring (DCR) / **Broken by Shor** (red) |
| BFV | Exact integers (RLWE), batched / Degree 8192, t = 1,146,881 / SEAL default coefficient modulus / **No known quantum break** (green) |
| CKKS | Approximate reals (RLWE) / Degree 8192, coeff 60/40/40/60, scale 2^40 / Two multiplicative levels / **No known quantum break** (green) |
- Footer caption: AES-GCM and RSA stay in the repo as context-only references. No NIST PQC algorithms are implemented yet.
- Notes: About 1 minute. Dr. Baza's feedback was that the baseline must be homomorphic, not RSA, so Paillier is the head-to-head baseline. Walk the parameters briefly. Paillier rests on factoring, which Shor breaks. BFV and CKKS rest on Ring-LWE, and they are not post-quantum replacements for RSA. All three are public algorithms and the key is the only secret.

### Slide 4: "Real utility data, verified end to end" (Title Only + 3 stat boxes)
- Stat boxes (big number, then label):
  - 42,372 | customers in the SGCC electricity-theft dataset
  - 50 | customers aggregated on date 2016-08-02
  - 1,153,960 Wh | Paillier total, decrypted equals plaintext
- Bullets:
  - Source: State Grid Corporation of China daily consumption readings
  - Sum check ran through Paillier. BFV and CKKS: demos on small vectors, full-total check pending
  - BFV needs a larger plaintext modulus first (1,146,881 is below the total)
  - 50 trials per operation, MacBook Pro (16 GB, 10 cores); repeated at 100 to 300 trials
- Notes: About 45 seconds. Scale the 50 readings to integers, encrypt each under Paillier, add, decrypt, compare with the plaintext sum. State plainly that this check ran through Paillier and that BFV and CKKS are benchmarked at telemetry-sized payloads but the full total has not gone through them yet. One shared benchmark runner means every scheme writes the same CSV schema.

### Slide 5: "BFV and CKKS are ~50x faster than Paillier" (Content + chart)
- Insert a clustered column chart, **linear axis**, title "Mean encryption time per ciphertext (ms)", one series:
  - Paillier-2048 = 125.8
  - BFV (n=8192) = 2.2
  - CKKS (n=8192) = 2.6
  - Show data labels, no legend. Make the Paillier bar amber/orange and the other two teal/green if the template allows.
  - Fallback if charts cannot be inserted: a 3-row table with the same values.
- Right side, two stat callouts: **58x** faster encryption, BFV vs Paillier; **46x** faster decryption, BFV vs Paillier
- Footer caption: Source: SGCC run, 50 trials, Apple-silicon MacBook Pro. Python `phe` vs C++ SEAL via TenSEAL: part of the gap is implementation. 300 trials: about 57x.
- Notes: About 1.25 minutes. Say the implementation caveat out loud: Paillier runs through Python `phe` and BFV and CKKS through TenSEAL over C++ SEAL, so a GMP-backed Paillier would narrow the ratio. Repeat at 300 trials gives 125.7 vs 2.2 ms, about 57x. The 300-trial decrypt was noisy (Paillier mean 40 ms, p95 67) and one 250-trial encrypt run hit 177 ms, so quote the 50-trial numbers. Paillier-3072 encrypts in about 390 ms and BFV-16384 in about 8 ms.

### Slide 6: "Batching changes the cost at fleet scale" (Two Content)
- Left card: **Paillier: 50 readings** | big number **about 6.3 s** | bullets: One value per ciphertext; 50 ciphertexts x 126 ms; No batching available
- Right card: **BFV: 50 readings** | big number **2.2 ms** | bullets: One batched ciphertext; 50 of 8,192 slots used; Roughly 2,900x faster in total
- Footer caption: Paillier total computed as 50 x 125.8 ms. BFV: degree 8192, one ciphertext holds the 400-byte payload. Day projection at 288 encrypts: Paillier about 36 s, BFV about 0.64 s.
- Notes: About 1 minute. The 6.3 seconds is arithmetic, 50 times 125.8 ms, and not a separate measurement. Slot headroom is untested. The 288-per-day figure is a projection, because the SGCC data holds daily readings. Tradeoffs: BFV multiply is about 9 ms at 8192 and about 45 at 16384, CKKS multiplies in about 2 ms, and Paillier cannot multiply ciphertexts. Addition costs about the same everywhere (0.057 ms Paillier, 0.070 ms BFV), so the savings come from encryption.

### Slide 7: "The quantum question" (Title Only + 3 rows; dark variant if available)
| Scheme | Attack | Result |
|---|---|---|
| Paillier | Recover p and q from n. Shor's algorithm: polynomial time | Breaks it (red) |
| BFV / CKKS | Find short vectors in a lattice. No known polynomial quantum algorithm | Open, believed hard (green) |
| AES-GCM | Search the key space. Grover: square-root speedup | Halves the key bits (amber) |
- Bottom line (bold): Claim to test: Paillier falls to Shor. So I ran it.
- Notes: About 1 minute. Paillier security rests on factoring n, and the modulus is public by design. BFV and CKKS rest on Ring-LWE; "no known" is a belief and not a proof. Grover only halves symmetric key strength, which is why AES-256 is recommended.

### Slide 8: "I ran Shor's attack on a real Paillier key" (Title Only + 4 step cards + 3 stats)
- Step cards:
  1. Real key and ciphertext: phe key, n = 667 = 23 x 29, encrypts a smart-grid reading
  2. Quantum order-finding: Qiskit Aer, 10 + 10 qubits, 2,048 shots, depth 31
  3. Factor n: Measured order 308 gives 23 and 29
  4. Decrypt: Key rebuilt from factors: 136 equals 136
- Stats row: **20** qubits simulated | **155 s** attack runtime | **136 = 136** decrypted reading matches owner
- Footer caption: Toy scale on a simulator. An earlier 8-bit run (n = 187) took 62 s. Success rate not measured.
- Notes: About 2.25 minutes, the centerpiece. Call it textbook order-finding; the contribution is that it runs end to end against a real `phe` key. One: key from the same library as the benchmarks, 10 bits so a simulator can hold it. Two: the circuit builds the modular exponentiation and measures the period, and nothing about the order is handed to it. Three: continued fractions give 308, gcd gives 23 and 29. Four: rebuild the private key, decrypt to 136, matching the owner. Success rate: it worked on the first base tried in both the 8-bit and 10-bit runs, and two runs cannot support a rate.

### Slide 9: "The gap between this demo and a real key" (Two Content)
- Left card, **What I ran**: **10-bit modulus**, **20 simulated qubits**; caption: Dense simulation cost grows with each added qubit: 12 counting qubits at 10 bits did not finish in 280 s
- Right card, **What a real key needs**: **2,048-bit modulus**, **about 4,099 logical qubits**; caption: Gidney 2025 estimate: under 1 million noisy qubits, under a week, for RSA-2048. Paillier-2048 factors the same way.
- Footer caption: Gidney, arXiv:2505.15917 (2025); Gidney and Ekera, Quantum 5, 433 (2021): about 20 million noisy qubits. 2n+3 is a textbook heuristic.
- Notes: About 1 minute. The demo proves the mechanism and threatens no deployed key. 4,099 is a classroom heuristic and not a hardware figure. Published estimates: about 20 million noisy qubits for about 8 hours (2021), under a million noisy qubits in under a week (2025). Why it still matters: harvest-now-decrypt-later, and meters stay deployed 15 to 20 years. `[Verify both citations before the talk.]`

### Slide 10: "Takeaways and next steps" (Title and Content; dark variant if available)
- Three rows: **BFV** Exact meter sums, batched | **CKKS** Averages and analytics, with an error budget | **Paillier** Cheap to add, slow to encrypt, quantum-breakable
- Next: Full-total check through BFV and CKKS | BGV third scheme | Raspberry Pi benchmarks | ML-KEM for the meter link | Malicious aggregator and sum integrity
- Closing line: Thank you. Questions?
- Notes: About 1.25 minutes, then 1 to 2 minutes of Q&A. Answers: works on real data end to end for Paillier, with the BFV and CKKS full-total check pending; worth it on timing for BFV and CKKS on my stack; smaller hardware unknown until the Raspberry Pi runs. Prepared answers for likely questions are in `TALK_SCRIPT.md` (Shor scope, ciphertext sizes, the implementation gap, CKKS noise, ML-KEM, collusion).

## Final QA checklist (do before reporting back)
- [ ] 10 slides, in the order above; no leftover template sample text or empty placeholders
- [ ] Every number on the slides matches the Facts table exactly
- [ ] Slide 4 says the sum check ran through Paillier, and no slide says BFV or CKKS passed it
- [ ] Speaker notes present on all 10 slides
- [ ] No text overflows its box; titles on one line where possible; no word or number split across lines
- [ ] Slide 5 chart bars match 125.8, 2.2, 2.6
- [ ] Slides 8 and 9 still say "toy scale" and "simulator"
- [ ] Tell Joshua: (a) the title placeholder, (b) the two citations to verify, (c) whether gmpy2 is installed, (d) any fallback you used
