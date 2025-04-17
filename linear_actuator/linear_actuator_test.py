import lgpio
import time

STEP = 21
DIR = 20

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, DIR, 1)
lgpio.gpio_claim_output(h, STEP, 0)

lgpio.gpio_write(h, DIR, 1)  # Set direction

print("Sending step pulses to motor...")
for i in range(200):  # One revolution (if 1.8° per step)
    lgpio.gpio_write(h, STEP, 1)
    time.sleep(0.01)

lgpio.gpiochip_close(h)
print("Done")
