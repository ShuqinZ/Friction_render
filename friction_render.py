import os
import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import joblib

from utils.pi5RC import pi5RC
from utils.tools import *
import csv



# === Hardware Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
pot = AnalogIn(ads, ADS.P0)
servo = pi5RC(18)  # GPIO18 with working PWM2 on pwmchip2
# static_model = joblib.load('assets/servo_speed_static.pkl')
# continues_model = joblib.load('assets/servo_speed_continues.pkl')

affective_history = 7
model_coeffs = np.load("assets/servo_model_coeffs.npy")
model_coeffs = model_coeffs[:affective_history]


# === Constants ===
# angle_to_distance = -0.21  # mm per degree
angle_to_distance = -0.18  # mm per degree
angularSpeed = 600  # degrees/s
gear_diameter = 22.0  # mm
spring_rate = 0.16

max_angle = 180
pwm_range = (500, 2400)
# pwm_range = (900, 2100)

maxStaticFriction = 0.8
dynamicFriction = 0.4
delta_v = 0.2  # mm/s
initTime = 1.0  # seconds
Kp, Ki, Kd = 0.8, 0, 0.05
alpha = 0.7  # smoothing factor for low-pass filter
pot_fluc = 0.012
high_pass_alpha = 0.3

try:
    # while True:
    for i in range(1):

        # === State Variables ===
        lastSmoothedPosition = None  # to be initialized with first reading
        integral = 0
        previous_error = 0
        servoBaseAngle = 0
        detectedForce = 0
        calibrated = False
        sliding = False
        lastTargetPosition = 0
        targetPosition = 0
        positionChange = 0
        last_angle_change = 0
        cold_start = True
        pid_scale_factor = 1
        external_velocity = 0

        motorVelocity_history = [0 for _ in range(affective_history)]

        log_list = []

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
                if smoothedPosition > (1.1 + 4):
                    targetPosition = smoothedPosition - 2
                elif smoothedPosition > (maxStaticFriction / spring_rate - 1 + 1):
                    targetPosition = smoothedPosition - 0.3
                elif smoothedPosition > (maxStaticFriction / spring_rate - 1 + 0.1):
                    targetPosition = smoothedPosition - 0.1
                elif smoothedPosition > (maxStaticFriction / spring_rate - 1 + 0.02):
                    targetPosition = smoothedPosition - 0.01
                elif smoothedPosition <= (maxStaticFriction / spring_rate - 1 + 0.03):
                    calibrated = True
                    integral = 0

            else:
                # === Control ===
                detectedForce = (smoothedPosition + 1.1) * spring_rate

                if sliding:
                    frictionForce = dynamicFriction
                else:
                    frictionForce = maxStaticFriction

                targetPosition = frictionForce / spring_rate - 1

            # === PID ===
            if calibrated:
                # if velocity - motorVelocity > delta_v:
                targetPosition -= external_velocity * 1.2 * dt
                if sliding:
                    targetPosition -= external_velocity * 1.5 * dt
            velocity = (smoothedPosition - lastSmoothedPosition) / dt
            error = targetPosition - smoothedPosition
            integral += error * dt
            derivative = (error - previous_error) / dt if dt > 0 else 0
            controlSignal = -(Kp * error * pid_scale_factor + Ki * integral + Kd * derivative)
            controlAngle = np.clip(servoBaseAngle + controlSignal, 0, max_angle)

            servo.set(controlAngle, angle_range=max_angle, pulse_range=pwm_range)
            # motorVelocity = last_angle_change / dt
            # motorVelocity = np.clip(motorVelocity, -angularSpeed, angularSpeed) * angle_to_distance

            # if cold_start:
            #     motorVelocity = np.sign(last_angle_change) * min(static_model.predict([[abs(last_angle_change)]])[0], 0)
            # else:
            #     motorVelocity = np.sign(last_angle_change) * min(continues_model.predict([[abs(last_angle_change)]])[0], 0)
            motorVelocity = np.dot(model_coeffs, motorVelocity_history[::-1])

            external_velocity = velocity - motorVelocity
            previous_error = error

            positionChange = high_pass_alpha * (positionChange + targetPosition - lastTargetPosition)

            pid_enhance = 0
            pid_scale_factor = 1
            if calibrated:
                if sliding:
                    pid_enhance = pid_enhance + min(np.tanh(abs(positionChange)), 0.15)
                if external_velocity > delta_v:
                    pid_enhance = pid_enhance + np.tanh(abs(external_velocity/50))

            pid_scale_factor += pid_enhance

            error_percent = 100 * (detectedForce - frictionForce) / frictionForce if frictionForce > 0 else 0

            print(f"{error:.2f}, {derivative:.2f}, {controlSignal:.2f}, {controlAngle:.2f}, {targetPosition:.2f}, {smoothedPosition:.2f}, {velocity:.3f}, {motorVelocity:.3f},{external_velocity:.3f}, {frictionForce:.2f}, {detectedForce:.2f}, {error_percent:.2f}%, {dt:.5f}")

            if calibrated and not sliding and velocity - motorVelocity > delta_v and smoothedPosition > (maxStaticFriction/spring_rate):
                sliding = True

            elif calibrated and sliding and velocity < 0 and motorVelocity > velocity + 5:
                time.sleep(2)
                break

            angle_change = controlAngle - servoBaseAngle
            # if angle_change * last_angle_change > 0:
            #     # movement same angle
            #     cold_start = False
            # else:
            #     cold_start = True
            # last_angle_change = angle_change

            motorVelocity_history.pop(0)
            motorVelocity_history.append(angle_change)

            servoBaseAngle = controlAngle
            lastSmoothedPosition = smoothedPosition
            lastTargetPosition = targetPosition

            log_list.append([now-start_time, velocity, frictionForce, detectedForce, error_percent])

            try:
                time.sleep(0.02 - (time.time() - last_time))  # 10ms loop (100Hz)
            except:
                pass

        os.makedirs("logs", exist_ok=True)
        with open("logs/force_error_log_h.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Velocity", "Desired force", "Rendered Force", "Percentage of Error"])
            for t, v, ff, rf, e in log_list:
                writer.writerow([t, v, ff, rf, e])

        print("Saved error log to logs/force_error_log_h.csv")
        servo.set(80, angle_range=max_angle, pulse_range=pwm_range)
        time.sleep(1)
        del servo


except KeyboardInterrupt:
    print("\nExiting...")
    servo.set(80, angle_range=max_angle, pulse_range=pwm_range)
    time.sleep(1)
    del servo
