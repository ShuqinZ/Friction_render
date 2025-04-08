import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import joblib

from utils.pi5RC import pi5RC
from utils.tools import *

# === Hardware Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)  # GPIO18 with working PWM2 on pwmchip2
model = joblib.load('assets/servo_angle_to_speed_model.pkl')

# === Constants ===
# angle_to_distance = -0.21  # mm per degree
angle_to_distance = -0.18  # mm per degree
angularSpeed = 600  # degrees/s
gear_diameter = 22.0  # mm
spring_rate = 0.16

max_angle = 120
# pwm_range = (500, 2400)
pwm_range = (900, 2100)

maxStaticFriction = 0.8
dynamicFriction = 0.4
delta_v = 0.2  # mm/s
initTime = 1.0  # seconds
Kp, Ki, Kd = 0.8, 0, 0
alpha = 0.3  # smoothing factor for low-pass filter

pot_fluc = 0.012

try:
    while True:
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
        pid_scale_factor = 1

        servo.set(0, angle_range=max_angle, pulse_range=pwm_range)
        time.sleep(1)

        start_time = time.time()
        last_time = start_time

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
                    targetPosition = smoothedPosition - 2
                elif smoothedPosition > (maxStaticFriction / spring_rate + 1):
                    targetPosition = smoothedPosition - 0.3
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
            controlSignal = -(Kp * error + Ki * integral + Kd * derivative) * pid_scale_factor
            controlAngle = np.clip(servoBaseAngle + controlSignal, 0, max_angle)

            servo.set(controlAngle, angle_range=max_angle, pulse_range=pwm_range)
            # motorVelocity = last_angle_change / dt
            # motorVelocity = np.clip(motorVelocity, -angularSpeed, angularSpeed) * angle_to_distance

            motorVelocity = np.sign(last_angle_change) * min(model.predict([[abs(last_angle_change)]])[0], 0)

            external_velocity = velocity - motorVelocity
            previous_error = error

            pid_scale_factor = 1 + (min(external_velocity, 50)-3)/50 if external_velocity > delta_v and calibrated and sliding else 1

            print(f"{error:.2f}, {controlSignal:.2f}, {controlAngle:.2f}, {targetPosition:.2f}, {smoothedPosition:.2f}, {velocity:.3f}, {motorVelocity:.3f},{external_velocity:.3f}, {frictionForce:.2f}, {detectedForce:.2f}, {100 * (detectedForce - frictionForce) / frictionForce if frictionForce > 0 else 0:.2f}%, {dt:.5f}")

            if calibrated and not sliding and external_velocity > delta_v and smoothedPosition > (maxStaticFriction + spring_rate * pot_fluc) * 1.2:
                sliding = True

            elif calibrated and sliding and velocity < 0 and external_velocity < -30:
                time.sleep(2)
                break

            last_angle_change = controlAngle - servoBaseAngle
            servoBaseAngle = controlAngle
            lastSmoothedPosition = smoothedPosition

            try:
                time.sleep(0.02 - (time.time() - last_time))  # 10ms loop (100Hz)
            except:
                pass

except KeyboardInterrupt:
    print("\nExiting...")
    servo.set(100, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(1)
    del servo
