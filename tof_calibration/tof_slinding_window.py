import numpy as np
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use("MACOSX")
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

def load_data(directory, filename):
    filepath = os.path.join(directory, filename)

    df = pd.read_csv(filepath)
    return df


def get_percentage_of_error(data, baseline):
    errors = data - baseline
    percentage_error = (errors / baseline) * 100
    return np.array(percentage_error)


def plot_percentage_error(directory, actual_distances, window_duration):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 10))

    for ax, gt_distance in zip(axes.flat, actual_distances):
        filename = f"W{window_duration}_D{gt_distance}_C20"

        data = load_data(directory, filename + ".csv")

        min_value = get_percentage_of_error(data["Min"], gt_distance)
        max_value = get_percentage_of_error(data["Max"], gt_distance)
        avg_value = get_percentage_of_error(data["Avg"], gt_distance)
        time_line = np.array(data["Time"])

        # Plot the percentage error over time

        ax.errorbar(time_line, avg_value, yerr=[avg_value-min_value, max_value-avg_value], linestyle='-', fmt='none', linewidth=1, capsize=1, color=colors[0], zorder=1)
        ax.plot(time_line, avg_value, marker='o', markersize=2, linestyle='-', linewidth=1, color=colors[1], zorder=2)

        ax.set_xlabel("Time Step")
        ax.set_ylabel("Percentage Error (%)")
        ax.set_title(f"{gt_distance} mm Error Rate")

    # plt.grid(True)
    fig.suptitle(f"Sliding Window Duration: {window_duration}ms", fontsize=16)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{directory}/W{window_duration}.png", dpi=300)


true_distances = [25, 30, 50, 100]  # Corresponding true values\
window_durations = [50, 100, 1000]

for window_duration in window_durations:
    plot_percentage_error("./results/VL53L0X", true_distances, window_duration)
