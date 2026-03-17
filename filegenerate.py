import os
import random
import string

sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]

for size in sizes:
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    with open(f"file_{size}.txt", "w") as f:
        f.write(content)

print("Files generated!")