import os
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load CSVs ---
def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

aes = load_csv("aes_results.csv")
rsa = load_csv("rsa_results.csv")
sha = load_csv("sha_results.csv")

sizes      = [int(r["size_bytes"]) for r in aes]
size_labels = [str(s) for s in sizes]

aes_enc_mean = [float(r["enc_mean_us"])  for r in aes]
aes_enc_std  = [float(r["enc_std_us"])   for r in aes]
aes_dec_mean = [float(r["dec_mean_us"])  for r in aes]
aes_dec_std  = [float(r["dec_std_us"])   for r in aes]

rsa_enc_mean = [float(r["enc_mean_us"])  for r in rsa]
rsa_enc_std  = [float(r["enc_std_us"])   for r in rsa]
rsa_dec_mean = [float(r["dec_mean_us"])  for r in rsa]
rsa_dec_std  = [float(r["dec_std_us"])   for r in rsa]

sha_mean = [float(r["mean_us"]) for r in sha]
sha_std  = [float(r["std_us"])  for r in sha]

xi = np.arange(len(sizes))

# --- Shared plot style ---
plt.rcParams.update({"font.size": 10, "figure.dpi": 150})

def styled_plot(ax, series, title):
    for label, means, stds, color, marker in series:
        ax.errorbar(xi, means, yerr=stds, label=label,
                    color=color, marker=marker, linewidth=1.8,
                    capsize=4, capthick=1.2, markersize=6, zorder=3)
    ax.set_xticks(xi)
    ax.set_xticklabels(size_labels, rotation=30, ha="right", fontsize=8)
    ax.set_xlabel("File size (bytes)")
    ax.set_ylabel("Time (µs)")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_yscale("log")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("Cryptographic Benchmark Results (mean ± std, log scale)", fontsize=13, fontweight="bold", y=1.01)

# Plot 1 — AES enc + dec
styled_plot(axes[0, 0], [
    ("AES-CTR Encrypt", aes_enc_mean, aes_enc_std, "steelblue",     "o"),
    ("AES-CTR Decrypt", aes_dec_mean, aes_dec_std, "darkorange",    "s"),
], "AES-CTR Encryption & Decryption (256-bit key)")

# Plot 2 — RSA enc + dec
styled_plot(axes[0, 1], [
    ("RSA Encrypt", rsa_enc_mean, rsa_enc_std, "mediumseagreen", "o"),
    ("RSA Decrypt", rsa_dec_mean, rsa_dec_std, "tomato",         "s"),
], "RSA Hybrid Encryption & Decryption (2048-bit key)")

# Plot 3 — AES enc vs SHA
styled_plot(axes[1, 0], [
    ("AES-CTR Encrypt", aes_enc_mean, aes_enc_std, "steelblue", "o"),
    ("SHA-256",         sha_mean,     sha_std,      "purple",    "^"),
], "AES-CTR Encryption vs SHA-256")

# Plot 4 — AES enc vs RSA enc
styled_plot(axes[1, 1], [
    ("AES-CTR Encrypt", aes_enc_mean, aes_enc_std, "steelblue",     "o"),
    ("RSA Encrypt",     rsa_enc_mean, rsa_enc_std, "mediumseagreen","o"),
], "AES-CTR Encryption vs RSA Encryption")

plt.tight_layout()
output_path = os.path.join(BASE_DIR, "crypto_benchmarks.png")
plt.savefig(output_path, bbox_inches="tight")
print(f"Plot saved to {output_path}")
