import lgpio
import time

# GPIO pin numbers
STEP_PIN = 21
DIR_PIN = 20

# Open the GPIO chip (0 = default)
h = lgpio.gpiochip_open(0)

# Set both pins as output
lgpio.gpio_claim_output(h, DIR_PIN, 1)  # Set DIR to HIGH (1)
lgpio.gpio_claim_output(h, STEP_PIN, 0) # Start STEP at LOW (0)

# Direction: 1 = forward, 0 = reverse
lgpio.gpio_write(h, DIR_PIN, 1)

# Create a pulse waveform for STEP pin
freq = 500  # step frequency in Hz
duration = 3  # how long to run (seconds)

delay_us = int(1_000_000 / (freq * 2))  # half-period

print(f"Running motor at {freq} Hz for {duration} seconds...")

end_time = time.time() + duration
while time.time() < end_time:
    lgpio.gpio_write(h, STEP_PIN, 1)
    time.sleep(delay_us / 1_000_000)
    lgpio.gpio_write(h, STEP_PIN, 0)
    time.sleep(delay_us / 1_000_000)

# Cleanup
lgpio.gpiochip_close(h)
print("Motor stopped.")
