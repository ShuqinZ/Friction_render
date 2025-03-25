from gpiozero import AngularServo
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

Device.pin_factory = LGPIOFactory()

# Set up servo on GPIO 17 (change if needed)
servo = AngularServo(17, min_pulse_width=0.0006, max_pulse_width=0.0023)

try:
    while True:
        for angle in range(-90, 91, 10):  # Sweep from -90 to 90
            servo.angle = angle
            sleep(0.05)
        for angle in range(90, -91, -10):  # Sweep back
            servo.angle = angle
            sleep(0.05)

finally:
    servo.angle = 0
