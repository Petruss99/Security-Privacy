import os
import struct
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

for file in FILE_SIZES:
    with open(f"file_{file}.bin", "rb") as f:
        data = f.read()
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    hash = digest.finalize()