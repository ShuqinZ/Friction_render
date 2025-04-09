import numpy as np


class HighPassFilter:
    def __init__(self, cutoff_freq, dt):
        RC = 1 / (2 * np.pi * cutoff_freq)
        self.alpha = RC / (RC + dt)
        self.prev_x = 0.0
        self.prev_y = 0.0

    def apply(self, x):
        y = self.alpha * (self.prev_y + x - self.prev_x)
        self.prev_x = x
        self.prev_y = y
        return y
