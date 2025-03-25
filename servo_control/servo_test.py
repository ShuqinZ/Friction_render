from gpiozero import Servo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep
import signal
import sys

# Use lgpio backend explicitly
factory = LGPIOFactory()

# Set up the servo
servo = Servo(15, pin_factory=factory)

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
        servo.min()
        sleep(1)
        servo.mid()
        sleep(1)
        servo.max()
        sleep(1)

except Exception as e:
    print("Error occurred:", e)
    cleanup()
