# Talk script: technical audience (about 12 minutes)

Matches the 10-slide deck in `BUILD_IN_POWERPOINT_ONLINE.md`. Every number comes
from `benchmarks/results/workstation/` or from the Shor run documented in the
build guide. Headline timings are the 50-trial `sgcc_latest` run; the 50 to 300
trial sweep is the repeat check.

**Slide 1: Title (0:00 to 0:50)**

Hi everyone, I'm Joshua Smith, a CS major at the College of Charleston, and this is work from my SURF project, mentored by Dr. Mohamed Baza.

Published results already say lattice schemes beat Paillier, so I did not set out to repeat that. I set out to measure three things: what the switch costs a meter per day on real utility data, where the schemes diverge once multiplication enters, and what a Shor attack looks like against the exact library this design would use. Whether any of this runs on meter-class hardware is still open, and I'll say where it stands.

**Slide 2: Private readings, useful totals (0:50 to 2:15)**

A smart meter reports usage many times a day, and that data says a lot about a household. Usage runs low overnight and spikes in the mornings and evenings, and a week of flat usage means nobody's home. Researchers have pulled individual appliance signatures out of signals like this for years.

The old defense was obscurity: a private network, an undocumented protocol, and hope that nobody looks. That fails once data gets copied, logged and leaked. Encrypting the readings with an ordinary cipher breaks the use case, because the utility needs totals and averages to run the grid, and a utility that decrypts every reading to compute them has seen everything.

The protocol I tested has three roles. Each meter encrypts its own reading under a public key, an aggregator adds the ciphertexts without being able to read any of them, and the utility decrypts the sum. The utility holds the secret key, so the design works only if the utility never sees individual ciphertexts. If the aggregator and utility collude, the protection ends. My threat model is an honest-but-curious aggregator that follows the protocol and tries to learn from what it sees. I leave out a malicious aggregator, integrity of the sums, and multi-key or threshold variants, and I'll return to them at the end.

This matters on a long clock. Meters stay deployed for 15 to 20 years, and Paillier-based aggregation designs in the smart-metering literature would carry a factoring-based key through that window. Replacing it raises a cost question: what the replacement costs per meter per day, and what it buys. I measured that on real utility data.

**Slide 3: Three schemes, one classical baseline (2:15 to 3:20)**

I compared three schemes. Paillier is the baseline. It is additively homomorphic, it holds one value per ciphertext, and its security rests on the decisional composite residuosity assumption, which comes down to factoring. My key is a 2048-bit modulus, about 112 bits of classical security. BFV does exact integer arithmetic over RLWE with batching, so many values pack into one ciphertext. I run it at degree 8192 with a plaintext modulus of 1,146,881 and SEAL's default coefficient modulus, which targets 128-bit classical security. CKKS does approximate arithmetic over real numbers, also on RLWE. I run it at degree 8192 with a 60, 40, 40, 60 bit coefficient modulus and scale 2 to the 40, which gives two multiplicative levels and a small error you have to budget for.

Dr. Baza pushed me off RSA as the baseline, and he was right: RSA isn't homomorphic, so it can't be compared with these schemes. I haven't implemented any NIST post-quantum algorithms yet, and BFV and CKKS don't take over RSA's role. All three schemes are public algorithms, so the key is the sole secret, and that matters on slide 7.

**Slide 4: Real utility data, verified end to end (3:20 to 4:05)**

First I needed to know the pipeline works on real data. I used the State Grid Corporation of China electricity-theft dataset: 42,372 customers with daily readings from January 2014 to October 2016, of whom 38,757 are normal and 3,615 are flagged for theft. I took 50 customers on August 2, 2016, scaled their readings to integers, encrypted each under Paillier, added the ciphertexts, and decrypted a total of 1,153,960 watt-hours that matched the plaintext sum.

That end-to-end sum check ran through Paillier. BFV and CKKS have encrypted-sum and encrypted-average demos on small sample vectors, and I benchmarked them on payloads sized from the same telemetry, but I have not yet pushed the full 50-customer total through them. BFV needs one change first. My default plaintext modulus of 1,146,881 is smaller than the 1,153,960 total, so the sum would wrap, and I need a larger modulus or a different scaling.

For the benchmarks, I ran 50 trials per operation on an Apple-silicon MacBook Pro with 16 gigabytes of RAM and 10 logical cores, then repeated at 100, 150, 200, 250 and 300 trials. One shared runner means every scheme writes the same CSV schema.

**Slide 5: BFV and CKKS are about 50x faster than Paillier (4:05 to 5:20)**

The ranking is the expected part. What I add is the size of the gap on real payloads. Paillier-2048 takes about 126 milliseconds to encrypt one value. BFV at degree 8192 takes about 2.2 milliseconds and CKKS about 2.6, which puts BFV 58 times faster. Decryption takes about 33 milliseconds for Paillier and 0.7 for BFV, which is 46 times faster.

Part of this gap comes from the implementation. Paillier runs through the Python `phe` library, which uses Python big integers unless gmpy2 is installed, and BFV and CKKS run through TenSEAL, a wrapper over C++ SEAL. A C or GMP-backed Paillier would narrow the ratio. I benchmarked the libraries a student would reach for, and I'm not claiming a pure algorithmic ratio.

The 300-trial run agrees on encryption, with Paillier at 125.7 milliseconds and BFV at 2.2, a ratio of about 57. Decryption was noisier in that run: Paillier's mean rose to 40 milliseconds with a 95th percentile near 67. I quote the 50-trial figures.

The axis is linear and starts at zero, so the lattice bars look tiny, and that is the true ratio. Encryption is the number to watch, because it runs on the meter. Key size widens the gap: Paillier at 3072 bits takes about 390 milliseconds to encrypt, while BFV at degree 16384 takes about 8.

**Slide 6: Batching changes the cost at fleet scale (5:20 to 6:20)**

The per-operation ratio undersells the difference once you scale up. Paillier encrypts one number per ciphertext, so 50 readings cost 50 encryptions, about 6.3 seconds. That figure is my arithmetic, 50 times 125.8 milliseconds, and not a separate measurement. BFV packs all 50 readings, 400 bytes of payload, into one ciphertext and encrypts them in 2.2 milliseconds. Degree 8192 offers 8,192 batching slots and I use 50, so per-reading cost falls further with a fuller batch. I have not measured that.

My projection shows the effect over a day. A meter that reports every five minutes makes 288 encryptions a day, and Paillier-2048 spends about 36 seconds of laptop time on them. BFV at degree 8192 spends about 0.64 seconds on 288 payloads of 50 readings each. The SGCC data holds daily readings, so the five-minute rate is a projection.

Multiplication is where the schemes split. It takes about 9 milliseconds in BFV at degree 8192 and about 45 at 16384, while CKKS multiplies in about 2 milliseconds at its balanced setting, roughly 4.6 times cheaper than BFV at the same degree. Paillier cannot multiply two ciphertexts at all. Addition costs about the same across schemes, 0.057 milliseconds for Paillier and 0.070 for BFV, so for plain aggregation encryption is the whole cost. That gives a rule for choosing: BFV for exact sums, and CKKS once multiplication enters and approximate results are acceptable, which is the case for the depth-two demand-response work I have planned.

**Slide 7: The quantum question (6:20 to 7:20)**

The quantum angle is part of why I started. Paillier relies on factoring n, and Shor's algorithm factors in polynomial time. BFV and CKKS rely on RLWE, where no known quantum algorithm helps beyond modest speedups. "No known" is short of proven, so I'm treating it as a working assumption. Grover's algorithm halves the effective key length for symmetric ciphers, which is why people recommend AES-256.

This returns us to the obscurity point. A Paillier public key is public, and the modulus n is published on purpose. An attacker needs nothing secret, and the scheme is as strong as the difficulty of factoring. I decided to test that and ran Shor against a real Paillier key.

**Slide 8: I ran Shor's attack on a real Paillier key (7:20 to 9:30)** *(slow down here)*

This is textbook order-finding on a simulator with a toy-sized key. The contribution is that the pipeline runs end to end against a real `phe` key, and I'll say so again at the end.

I generated a Paillier key with the same library I used for the benchmarks. The modulus has 10 bits instead of 2048, so a simulator can hold it, and it came out to 667. I encrypted a real smart-grid reading under that key.

The quantum part is a Qiskit Aer circuit with 10 plus 10 qubits, 20 in total, run for 2,048 shots, with a circuit depth of 31. The circuit receives no hint about the order. Many demos hand the circuit the answer and run the quantum part for show, but mine builds the modular exponentiation and measures the period itself.

Classical post-processing finishes the job. Continued fractions gave an order of 308, and a gcd turned that into the factors 23 and 29, so n is 23 times 29. I rebuilt the private key from those factors and decrypted the ciphertext. I got 136, and the original reading was 136.

The attack took 155 seconds. An earlier 8-bit run, with n of 187, took 62 seconds. Two limits apply. I ran too few trials to claim a success rate, and the attack found the answer on the first base in both the 8-bit and 10-bit runs. Everything the attack used came from the public modulus.

**Slide 9: The gap between this demo and a real key (9:30 to 10:40)**

This slide covers what the demo proves and what it leaves open. It shows the mechanism end to end, and it poses no threat to a deployed key. Dense classical simulation grows costly with each added qubit: at 10 bits, a run with 12 counting qubits had not finished after 280 seconds.

A 2048-bit modulus needs thousands of logical qubits. The 2n plus 3 rule gives 4,099, a textbook heuristic and not a hardware figure. Published estimates were about 20 million noisy qubits for about 8 hours in 2021, and under a million noisy qubits in under a week in 2025.

The reason to care today is harvest now, decrypt later. Meters stay deployed for 15 to 20 years, and an attacker can store ciphertexts today and decrypt them when the hardware exists.

**Slide 10: What I add, and what's left (10:40 to 12:00)**

The speed ranking is known, and I'm not claiming it. I add three things. First, a per-meter-day cost on real utility payloads: at five-minute reporting, about 36 seconds of laptop time for Paillier against 0.64 seconds for batched BFV, with variance across 50 to 300 trials. Second, a rule for choosing by operation and not by name: addition costs the same everywhere, so encryption dominates plain aggregation, and multiplication is where CKKS and BFV part ways. Third, a reproducible attack against a real `phe` key, with no order handed to the circuit and a real reading decrypted at the end, which ties the quantum claim to the specific library this design would use.

On correctness, Paillier aggregated 50 SGCC customers end to end and matched the plaintext total. BFV and CKKS pass their own demos and run at telemetry-sized payloads, and the full-total check through them is the next step.

The largest open piece is the one that would matter most: whether any of this runs on a meter. All my numbers come from a laptop. The ratios suggest the lattice schemes have room, but a ratio on a MacBook is a different thing from a measurement on a meter, and I'm not aware of many published meter-class numbers for this comparison. The Raspberry Pi benchmarks are in progress.

The rest of the roadmap is BGV for depth-two demand-response computations, ML-KEM for the meter-to-aggregator channel since BFV and CKKS protect the computation and leave the link open, a larger BFV plaintext modulus, ciphertext-size measurements, and a threat model that includes a malicious aggregator and integrity of the aggregate.

Thank you to Dr. Baza, LS-STAR and the Honors College. I'm happy to take questions.

## Prepared answers

| Question | Answer |
|---|---|
| Is the Shor run just textbook order-finding on a toy modulus? | Yes. It shows the pipeline against a real `phe` key, with no order handed to the circuit. It makes no resource claim. |
| Success rate? | It worked on the first base in two runs. Two runs cannot support a rate. |
| Ciphertext sizes? | Not benchmarked. A Paillier-2048 ciphertext lives in Z mod n squared, so it is 4,096 bits (512 bytes) per reading. State BFV and CKKS sizes only after measuring. |
| Is the 58x an algorithm gap? | No. It compares Python `phe` with C++ SEAL through TenSEAL. |
| Why is the sum check Paillier only? | The runner's aggregation check calls the Paillier demo. BFV and CKKS have separate demos on small vectors. The BFV default plaintext modulus (1,146,881) is below the 1,153,960 total and needs raising. |
| CKKS noise and IND-CPA-D? | CKKS decryptions can leak noise information. I use it as the analytics scheme with an error budget and did not model that attack. |
| Why not ML-KEM now? | It protects the channel and not the computation. It is on the roadmap for the meter link. |
| Malicious aggregator or colluding utility? | Out of scope. Single-key design, honest-but-curious aggregator only. |
| What is actually new? | The speed ranking is expected. I add the per-meter-day cost on real SGCC payloads with variance, the operation-level rule (encryption dominates aggregation, CKKS multiplies about 4.6x cheaper than BFV at degree 8192), and an end-to-end Shor run against a real `phe` key. Meter-class numbers are the open piece. |
