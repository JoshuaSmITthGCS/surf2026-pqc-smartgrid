# Talk script: SURF2026_Research_Presentation_v2_4 (19 slides)

Follows the deck slide by slide. Numbers come from the deck and were checked
against `benchmarks/results/workstation/`. The Shor demo is an optional insert
(Insert A) because it is not on the slides.

## Time budget

| Block | Slides | Time |
|---|---|---|
| Opening and framing | 1 to 4 | 3:15 |
| Related work and contribution | 5, 6 | 2:45 |
| Background, system, method | 7 to 10 | 4:30 |
| Results | 11 to 14 | 4:45 |
| Discussion and close | 15 to 17 | 3:15 |
| Total without Insert A | | about 18:30 |
| Insert A (Shor demo) | after slide 14 | 2:30 |

For a 12-minute slot: skip slide 2, speak slides 8 and 10 in one sentence each,
skip slide 12, cut Insert A to its first two paragraphs, and skip slide 18.

## Fix these slides so the spoken script and the slides agree

| Slide | Change |
|---|---|
| 5 | Shi et al. (NDSS '11) is not Paillier-based as far as I know. Drop "using Paillier" for both, and soften "no prior study" to "I did not find one". Verify the Valera-Rodriguez citation. |
| 6, 13, 17 | Slide 13 shows BFV-4096 add at −6.2%, so "under 5%" and "under 6%" are both wrong. Say "50 to 300 trial endpoints" and drop "sufficient". |
| 13 | The Paillier decrypt rise is in the 300-trial run (33.0 ms to 40.3 ms). Replace "OS scheduling spike at low trial count" with "noisy at 300 trials, cause unknown". |
| 9, 10 | The 1,153,960 Wh total exceeds t, so BFV would wrap it. Delete "staying within the plaintext modulus". The code uses t = 1,146,881 at every degree, and `786,433` is in no file. |
| 6, 9 | The sum check ran through Paillier only. Change "Dec(HE aggregate)" to "Dec(Paillier aggregate)". |
| 7, 15 | BFV batching gives n slots (two rows of n/2), so 4,096 slots at n = 4096, not n/2 and not 2,048. CKKS n/2 is correct. Verify against TenSEAL. |
| 11 | The Paillier "Multiply" column is ciphertext times plaintext. Add a footnote, and call CKKS the "cheapest ciphertext-ciphertext multiply". |
| 11, 16 | Delete "Not viable at the edge". You have no edge data. |
| 14 | Add a per-reading line: Paillier does 1 reading per call and BFV does 50. |
| 15, 16, 17 | CKKS error near 10⁻⁶ is not measured in the repo. Remove it or measure it first. |

## Script

**Slide 1: Title (0:00 to 0:30)**

Hi everyone, I'm Joshua Smith, a computer science student at the College of Charleston, and this is my SURF 2026 work with Dr. Mohamed Baza. I benchmarked three homomorphic encryption schemes, Paillier, BFV and CKKS, for private aggregation of smart-meter data.

**Slide 2: Outline (0:30 to 0:50)**

The talk follows a standard paper structure. The three highlighted sections, the problem, the related work and my contribution, are the ones I'll spend the most care on, and the rest is method and results.

**Slide 3: Introduction (0:50 to 2:05)**

Three things motivate this. The first is privacy. A 15-minute load curve reveals when people are home, which appliances they run, and their daily routine. Ordinary encryption forces the aggregator to decrypt every reading before it sums, so the aggregator sees every household in plaintext. Homomorphic encryption lets an untrusted aggregator compute on ciphertext and never hold plaintext.

The second is a quantum threat. Smart-grid hardware lasts 20 to 30 years, so under harvest now, decrypt later, ciphertext captured today can be decrypted once quantum hardware matures. NIST finalized its post-quantum standards in 2024. Paillier relies on the decisional composite residuosity assumption, which Shor's algorithm breaks. BFV and CKKS rely on Ring-LWE, where no efficient quantum attack is known.

The third is a gap. The smart-metering benchmarks I found use synthetic workloads and report point estimates. My research question is which homomorphic encryption family fits which smart-grid task, and at what measured computational cost on workstation-class hardware.

**Slide 4: Problem Formulation (2:05 to 3:35)**

I'll state the problem formally. There are N meters, and meter i holds reading m sub i in interval t. The utility needs the sum S of those readings. The aggregator is honest-but-curious, so it follows the protocol and tries to learn from what it sees. With classical encryption, the aggregator must decrypt each ciphertext before summing, so every individual reading is exposed. What we require is a scheme where the aggregator combines the ciphertexts into one, the utility decrypts that one to get S, and the aggregator never holds any m sub i.

Three constraints bind the design. C1 is correctness: the decrypted aggregate must equal the plaintext sum exactly, because billing tolerates no drift. C2 is post-quantum hardness across a 20-to-30-year asset lifetime. C3 is measured cost: latency has to be measured at grid reporting rates of 24 to 1,440 events a day, and not assumed.

The right-hand side explains why this is hard. Additive homomorphism alone cannot compute variance or a z-score for anomaly detection, which needs multiplication. Approximate schemes are cheaper but cannot be trusted for billing. Post-quantum hardness rules out Paillier, which is the classic smart-metering choice. And I found no study that measures all three families head to head on real metering data.

**Slide 5: Related Work (3:35 to 4:50)**

The literature has four strands. Erkin and Tsudik and Shi and colleagues established privacy-preserving aggregation for smart metering, with Erkin and Tsudik building on Paillier. The RLWE constructions, BFV from Fan and Vercauteren, CKKS from Cheon and colleagues, and BGV from Brakerski and colleagues, were proposed as general-purpose primitives and were not evaluated on smart-grid workloads.

Valera-Rodriguez and colleagues benchmark Microsoft SEAL, which is the closest methodological parallel. They use general-purpose data and report point estimates, and they establish a finding I rely on, that homomorphic encryption latency is data-independent once parameters are fixed. The grid and post-quantum context comes from the SGCC dataset paper by Zheng and colleagues and from the NIST FIPS standards.

The gap I did not find filled is a head-to-head Paillier, BFV and CKKS comparison on a real smart-grid archive, with the stability of the measurements checked and a recommendation for each task.

**Slide 6: Contribution (4:50 to 6:20)**

This table separates what I add from what exists. Prior benchmarks use synthetic meter vectors, and I run on the SGCC archive, 42,372 customers with 1,034 daily columns. Because latency is data-independent, the real data does not change the timings. Its value is realistic payload sizes and a correctness check.

Prior work benchmarks Paillier alone, and I compare Paillier, BFV and CKKS under one harness. For statistical rigor, I swept the trial count from 50 to 300 and compared the endpoints, which differ by under 6% for the Ring-LWE operations I checked. Some intermediate trial counts were noisier, and I'll show that on the stability slide.

For correctness, I verified that the decrypted Paillier aggregate equals the plaintext sum of 1,153,960 watt-hours. BFV and CKKS pass their own demos on small vectors, and the full-total check through them is pending. I also document that BFV batching needs the plaintext modulus to be 1 mod 2n, a constraint that is easy to miss.

The output is a mapping from task to scheme: BFV for billing, CKKS for anomaly detection, BGV for demand response. In one sentence, prior work asks whether homomorphic encryption is affordable, and I measure which scheme is affordable for which grid task.

**Slide 7: Background (6:20 to 7:35)**

Here are the three families. Paillier's hardness is the decisional composite residuosity assumption, and Shor breaks it. It does exact integer arithmetic, adds without limit, and has no batching, so one value goes in each ciphertext. BFV and CKKS both rest on Ring-LWE. BFV does exact integer arithmetic modulo t with additions and leveled multiplications. CKKS does approximate real and complex arithmetic, and each multiplication consumes one modulus level. Both batch many values into one ciphertext, with CKKS holding n over 2 complex slots.

In this study Paillier is the prior-generation reference, BFV is the candidate for demand aggregation and billing, and CKKS is the candidate for anomaly detection through variance. BGV is a leveled integer scheme whose modulus switching handles noise better than BFV across multi-step circuits, so I assigned it to the demand-response pipeline on cryptographic grounds. I have not implemented or measured it.

**Slide 8: System Model (7:35 to 8:35)**

There are three actors. The meter or edge node runs encryption only, using the utility's public key, and never holds the decryption key. The aggregator, which can be a third-party cloud, runs the homomorphic computation, sums and averages ciphertexts, and never holds plaintext. The utility holds the private key, decrypts only the aggregate, and issues public keys to meters.

The adversary is an honest-but-curious aggregator. Homomorphic encryption guarantees it learns only the decrypted aggregate. This is a single-key design, so a colluding aggregator and utility would defeat it. It also gives no authentication and no zero-knowledge proofs. Those are separate concerns and out of scope here.

**Slide 9: Methodology, Dataset (8:35 to 9:50)**

The dataset is the State Grid Corporation of China electricity-theft archive from Zheng and colleagues. It has 42,372 customers and 1,034 daily columns from January 2014 to October 2016, with 38,757 normal customers and 3,615 theft-flagged. My benchmark slice is 50 customers on August 2, 2016, which makes a 400-byte payload of 50 readings at 8 bytes each.

For encoding, Paillier and BFV take kilowatt-hours scaled by 1,000 to integer watt-hours, and CKKS takes floats directly. Each date column supplies 50 readings that pack into one BFV or CKKS ciphertext. I also have a secondary dataset, df.csv, with 560,655 rows and six electricity features.

On correctness, I encrypted the 50 readings under Paillier, added the ciphertexts, and the decrypted total matched the plaintext sum of 1,153,960 watt-hours. That check ran through Paillier. The BFV plaintext modulus I use, 1,146,881, is smaller than this total, so a BFV sum of these readings would wrap, and I need a larger modulus before running the same check through BFV. The dataset's role is workload realism and a correctness check, and it does not drive the timings.

**Slide 10: Methodology, Implementation (9:50 to 11:05)**

TenSEAL 0.3, which wraps Microsoft SEAL, supplies BFV and CKKS, and the python-paillier library supplies the Paillier baselines at 2048 and 3072 bits. That difference matters: Paillier runs in Python and BFV and CKKS run in C++, so part of the speed gap is implementation and not algorithm. Everything ran on an Apple M-series machine with 16 GB of RAM, in a Python 3.11 environment with versions pinned.

For BFV, I test degrees 4096, 8192 and 16384 with plaintext modulus 1,146,881, which satisfies the batching condition at the degrees I use. CKKS has two sets: balanced 8192 with scale 2 to the 40 and coefficient bits 60, 40, 40, 60, and high-depth 16384 with 60, 40, 40, 40, 60.

The harness warms up with three calls, then times N calls and records mean, median, standard deviation and 95th percentile into one shared CSV schema. I swept N over 50, 100, 150, 200, 250 and 300. The constraint at the bottom matters: BFV batching requires p to be 1 mod 2n, and a violation is easy to miss and invalidates the throughput figures, so I document it.

**Slide 11: Results A, Per-Operation Latency (11:05 to 12:35)**

This is the 50-trial table. Paillier at 2048 bits takes 125.84 milliseconds to encrypt and 33.22 to decrypt, and at 3072 bits it takes 389.61 and 108.44. BFV at degree 4096 encrypts in 0.824 milliseconds, which makes Paillier 152.7 times slower to encrypt against that smallest degree. Against BFV at degree 8192, which encrypts in 2.168, the ratio is 58.

Addition costs about the same everywhere, 0.057 milliseconds for Paillier and 0.022 to 0.070 for BFV, so for plain aggregation encryption is the whole cost. Multiplication is where the schemes split. BFV multiplies in 2.2 milliseconds at degree 4096, 9.0 at 8192 and 45.0 at 16384. CKKS multiplies in 1.956 milliseconds at 8192, the cheapest ciphertext-ciphertext multiply I measured. The Paillier multiply column is ciphertext times a plaintext scalar, and Paillier cannot multiply two ciphertexts.

**Slide 12: Results B, Encryption Throughput (12:35 to 13:20)**

At 300 trials, BFV at 4096 sustains 1,236.7 payload encryptions a second, BFV at 8192 sustains 450, CKKS balanced sustains 390, and Paillier at 2048 bits sustains 8.0. That puts BFV-4096 at 154.6 times Paillier's throughput. The bars are on a log scale, and this ratio comes from the 300-trial run, so it differs slightly from the 152.7 latency ratio at 50 trials.

**Slide 13: Results C, Trial-Sweep Stability (13:20 to 14:35)**

Does the trial count change the estimate? I compared each mean at 300 trials against 50 trials. Most Ring-LWE operations move by a few percent, and the largest I show is BFV-4096 add at −6.2%. Paillier encrypt moves 0.3%, but Paillier decrypt rises 22.2%, from 33.0 to 40.3 milliseconds.

I need to be careful here. These are endpoint comparisons. At intermediate trial counts, some means swung widely, for example CKKS-16384 multiply was 164% above its 50-trial value at 200 trials. Outliers drive that, which is why I report the 95th percentile alongside the mean. The Paillier decrypt rise is in the 300-trial run and I don't yet know its cause. The robust conclusion is that the ranking between schemes never changed. A stronger claim about stable means needs medians, and that is the next check.

**Slide 14: Results D, Compute-Time Projections (14:35 to 15:50)**

I convert latency into daily compute time with a linear model: mean encrypt latency times events per day, using 300-trial means. This excludes network, serialization and key distribution. At 288 events a day, Paillier-2048 spends 36.2 seconds, BFV-4096 spends 0.233 seconds, and CKKS balanced spends 0.739. At 1,440 events a day, Paillier spends 181 seconds and BFV 1.16 seconds, under 0.002% of a day.

The 155 times gap understates the difference. In this model Paillier encrypts one reading per call while BFV and CKKS encrypt a 50-reading payload per call, so per reading the gap is about 50 times larger, roughly two orders of magnitude on top of the 155. The SGCC data holds daily readings, so the higher rates are projections and not measurements.

**Insert A (optional): The quantum question, tested (15:50 to 18:20)**

Paillier's weakness is not only theoretical, so I tested it. Paillier's modulus n is public by design, and Shor's algorithm factors it in polynomial time on a large enough quantum computer.

I ran Shor against a real Paillier key from the same library I used for the benchmarks. The modulus has 10 bits instead of 2048, so a simulator can hold it, and it came out to 667. I encrypted a real smart-grid reading under that key. The quantum part is a Qiskit Aer circuit with 10 plus 10 qubits, 20 in total, run for 2,048 shots, with a circuit depth of 31. The circuit is not handed the order. It builds the modular exponentiation and measures the period itself.

Continued fractions gave an order of 308, and a gcd turned that into the factors 23 and 29, so n is 23 times 29. I rebuilt the private key from those factors, decrypted the ciphertext, and got 136, which matched the original reading. The attack took 155 seconds, and an earlier 8-bit run with n of 187 took 62 seconds.

This is textbook order-finding on a simulator with a toy key. It worked on the first base in both runs, and two runs cannot support a success rate. It poses no threat to a deployed key: at 10 bits, a run with 12 counting qubits had not finished after 280 seconds, and a 2048-bit modulus needs thousands of logical qubits. Published estimates run from about 20 million noisy qubits for about 8 hours in 2021 to under a million noisy qubits in under a week in 2025. What it shows is the mechanism, end to end, against the exact library a Paillier-based design would use.

**Slide 15: Discussion, Scheme-to-Task Mapping (15:50 to 17:05)**

The benchmarks support a mapping from task to scheme. For billing, which needs exact integers, BFV at 4096 fits. It batches many readings into one ciphertext, and a single batched addition costs 0.022 milliseconds, so one operation yields a neighborhood total. Paillier is correct but 152.7 times slower to encrypt, offers no batching, and is not post-quantum.

For anomaly detection, variance needs multiplication for squaring, and CKKS multiplies in 1.956 milliseconds against 9.045 for BFV at the same degree, about 4.6 times cheaper. CKKS is approximate, and I have not yet measured its error on these data, so measuring that is the next step before recommending it for theft detection. A rotation-based mean takes a logarithmic number of additions. A full demand-response pipeline subtracts a baseline, multiplies a weighted share, sums and compares, which gives multiplicative depth of at least 2, and I assign BGV to that on cryptographic grounds.

On the quantum side, BFV and CKKS rest on Ring-LWE with no known efficient quantum attack, which is the prudent default for 20-to-30-year infrastructure.

**Slide 16: Discussion, Limitations (17:05 to 18:15)**

These six limits bound every result. All timings come from one Apple M-series machine, and Raspberry Pi measurements are pending, so a smaller cache and slower memory could shift the Ring-LWE figures more than a near-linear projection assumes. Serialization, transmission and key distribution are excluded and unmeasured. BGV is not implemented, so it has no latency data.

I use a single dataset slice of 50 customers and one date, so daily and seasonal variation are not characterized. CKKS error is not yet measured or formally bounded. And I deliberately deferred post-quantum key-exchange coverage and Pi benchmarking, which reframes the claims from edge viability to relative performance and scheme selection.

**Slide 17: Conclusion and Future Work (18:15 to 19:30)**

Four findings. First, Paillier is the baseline and not the answer: 152.7 times slower to encrypt than BFV-4096, no batching, and broken by Shor. Second, BFV at degree 4096 suits demand aggregation, with 1,236.7 encryptions a second and a 0.022 millisecond addition, and under 1.2 seconds a day at one event a minute. Third, CKKS balanced-8192 suits anomaly detection, with the cheapest ciphertext multiply at 1.956 milliseconds, pending an error measurement. Fourth, the ranking between schemes held across 50 to 300 trials, though single means can be noisy.

Future work is Raspberry Pi edge benchmarks, a leveled BGV implementation, ciphertext serialization and network overhead, an end-to-end billing and detection pipeline, a full-total check through BFV and CKKS with a larger plaintext modulus, CKKS error measurement, and ML-KEM for the meter-to-aggregator channel, since these schemes protect the computation and leave the link open.

**Slides 18 and 19: References and Thank you (19:30 to 19:45)**

Thank you to Dr. Baza and to URCA for supporting this work through SURF 2026. Code and benchmark CSVs are in the repository, and I'm happy to take questions.

## Prepared answers

| Question | Answer |
|---|---|
| What is actually new? | Latency ranking is expected. I add the daily-cost model on real payloads, the task-to-scheme mapping with CKKS multiplying about 4.6x cheaper than BFV at degree 8192, a documented BFV batching constraint, and an end-to-end Shor run against a real `phe` key. Meter-class numbers are the open piece. |
| Is the 152.7x an algorithm gap? | No. It compares Python `phe` with C++ SEAL via TenSEAL, and it is against the smallest BFV degree. Against degree 8192 it is 58x. |
| Why is real data a contribution if latency is data-independent? | It checks correctness and sizes payloads realistically. It does not change timings. |
| Did BFV and CKKS pass the 1,153,960 Wh check? | Not yet. It ran through Paillier. BFV's plaintext modulus (1,146,881) is below the total, so it needs raising. |
| Why report endpoint drift only? | It is what I compared. Intermediate trial counts had outlier-driven swings, so medians and p95 are the next check. |
| CKKS error? | Not measured yet. It is planned, and the scheme recommendation depends on it. |
| BFV slot count? | Batching gives n slots as two rows of n/2. I use 50 per payload. |
| Ciphertext sizes? | Not benchmarked. A Paillier-2048 ciphertext is 4,096 bits per reading. |
| Success rate of the Shor run? | Two runs, first base each time. That cannot support a rate. |
| Malicious aggregator or collusion? | Out of scope. Single-key design, honest-but-curious aggregator. |
| Why not ML-KEM now? | It protects the channel and not the computation. It is on the roadmap. |
