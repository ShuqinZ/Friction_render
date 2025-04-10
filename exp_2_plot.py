import pandas as pd
import matplotlib.pyplot as plt

# Set global font sizes
plt.rcParams.update({
    "font.size": 16,          # Base font size
    "axes.titlesize": 18,     # Title size
    "axes.labelsize": 16,     # Axis label size
    "xtick.labelsize": 14,    # X tick size
    "ytick.labelsize": 14,    # Y tick size
    "legend.fontsize": 14     # Legend font size
})

# Load the CSV file
csv_path = "logs/force_error_log_h_final_4.csv"
df = pd.read_csv(csv_path)

# Filter data after 2.8 seconds
df = df[df["Time (s)"] > 2.8].copy()

df = df[df["Time (s)"] < 5].copy()

# Reset time to start from zero
df["Time (s)"] = df["Time (s)"] - 2.8

# --- Plot 1: Desired vs Rendered Force ---
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df["Time (s)"], df["Desired force"], label="Commanded Friction", linestyle='--')

ax1.axvline(x=0.6, color='gray', linestyle='--', linewidth=1, label="Human Interaction")

ax1.plot(df["Time (s)"], df["Rendered Force"], label="Rendered Force")
ax1.set_xlabel("Time (s)")
ax1.set_title("Force (N)", loc="left")
ax1.legend()

# Show only bottom and left spines
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/force_plot.png")

# --- Plot 2: Percentage of Error ---
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(df["Time (s)"], df["Percentage of Error"], label="Difference (%)", color='red')

ax2.axvline(x=0.6, color='gray', linestyle='--', linewidth=1, label="Human Interaction")

ax2.set_xlabel("Time (s)")
ax2.set_title("Percentage of Difference (%)", loc="left")
ax2.set_yscale("symlog", linthresh=1e-2)  # Log-like, but allows negatives
ax2.legend()

# Show only bottom and left spines
for spine in ["top", "right"]:
    ax2.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/error_plot.png")
