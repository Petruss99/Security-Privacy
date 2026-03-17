import os

# File sizes in bytes (powers of 8, starting at 8)
FILE_SIZES = [8, 64, 512, 4096, 32768, 262144, 2097152]
FILES_DIR = "C:\FI_MUNI\ERASMUS\security_and_privacy"

def generate_files():
    for size in FILE_SIZES:
        path = os.path.join(FILES_DIR, f"file_{size}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(size))
        print(f"Generated: {path} ({size} bytes)")

if __name__ == "__main__":
    generate_files()
    print("\nAll files generated successfully.")
