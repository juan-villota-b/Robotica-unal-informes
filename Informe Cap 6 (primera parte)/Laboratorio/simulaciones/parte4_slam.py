"""Parte 4 de la guía CAP6 — Introducción a SLAM.

Localización y mapeo simultáneos: el filtro estima a la vez la pose del robot y
la posición de los landmarks, sin conocer el mapa de antemano (``map=None``).

La incertidumbre de la pose en SLAM es **mayor** que con mapa conocido (parte 3),
porque también hay que estimar los landmarks. La métrica ``get_Pnorm()`` de la
guía es ``sqrt(det(P))`` sobre todo el estado (3 + 2N): al entrar landmarks el
determinante cae por dimensión, no porque la pose mejore. Por eso aquí se grafica
también ``sqrt(det(P[:3, :3]))``, que es la incertidumbre real de la pose.

Ejecutar::

    source ~/venvs/robotica/bin/activate
    python simulaciones/parte4_slam.py
"""

import matplotlib.pyplot as plt
import numpy as np
from roboticstoolbox import Bicycle, EKF, LandmarkMap, RandomPath, RangeBearingSensor

T = 40

# ==============================
# Covarianza de odometría
# ==============================
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2

# ==============================
# Covarianza del sensor
# ==============================
W = np.diag([0.1, np.deg2rad(1)]) ** 2

# ==============================
# Covarianza inicial
# ==============================
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2


def simular():
    """EKF SLAM: mapa desconocido, pose y landmarks estimados en línea."""
    # ==============================
    # Robot
    # ==============================
    robot = Bicycle(covar=V, animation=None)

    # ==============================
    # Mapa real
    # ==============================
    mapa = LandmarkMap(20, workspace=10, seed=0)

    # Trayectoria "aleatoria" dentro del mapa
    robot.control = RandomPath(workspace=mapa, seed=0)

    # ==============================
    # Sensor
    # ==============================
    sensor = RangeBearingSensor(
        robot=robot,
        map=mapa,
        covar=W,
        angle=[-np.pi / 2, np.pi / 2],
        range=4,
        seed=0,
    )

    # ==============================
    # EKF SLAM
    # ==============================
    slam = EKF(
        robot=(robot, V),
        P0=P0,
        sensor=(sensor, W),
        map=None,  # No conoce el mapa de landmarks previamente
    )

    # ==============================
    # Ejecutar simulación
    # ==============================
    slam.run(T=T)

    return robot, mapa, slam


def incertidumbre_pose(slam):
    """``sqrt(det(P[:3, :3]))`` por paso: incertidumbre de la pose, sin landmarks."""
    return np.array([np.sqrt(np.linalg.det(P[:3, :3])) for P in slam.get_P()])


def graficar(robot, mapa, slam):
    """Mapa, trayectorias, elipses de confianza e incertidumbre del SLAM."""
    # ==============================
    # Graficar resultados
    # ==============================
    # Mapa real (abre la figura con su propia escala)
    mapa.plot()
    plt.gcf().set_size_inches(10, 8)

    # Trayectoria real
    robot.plot_xy(color="blue", label="Trayectoria real")

    # Trayectoria estimada
    slam.plot_xy(color="red", label="Trayectoria estimada")

    # Elipses de confianza
    slam.plot_ellipse()

    # Landmarks estimados (construcción del mapa)
    slam.plot_map()

    plt.title("SLAM usando EKF")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()

    # ==============================
    # Incertidumbre
    # ==============================
    plt.figure(figsize=(8, 6))

    plt.plot(
        slam.get_t(),
        slam.get_Pnorm(),
        linewidth=2,
        label=r"$\sqrt{\det(P)}$ (estado completo)",
    )

    plt.plot(
        slam.get_t(),
        incertidumbre_pose(slam),
        linewidth=2,
        label=r"$\sqrt{\det(P_{pose})}$ (pose 3x3)",
    )

    plt.yscale("log")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Incertidumbre")
    plt.title("Evolución de incertidumbre en SLAM")
    plt.grid(True, which="both", alpha=0.4)
    plt.legend()


def main():
    robot, mapa, slam = simular()
    graficar(robot, mapa, slam)
    print("Transformación mapa estimado -> mapa real:")
    print(slam.get_transform(mapa))
    plt.show()


if __name__ == "__main__":
    main()
