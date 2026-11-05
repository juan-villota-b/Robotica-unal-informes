"""Parte 3 de la guía CAP6 — EKF con landmarks.

El robot conoce de antemano el mapa de ``20`` landmarks y usa un sensor de rango
y rumbo tipo LiDAR. Cada observación corrige la pose: la incertidumbre baja en
los pasos donde hay landmarks dentro del alcance del sensor.

Ejecutar::

    source ~/venvs/robotica/bin/activate
    python simulaciones/parte3_ekf_landmarks.py
"""

import matplotlib.pyplot as plt
import numpy as np
from roboticstoolbox import Bicycle, EKF, LandmarkMap, RandomPath, RangeBearingSensor

T = 40

# Covarianza odometría
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2

# Covarianza sensor de rango
W = np.diag([0.1, np.deg2rad(1)]) ** 2

# Covarianza inicial
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2


def simular():
    """EKF con mapa conocido: construye robot, mapa, sensor y filtro."""
    # Robot
    robot = Bicycle(covar=V, animation=None)

    # Mapa de landmarks
    mapa = LandmarkMap(20, workspace=10, seed=0)

    # Trayectoria "aleatoria" dentro del mapa
    robot.control = RandomPath(workspace=mapa, seed=0)

    # Sensor de rango, tipo Lidar
    sensor = RangeBearingSensor(
        robot=robot,
        map=mapa,
        covar=W,
        angle=[-np.pi / 2, np.pi / 2],
        range=4,
        seed=0,
    )

    # EKF: conoce el mapa de landmarks previamente
    ekf = EKF(
        robot=(robot, V),
        P0=P0,
        map=mapa,
        sensor=(sensor, W),
    )

    # Simulación
    ekf.run(T=T)

    return robot, mapa, ekf


def graficar(robot, mapa, ekf):
    """Mapa, trayectorias, elipses de confianza e incertidumbre."""
    # Trayectorias
    mapa.plot()
    plt.gcf().set_size_inches(8, 6)
    robot.plot_xy(color="blue", label="Trayectoria real")
    ekf.plot_xy(color="red", label="Trayectoria estimada")
    ekf.plot_ellipse()
    plt.title("EKF con landmarks")
    plt.grid(True)
    plt.legend()

    # Incertidumbre
    plt.figure(figsize=(8, 6))
    plt.plot(ekf.get_t(), ekf.get_Pnorm(), linewidth=2)
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Incertidumbre")
    plt.title("Incertidumbre con correcciones")
    plt.grid(True)


def main():
    robot, mapa, ekf = simular()
    graficar(robot, mapa, ekf)
    plt.show()


if __name__ == "__main__":
    main()
