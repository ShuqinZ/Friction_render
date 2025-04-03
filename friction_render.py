import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from utils.pi5RC import pi5RC
from utils.tools import *

# === Hardware Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)  # GPIO18 with working PWM2 on pwmchip2

# === Constants ===
angle_to_distance = -0.21  # mm per degree
angularSpeed = 600  # degrees/s
gear_diameter = 22.0  # mm
spring_rate = 0.16

maxStaticFriction = 0.8
dynamicFriction = 0.4
delta_v = 0.2  # mm/s
initTime = 1.0  # seconds
Kp, Ki, Kd = 0.8, 0, 0
alpha = 0.3  # smoothing factor for low-pass filter

pot_fluc = 0.012

# === State Variables ===
lastSmoothedPosition = None  # to be initialized with first reading
integral = 0
previous_error = 0
servoBaseAngle = 0
detectedForce = 0
calibrated = False
sliding = False
targetPosition = 0
last_angle_change = 0

servo.set(0)
time.sleep(1)

start_time = time.time()
last_time = start_time

try:
    while True:
        now = time.time()
        dt = now - last_time
        last_time = now

        # === Read and smooth position ===
        raw_val = pot.value  # 0–32767
        position = read_potentialmeter(raw_val)

        if lastSmoothedPosition is None:
            smoothedPosition = position
        else:
            smoothedPosition = alpha * position + (1 - alpha) * lastSmoothedPosition

        # === Initialization Phase ===
        if now - start_time < initTime:
            targetPosition = smoothedPosition
            lastSmoothedPosition = smoothedPosition
            previous_error = 0
            continue

        # === Calibration ===
        if not calibrated:
            print("Calibrating...", end=" ")
            frictionForce = 0
            if smoothedPosition > (maxStaticFriction / spring_rate + 4):
                targetPosition = smoothedPosition - 1
            elif smoothedPosition > (maxStaticFriction / spring_rate + 1):
                targetPosition = smoothedPosition - 0.2
            elif smoothedPosition > (maxStaticFriction / spring_rate + 0.1):
                targetPosition = smoothedPosition - 0.1
            elif smoothedPosition > (maxStaticFriction / spring_rate + 0.02):
                targetPosition = smoothedPosition - 0.01
            elif smoothedPosition <= (maxStaticFriction / spring_rate + 0.01):
                calibrated = True
                integral = 0

        else:
            # === Control ===
            detectedForce = smoothedPosition * spring_rate

            if sliding:
                frictionForce = dynamicFriction
            else:
                frictionForce = maxStaticFriction

            targetPosition = frictionForce / spring_rate

        # === PID ===
        velocity = (smoothedPosition - lastSmoothedPosition) / dt
        error = targetPosition - smoothedPosition
        integral += error * dt
        derivative = (error - previous_error) / dt if dt > 0 else 0
        controlSignal = -(Kp * error + Ki * integral + Kd * derivative)
        controlAngle = np.clip(servoBaseAngle + controlSignal, 0, 180)

        servo.set(controlAngle)
        motorVelocity = last_angle_change / dt
        motorVelocity = np.clip(motorVelocity, -angularSpeed, angularSpeed) * angle_to_distance


        external_velocity = velocity - motorVelocity

        if calibrated and not sliding and external_velocity > 3 and smoothedPosition > (maxStaticFriction + spring_rate * pot_fluc) * 1.2:
            sliding = True

        elif calibrated and sliding and external_velocity < -3:
            time.sleep(2)
            sliding = False
            calibrated = False
            servo.set(0)
            lastSmoothedPosition = None  # to be initialized with first reading
            integral = 0
            previous_error = 0
            servoBaseAngle = 0
            detectedForce = 0
            targetPosition = 0
            last_angle_change = 0
            start_time = time.time()
            last_time = start_time
            time.sleep(1)


        previous_error = error

        print(f"{error:.2f}, {controlSignal:.2f}, {controlAngle:.2f}, {targetPosition:.2f}, {smoothedPosition:.2f}, {velocity:.3f}, {motorVelocity:.3f},{external_velocity:.3f}, {frictionForce:.2f}, {detectedForce:.2f}, {100 * (detectedForce - frictionForce)/frictionForce if frictionForce > 0 else 0:.2f}%, {dt:.5f}")
        last_angle_change = controlAngle - servoBaseAngle
        servoBaseAngle = controlAngle
        lastSmoothedPosition = smoothedPosition

        try:
            time.sleep(0.02 - (time.time() - last_time))  # 10ms loop (100Hz)
        except:
            pass

except KeyboardInterrupt:
    print("\nExiting...")
    servo.set(100)
    time.sleep(1)
    del servo
