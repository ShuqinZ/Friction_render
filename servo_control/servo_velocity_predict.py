import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

import joblib

# Load CSV
df = pd.read_csv("../assets/servo_velocity_calibration_0.2_continues.csv")

# Check the columns
print("Columns:", df.columns)

# Rename columns for convenience (update as needed)
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Assume columns: command_angle_change and linear_speed
X = df[['angle']].values
y = df['velocity_mm_per_s'].values

# Fit a linear model
model = LinearRegression()
model.fit(X, y)


# Save the trained model to a file
joblib.dump(model, '../assets/servo_speed_continues.pkl')
print("Model saved to servo_speed_continues.pkl")

# Print the relationship
print(f"Estimated linear speed = {model.coef_[0]:.4f} * command_angle_change + {model.intercept_:.4f}")

# Define a function you can use to get linear speed from command angle
def get_linear_speed(command_angle):
    return model.predict(np.array([[command_angle]]))[0]


# Plot the fit
plt.scatter(X, y, label='Data')
plt.plot(X, model.predict(X), color='red', label='Linear Fit')
plt.xlabel('Command Angle Change')
plt.ylabel('Linear Speed')
plt.title('Servo Angle to Linear Speed Calibration')
plt.legend()
plt.grid(True)
plt.show()

