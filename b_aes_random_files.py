import os
import csv
import timeit
import statistics

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
# We test a few representative sizes rather than all 7
TEST_SIZES = [512, 32768, 262144]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPEATS = 100
NUMBER = 100

key = os.urandom(32)  # fixed key, same as in aes.py


def aes_encrypt(data, key):
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    return nonce, encryptor.update(data) + encryptor.finalize()


def compute_stats(times):
    mean = statistics.mean(times)
    std  = statistics.stdev(times)
    med  = statistics.median(times)
    cv   = std / mean
    return mean, std, med, cv


with open(os.path.join(BASE_DIR, "aes_random_files_results.csv"), "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["size_bytes", "mean_us", "std_us", "median_us", "cv"])

    for size in TEST_SIZES:
        times = []
        for _ in range(REPEATS):
            # Fresh random file generated each repetition
            data = os.urandom(size)
            t = timeit.timeit(lambda: aes_encrypt(data, key), number=NUMBER)
            times.append((t / NUMBER) * 1e6)

        mean, std, med, cv = compute_stats(times)
        writer.writerow([size, round(mean, 2), round(std, 2), round(med, 2), round(cv, 3)])
        print(f"Done: {size} bytes — mean={mean:.2f}µs, std={std:.2f}µs, cv={cv:.3f}")

print("Results saved to aes_random_files_results.csv")
