import numpy as np


def cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.cross(a, b)


def read_potentialmeter(raw):
    pos = ((raw / 32767.0) * 10.5) / 1.01 + 1  # same mapping as your main script
    return pos


def read_smoothed_position(pot, duration=0.01, read_delay=1 / 400):
    vals = []
    for _ in range(int(np.floor(duration / read_delay))):
        raw = pot.value
        pos = read_potentialmeter(raw)
        vals.append(pos)
        # time.sleep(read_delay)
    return sum(vals) / len(vals)
