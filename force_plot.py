import pandas as pd
import matplotlib.pyplot as plt

csv_path = "logs/Modified_Force_Data.csv"
df = pd.read_csv(csv_path)

# Filter the relevant data
df = df[df["Time (s)"] > 4.4].copy()

# Shift the velocity column down by one to align it with the correct force values
df['Aligned Velocity'] = df['Handler Velocity'].shift(1)

# Drop the first row since it now has NaN for Aligned Velocity
df = df.dropna(subset=['Aligned Velocity'])

# Plot Desired vs Rendered Force as a Function of Velocity
plt.figure(figsize=(10, 6))
plt.scatter(df['Aligned Velocity'], df['Desired force'], label='Desired Force', alpha=0.7)
plt.scatter(df['Aligned Velocity'], df['Rendered Force'], label='Rendered Force', alpha=0.7)
plt.xlabel('External Velocity')
plt.ylabel('Force')
plt.title('Desired vs Rendered Force as a Function of External Velocity')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot Percentage of Error vs Velocity
plt.figure(figsize=(10, 6))
plt.scatter(df['Aligned Velocity'], df['Percentage of Error'], color='red', alpha=0.7, label='Force Error (%)')
plt.xlabel('External Velocity')
plt.ylabel('Percentage of Error')
plt.title('Force Error as a Function of External Velocity')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
