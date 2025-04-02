import time
import board
import busio
import numpy as np
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from pi5RC import pi5RC  # your fixed class

# === Hardware Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
pot = AnalogIn(ads, ADS1115.P0)
servo = pi5RC(18)  # GPIO18 with working PWM2 on pwmchip2

# === Constants ===
NUM_SAMPLES = 10
angle_to_distance = 0.0556  # mm per degree
angularSpeed = 0.6  # degrees/ms
gear_diameter = 22.0  # mm
maxStaticFriction = 0.8
dynamicFriction = 0.4
delta_v = 0.5  # mm/s
initTime = 1.0  # seconds
Kp, Ki, Kd = 1.5, 0.05, 2

# === State Variables ===
posBuffer = [0.0] * NUM_SAMPLES
posIndex = 0
lastSmoothedPosition = 0
integral = 0
previous_error = 0
servoBaseAngle = 0
calibrated = False
sliding = False
targetPosition = 0

start_time = time.time()
last_time = start_time

try:
    while True:
        now = time.time()
        dt = now - last_time
        last_time = now

        # === Read and smooth position ===
        raw_val = pot.value  # 0–32767
        position = ((raw_val / 32767.0) * 10.5) / 1.01 + 1
        posBuffer[posIndex] = position
        posIndex = (posIndex + 1) % NUM_SAMPLES
        smoothedPosition = sum(posBuffer) / NUM_SAMPLES

        # === Initialization Phase ===
        if now - start_time < initTime:
            targetPosition = smoothedPosition
            continue

        # === Calibration ===
        if not calibrated:
            print("Calibrating...", end=" ")
            frictionForce = 0
            if smoothedPosition > (maxStaticFriction / 0.16 + 4):
                targetPosition = smoothedPosition - 1
            elif smoothedPosition > (maxStaticFriction / 0.16 + 1):
                targetPosition = smoothedPosition - 0.2
            elif smoothedPosition > (maxStaticFriction / 0.16 + 0.1):
                targetPosition = smoothedPosition - 0.1
            elif smoothedPosition > (maxStaticFriction / 0.16 + 0.02):
                targetPosition = smoothedPosition - 0.01
            elif smoothedPosition <= (maxStaticFriction / 0.16 + 0.01):
                calibrated = True
                integral = 0
            velocity = (smoothedPosition - lastSmoothedPosition) / dt
            lastSmoothedPosition = smoothedPosition

        else:
            # === Control ===
            velocity = (smoothedPosition - lastSmoothedPosition) / dt
            lastSmoothedPosition = smoothedPosition

            detectedForce = smoothedPosition * 0.16
            if not sliding and detectedForce > maxStaticFriction * 1.2:
                sliding = True

            frictionForce = dynamicFriction if sliding else maxStaticFriction
            targetPosition = frictionForce / 0.16

            # === PID ===
            error = targetPosition - smoothedPosition
            integral += error * dt
            derivative = (error - previous_error) / dt if dt > 0 else 0
            controlSignal = -(Kp * error + Ki * integral + Kd * derivative)
            controlAngle = np.clip(servoBaseAngle + controlSignal, 0, 180)
            angle_change = controlAngle - servoBaseAngle
            servoBaseAngle = controlAngle

            motorVelocity = angle_change / dt if dt > 0 else 0
            motorVelocity = np.clip(motorVelocity, -angularSpeed * dt, angularSpeed * dt)
            external_velocity = velocity - motorVelocity * angle_to_distance

            # Only move servo if movement is needed
            if abs(external_velocity) > 0.2:
                servo.set(controlAngle)

            previous_error = error

            # === Logging ===
            print(f"{error:.3f}, {integral:.3f}, {derivative:.3f}, {controlAngle:.2f}, "
                  f"{targetPosition:.2f}, {smoothedPosition:.2f}, {velocity:.3f}, {frictionForce:.2f}")

        time.sleep(0.01)  # 10ms loop (100Hz)

except KeyboardInterrupt:
    print("\nExiting...")
    del servo
