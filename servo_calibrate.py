import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from utils.pi5RC import pi5RC

# === Setup ===
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)  # GPIO18 using pwmchip2/pwm2

NUM_SAMPLES = 20

calibrate_angle = [15, 60]


def read_smoothed_position():
    vals = []
    for _ in range(NUM_SAMPLES):
        raw = pot.value
        pos = ((raw / 32767.0) * 10.5) / 1.01 + 1  # same mapping as your main script
        vals.append(pos)
        time.sleep(0.005)
    return sum(vals) / len(vals)


try:
    print("Measuring initial position...")
    servo.set(calibrate_angle[0])
    time.sleep(1.5)
    pos_start = read_smoothed_position()
    print(f"Position at {calibrate_angle[0]}°: {pos_start:.3f} mm")

    print(f"Moving to {calibrate_angle[1]}°...")
    angle = calibrate_angle[1]
    servo.set(angle)
    time.sleep(2.0)
    pos_end = read_smoothed_position()
    print(f"Position at {calibrate_angle[1]}°: {pos_end:.3f} mm")

    distance_change = pos_end - pos_start
    angle_change = calibrate_angle[1] - calibrate_angle[0]
    angle_to_distance = distance_change / angle_change

    print("\n=== Calibration Result ===")
    print(f"Potentiometer distance change: {distance_change:.3f} mm")
    print(f"Servo angle change: {angle_change}°")
    print(f"\033[92mEstimated angle_to_distance: {angle_to_distance:.5f} mm/deg\033[0m")

except KeyboardInterrupt:
    print("Aborted by user.")

finally:
    del servo
