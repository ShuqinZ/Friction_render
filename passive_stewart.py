import numpy as np

from utils.tools import *


class Passive_Stewart:

    def __init__(self, spring_rate, psi_B, r_B, psi_P, r_P, d):
        self.spring_rate = spring_rate  # N/m

        # Coordinate of the points where servo arms
        # are attached to the corresponding servo axis.
        B = r_B * np.array([
            [np.cos(psi_B[0]), np.sin(psi_B[0]), 0],
            [np.cos(psi_B[1]), np.sin(psi_B[1]), 0],
            [np.cos(psi_B[2]), np.sin(psi_B[2]), 0],
            [np.cos(psi_B[3]), np.sin(psi_B[3]), 0],
            [np.cos(psi_B[4]), np.sin(psi_B[4]), 0],
            [np.cos(psi_B[5]), np.sin(psi_B[5]), 0]])
        self.base_distribution = np.transpose(B)

        # Coordinates of the points where the rods
        # are attached to the platform.
        P = r_P * np.array([
            [np.cos(psi_P[0]), np.sin(psi_P[0]), d],
            [np.cos(psi_P[1]), np.sin(psi_P[1]), d],
            [np.cos(psi_P[2]), np.sin(psi_P[2]), d],
            [np.cos(psi_P[3]), np.sin(psi_P[3]), d],
            [np.cos(psi_P[4]), np.sin(psi_P[4]), d],
            [np.cos(psi_P[5]), np.sin(psi_P[5]), d]])
        self.platform_distribution = np.transpose(P)

    def compute_force(self, compression):
        """
        Compute the total force and torque on a Stewart Platform using spring compression.

        Parameters:
        - compression: (6,1) array, amount each spring is compressed [m]

        Returns:
        - F_total: (3,1) array, total force vector [N]
        """

        # Compute force magnitudes
        F_magnitudes = self.spring_rate * compression  # Hooke's Law: F = k * ΔL

        # Compute unit direction vectors from base to platform
        L_vectors = self.platform_distribution - self.base_distribution  # Spring vectors
        L_norms = np.linalg.norm(L_vectors, axis=1, keepdims=True)  # Compute norms
        D = L_vectors / L_norms  # Normalize to unit vectors

        # Compute force vectors
        F_vectors = (F_magnitudes * D.T).T  # Scale unit vectors by force magnitude

        # Compute total force (sum of all forces)
        F_total = np.sum(F_vectors, axis=0)

        return F_total

    def compute_torque(self, F):
        """
            Compute total torque on a Stewart Platform from spring forces alone.

            Parameters:
            - F: (3,1) array, external force applied (default: [0, 0, 0])

            Returns:
            - torque: (3,1) array, total torque vector [Nm]
        """

        # Compute total torque (sum of individual spring torques)
        torque = np.sum(cross(self.platform_distribution.T, F.T).T, axis=0)
        return torque

    def estimate_force_application_point(self, F, torque):
        """
        Compute the total force and torque on a Stewart Platform using spring compression.

        Parameters:
        - F: (3,1) array, external force applied (default: [0, 0, 0])

        Returns:
        - F_total: (3,1) array, total force vector [N]
        """

        # Estimate force application point r_f using cross product equation
        F_ext_norm_sq = np.dot(F, F)  # ||F_ext||^2
        if F_ext_norm_sq == 0:
            raise ValueError("External force vector is zero, cannot determine force application point.")

        r_f = cross(torque, F) / F_ext_norm_sq

        return r_f


# Example usage
k = 1000  # Example spring constant in N/m
compression = np.array([0.02, 0.015, 0.018, 0.016, 0.014, 0.017])  # Example spring compressions in meters
B = np.random.rand(6, 3)  # Replace with actual base anchor points
P = np.random.rand(6, 3)  # Replace with actual platform anchor points

F, M = compute_force_torque(k, compression, B, P)
print("Total Force (N):", F)
print("Total Torque (Nm):", M)
