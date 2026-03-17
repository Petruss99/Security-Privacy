import os
import timeit
import statistics
import json
import struct

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- Configuration ---
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
FILES_DIR = "C:\FI_MUNI\ERASMUS\security_and_privacy"
KEY_SIZE_BITS = 2048
# r size: PKCS1v15 allows at most key_size_bytes - 11 = 245 bytes.
# We use 128 bytes (1024 bits) — more than enough security for a random seed.
R_SIZE_BYTES = 128
HASH_BLOCK_SIZE = 32    # SHA-256 output = 32 bytes
REPEATS = 20

# --- Generate RSA key pair (done once) ---
print("Generating 2048-bit RSA key pair (this takes a moment)...")
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=KEY_SIZE_BITS,
    backend=default_backend()
)
public_key = private_key.public_key()
print("Key pair ready.\n")

# --- H(i, r): SHA-256 of (4-byte counter || r) ---
def H(i: int, r: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(struct.pack(">I", i))
    digest.update(r)
    return digest.finalize()

# --- RSA Hybrid Encryption ---
def rsa_hybrid_encrypt(plaintext: bytes) -> tuple:
    r = os.urandom(R_SIZE_BYTES)
    enc_r = public_key.encrypt(r, padding.PKCS1v15())

    n = (len(plaintext) + HASH_BLOCK_SIZE - 1) // HASH_BLOCK_SIZE
    blocks = []
    for i in range(n):
        block = plaintext[i * HASH_BLOCK_SIZE : (i + 1) * HASH_BLOCK_SIZE]
        keystream = H(i, r)[:len(block)]
        blocks.append(bytes(a ^ b for a, b in zip(block, keystream)))

    return enc_r, blocks

# --- RSA Hybrid Decryption ---
def rsa_hybrid_decrypt(enc_r: bytes, blocks: list) -> bytes:
    r = private_key.decrypt(enc_r, padding.PKCS1v15())
    parts = []
    for i, block in enumerate(blocks):
        keystream = H(i, r)[:len(block)]
        parts.append(bytes(a ^ b for a, b in zip(block, keystream)))
    return b"".join(parts)

# --- Benchmark ---
def benchmark_rsa(size: int) -> dict:
    filepath = os.path.join(FILES_DIR, f"file_{size}.bin")
    with open(filepath, "rb") as f:
        plaintext = f.read()

    enc_times = []
    dec_times = []

    for _ in range(REPEATS):
        t_enc = timeit.timeit(lambda: rsa_hybrid_encrypt(plaintext), number=1)
        enc_times.append(t_enc * 1e6)

        enc_r, blocks = rsa_hybrid_encrypt(plaintext)

        t_dec = timeit.timeit(lambda: rsa_hybrid_decrypt(enc_r, blocks), number=1)
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
        result = benchmark_rsa(size)
        all_results.append(result)
        print(f"{result['size']:>12} | {result['enc_mean_us']:>14.2f} | {result['enc_std_us']:>13.2f} | {result['dec_mean_us']:>14.2f} | {result['dec_std_us']:>13.2f}")

    with open("C:\FI_MUNI\ERASMUS\security_and_privacy\\rsa_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nResults saved to rsa_results.json")
