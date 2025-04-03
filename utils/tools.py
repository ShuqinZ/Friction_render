import numpy as np


def cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.cross(a, b)

def read_potentialmeter(raw):
    pos = (((raw / 32767.0) * 10.5) / 1.01 + 1  # same mapping as your main script
    return pos