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

# Load the combined CSV file
df = pd.read_csv("results/Sensor_Compare_Combined.csv")

# Create plot
fig, ax = plt.subplots(figsize=(8, 5))

# Group by sensor and plot each
for sensor, group in df.groupby("Sensor"):
    ax.plot(group["Distance (mm)"], group["Measured Distance (Sensor Output)"],
            marker='o', label=sensor)

# Style the plot
ax.set_xlabel("Ground Truth Distance (mm)")
ax.set_title("Measured Distance (mm)", loc="left")
ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax.legend()


for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/sensor_compare.png", dpi=300)
