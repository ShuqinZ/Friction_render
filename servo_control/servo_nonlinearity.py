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

step_sizes = [0.05, 0.1, 0.5, 0.6, 0.7, 0.8, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 10, 45]
start_angle = 20
csv_filename = "servo_velocity_calibration.csv"

# === Start test ===
try:
    print("Measuring angle-to-distance scale...")
    servo.set(start_angle, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(1.5)
    pos_start = read_smoothed_position(pot)

    servo.set(60, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(2.0)
    pos_end = read_smoothed_position(pot)

    angle_to_distance = (pos_end - pos_start) / (60 - start_angle)
    print(f"angle_to_distance: {angle_to_distance:.5f} mm/deg")

    results = []

    print("\n=== Running Step Tests ===")
    for step in step_sizes:
        from_angle = start_angle
        to_angle = start_angle + step

        if to_angle > 60:
            print(f"Skipping step size {step}° — exceeds 60°")
            continue

        print(f"\nStep: {step:.2f}° from {from_angle}° to {to_angle}°")

        servo.set(0, angle_range=max_angle, pulse_range=pwm_range)
        time.sleep(1.5)

        servo.set(from_angle, angle_range=max_angle, pulse_range=pwm_range)
        time.sleep(1.5)
        pos1 = read_smoothed_position(pot)

        start_time = time.time()
        move_time = start_time
        servo.set(to_angle, angle_range=max_angle, pulse_range=pwm_range)
        # Wait briefly for movement to complete
        # time.sleep(0.1)  # start delay to ensure motion starts
        last_position = None
        while True:
            pos2 = read_smoothed_position(pot)

            if last_position is not None:
                pos2 = alpha * pos2 + (1 - alpha) * last_position
            if abs(pos2 - pos1) > pos1 + 0.002:  # close enough
                move_time = time.time()
            if last_position is not None and abs(pos2 - last_position) < 0.002:  # close enough
                break
            last_position = pos2
            print(f"{pos2}, ")
            # time.sleep(0.01)
        end_time = time.time()

        delay = move_time - start_time
        duration = end_time - start_time
        distance_moved = pos2 - pos1
        velocity = distance_moved / duration if duration > 0 else 0

        angle_to_distance = (pos2 - pos1) / (to_angle - from_angle)

        print(
            f"Moved {distance_moved:.4f} mm in {duration:.4f} s, delay:{delay:.4f} s — angle_to_distance: {angle_to_distance:.5f} mm/deg, velocity: {velocity:.4f} mm/s")

        results.append({
            "step_deg": step,
            "distance_mm": distance_moved,
            "duration_s": duration,
            "velocity_mm_per_s": velocity
        })

    # === Write CSV ===
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["step_deg", "distance_mm", "duration_s", "velocity_mm_per_s"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nSaved results to {csv_filename}")

except KeyboardInterrupt:
    print("Aborted by user.")
finally:
    del servo
