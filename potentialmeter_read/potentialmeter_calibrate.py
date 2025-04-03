import os
import sys

import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.tools import *

# Initialize the I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)

# Define the analog input channel
pot = AnalogIn(ads, ADS.P0)

start_time = time.time()

readings = []

# Loop to read the analog input continuously
while time.time() < start_time + 10:

    pos = read_smoothed_position(pot)
    readings.append(pos)

avg = sum(readings)/len(readings)
max_pos = max(readings)
min_pos = min(readings)
print(f"Average: {avg:.6f}, Upper: {max_pos - avg:.6f}, lower: {min_pos - avg:.6f}")
