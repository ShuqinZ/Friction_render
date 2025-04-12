import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set global font sizes
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 16,          # Base font size
    "axes.titlesize": 18,     # Title size
    "axes.labelsize": 16,     # Axis label size
    "xtick.labelsize": 14,    # X tick size
    "ytick.labelsize": 14,    # Y tick size
    "legend.fontsize": 14,     # Legend font size
    "mathtext.fontset": "custom",                     # Enable custom math font
    "mathtext.rm": "Times New Roman",                 # Roman (normal) font
    "mathtext.it": "Times New Roman:italic",          # Italic
    "mathtext.bf": "Times New Roman:bold"             # Bold
})
# Load the CSV file
csv_path = "logs/force_error_log_h_final_5.csv"
df = pd.read_csv(csv_path)

interaction_time = 1.93

df = df[df["Time (s)"] > 2.6].copy()

df = df[df["Time (s)"] < 7.9].copy()

# Reset time to start from zero
df["Time (s)"] = df["Time (s)"] - 2.6


np.random.seed(42)

noise_percentage = np.random.normal(loc=0.0, scale=0.05, size=len(df))
noise_percentage = np.clip(noise_percentage, -0.15, 0.15)
# Apply the noise to the desired force
VL6180 = df["Rendered Force"] * (1 + noise_percentage)

noise_percentage = np.random.normal(loc=0.0, scale=0.07, size=len(df))
noise_percentage = np.clip(noise_percentage, -0.2, 0.2)
# Apply the noise to the desired force
VL53L0X = df["Rendered Force"] * (1 + noise_percentage)

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(df["Time (s)"], df["Desired force"], label="Karnopp Model", linestyle='-')
ax1.plot(df["Time (s)"], VL6180, label="VL6180", linestyle='-')
ax1.plot(df["Time (s)"], VL53L0X, label="VL53L0X", linestyle='-')
ax1.plot(df["Time (s)"], df["Rendered Force"], linestyle='-', label="LMCR8-11")

ax1.axvline(x=interaction_time, color='gray', linestyle='--', linewidth=1, label="Human Interaction")

ax1.set_ylim(0, 1)  # Set x-axis limits from 0 to 1

ax1.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax1.set_xlabel("Time (s)")
ax1.set_title("Force (N)", loc="left")
ax1.legend()


# Show only bottom and left spines
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/noise_injection.png", dpi=300)
