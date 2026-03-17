import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# --- Load results ---
with open("results/aes_results.json") as f:
    aes = json.load(f)
with open("results/rsa_results.json") as f:
    rsa = json.load(f)
with open("results/sha_results.json") as f:
    sha = json.load(f)

sizes   = [r["size"] for r in aes]
x       = np.array(sizes)
x_ticks = [str(s) for s in sizes]

aes_enc_mean = [r["enc_mean_us"] for r in aes]
aes_enc_std  = [r["enc_std_us"]  for r in aes]
aes_dec_mean = [r["dec_mean_us"] for r in aes]
aes_dec_std  = [r["dec_std_us"]  for r in aes]

rsa_enc_mean = [r["enc_mean_us"] for r in rsa]
rsa_enc_std  = [r["enc_std_us"]  for r in rsa]
rsa_dec_mean = [r["dec_mean_us"] for r in rsa]
rsa_dec_std  = [r["dec_std_us"]  for r in rsa]

sha_mean = [r["mean_us"] for r in sha]
sha_std  = [r["std_us"]  for r in sha]

# --- Shared style ---
plt.rcParams.update({"font.size": 11, "figure.dpi": 130})

def make_plot(ax, x_labels, series, title, ylabel="Time (µs)"):
    xi = np.arange(len(x_labels))
    for label, means, stds, color, marker in series:
        ax.errorbar(xi, means, yerr=stds, label=label,
                    color=color, marker=marker, linewidth=1.8,
                    capsize=4, capthick=1.2, markersize=6)
    ax.set_xticks(xi)
    ax.set_xticklabels(x_labels, rotation=30, ha="right", fontsize=9)
    ax.set_xlabel("File size (bytes)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_yscale("log")


fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("Cryptographic Benchmarks (mean ± std, log scale)", fontsize=13, fontweight="bold")

# Plot 1: AES enc + dec
make_plot(axes[0, 0], x_ticks, [
    ("AES Encrypt", aes_enc_mean, aes_enc_std, "steelblue", "o"),
    ("AES Decrypt", aes_dec_mean, aes_dec_std, "darkorange", "s"),
], "AES-CTR (256-bit key)")

# Plot 2: RSA enc + dec
make_plot(axes[0, 1], x_ticks, [
    ("RSA Encrypt", rsa_enc_mean, rsa_enc_std, "mediumseagreen", "o"),
    ("RSA Decrypt", rsa_dec_mean, rsa_dec_std, "tomato", "s"),
], "RSA Hybrid (2048-bit key)")

# Plot 3: AES enc vs SHA
make_plot(axes[1, 0], x_ticks, [
    ("AES Encrypt", aes_enc_mean, aes_enc_std, "steelblue", "o"),
    ("SHA-256",     sha_mean,     sha_std,      "purple",    "^"),
], "AES Encrypt vs SHA-256")

# Plot 4: AES enc vs RSA enc
make_plot(axes[1, 1], x_ticks, [
    ("AES Encrypt", aes_enc_mean, aes_enc_std, "steelblue", "o"),
    ("RSA Encrypt", rsa_enc_mean, rsa_enc_std, "mediumseagreen", "o"),
], "AES Encrypt vs RSA Encrypt")

plt.tight_layout()
plt.savefig("results/crypto_benchmarks.png", bbox_inches="tight")
print("Plot saved to results/crypto_benchmarks.png")
