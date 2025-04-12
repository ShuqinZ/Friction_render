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

# --- Plot 1: Desired vs Rendered Force ---
fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(df["Time (s)"], df["Desired force"], label="Karnopp Model", linestyle='--')

ax1.axvline(x=interaction_time, color='gray', linestyle='--', linewidth=1, label="User Interaction")

ax1.set_ylim(0, 1)  # Set x-axis limits from 0 to 1

ax1.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax1.plot(df["Time (s)"], df["Rendered Force"], label="Rendered Force")
ax1.set_xlabel("Time (s)")
ax1.set_title("Force (N)", loc="left")
ax1.legend()


# Show only bottom and left spines
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/force_plot.png", dpi=300)

# --- Plot 2: Percentage of Error ---
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.plot(df["Time (s)"], df["Percentage of Error"], label="Difference (%)", color='red')

ax2.axvline(x=interaction_time, color='gray', linestyle='--', linewidth=1, label="User Interaction")

ax2.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax2.set_xlabel("Time (s)")
ax2.set_title("Percentage of Difference (%)", loc="left")

tick_locs = [0.1, 1, 10, 100]
tick_labels = ["0.1", "1", "10", "100"]
ax2.set_yscale("log")
ax2.set_yticks(tick_locs)
ax2.set_yticklabels(tick_labels)

ax2.legend()

# Show only bottom and left spines
for spine in ["top", "right"]:
    ax2.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/error_plot.png", dpi=300)

df['Handler Velocity'] = -df['Handler Velocity']
df['Calculated Desired Force'] = df['Handler Velocity'].apply(lambda v: 0.8 if v < 0.2 else 0.4)


fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.plot([0, 0.2], [0.8, 0.8], color='#1f77b4', linestyle='--', linewidth=1, label="Friction Reference")
ax3.plot([0.2, 100], [0.4, 0.4], color='#1f77b4', linestyle='--', linewidth=1)
# ax3.scatter(df['Handler Velocity'], df['Calculated Desired Force'], label='Karnopp Model', alpha=0.7, linestyle='--')
ax3.scatter(df['Handler Velocity'], df['Rendered Force'], color='#ff7f0e', marker='x', s=20, label='Rendered Force', alpha=0.7)

ax3.axvline(x=0.2, color='gray', linestyle='--', linewidth=1, label="Stick to slip")

ax3.set_ylim(0, 1)  # Set x-axis limits from 0 to 1
ax3.set_xlim(0.01, 22)  # Set x-axis limits from 0 to 1
ax3.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax3.set_xlabel(r"log scale $v_{\mathrm{ext}}$ (mm/s)")
ax3.set_title("Force (N)", loc="left")
tick_locs = [0.01, 0.1, 0.2, 1, 10, 22]
tick_labels = [0.01, 0.1, 0.2, 1, 10, 22]

ax3.set_xscale("log")
ax3.set_xticks(tick_locs)
ax3.set_xticklabels(tick_labels)
ax3.legend()

# Show only bottom and left spines
for spine in ["top", "right"]:
    ax3.spines[spine].set_visible(False)
plt.tight_layout()

plt.savefig("results/figs/force_by_v.png", dpi=300)

fig4, ax4 = plt.subplots(figsize=(8, 5))
ax4.scatter(df['Handler Velocity'], df['Percentage of Error'],  marker='x', s=20, color='red', alpha=0.7, label='Percentage of Difference (%)')

ax4.axvline(x=0.2, color='gray', linestyle='--', linewidth=1, label="Stick to slip")
tick_locs = [0.01, 0.1, 0.2, 1, 10, 22]
tick_labels = [0.01, 0.1, 0.2, 1, 10, 22]
ax4.set_xscale("log")
ax4.set_xticks(tick_locs)
ax4.set_xticklabels(tick_labels)

ax4.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
ax4.set_title("Percentage of Difference (%)", loc="left")
ax4.set_xlim(0.01, 22)
ax4.legend()

ax4.set_xlabel(r"log scale $v_{\mathrm{ext}}$ (mm/s)")
# Show only bottom and left spines
for spine in ["top", "right"]:
    ax4.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("results/figs/error_by_v.png", dpi=300)
