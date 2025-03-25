from gpiozero import AngularServo, Device
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep
import signal
import sys

# Use lgpio backend explicitly
factory = LGPIOFactory()
Device.pin_factory = factory

# Set up the servo
servo = AngularServo(15, min_pulse_width=0.0006, max_pulse_width=0.0023)

# Graceful exit on Ctrl+C or script exit
def cleanup(signum=None, frame=None):
    print("Cleaning up...")
    servo.detach()  # Optional: detaches the signal from the pin
    servo.close()   # Required: tells gpiozero to release the pin
    factory.close() # Required: tells lgpio to release the handle
    sys.exit(0)

# Register the cleanup handler
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Example: sweep servo back and forth
try:
    while True:
        for angle in range(-90, 91, 10):
            servo.angle = angle
            # sleep(0.05)
        for angle in range(90, -91, -10):
            servo.angle = angle
            # sleep(0.05)

except Exception as e:
    print("Error occurred:", e)
    cleanup()
