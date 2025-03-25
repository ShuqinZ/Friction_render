import math
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import signal
import sys

# Use pigpio backend (requires pigpiod daemon running!)
factory = PiGPIOFactory()  # Connects to localhost:8888 by default

servo = Servo(15, pin_factory=factory, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

def cleanup(signum=None, frame=None):
    print("Cleaning up...")
    servo.detach()
    servo.close()
    factory.close()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    while True:
        for i in range(0, 360):
            servo.value = math.sin(math.radians(i))
            sleep(0.01)
except Exception as e:
    print("Error occurred:", e)
    cleanup()
