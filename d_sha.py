import os
import csv
import timeit
import statistics

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPEATS = 100
NUMBER = 100   # timeit runs per measurement — improves accuracy for fast operations


# --- SHA-256 hash ---
def sha256_hash(data):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    return digest.finalize()


# --- Statistics helper ---
def compute_stats(times):
    mean = statistics.mean(times)
    std  = statistics.stdev(times)
    med  = statistics.median(times)
    cv   = std / mean
    return mean, std, med, cv


# --- Benchmark ---
with open(os.path.join(BASE_DIR, "sha_results.csv"), "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["size_bytes", "mean_us", "std_us", "median_us", "cv"])

    for file_size in FILE_SIZES:
        with open(os.path.join(BASE_DIR, f"file_{file_size}.bin"), "rb") as f:
            data = f.read()

        times = []
        for _ in range(REPEATS):
            t = timeit.timeit(lambda: sha256_hash(data), number=NUMBER)
            times.append((t / NUMBER) * 1e6)

        mean, std, med, cv = compute_stats(times)

        writer.writerow([file_size, round(mean, 2), round(std, 2), round(med, 2), round(cv, 3)])
        print(f"Done: {file_size} bytes")

print("Results saved to sha_results.csv")