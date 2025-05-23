
import time

from utils.pi5RC import pi5RC

# Create servo instance on GPIO18
servo = pi5RC(18)

try:
    print("Centering servo...")
    servo.set_pwm(1500)  # center
    time.sleep(1)

    print("Sweeping servo from 0° to 180°...")
    for pulse in range(1000, 2000 + 1, 10):  # sweep right
        servo.set_pwm(pulse)
        time.sleep(0.01)

    print("Sweeping servo back from 180° to 0°...")
    for pulse in range(2000, 1000 - 1, -10):  # sweep left
        servo.set_pwm(pulse)
        time.sleep(0.01)

    print("Returning to center...")
    servo.set_pwm(1500)
    time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    del servo  # clean up PWM and pin state
