import os
import timeit
import statistics
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
FILES_DIR = "files"
REPEATS = 100

def sha256_hash(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    return digest.finalize()

def benchmark_sha(size: int) -> dict:
    filepath = os.path.join(FILES_DIR, f"file_{size}.bin")
    with open(filepath, "rb") as f:
        data = f.read()

    times = []
    for _ in range(REPEATS):
        t = timeit.timeit(lambda: sha256_hash(data), number=1)
        times.append(t * 1e6)

    return {
        "size": size,
        "mean_us": statistics.mean(times),
        "std_us": statistics.stdev(times),
    }

if __name__ == "__main__":
    print(f"{'Size (B)':>12} | {'Mean (us)':>12} | {'Std (us)':>11}")
    print("-" * 42)

    all_results = []
    for size in FILE_SIZES:
        result = benchmark_sha(size)
        all_results.append(result)
        print(f"{result['size']:>12} | {result['mean_us']:>12.2f} | {result['std_us']:>11.2f}")

    with open("results/sha_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nResults saved to results/sha_results.json")
