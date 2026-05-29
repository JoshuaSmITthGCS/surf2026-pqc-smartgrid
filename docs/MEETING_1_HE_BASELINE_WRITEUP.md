# Meeting 1 Write-Up: Homomorphic Encryption Baselines

**Researcher:** Joshua Smith  
**Mentor:** Dr. Mohamed Baza  
**Project:** Benchmarking encryption techniques for privacy-preserving smart-grid telemetry  
**Meeting focus:** Homomorphic encryption techniques and Phase 1 baseline plan

## 1. Response to Mentor Feedback

Thank you for the clarification about RSA. I agree that RSA should not be a main baseline at this stage because RSA is classical public-key encryption and does not support computation over encrypted data. Since the current research direction is homomorphic encryption, the first phase should focus on encryption schemes that allow operations to be performed while the data remains encrypted.

I will keep RSA only as setup/reference code in the repository, but I will not use it as a Phase 1 research baseline. Instead, I propose using one classical encryption baseline, AES-GCM, to show the performance cost of normal encryption compared with homomorphic encryption.

## 2. Updated Phase 1 Scope

The updated first phase of the project will compare:

1. **BFV homomorphic encryption**
2. **CKKS homomorphic encryption**
3. **AES-GCM classical encryption baseline**

The goal is to measure the cost and usefulness of homomorphic encryption for smart-grid telemetry workloads, while using AES-GCM as the conventional encryption reference.

AES-GCM will not be presented as functionally equivalent to homomorphic encryption. It will be used only to answer the question:

> How much overhead do we introduce when we move from normal encrypted communication to encrypted computation?

## 3. Three Homomorphic Encryption Techniques

### Technique 1: BFV

BFV is a homomorphic encryption scheme designed for exact integer arithmetic.

**Best smart-grid fit:**

- encrypted meter-reading aggregation
- encrypted sums of integer-transformed power readings
- counting overload or transformer-fault events
- workloads where the decrypted result must be exact

**Why BFV matters for this project:**

Smart-grid systems often need aggregate values such as total power consumption or event counts. BFV can support this kind of computation while keeping individual readings encrypted.

**Example project workload:**

Encrypt integer power-consumption readings, compute an encrypted sum, then decrypt only the final aggregate.

### Technique 2: CKKS

CKKS is a homomorphic encryption scheme designed for approximate real-number arithmetic.

**Best smart-grid fit:**

- encrypted voltage averages
- encrypted current averages
- encrypted power-consumption averages
- predicted load and price analytics
- workloads where small numerical error is acceptable

**Why CKKS matters for this project:**

Most fields in the smart-grid dataset are real-valued, including voltage, current, power consumption, temperature, humidity, electricity price, and predicted load. CKKS is a better fit than BFV for these floating-point analytics.

**Example project workload:**

Encrypt voltage readings, compute an encrypted average, decrypt the result, and measure both runtime and approximation error.

### Technique 3: BGV or TFHE

The third technique can be presented as a candidate for future expansion.

**BGV** is another homomorphic encryption scheme for exact integer arithmetic. It is similar to BFV in the type of arithmetic it supports, so it could be useful for comparing exact-integer HE schemes.

**TFHE** is better suited for Boolean logic and threshold-style encrypted decisions. It could fit smart-grid use cases such as encrypted overload detection or transformer-fault flags.

**Recommendation for Phase 1:**

I recommend presenting BGV or TFHE as the third technique, but not implementing it first unless we decide that a third HE baseline is necessary immediately. BFV and CKKS already cover the two most important data types in the current smart-grid dataset: integers and real numbers.

## 4. Recommended First Two HE Baselines

I recommend starting with:

1. **BFV**
2. **CKKS**

These are the best first two baselines because:

- BFV handles exact integer aggregation.
- CKKS handles real-valued telemetry analytics.
- Both map directly to the dataset already added to the project.
- Both are already supported by TenSEAL, which is installed and working in the environment.
- Both can be benchmarked with the existing `BenchmarkRunner`.

## 5. Classical Baseline

I recommend using:

**AES-GCM**

AES-GCM is a strong classical baseline because:

- it is widely used for fast symmetric encryption;
- it provides authenticated encryption;
- it works naturally on serialized smart-grid telemetry payloads;
- it gives a clear reference point for normal encryption cost.

Important limitation:

AES-GCM cannot compute over encrypted data. It only protects data in transit or storage. Therefore, AES-GCM should be used as a performance reference, not as a functional replacement for BFV or CKKS.

## 6. Proposed Benchmark Questions

The first phase should answer these questions:

1. How much slower is BFV encrypted aggregation compared with AES-GCM encryption of the same telemetry payload?
2. How much slower is CKKS encrypted averaging compared with AES-GCM encryption of the same telemetry payload?
3. How does BFV scale as the number of integer readings increases?
4. How does CKKS scale as the number of real-valued readings increases?
5. What approximation error does CKKS introduce for voltage, power, and predicted-load averages?
6. Which homomorphic technique fits the smart-grid dataset best?

## 7. Proposed Experiments

### Experiment 1: AES-GCM Classical Baseline

**Input:** serialized smart-grid telemetry rows  
**Operation:** AES-GCM encrypt and decrypt  
**Metrics:** mean latency, median latency, p95 latency, payload size

Purpose:

Establish the conventional encryption baseline.

### Experiment 2: BFV Encrypted Integer Aggregation

**Input:** integer-transformed meter or power readings  
**Operation:** encrypt, homomorphic sum, decrypt final aggregate  
**Metrics:** encryption latency, addition latency, decryption latency, correctness

Purpose:

Measure exact encrypted aggregation over smart-grid data.

### Experiment 3: CKKS Encrypted Real-Valued Average

**Input:** voltage, current, power consumption, or predicted load  
**Operation:** encrypt, homomorphic sum/average, decrypt final result  
**Metrics:** encryption latency, addition latency, multiplication/scaling latency, decryption latency, approximation error

Purpose:

Measure encrypted analytics over real-valued smart-grid telemetry.

### Experiment 4: Third-Technique Feasibility

**Candidate:** BGV or TFHE  
**Goal:** decide whether to implement a third HE scheme in code or keep it as a literature comparison

Purpose:

Avoid overextending the project before BFV and CKKS results are stable.

## 8. Implementation Plan

### Step 1: Clean Phase 1 Benchmark Scope

- Keep AES-GCM as the one classical encryption baseline.
- Keep BFV and CKKS as the first two HE baselines.
- Move RSA to reference/setup status only.

### Step 2: Improve BFV Workload

- Use real smart-grid data.
- Convert selected readings to integers.
- Encrypt vectors of readings.
- Compute encrypted sums.
- Decrypt only the final aggregate.
- Verify exact correctness.
- Export results to CSV.

### Step 3: Improve CKKS Workload

- Use real-valued smart-grid columns.
- Encrypt voltage, current, power consumption, and predicted-load values.
- Compute encrypted averages.
- Decrypt final results.
- Measure approximation error.
- Export results to CSV.

### Step 4: Compare Against AES-GCM

- Serialize the same smart-grid data into byte payloads.
- Encrypt and decrypt with AES-GCM.
- Compare latency against BFV and CKKS.
- Clearly state that AES-GCM is not computing over encrypted data.

### Step 5: Decide Third Technique

- If the project needs a third implemented HE scheme, choose BGV for another exact-integer comparison or TFHE for encrypted threshold logic.
- If time is limited, keep the third technique as a discussion/literature comparison and focus on strong BFV/CKKS results.

## 9. My Recommendation

My recommendation is:

> Start Phase 1 with BFV and CKKS as the two homomorphic encryption baselines, and use AES-GCM as the single classical encryption baseline.

This gives the project a clear and fair comparison:

- AES-GCM shows the cost of conventional encryption.
- BFV shows the cost and capability of exact encrypted aggregation.
- CKKS shows the cost and capability of approximate encrypted analytics.

This scope is realistic for the first phase and directly matches the smart-grid dataset.

## 10. Questions For The Meeting

1. Do you agree that AES-GCM should be the one classical encryption baseline?
2. Should the first two HE baselines be BFV and CKKS?
3. For the third HE technique, would you prefer BGV or TFHE?
4. Should the third technique be implemented now, or discussed as future work after BFV and CKKS results are complete?
5. Which smart-grid workload should be prioritized first: encrypted aggregation, encrypted averaging, or encrypted threshold/fault detection?

## 11. Sources Reviewed

- TenSEAL: supports BFV for encrypted integer vectors and CKKS for encrypted real-number vectors.
  - https://github.com/OpenMined/TenSEAL
- Microsoft SEAL: open-source homomorphic encryption library with BFV, BGV, and CKKS-style support.
  - https://github.com/microsoft/SEAL
- OpenFHE: documents BFV and BGV for integer arithmetic, CKKS for real-number arithmetic, and TFHE/FHEW-style Boolean/function evaluation.
  - https://openfhe-development.readthedocs.io/
