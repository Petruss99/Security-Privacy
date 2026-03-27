# Assignment #1: Performance Benchmarking of Cryptographic Mechanisms

## FCUP-CC2009-2025/2026-2S Security and Privacy
Group PL3G3

## Overview
This project benchmarks the execution time of three cryptographic mechanisms — AES-CTR, RSA hybrid encryption, and SHA-256 — across files of different sizes. Results are saved as CSV files and visualized in a single plot.

---

## Repository Structure

```
.
├── a_generate_files.py           # Generates random binary test files
├── b_aes.py                      # AES-CTR encryption/decryption benchmark (Task B)
├── b_aes_random_files.py         # Supplementary experiment: AES over random files
├── c_rsa.py                      # RSA hybrid encryption/decryption benchmark (Task C)
├── d_sha.py                      # SHA-256 hashing benchmark (Task D)
├── e_plot_results.py             # Generates plots from CSV results
├── aes_results.csv               # Output: AES benchmark results
├── rsa_results.csv               # Output: RSA benchmark results
├── sha_results.csv               # Output: SHA-256 benchmark results
├── aes_random_files_results.csv  # Output: random files experiment results
└── crypto_benchmarks.png         # Output: benchmark plots
```

---

## Requirements

Python 3.10+ and the following libraries:

```bash
pip install cryptography matplotlib
```

---

## How to Run

All scripts use `BASE_DIR` to resolve file paths relative to their own location, so they can be run from any working directory.

### Step 1 — Generate test files
```bash
python3 a_generate_files.py
```
Creates 7 binary files (`file_8.bin` to `file_2097152.bin`) in the same directory.

### Step 2 — Run benchmarks
```bash
python3 b_aes.py
python3 c_rsa.py
python3 d_sha.py
```
Each script reads the `.bin` files, runs the benchmark, and saves results to a CSV file in the same directory. Note that `c_rsa.py` may take several minutes due to the computational cost of RSA on large files.

### Step 3 — (Optional) Run the random files experiment
```bash
python3 b_aes_random_files.py
```
Runs AES encryption on freshly generated random files of fixed sizes to verify that results are data-agnostic.

### Step 4 — Generate plots
```bash
python3 e_plot_results.py
```
Reads the three CSV result files and saves `crypto_benchmarks.png` in the same directory.

---

## Output Format

All CSV files report times in **microseconds (µs)**. Each benchmark reports per file size:
- `mean_us` — arithmetic mean across all repetitions
- `std_us` — standard deviation
- `median_us` — median (robust to outliers)
- `cv` — coefficient of variation (std / mean)

### Repetitions
| Script | Repeats | timeit number | Total calls per file size |
|---|---|---|---|
| `b_aes.py` | 100 | 100 | 10,000 |
| `c_rsa.py` | 20 | 1 | 20 |
| `d_sha.py` | 100 | 100 | 10,000 |

`timeit number` controls how many times the function is called in a single measurement — the total time is then divided by `number` to get the per-call time. This improves accuracy for fast operations like AES and SHA where a single call may be too short to measure reliably. RSA uses `number=1` since each call already takes hundreds of microseconds.