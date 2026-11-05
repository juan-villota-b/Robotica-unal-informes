"""Parte 2 de la guía CAP6 — Estimación usando EKF (Extended Kalman Filter).

El filtro propaga la pose y su covarianza solo con la odometría, sin
observaciones del entorno. La incertidumbre crece de forma continua porque no
hay ninguna corrección externa.

Ejecutar::

    source ~/venvs/robotica/bin/activate
    python simulaciones/parte2_ekf.py
"""

import matplotlib.pyplot as plt
import numpy as np
from roboticstoolbox import Bicycle, EKF, RandomPath

T = 20

# Covarianza odometría
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2

# Covarianza inicial
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2


def simular():
    """Corre el EKF solo con odometría sobre una trayectoria aleatoria."""
    # Robot
    robot = Bicycle(covar=V, animation=None)

    # Trayectoria "aleatoria"
    robot.control = RandomPath(workspace=10, seed=0)

    # EKF
    ekf = EKF(robot=(robot, V), P0=P0)

    # Ejecutar simulación
    ekf.run(T=T)

    return robot, ekf


def graficar(robot, ekf):
    """Trayectoria real vs estimada e incertidumbre contra el tiempo."""
    # Trayectoria
    plt.figure(figsize=(8, 6))
    robot.plot_xy(color="blue")
    ekf.plot_xy(color="red")
    ekf.plot_ellipse(filled=True, facecolor="g", alpha=0.3)
    plt.title("Trayectoria real vs estimada")
    plt.grid(True)
    plt.legend()

    # Incertidumbre
    plt.figure(figsize=(8, 6))
    plt.plot(ekf.get_t(), ekf.get_Pnorm(), linewidth=2)
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Incertidumbre")
    plt.title("Crecimiento de incertidumbre")
    plt.grid(True)


def main():
    robot, ekf = simular()
    graficar(robot, ekf)
    plt.show()


if __name__ == "__main__":
    main()
