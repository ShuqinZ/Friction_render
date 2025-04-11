import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 16,          # Base font size
    "axes.titlesize": 18,     # Title size
    "axes.labelsize": 16,     # Axis label size
    "xtick.labelsize": 14,    # X tick size
    "ytick.labelsize": 14,    # Y tick size
    "legend.fontsize": 14     # Legend font size
})


model_coeffs = -np.load("assets/servo_model_coeffs.npy")

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.bar(range(len(model_coeffs)), model_coeffs)

ax1.set_xlabel("Command Steps Ago")
ax1.set_title("Influence on Velocity", loc="left")
# ax1.legend(["Influence on Velocity"], loc="upper right")

# Show only bottom and left spines
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)

# Optional grid
ax1.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)

plt.tight_layout()
plt.savefig("results/figs/servo_hysteresis.png", dpi=300)
plt.show()