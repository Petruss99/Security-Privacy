import os
import csv
import timeit
import statistics

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPEATS = 100
NUMBER = 100   # timeit runs per measurement — improves accuracy for fast operations

# --- Key generated once, outside any timed section ---
key = os.urandom(32)  # 256-bit key


# --- Encryption ---
def aes_encrypt(data, key):
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    return nonce, encryptor.update(data) + encryptor.finalize()


# --- Decryption ---
def aes_decrypt(data, key, nonce):
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()


# --- Statistics helper ---
def compute_stats(times):
    mean = statistics.mean(times)
    std  = statistics.stdev(times)
    med  = statistics.median(times)
    cv   = std / mean
    return mean, std, med, cv


# --- Benchmark ---
with open(os.path.join(BASE_DIR, "aes_results.csv"), "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["size_bytes", "enc_mean_us", "enc_std_us", "enc_median_us", "enc_cv",
                                   "dec_mean_us", "dec_std_us", "dec_median_us", "dec_cv"])

    for file_size in FILE_SIZES:
        with open(os.path.join(BASE_DIR, f"file_{file_size}.bin"), "rb") as f:
            data = f.read()

        # --- Encryption benchmark ---
        times_enc = []
        for _ in range(REPEATS):
            t = timeit.timeit(lambda: aes_encrypt(data, key), number=NUMBER)
            times_enc.append((t / NUMBER) * 1e6)

        # --- Decryption benchmark ---
        nonce, encrypted = aes_encrypt(data, key)

        times_dec = []
        for _ in range(REPEATS):
            t = timeit.timeit(lambda: aes_decrypt(encrypted, key, nonce), number=NUMBER)
            times_dec.append((t / NUMBER) * 1e6)

        enc_mean, enc_std, enc_med, enc_cv = compute_stats(times_enc)
        dec_mean, dec_std, dec_med, dec_cv = compute_stats(times_dec)

        writer.writerow([file_size,
                         round(enc_mean, 2), round(enc_std, 2), round(enc_med, 2), round(enc_cv, 3),
                         round(dec_mean, 2), round(dec_std, 2), round(dec_med, 2), round(dec_cv, 3)])
        print(f"Done: {file_size} bytes")

print("Results saved to aes_results.csv")