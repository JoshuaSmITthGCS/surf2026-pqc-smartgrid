# Talk script: LS-STAR_Presentation.pptx (10 slides, about 15 minutes)

Written for the 10-slide LS-STAR deck. It folds in the material from the older
19-slide research deck (system model, background, implementation, stability,
limitations) and from the earlier LS-STAR build guide. Numbers come from the
deck and were checked against `benchmarks/results/workstation/`.

## Time budget

| Slide | Topic | Time | Clock |
|---|---|---|---|
| 1 | Title and framing | 0:40 | 0:00 |
| 2 | Problem, system model, constraints | 1:30 | 0:40 |
| 3 | What is known, what this adds | 1:30 | 2:10 |
| 4 | Three HE families | 1:10 | 3:40 |
| 5 | Methodology | 1:30 | 4:50 |
| 6 | Per-operation latency | 2:00 | 6:20 |
| 7 | Throughput, cost per meter-day, stability | 2:00 | 8:20 |
| 8 | Shor against a real Paillier key | 2:30 | 10:20 |
| 9 | Scheme-to-task mapping and limits | 1:30 | 12:50 |
| 10 | Conclusions and future work | 1:00 | 14:20 |

For 12 minutes: shorten slide 2 to its first two paragraphs, give slide 4 one
sentence per scheme, merge slide 5 into slide 6, and keep slide 8 to its first
three paragraphs.

## Fix these slide items so the deck and the speech agree

| Slide | Change |
|---|---|
| 3, 7, 10 | "Ring-LWE means move at most 6.2%" and "Fifty trials is enough" rest on a 50-versus-300 endpoint comparison. Intermediate runs swung much more (CKKS-16384 multiply +164% at 200 trials, BFV-8192 decrypt +100% at 100). Say "50 versus 300 trial endpoints" and retitle slide 10's finding "Scheme ranking held from 50 to 300 trials." |
| 7 | Paillier-2048 decrypt (+22.2%, 33.0 ms to 40.3 ms) is in the 300-trial run and the cause is unknown. Replace "treated as measurement noise" with "cause not yet identified." |
| 7 | Add a per-reading line. Paillier does 1 reading per call and BFV does 50, so the per-reading gap is about 50 times larger than 155x. |
| 9 | CKKS "error about 1e-6 relative" is not measured anywhere in the repo. Remove it, and change the limitation to "CKKS error not yet measured." |
| 6 | Footnote the Paillier Multiply column. It is `mul_plain`, ciphertext times plaintext scalar. |
| 3 | The prior-work column (Erkin and Tsudik, Shi et al., Valera-Rodriguez) comes from your literature review. Verify those attributions before claiming them. |

## Script

**Slide 1: Title (0:00 to 0:40)**

Hi everyone, I'm Joshua Smith, a computer science student at the College of Charleston, and this is my SURF 2026 work with Dr. Mohamed Baza.

Published results already say lattice-based homomorphic schemes beat Paillier, so I did not set out to repeat that. I measured what the gap is worth per meter per day on real utility data, where the schemes diverge once multiplication enters, and what a Shor attack looks like against the library a Paillier-based design would use. I started with three questions: is it possible, is it worth it, and can it run on small hardware. I answer the first two with measurements. The third is open, and I'll say exactly where it stands.

**Slide 2: Problem, private aggregation (0:40 to 2:10)**

Here is the setting. There are N smart meters, and meter i holds a reading m sub i. The utility needs the sum S of those readings, and an aggregator in the middle is honest-but-curious: it follows the protocol and tries to learn from what it sees. Readings matter because a 15-minute load curve can reveal occupancy and appliance use. That is general background on load monitoring and not something I tested.

Classical encryption fails here. The aggregator must decrypt every ciphertext before summing, so every individual reading is exposed at the aggregator. What we require is a scheme where the aggregator adds the ciphertexts into one, the utility decrypts that one to get S, and the aggregator never holds any m sub i.

The system has three actors. Each meter runs encryption only, under the utility's public key, and never holds a decryption key. The aggregator, which can be a third-party cloud, runs the homomorphic computation. The utility holds the private key and decrypts only the aggregate. That is a single-key design, so if the aggregator and utility collude, the protection ends. It also gives no authentication and no integrity guarantee on the sum.

Three constraints bind the design. C1 is correctness: the decrypted aggregate must equal the plaintext sum exactly, because billing tolerates no drift. C2 is post-quantum hardness over a decades-long asset lifetime, because of harvest now, decrypt later. C3 is measured cost: latency measured and not assumed, at 24 to 1,440 reports a day. My research question is which family fits which smart-grid task, and at what measured cost on workstation-class hardware.

**Slide 3: What is known, and what this work adds (2:10 to 3:40)**

I'll say it in one line: these results confirm what is expected. Paillier is slower than lattice schemes, batching helps BFV, and Shor breaks factoring. I'm not claiming those. Here is what I add, row by row.

For workload, the prior smart-metering work I reviewed used synthetic meter vectors, and I use the real State Grid archive, 42,372 customers with a 50-customer slice. For schemes, I compare Paillier, BFV and CKKS head to head under one harness. For rigor, I swept the trial count from 50 to 300 and compared the endpoints. The Ring-LWE means move at most 6.2%, and I'll show on slide 7 that some intermediate runs were noisier.

For cost per meter-day, I turned per-operation latency into daily compute: Paillier-2048 spends 36.2 seconds a day at 288 reports. For quantum exposure, I ran Shor end to end against a real python-paillier key, on a toy modulus on a simulator, and I did not just argue from the hardness assumption. And for output, I give a scheme-to-task mapping instead of a verdict on whether homomorphic encryption is practical. The prior-work column comes from my literature review and is not an exhaustive search, so I'm not claiming first.

**Slide 4: Three HE families (3:40 to 4:50)**

Here are the three schemes. Paillier is additively homomorphic with unlimited additions and no batching, so one value goes in each ciphertext. Its security rests on the decisional composite residuosity assumption, which is factoring, and Shor breaks it. BFV does exact integer arithmetic over Ring-LWE, with leveled multiplication and SIMD batching. CKKS does approximate real arithmetic over Ring-LWE, where each multiplication consumes one modulus level, and the approximation error is something you budget for.

There is no known quantum attack on Ring-LWE. That is short of proven, so I treat it as a working assumption. For libraries, Paillier runs through Python `phe` and BFV and CKKS run through TenSEAL over C++ SEAL. That matters when you read the speed ratios, because part of the gap is implementation and I'm not claiming a pure algorithmic ratio.

Dr. Baza had me use Paillier and not RSA as the baseline, because RSA isn't homomorphic. BGV is assigned to multi-step demand response with multiplicative depth of 2 or more, on cryptographic grounds, and I have not implemented or measured it. All of these are public algorithms, so the key is the only secret, and that matters on slide 8.

**Slide 5: Methodology, real data, one harness (4:50 to 6:20)**

The dataset is the State Grid Corporation of China electricity-theft archive from Zheng and colleagues: 42,372 customers and 1,034 daily columns from January 2014 to October 2016, with 38,757 normal customers and 3,615 flagged for theft. My slice is 50 customers on August 2, 2016, a 400-byte payload. The data grounds parameter sizing and checks correctness. It does not drive timings, because latency is data-independent once parameters are fixed. Paillier and BFV take kilowatt-hours scaled to integer watt-hours, and CKKS takes floats.

For implementation, BFV runs at degrees 4096, 8192 and 16384 with plaintext modulus 1,146,881, and CKKS runs balanced at 8192 with scale 2 to the 40 and coefficient bits 60, 40, 40, 60, and high-depth at 16384. Paillier runs at 2048 and 3072 bits, all on an Apple M-series machine with 16 gigabytes of RAM. The harness warms up with three calls, then records mean, median, standard deviation and 95th percentile into one CSV schema, swept from 50 to 300 trials.

On correctness, the 50-customer Paillier sum decrypts to 1,153,960 watt-hours and matches the plaintext sum. The check through BFV and CKKS is pending, and BFV needs a larger plaintext modulus first, because 1,146,881 is smaller than that total and the sum would wrap. One more detail: BFV batching needs the plaintext modulus to be 1 mod 2n. A wrong value is easy to miss, because batching can end up disabled and then the throughput figures are invalid, so I document it.

**Slide 6: Results, per-operation latency (6:20 to 8:20)**

This is the per-operation table, 50-trial means in milliseconds. Paillier at 2048 bits takes about 126 milliseconds to encrypt and 33 to decrypt, and at 3072 bits it takes about 390 and 108. Its keygen takes 1.5 seconds at 2048 bits and 4.3 seconds at 3072.

BFV at degree 4096 encrypts in 0.824 milliseconds, which is 152.7 times faster than Paillier-2048. At degree 8192 it takes 2.168 milliseconds, 58 times faster, and decryption is 46 times faster at 0.717 against 33.22. Remember that the smallest BFV degree sets the larger ratio and that the stacks differ.

Addition is a wash in absolute terms, 0.057 milliseconds for Paillier and 0.022 to 0.070 for BFV, so the cost of plain aggregation is encryption. Multiplication is where the schemes split. CKKS balanced-8192 multiplies in 1.956 milliseconds against 9.045 for BFV at the same ring dimension, about 4.6 times cheaper, and BFV at 16384 reaches 44.963, which I flag as one to avoid. Paillier cannot multiply two ciphertexts. Its 0.112 millisecond entry is ciphertext times a plaintext scalar.

**Slide 7: Results, throughput and cost per meter-day (8:20 to 10:20)**

On the left, throughput at 300 trials. BFV at 4096 sustains 1,236.7 payload encryptions a second, BFV at 8192 sustains 450, CKKS balanced sustains 390, and Paillier-2048 sustains 8.0. The ratio against Paillier is 154.6, which differs slightly from the 152.7 latency ratio at 50 trials.

On the right is the number I add, the cost per meter-day. Daily compute equals mean encrypt latency times reports per day, using 300-trial means. At 288 reports a day, Paillier-2048 spends 36.2 seconds of laptop time per meter and BFV-4096 spends 0.233 seconds. At 1,440 a day, Paillier spends 181 seconds and BFV 1.16 seconds, under 0.002% of a day. CKKS balanced-8192 spends 3.69 seconds at 1,440.

The comparison understates the gap. BFV and CKKS batch 50 readings per payload while Paillier encrypts one reading per call, so per reading the gap is about 50 times larger than 155. This is compute time under a linear model, with network, serialization and key distribution excluded, and the SGCC data is daily, so the report rates are projections.

On stability, the endpoint comparison between 50 and 300 trials moves Ring-LWE means by at most 6.2%, at BFV-4096 add. Paillier-2048 decrypt rose 22.2%, from 33.0 to 40.3 milliseconds, while its encrypt moved 0.3%. I don't know the cause. Intermediate trial counts were noisier, for example CKKS-16384 multiply was 164% above its 50-trial value at 200 trials, driven by outliers. What held was the ranking between schemes. A claim about stable means would need medians, and that is the next check.

**Slide 8: Shor against a real Paillier key (10:20 to 12:50)** *(slow down here)*

This is textbook order-finding on a simulator with a toy-sized key. The contribution is that the pipeline runs end to end against a real python-paillier key, the same primitive a Paillier-based aggregation design would use, and I'll say so again at the end. A Paillier public key is public. The modulus n is published on purpose, so the attack needs nothing secret.

Step one, I generated a Paillier key with the same library as the benchmarks. The modulus has 10 bits instead of 2048, so a simulator can hold it, and it came out to 667, which is 23 times 29. I encrypted a real smart-grid reading under it.

Step two, a Qiskit Aer circuit with 10 plus 10 qubits, 20 in total, run for 2,048 shots, with circuit depth 31. The circuit is not given the order. A lot of demos hand the circuit the answer and run the quantum part for show, but mine builds the modular exponentiation and measures the period itself.

Step three is classical post-processing. Continued fractions gave an order of 308, and a gcd turned that into the factors 23 and 29. Step four, I rebuilt the private key from those factors and decrypted the ciphertext. I got 136, which matched the original reading. The attack took 155 seconds, and an earlier 8-bit run with n of 187 took 62 seconds.

Now the gap. This demo poses no threat to a deployed key. At 10 bits, a run with 12 counting qubits had not finished after 280 seconds. A 2048-bit modulus needs about 4,099 logical qubits by the 2n plus 3 rule, a textbook heuristic and not a hardware figure. Published estimates run from about 20 million noisy qubits in 2021 to under a million noisy qubits in under a week in 2025. It worked on the first base both times, and two runs cannot support a success rate. It shows the mechanism, and harvest now, decrypt later is why the mechanism matters for meters that stay deployed for decades.

**Slide 9: Scheme-to-task mapping and limits (12:50 to 14:20)**

The benchmarks support a mapping from task to scheme. For billing and demand aggregation, BFV at 4096 fits: exact integers, SIMD batching and a 0.022 millisecond addition, where Paillier is correct but 152.7 times slower to encrypt, has no batching and is not post-quantum. For anomaly detection, variance needs multiplication for squaring, and CKKS multiplies in 1.956 milliseconds against 9.045 for BFV-8192. I have not yet measured CKKS approximation error on these data, and I need that before recommending it for theft detection. BGV is future work for demand response at depth 2 or more, and no measurements exist yet.

These limits bound every result. It is one Apple M-series workstation, with Raspberry Pi measurements pending, so a smaller cache and slower memory could shift the Ring-LWE figures. Network, serialization and key distribution are excluded. It is one 50-customer slice, so seasonal variation isn't characterized. CKKS error is not yet measured. The model is an honest-but-curious aggregator only, with no integrity or authentication. And the Shor demo is toy scale and simulated.

**Slide 10: Conclusions and future work (14:20 to 15:20)**

Back to the three questions. Is it possible? The pipeline works on real data: the Paillier 50-customer sum matched the plaintext, and the full-total check through BFV and CKKS is the next correctness step. Is it worth it? For BFV and CKKS, yes. BFV-4096 encrypts 152.7 times faster than Paillier-2048 on my stack, it sustains 1,236.7 encryptions a second, and it costs 1.16 seconds a day at 1,440 reports. CKKS has the cheapest ciphertext multiply at 1.956 milliseconds. Neither depends on factoring, and Paillier falls to Shor. The ranking between schemes held from 50 to 300 trials.

Can it run on small hardware? I don't know yet. All my numbers come from a workstation. The ratios suggest the lattice schemes have room, but a ratio on a laptop is a different thing from a measurement on a meter. The Raspberry Pi benchmarks come next.

Future work is the Pi, a leveled BGV implementation, serialization and network cost, an end-to-end billing and detection pipeline, the full-total check and a larger plaintext modulus for BFV, CKKS error measurement, ML-KEM for the meter-to-aggregator channel, and a malicious aggregator with integrity of the sum. Thank you to Dr. Baza and to the Office of Undergraduate Research and Creative Activities for supporting this work. I'm happy to take questions.

## Prepared answers

| Question | Answer |
|---|---|
| What is actually new? | The ranking is expected. I add the per-meter-day cost on real payloads, the operation-level rule (encryption dominates aggregation, CKKS multiplies about 4.6x cheaper than BFV at degree 8192), and an end-to-end Shor run against a real `phe` key. Meter-class numbers are the open piece. |
| Is the 152.7x an algorithm gap? | No. It compares Python `phe` with C++ SEAL via TenSEAL, and it is against the smallest BFV degree. Against degree 8192 it is 58x. |
| Why is real data a contribution if latency is data-independent? | It checks correctness and sizes payloads realistically. It does not change timings. |
| Did BFV and CKKS pass the 1,153,960 Wh check? | Not yet. It ran through Paillier. BFV's plaintext modulus (1,146,881) is below the total, so it needs raising. |
| Why only endpoint drift? | It is what I compared. Intermediate trial counts had outlier-driven swings, so medians and p95 are the next check. |
| CKKS error? | Not measured yet. The scheme recommendation depends on it. |
| BFV slot count? | Batching gives n slots as two rows of n/2. I use 50 per payload. |
| Ciphertext sizes? | Not benchmarked. A Paillier-2048 ciphertext is 4,096 bits per reading. |
| Shor success rate? | Two runs, first base each time. That cannot support a rate. |
| Malicious aggregator or collusion? | Out of scope. Single-key design, honest-but-curious aggregator. |
| Why not ML-KEM now? | It protects the channel and not the computation. It is on the roadmap. |
