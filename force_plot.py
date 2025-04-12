import pandas as pd
import matplotlib.pyplot as plt

csv_path = "logs/Modified_Force_Data.csv"
df = pd.read_csv(csv_path)

# Filter the relevant data
df = df[df["Time (s)"] > 4.4].copy()

# Shift the velocity column down by one to align it with the correct force values
df['Aligned Velocity'] = df['Handler Velocity'].shift(1)
