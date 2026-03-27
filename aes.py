import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]

key = os.urandom(32)  # 256 bit key

for file in FILE_SIZES:
    with open(f"file_{file}.bin", "rb") as f:
        data = f.read()

    # encrypt
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data) + encryptor.finalize()

    # decrypt
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()