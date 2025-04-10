import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file (please upload if not yet available)
csv_path = "logs/force_error_log_h_final.csv"
df = pd.read_csv(csv_path)

# Create a single figure with two subplots
fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# Plot 1: Desired vs Rendered Force
axs[0].plot(df["Time (s)"], df["Desired force"], label="Desired Force", linestyle='--')
axs[0].plot(df["Time (s)"], df["Rendered Force"], label="Rendered Force")
axs[0].set_ylabel("Force (N)")
axs[0].set_title("Force and Error Over Time")
axs[0].legend()
axs[0].grid(True)

# Plot 2: Percentage of Error
axs[1].plot(df["Time (s)"], df["Percentage of Error"], label="Error (%)", color='red')
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Percentage of Error (%)")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.savefig("results/figs/force_and_error_combined_plot.png")
