# Model Predictive Control (MPC) for Spring-Actuated Force Feedback System
#
# This code replaces a PID controller with an MPC to control a servo-driven spring
# for force rendering (haptic friction simulation). It uses a convex optimization
# (cvxpy) to compute the optimal servo angle at 100 Hz, minimizing force error
# and limiting excessive servo motion.
#
# **Hardware Assumptions:**
# - Raspberry Pi with ADS1115 ADC reading a potentiometer that measures spring compression.
# - Servo motor controlled via a suitable library (e.g., RPi.GPIO or PCA9685 driver).
# - Potentiometer calibrated to convert ADC value to spring compression in mm.
# - The servo angle range [0,180] degrees maps linearly to spring compression via factor -0.18 mm/deg.
# - Spring constant k = 0.16 N/mm (160 N/m).
# - Static friction force = 0.8 N, Dynamic friction force = 0.4 N.
#
# The friction logic:
# - Start in static friction mode (stiction). As soon as the user pushes, the controller targets 0.8 N.
# - If measured force >= 0.8 N and user is moving (compression velocity > 0.2 mm/s), switch to dynamic mode.
# - In dynamic mode, hold target force at 0.4 N (kinetic friction). Do not revert to static until session reset.
#
# MPC setup:
# - Horizon of N steps (e.g., 5 steps at 10ms each = 50ms prediction).
# - Decision variables: servo angles over the horizon (u[0..N-1]).
# - Cost = sum((predicted_compression - target_compression)^2) + λ * sum((Δservo_angle)^2).
#   (Tracks the desired compression while smoothing rapid servo changes.)
# - Constraints: 0 <= servo_angle <= 180, and |Δservo_angle| <= max_step (rate limit per 0.01s).
#
# The first control in the optimized sequence (u[0]) is applied each loop iteration.
# The optimization is solved with OSQP (quadratic programming solver) for speed.
#
# Note: Ensure cvxpy and its solver (like OSQP) are installed: `pip install cvxpy osqp`

import cvxpy as cp
import numpy as np
import time

# System constants
k_spring = 160.0  # Spring constant in N/m (0.16 N/mm)
F_static = 0.8  # Static friction force (N)
F_dynamic = 0.4  # Dynamic friction force (N)
delta_v_thresh = 0.0002  # Slip velocity threshold in m/s (0.2 mm/s)
angle_min = 0.0  # Servo angle min (deg)
angle_max = 180.0  # Servo angle max (deg)
angle_to_comp = 0.00018  # Conversion: servo deg -> spring compression (m/deg).
# (Given -0.18 mm/deg, we use magnitude and handle sign separately)
angle_baseline = 90.0  # Baseline servo angle (deg) that corresponds to zero compression.

# MPC parameters
dt = 0.01  # Control loop period (s) = 100 Hz
N = 5  # MPC prediction horizon (5 steps * 10ms = 50ms)
lambda_mpc = 0.1  # Weight on servo movement (tune as needed for smoothness)
max_delta_angle = 3.0  # Max servo angle change per step (deg) ~ (rate limit)

# MPC optimization variables and parameters
u = cp.Variable(N)  # servo angle decisions for N future steps
prev_angle_param = cp.Parameter(nonneg=True)  # previous servo angle (deg)
target_comp_param = cp.Parameter(nonneg=True)  # target compression (m) this cycle (constant over horizon)
# Define cost function:
# Compression at each step i if servo moves to u[i]:
# Servo angle -> compression (assuming servo reaches commanded angle within one step)
# compression_i = (angle_baseline - u[i]) * angle_to_comp
# (We use baseline minus angle because decreasing angle increases compression.)
compression_pred = angle_baseline - u  # vector of (90 - u[i]) for each step
compression_pred = compression_pred * angle_to_comp  # convert to meters
# Force error cost: want compression_pred ~ target_comp (for all steps)
force_error_cost = cp.sum_squares(compression_pred - target_comp_param)
# Smoothness cost: penalize change in u. Include delta from prev actual and deltas between u's.
delta_0 = u[0] - prev_angle_param  # first step change from last angle
delta_seq = cp.diff(u)  # subsequent changes
smoothness_cost = cp.sum_squares(delta_0) + cp.sum_squares(delta_seq)
# Total cost
objective = cp.Minimize(force_error_cost + lambda_mpc * smoothness_cost)
# Constraints: angle bounds and rate limits
constraints = [
    u >= angle_min,
    u <= angle_max,
    delta_0 <= max_delta_angle,  # u[0] - prev_angle <= max_delta
    -delta_0 <= max_delta_angle,
    delta_seq <= max_delta_angle,
    -delta_seq <= max_delta_angle
]
# Set up problem (will be solved each loop iteration with updated parameters)
mpc_problem = cp.Problem(objective, constraints)

# Initialize state variables
prev_angle = 90.0  # start servo at baseline (0 compression)
friction_mode = "static"
dynamic_triggered = False

# Data logging lists for analysis (optional)
log_time = []
log_target_force = []
log_actual_force = []
log_target_comp = []
log_measured_comp = []
log_servo_angle = []
start_time = time.time()

# Main control loop (terminate condition or KeyboardInterrupt should be handled outside)
while True:
    # Read spring compression via ADC (potentiometer).
    # (Replace the next line with actual ADC reading code)
    adc_value = 0  # e.g., ads1115.read_adc(0, gain=1)
    # Convert ADC value to compression (mm or m). This calibration is system-specific.
    # For demonstration, assume adc_value ranges 0-32767 for 0-??? mm. Replace with proper calibration:
    compression_m = (adc_value / 32767.0) * 0.0  # <--- replace 0.0 with max compression in meters
    # If no contact (adc reading indicates 0 or baseline), compression_m might be 0.

    # Compute compression velocity (simple finite difference)
    # We need previous compression; store it from last loop iteration. Use 0 if none.
    if 'prev_comp' not in locals():
        prev_comp = compression_m
    comp_velocity = (compression_m - prev_comp) / dt
    prev_comp = compression_m  # update for next iteration

    # Determine friction mode and target force based on static/dynamic friction logic
    if friction_mode == "static":
        # If user is pushing (any contact), target static friction force
        target_force = F_static if compression_m > 0 else 0.0
        # Check slip condition: if force threshold reached and user moving, switch to dynamic mode
        if not dynamic_triggered and target_force >= F_static and comp_velocity > delta_v_thresh:
            friction_mode = "dynamic"
            dynamic_triggered = True
            target_force = F_dynamic
    else:
        # Dynamic friction mode
        target_force = F_dynamic

    # Compute target compression from target force (Hooke's law)
    target_compression = target_force / k_spring  # in meters

    # Update MPC problem parameters
    prev_angle_param.value = prev_angle
    target_comp_param.value = target_compression

    # Solve MPC optimization for current step
    # (Use OSQP solver for efficiency, warm_start speeds up successive solves)
    try:
        mpc_problem.solve(solver=cp.OSQP, warm_start=True, verbose=False)
    except Exception as e:
        print("MPC solve failed:", e)
        break

    # Get the first step optimal servo angle
    if u.value is None:
        print("MPC did not return a solution!")
        break
    servo_angle_cmd = float(u.value[0])

    # Apply command to servo (replace with actual servo control code)
    # e.g., pwm.set_angle(channel, servo_angle_cmd) or servoKit.servo[0].angle = servo_angle_cmd
    # print(f"Setting servo to {servo_angle_cmd:.1f} deg")  # debug

    # Update stored previous angle for next iteration
    prev_angle = servo_angle_cmd

    # (Optional) Measure or estimate the actual force for logging
    actual_force = k_spring * compression_m  # since F = k * x (if user in contact)

    # Log data for analysis (optional)
    current_time = time.time() - start_time
    log_time.append(current_time)
    log_target_force.append(target_force)
    log_actual_force.append(actual_force)
    log_target_comp.append(target_compression)
    log_measured_comp.append(compression_m)
    log_servo_angle.append(servo_angle_cmd)

    # Loop timing control: wait for next 10ms interval
    # (Important in real code to maintain 100Hz loop, e.g., using time.sleep or a scheduler)
    time.sleep(dt)

    # (Optional exit condition for demonstration; in real use, loop runs indefinitely)
    if current_time > 3.0:  # run for 3 seconds then break (for example)
        break

# End of control loop

# (Optional) After loop, plot results for analysis
try:
    import matplotlib.pyplot as plt

    t_arr = np.array(log_time)
    if len(t_arr) > 0:
        # Convert compression to mm for plotting
        comp_measured_mm = np.array(log_measured_comp) * 1000.0
        comp_target_mm = np.array(log_target_comp) * 1000.0
        plt.figure(figsize=(8, 4))
        plt.plot(t_arr, log_target_force, 'y--', label="Target Force (N)")
        plt.plot(t_arr, log_actual_force, 'r-', label="Actual Force (N)")
        plt.axvline(x=t_arr[np.argmax(np.array(log_target_force) < np.array(log_actual_force))]
        if dynamic_triggered else t_arr[-1],
                    color='k', ls='--', label="Slip Triggered")
        plt.xlabel("Time (s)");
        plt.ylabel("Force (N)");
        plt.legend();
        plt.title("Force Tracking")
        plt.figure(figsize=(8, 4))
        plt.plot(t_arr, comp_target_mm, 'y--', label="Target Compression (mm)")
        plt.plot(t_arr, comp_measured_mm, 'r-', label="Actual Compression (mm)")
        plt.axvline(x=t_arr[np.argmax(np.array(log_target_force) < np.array(log_actual_force))]
        if dynamic_triggered else t_arr[-1],
                    color='k', ls='--', label="Slip Triggered")
        plt.xlabel("Time (s)");
        plt.ylabel("Compression (mm)");
        plt.legend();
        plt.title("Compression Tracking")
        plt.show()
except ImportError:
    pass
