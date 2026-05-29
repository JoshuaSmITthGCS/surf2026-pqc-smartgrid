# Homomorphic Encryption Baseline Meeting Notes

## Updated Phase 1 Scope

Phase 1 should compare homomorphic encryption techniques against one classical
encryption baseline.

Recommended Phase 1 comparison:

- BFV homomorphic encryption
- CKKS homomorphic encryption
- AES-GCM classical encryption baseline

RSA should not be a main Phase 1 baseline because it is classical public-key
encryption and does not support computation over encrypted data. It can remain
in the repository as reference code, but the meeting and first paper direction
should focus on encrypted computation.

## Three Homomorphic Encryption Techniques To Present

### 1. BFV

BFV is a homomorphic encryption scheme for exact integer arithmetic.

Best fit for this project:

- encrypted meter-reading sums
- integer aggregation
- counts of overload or fault events
- exact totals where decrypted output should match the expected integer result

Why it is a strong baseline:

- It maps directly to smart-grid aggregation.
- It is already implemented in the current codebase through TenSEAL.
- It supports addition and multiplication over encrypted integer vectors.

### 2. CKKS

CKKS is a homomorphic encryption scheme for approximate real-number arithmetic.

Best fit for this project:

- encrypted voltage averages
- encrypted current averages
- load and predicted-load averages
- real-valued telemetry analytics where small approximation error is acceptable

Why it is a strong baseline:

- Most columns in the smart-grid dataset are real-valued.
- It is already implemented in the current codebase through TenSEAL.
- It supports approximate encrypted addition and multiplication over vectors.

### 3. BGV or TFHE

The third technique can be presented as a candidate for later implementation.

BGV:

- exact integer arithmetic, similar use category to BFV
- useful as a second exact-arithmetic HE comparison
- supported by libraries such as Microsoft SEAL and OpenFHE

TFHE:

- strong fit for Boolean logic and encrypted decision rules
- useful for threshold-style smart-grid checks, such as overload or fault flags
- likely more complex to add in Python than BFV/CKKS through TenSEAL

Recommended meeting position:

- Present BFV, CKKS, and BGV/TFHE as the three techniques.
- Recommend implementing BFV and CKKS first.
- Treat BGV or TFHE as the third candidate to revisit after Phase 1 results.

## Classical Encryption Baseline

Use AES-GCM as the one classical encryption baseline.

Why AES-GCM:

- It is a fast and widely used symmetric authenticated encryption mode.
- It works naturally for telemetry payload encryption.
- It gives a clear comparison point for how much overhead HE adds.

Important limitation:

- AES-GCM does not allow computation over encrypted data.
- It should be described as a conventional encryption performance baseline, not
  as a functional equivalent to BFV or CKKS.

## Proposed First Experiments

### Experiment 1: Encrypted Integer Aggregation

- Input: integer-transformed smart-grid readings
- HE method: BFV
- Classical baseline: AES-GCM encrypt/decrypt same serialized payload
- Metric: encryption time, operation time, decryption time, output correctness

### Experiment 2: Encrypted Real-Valued Average

- Input: voltage, current, power consumption, or predicted load
- HE method: CKKS
- Classical baseline: AES-GCM encrypt/decrypt same serialized payload
- Metric: encryption time, operation time, decryption time, p95 latency, average error

### Experiment 3: Candidate Third Technique

- Option A: BGV for exact integer aggregation comparison against BFV
- Option B: TFHE for encrypted threshold/fault logic
- Decision: choose after mentor feedback and implementation feasibility check

## Recommendation

Start with BFV and CKKS as the two homomorphic encryption baselines, and compare
both against AES-GCM as the single classical encryption baseline.

Reason:

- BFV covers exact integer smart-grid aggregation.
- CKKS covers real-valued telemetry analytics.
- AES-GCM gives a clean classical performance reference.
- All three can be connected directly to the existing smart-grid dataset.

## Sources To Review

- TenSEAL: supports BFV for encrypted integer vectors and CKKS for encrypted real-number vectors.
  - https://github.com/OpenMined/TenSEAL
- Microsoft SEAL: open-source homomorphic encryption library supporting BFV, BGV, and CKKS-style workflows.
  - https://github.com/microsoft/SEAL
- OpenFHE: documents BFV and BGV for integer arithmetic, CKKS for real-number arithmetic, and TFHE/FHEW-style Boolean/function evaluation.
  - https://openfhe-development.readthedocs.io/
