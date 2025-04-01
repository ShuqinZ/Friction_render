from time import sleep

from utils.pi5RC import pi5RC

servo = pi5RC(18)  # GPIO18 is PWM-capable on Pi 5

# Sweep servo slowly
try:
    while True:
        for pulse in range(500, 2500, 100):  # microseconds
            servo.set(pulse)
            sleep(0.02)
        for pulse in range(2500, 500, -100):
            servo.set(pulse)
            sleep(0.02)
except KeyboardInterrupt:
    del servo
