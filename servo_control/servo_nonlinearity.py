import time
import csv
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pi5RC import pi5RC
from utils.tools import *

# === Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)  # GPIO18 using pwmchip2/pwm2

alpha = 0.3

max_angle = 120
# pwm_range = (500, 2400)
pwm_range = (900, 2100)

step_sizes = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 1.2, 1.5, 1.7, 2, 2.2, 2.5, 2.7, 3, 3.5, 4, 4.5, 5, 7, 10, 15, 20, 30, 45]
start_angle = 20
csv_filename = "servo_velocity_calibration.csv"

# === Start test ===
try:
    print("Measuring angle-to-distance scale...")
    servo.set(start_angle, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(1.5)
    pos_start = read_smoothed_position(pot)

    # servo.set(60, angle_range=max_angle, pulse_range=pwm_range)
    # time.sleep(2.0)
    # pos_end = read_smoothed_position(pot)
    #
    # angle_to_distance = (pos_end - pos_start) / (60 - start_angle)
    # print(f"angle_to_distance: {angle_to_distance:.5f} mm/deg")

    results = []

    print("\n=== Running Step Tests ===")

    for i in range(3):
        for step in step_sizes:
            from_angle = start_angle
            to_angle = start_angle + step

            if to_angle > 60:
                print(f"Skipping step size {step}° — exceeds 60°")
                continue

            print(f"\nStep: {step:.2f}° from {from_angle}° to {to_angle}°")

            servo.set(0, angle_range=max_angle, pulse_range=pwm_range)
            time.sleep(2)

            servo.set(from_angle, angle_range=max_angle, pulse_range=pwm_range)
            time.sleep(1.5)
            pos1 = read_smoothed_position(pot)

            servo.set(to_angle, angle_range=max_angle, pulse_range=pwm_range)
            time.sleep(0.019)
            pos2 = read_potentialmeter(pot)

            distance_moved = pos2 - pos1
            velocity = distance_moved / 0.2

            results.append({
                "distance_mm": distance_moved,
                "duration_s": 0.2,
                "velocity_mm_per_s": velocity
            })

    # === Write CSV ===
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["distance_mm", "duration_s", "velocity_mm_per_s"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nSaved results to {csv_filename}")

except KeyboardInterrupt:
    print("Aborted by user.")
finally:
    del servo
