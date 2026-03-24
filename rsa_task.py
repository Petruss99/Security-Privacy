import os
import struct
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()



for file in FILE_SIZES:
    r = os.urandom(32)

    cipher_r = public_key.encrypt(r, padding.PKCS1v15())
    result = []
    blocks = file // 32
    if file % 32 != 0:
        blocks += 1
    with open(f"file_{file}.bin", "rb") as f:
            data = f.read()
    for i in range(blocks):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(r)
        digest.update(struct.pack(">Q", i))
        hash = digest.finalize()
        cur = data[i*32 : (i+1)*32]
        for a, b in zip(hash, cur):
            result.append(a ^ b)
    result = bytes(result)
    final = (cipher_r, result)   
    enc_blocks = final[1]
    r_decrypted = private_key.decrypt(cipher_r, padding.PKCS1v15())

    result_decrypt = []
    for i in range(blocks):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(r_decrypted)
        digest.update(struct.pack(">Q", i))
        hash = digest.finalize()
        cur = enc_blocks[i*32 : (i+1)*32]
        for a, b in zip(hash, cur):
            result_decrypt.append(a ^ b)
    result_decrypt = bytes(result_decrypt)



