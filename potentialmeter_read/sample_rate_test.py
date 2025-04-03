import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Optional: change data rate (default is 128 samples/sec)
ads.data_rate = 860  # max supported for ADS1115

# Setup input channel
channel = AnalogIn(ads, ADS.P0)

# Sampling rate test
num_samples = 0
start_time = time.time()
duration = 5  # seconds

while time.time() - start_time < duration:
    _ = channel.value  # just read it
    num_samples += 1

elapsed_time = time.time() - start_time
print(f"Total samples: {num_samples}")
print(f"Elapsed time: {elapsed_time:.4f} seconds")
print(f"Sampling rate: {num_samples / elapsed_time:.2f} samples/second")
