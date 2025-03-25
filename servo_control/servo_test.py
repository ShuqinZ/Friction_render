from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import signal
import sys

# Use lgpio backend explicitly
factory = PiGPIOFactory()

# Set up the servo
servo = Servo(14, pin_factory=factory)
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
        for angle in range(-90, 91, 1):
            servo.angle = angle
            sleep(0.2)
        for angle in range(90, -91, -1):
            servo.angle = angle
            sleep(0.2)

except Exception as e:
    print("Error occurred:", e)
    cleanup()
