from pi5RC import pi5RC
import time

# Create servo instance on GPIO18
servo = pi5RC(18)

try:
    print("Centering servo...")
    servo.set(1500)  # center
    time.sleep(1)

    print("Sweeping servo from 0° to 180°...")
    for pulse in range(1000, 2000 + 1, 10):  # sweep right
        servo.set(pulse)
        time.sleep(0.01)

    print("Sweeping servo back from 180° to 0°...")
    for pulse in range(2000, 1000 - 1, -10):  # sweep left
        servo.set(pulse)
        time.sleep(0.01)

    print("Returning to center...")
    servo.set(1500)
    time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    del servo  # clean up PWM and pin state
