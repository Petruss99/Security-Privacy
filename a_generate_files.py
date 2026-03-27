import os

FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_files():
    for size in FILE_SIZES:
        path = os.path.join(BASE_DIR, f"file_{size}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(size))
        print(f"Generated: {path} ({size} bytes)")

if __name__ == "__main__":
    generate_files()
    print("\nAll files generated successfully.")