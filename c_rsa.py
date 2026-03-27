import os
import csv
import struct
import timeit
import statistics

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
R_SIZE = 32        # bytes (256 bits) — matches AES-256 security level, fits within PKCS1v15 limit (max 245 for 2048-bit key)
REPEATS = 20       # number of timing measurements per file size

# --- RSA key pair (generated once, outside any timed section) ---
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()


# --- Encryption ---
def rsa_encrypt(data, public_key):
    r = os.urandom(R_SIZE)
    cipher_r = public_key.encrypt(r, padding.PKCS1v15())

    blocks = (len(data) + 31) // 32
    result = []
    for i in range(blocks):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(struct.pack(">Q", i))
        digest.update(r)
        keystream = digest.finalize()
        cur = data[i*32 : (i+1)*32]
        for a, b in zip(keystream, cur):
            result.append(a ^ b)

    return cipher_r, bytes(result)


# --- Decryption ---
def rsa_decrypt(cipher_r, enc_blocks, private_key):
    r = private_key.decrypt(cipher_r, padding.PKCS1v15())

    blocks = (len(enc_blocks) + 31) // 32
    result = []
    for i in range(blocks):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(struct.pack(">Q", i))
        digest.update(r)
        keystream = digest.finalize()
        cur = enc_blocks[i*32 : (i+1)*32]
        for a, b in zip(keystream, cur):
            result.append(a ^ b)

    return bytes(result)


# --- Statistics helper ---
def compute_stats(times):
    mean = statistics.mean(times)
    std  = statistics.stdev(times)
    med  = statistics.median(times)
    cv   = std / mean
    return mean, std, med, cv


# --- Benchmark ---
with open(os.path.join(BASE_DIR, "rsa_results.csv"), "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["size_bytes", "enc_mean_us", "enc_std_us", "enc_median_us", "enc_cv",
                                   "dec_mean_us", "dec_std_us", "dec_median_us", "dec_cv"])

    for file_size in FILE_SIZES:
        with open(os.path.join(BASE_DIR, f"file_{file_size}.bin"), "rb") as f:
            data = f.read()

        # --- Encryption benchmark ---
        times_enc = []
        for _ in range(REPEATS):
            t = timeit.timeit(lambda: rsa_encrypt(data, public_key), number=1)
            times_enc.append(t * 1e6)

        # --- Decryption benchmark ---
        cipher_r, enc_blocks = rsa_encrypt(data, public_key)

        times_dec = []
        for _ in range(REPEATS):
            t = timeit.timeit(lambda: rsa_decrypt(cipher_r, enc_blocks, private_key), number=1)
            times_dec.append(t * 1e6)

        enc_mean, enc_std, enc_med, enc_cv = compute_stats(times_enc)
        dec_mean, dec_std, dec_med, dec_cv = compute_stats(times_dec)

        writer.writerow([file_size,
                         round(enc_mean, 2), round(enc_std, 2), round(enc_med, 2), round(enc_cv, 3),
                         round(dec_mean, 2), round(dec_std, 2), round(dec_med, 2), round(dec_cv, 3)])
        print(f"Done: {file_size} bytes")

print("Results saved to rsa_results.csv")