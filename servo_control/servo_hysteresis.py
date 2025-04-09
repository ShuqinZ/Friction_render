import time
import csv
import board
import busio
import numpy as np
import matplotlib.pyplot as plt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import sys
import os
from sklearn.linear_model import LinearRegression

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.pi5RC import pi5RC
from utils.tools import *

# === Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)

alpha = 0.3
max_angle = 120
pwm_range = (900, 2100)
timestep = 0.2
start_angle = 20
num_steps = 200
max_history = 10  # Number of past commands to analyze

# Generate bounded random sequence of angles (between 15° and 60°)
np.random.seed(42)
current_angle = start_angle
angle_sequence = []

for _ in range(num_steps):
    delta = np.random.choice([-5, -4, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 4, 5])
    next_angle = current_angle + delta
    # Clamp angle to [15, 60]
    next_angle = max(15, min(60, next_angle))
    angle_sequence.append(next_angle)
    current_angle = next_angle

# Warm up
servo.set(start_angle, angle_range=max_angle, pulse_range=pwm_range)
time.sleep(1.0)

print("Starting data collection...")

# === Data collection ===
for i in range(num_steps):
    if i > 0:
        last_angle = angle_sequence[i-1]
    else:
        last_angle = start_angle

    current_angle = angle_sequence[i]
    angle_delta = current_angle - last_angle

    servo.set(current_angle, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(timestep - 0.01)

    pos = read_potentialmeter(pot.value)
    positions.append(pos)
    if i > 0:
        distance = pos - positions[-2]
        velocity = distance / timestep
        velocities.append(velocity)
        angle_deltas.append(angle_delta)

# Pad data for history regression
X = []
y = []

for i in range(max_history, len(velocities)):
    past_deltas = angle_deltas[i-max_history+1:i+1]  # includes current step
    X.append(past_deltas[::-1])  # recent command first
    y.append(velocities[i])

X = np.array(X)
y = np.array(y)

# === Fit linear model ===
model = LinearRegression()
model.fit(X, y)
coeffs = model.coef_

print("\n=== Hysteresis Analysis ===")
for i, coef in enumerate(coeffs):
    print(f"Step t-{i}: coeff = {coef:.5f}")

print(f"\nR^2 Score: {model.score(X, y):.3f}")

# === Save data ===
with open("servo_command_history_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t_minus_" + str(i) for i in range(max_history)] + ["velocity"])
    for row_x, row_y in zip(X, y):
        writer.writerow(list(row_x) + [row_y])

print("Data saved to servo_command_history_analysis.csv")

# === Visualization ===
plt.figure(figsize=(8, 5))
plt.bar(range(max_history), coeffs)
plt.xlabel("Command Steps Ago (t - k)")
plt.ylabel("Influence on Velocity")
plt.title("Influence of Past Commands on Current Velocity")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Cleanup ===
del servo
