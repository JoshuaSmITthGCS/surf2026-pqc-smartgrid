# BUILD.md: Fill the LS-STAR template in PowerPoint Online

Instructions for Claude in the browser. Edit the **already-open** copy of
"Student Template - Copy.pptx" in PowerPoint for the web. Do not create a new
file, do not touch the original template, and do not share or publish anything.

## Ground rules

1. Keep the template's own theme, fonts, colors, and layouts. Reuse its layouts
   (Title, Title and Content, Two Content, Section, Title Only) instead of
   drawing new frames. Delete template slides and sample text you do not use.
2. Target **10 slides** (about 10 to 12 minutes, 1 to 2 minutes of Q&A after).
3. One message per slide. Slide text stays short: titles about 40 characters or
   fewer, body text 18 pt or larger, captions 12 pt or larger.
4. Put the "Speaker notes" blocks below into each slide's Notes pane, not on the
   slide.
5. **Do not invent or round any number.** Use only the numbers written here.
   Anything in `[BRACKETS]` is for Joshua to confirm, so leave it highlighted
   and tell him at the end.
6. If an instruction cannot be done in PowerPoint for the web, use the fallback
   given, and list what you changed at the end.

## Facts you may use (all measured or computed from the project repo)

| Item | Value |
|---|---|
| Presenter | Joshua Smith, College of Charleston, Computer Science, Honors College |
| Program | SURF 2026, Mentor Dr. Mohamed Baza |
| Event | 2026 LS-STAR Research Banquet, Wed 10/14, RITA 101 |
| Working title | `[Computing on Encrypted Smart-Grid Data]` (Joshua to confirm with Dr. Vulava) |
| Dataset | SGCC electricity-theft data, 42,372 customers |
| Aggregation slice | 50 customers, date 2016-08-02, total 1,153,960 Wh, decrypted equals expected |
| Encrypt, Paillier-2048 | 125.8 ms |
| Encrypt, BFV (degree 8192) | 2.2 ms |
| Encrypt, CKKS (degree 8192) | 2.6 ms |
| Decrypt, Paillier-2048 | 33.2 ms |
| Decrypt, BFV / CKKS (8192) | 0.72 ms / 0.71 ms |
| Speedup, BFV vs Paillier | 58x encrypt, 46x decrypt |
| Paillier, 50 readings | about 6.3 s (50 x 125.8 ms, computed, not separately measured) |
| BFV, 50 readings | 2.2 ms in one batched ciphertext |
| Hardware / trials | Apple-silicon MacBook Pro, 50 trials |
| Shor attack target | Real `phe` Paillier key, n = 667 = 23 x 29 (10-bit) |
| Shor attack method | Qiskit Aer simulator, 10 work + 10 counting qubits (20 total), 2,048 shots |
| Shor attack outcome | Measured order 308, factors 23 and 29, circuit depth 31, 155 s |
| Decryption check | Key rebuilt from factors decrypted the ciphertext to 136; owner's decryption was 136 |
| Earlier run | 8-bit key n = 187, 62 s |
| Real-key estimate | 2048-bit modulus needs about 4,099 logical qubits (2n+3 textbook heuristic) |
| Published estimates | Gidney 2025, arXiv:2505.15917, under 1 million noisy qubits, under a week; Gidney and Ekera 2021, Quantum 5, 433, about 20 million noisy qubits `[Joshua to verify both before presenting]` |

## Slides

### Slide 1: Title (Title layout)
- Title: `[Computing on Encrypted Smart-Grid Data]`
- Subtitle: Benchmarking Paillier, BFV and CKKS, and testing the quantum threat with a real Shor attack
- Name line: Joshua Smith | College of Charleston | Computer Science | Honors College
- Second line: SURF 2026 | Mentor: Dr. Mohamed Baza
- Small tag: 2026 LS-STAR Research Banquet
- Notes: About 30 seconds. Thank Dr. Vulava and LS-STAR, name Dr. Baza. Preview: I benchmarked three ways of adding up smart-meter readings without decrypting them, then tried to break the oldest one with a quantum algorithm.

### Slide 2: "Private readings, useful totals" (Title Only + 3 shapes)
- Draw three rounded boxes left to right joined by arrows:
  1. Smart meters: Encrypt each reading at the edge
  2. Aggregator: Adds ciphertexts, sees no readings
  3. Utility: Decrypts only the total
- Below, three bullets:
  - Readings reveal when people are home, asleep, or away
  - Homomorphic encryption lets the aggregator add without decrypting
  - Question: which scheme is practical on a smart meter, and which survives quantum computers?
- Notes: About 1 minute. The utility needs sums and averages, not individual readings, and individual readings leak household behavior. Homomorphic encryption makes the middle box useful without trusting it. Two questions: speed on constrained devices, and security against a future quantum computer.

### Slide 3: "Three schemes, one classical baseline" (Three Content, or 3 cards)
| Card | Lines |
|---|---|
| Paillier | Baseline (PHE) / Adds encrypted values only / Hardness: factoring (DCR) / **Broken by Shor** (red) |
| BFV | Exact integers (RLWE) / Add and multiply, batched / Hardness: Ring-LWE / **No known quantum break** (green) |
| CKKS | Approximate reals (RLWE) / Averages and analytics / Hardness: Ring-LWE / **No known quantum break** (green) |
- Footer caption: AES-GCM and RSA stay in the repo as context-only references. No NIST PQC algorithms are implemented yet.
- Notes: About 1 minute. Dr. Baza's feedback was that the baseline must be a homomorphic scheme, not RSA, so Paillier is the head-to-head baseline. BFV is exact integer arithmetic for meter sums, CKKS is approximate real arithmetic for averages. Paillier rests on factoring, which Shor breaks. BFV and CKKS rest on Ring-LWE. They are not post-quantum replacements for RSA, they serve a different purpose, and I have not implemented NIST PQC algorithms such as ML-KEM yet.

### Slide 4: "Real utility data, verified end to end" (Title Only + 3 stat boxes)
- Stat boxes (big number, then label):
  - 42,372 | customers in the SGCC electricity-theft dataset
  - 50 | customers aggregated on date 2016-08-02
  - 1,153,960 Wh | encrypted total, decrypted equals expected
- Bullets:
  - Source: State Grid Corporation of China daily consumption readings
  - Paillier and BFV use scaled integers; CKKS uses real values
  - Every scheme passed the same correctness check before timing
- Notes: About 1 minute. Before trusting any timing, the encrypted sum of 50 customers' readings must decrypt to exactly 1,153,960 watt-hours. I also validated an earlier London smart-meter dataset. Benchmarks ran on an Apple-silicon MacBook Pro, 50 trials per operation, through one shared benchmark runner so every scheme writes the same CSV schema.

### Slide 5: "BFV and CKKS are ~50x faster than Paillier" (Content + chart)
- Insert a clustered column chart, **linear axis**, title "Mean encryption time per ciphertext (ms)", one series:
  - Paillier-2048 = 125.8
  - BFV (n=8192) = 2.2
  - CKKS (n=8192) = 2.6
  - Show data labels, no legend. Make the Paillier bar amber/orange and the other two teal/green if the template allows.
  - Fallback if charts cannot be inserted: a 3-row table with the same values.
- Right side, two stat callouts: **58x** faster encryption, BFV vs Paillier; **46x** faster decryption, BFV vs Paillier
- Footer caption: Source: SGCC run, 50 customers, 50 trials, Apple-silicon MacBook Pro. Decrypt: 33.2 ms vs 0.72 ms.
- Notes: About 1.5 minutes. Paillier-2048 takes about 126 ms to encrypt one value and 33 ms to decrypt it. BFV at degree 8192 takes about 2.2 ms to encrypt and 0.7 ms to decrypt, which is 58 and 46 times faster. The axis is linear, so the BFV and CKKS bars are small on purpose. Encryption matters most because it runs on the meter itself.

### Slide 6: "Batching changes the cost at fleet scale" (Two Content)
- Left card: **Paillier: 50 readings** | big number **about 6.3 s** | bullets: One value per ciphertext; 50 ciphertexts x 126 ms; No batching available
- Right card: **BFV: 50 readings** | big number **2.2 ms** | bullets: One batched ciphertext; All 50 values packed together; Roughly 2,900x faster in total
- Footer caption: Paillier total computed as 50 x 125.8 ms. BFV: degree 8192, one ciphertext holds the 400-byte payload.
- Notes: About 1 minute. Fairness point: Paillier encrypts one number per ciphertext, so 50 readings means 50 encryptions, about 6.3 seconds. BFV packs all 50 into one ciphertext. The 6.3 seconds is my arithmetic, 50 times 125.8 ms, not a separate measurement. Be honest about the tradeoff: BFV multiplication is heavier (about 9 ms at degree 8192, 45 ms at 16384), while Paillier cannot multiply two ciphertexts at all.

### Slide 7: "The quantum question" (Title Only + 3 rows; dark variant if available)
| Scheme | Attack | Result |
|---|---|---|
| Paillier | Recover p and q from n. Shor's algorithm: polynomial time | Breaks it (red) |
| BFV / CKKS | Find short vectors in a lattice. No known polynomial quantum algorithm | Open, believed hard (green) |
| AES-GCM | Search the key space. Grover: square-root speedup | Halves the key bits (amber) |
- Bottom line (bold): Claim to test: Paillier falls to Shor. So I ran it.
- Notes: About 1 minute. Paillier security rests on factoring n, and Shor factors in polynomial time on a large enough quantum computer. BFV and CKKS rest on Ring-LWE; no known polynomial quantum algorithm breaks it, but that is a belief, not a proof. Grover only halves symmetric key strength, which is why AES-256 is recommended.

### Slide 8: "I ran Shor's attack on a real Paillier key" (Title Only + 4 step cards + 3 stats)
- Step cards:
  1. Real key and ciphertext: phe key, n = 667 = 23 x 29, encrypts a smart-grid reading
  2. Quantum order-finding: Qiskit Aer, 10 + 10 qubits, 2,048 shots
  3. Factor n: Measured order 308 gives 23 and 29
  4. Decrypt: Key rebuilt from factors: 136 equals 136
- Stats row: **20** qubits simulated | **155 s** attack runtime | **136 = 136** decrypted reading matches owner
- Footer caption: Toy scale on a simulator. An earlier 8-bit run (n = 187) took 62 s.
- Notes: About 2 minutes, the centerpiece. One: a real Paillier key from the same library as the benchmarks, at 10 bits instead of 2048 so a simulator can hold it, encrypting a real smart-grid reading. Two: a quantum circuit builds the modular-exponentiation operations and measures the period; nothing about the answer is given to it, unlike textbook demos that hand the circuit the order. Three: continued fractions give order 308, and gcd gives 23 and 29. Four: I rebuilt the private key from those factors and decrypted to 136, matching the owner. Say plainly it is a simulator and a toy key. If asked about success rate: it worked on the first base tried in both the 8-bit and 10-bit runs, but I did not run enough trials to claim a rate.

### Slide 9: "The gap between this demo and a real key" (Two Content)
- Left card, **What I ran**: **10-bit modulus**, **20 simulated qubits**; caption: Dense simulation cost grows steeply: 12 counting qubits at 10 bits did not finish in 280 s
- Right card, **What a real key needs**: **2,048-bit modulus**, **about 4,099 logical qubits**; caption: Gidney 2025 estimate: under 1 million noisy qubits, under a week, for RSA-2048. Paillier-2048 factors the same way.
- Footer caption: Gidney, arXiv:2505.15917 (2025); Gidney and Ekera, Quantum 5, 433 (2021): about 20 million noisy qubits. 2n+3 is a textbook heuristic.
- Notes: About 1 minute. This slide protects the credibility of the experiment: my demo proves the mechanism and is not a threat to any deployed key today. A real 2048-bit modulus needs thousands of logical qubits (4,099 is a classroom heuristic). Published estimates: about 20 million noisy qubits for roughly 8 hours (2021), lowered to under a million noisy qubits in under a week (2025). Why it still matters: harvest-now-decrypt-later, and smart meters stay deployed 15 to 20 years. `[Verify both citations before the talk.]`

### Slide 10: "Takeaways and next steps" (Title and Content; dark variant if available)
- Three rows: **BFV** Best fit for exact meter sums | **CKKS** Best fit for averages and analytics | **Paillier** Fast to add, slow to encrypt, and quantum-breakable
- Next: BGV third scheme | Raspberry Pi benchmarks | ML-KEM for the meter link
- Closing line: Thank you. Questions?
- Notes: About 1 minute, then 1 to 2 minutes of Q&A. Next steps: BGV for depth-two demand-response computations, a Raspberry Pi to test meter-class hardware, and ML-KEM (NIST post-quantum) for the meter-to-aggregator link, since BFV and CKKS protect computation but not the channel. Thank Dr. Baza, LS-STAR, and the Honors College. Likely questions: why not RSA as the baseline (not homomorphic, Dr. Baza's guidance); are BFV and CKKS quantum-safe (believed, not proven, and not a replacement for RSA's role); how big a key could you break (slide 9).

## Final QA checklist (do before reporting back)
- [ ] 10 slides, in the order above; no leftover template sample text or empty placeholders
- [ ] Every number on the slides matches the Facts table exactly
- [ ] Speaker notes present on all 10 slides
- [ ] No text overflows its box; titles on one line where possible; no word or number split across lines
- [ ] Slide 5 chart bars match 125.8, 2.2, 2.6
- [ ] Slides 8 and 9 still say "toy scale" and "simulator"
- [ ] Tell Joshua: (a) the title placeholder, (b) the two citations to verify, (c) any fallback you used
