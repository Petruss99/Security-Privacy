import os
import timeit
import statistics
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
FILES_DIR = "C:\FI_MUNI\ERASMUS\security_and_privacy"
KEY_SIZE_BITS = 256
KEY_SIZE_BYTES = KEY_SIZE_BITS // 8
NONCE_SIZE_BYTES = 16   # AES block size = 128 bits
REPEATS = 100           # how many times to repeat each measurement
TIMEIT_NUMBER = 1       # how many times timeit runs the function per repeat

# --- AES-CTR Encryption ---
def aes_ctr_encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

# --- AES-CTR Decryption (same operation, symmetric) ---
def aes_ctr_decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# --- Benchmark a single file size ---
def benchmark_aes(size: int) -> dict:
    filepath = os.path.join(FILES_DIR, f"file_{size}.bin")
    with open(filepath, "rb") as f:
        plaintext = f.read()

    enc_times = []
    dec_times = []

    for _ in range(REPEATS):
        # Generate fresh key and nonce for each run
        key = os.urandom(KEY_SIZE_BYTES)
        nonce = os.urandom(NONCE_SIZE_BYTES)

        # --- Time encryption ---
        t_enc = timeit.timeit(
            lambda: aes_ctr_encrypt(key, nonce, plaintext),
            number=TIMEIT_NUMBER
        )
        enc_times.append(t_enc * 1e6)  # convert to microseconds

        # Encrypt once to get ciphertext for decryption benchmark
        ciphertext = aes_ctr_encrypt(key, nonce, plaintext)

        # --- Time decryption ---
        t_dec = timeit.timeit(
            lambda: aes_ctr_decrypt(key, nonce, ciphertext),
            number=TIMEIT_NUMBER
        )
        dec_times.append(t_dec * 1e6)

    return {
        "size": size,
        "enc_mean_us": statistics.mean(enc_times),
        "enc_std_us": statistics.stdev(enc_times),
        "dec_mean_us": statistics.mean(dec_times),
        "dec_std_us": statistics.stdev(dec_times),
    }

# --- Run all benchmarks ---
if __name__ == "__main__":
    print(f"{'Size (B)':>12} | {'Enc Mean (us)':>14} | {'Enc Std (us)':>13} | {'Dec Mean (us)':>14} | {'Dec Std (us)':>13}")
    print("-" * 75)

    all_results = []
    for size in FILE_SIZES:
        result = benchmark_aes(size)
        all_results.append(result)
        print(f"{result['size']:>12} | {result['enc_mean_us']:>14.2f} | {result['enc_std_us']:>13.2f} | {result['dec_mean_us']:>14.2f} | {result['dec_std_us']:>13.2f}")

    # Save results
    with open('C:\FI_MUNI\ERASMUS\security_and_privacy\\aes_results.json', "w") as f:
        json.dump(all_results, f, indent=2)

    print("\nResults saved to aes_results.json")
