"""Parte 1 de la guía CAP6 — Odometría (dead reckoning).

Simula un robot ``Bicycle`` con odometría ruidosa y otro ideal sin ruido, y
compara las trayectorias para evidenciar el crecimiento del error.

Ejecutar::

    source ~/venvs/robotica/bin/activate
    python simulaciones/parte1_odometria.py
"""

import matplotlib.pyplot as plt
import numpy as np
from roboticstoolbox import Bicycle

PASOS = 200
ENTRADA = (1.0, 0.2)

# Covarianza del ruido: incertidumbre para estimación de pose.
# La guía escribe 0.2; el libro (chap6.py) usa 0.02, igual que las partes 2-4.
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2


def simular():
    """Integra la odometría del robot real (con ruido) y del ideal (sin ruido)."""
    # Robot con ruido
    robot = Bicycle(covar=V)

    # Robot ideal (sin ruido)
    robot_ideal = Bicycle(covar=np.zeros((2, 2)))

    # Variables para almacenar trayectorias
    x_real, y_real = [], []
    x_ideal, y_ideal = [], []
    qp_real = [0, 0, 0]
    qp_ideal = [0, 0, 0]

    for _ in range(PASOS):
        # Movimiento robot real
        odo_real = robot.step(ENTRADA)
        qp_real = robot.f(qp_real, odo_real)

        # Movimiento robot ideal
        odo_ideal = robot_ideal.step(ENTRADA)
        qp_ideal = robot_ideal.f(qp_ideal, odo_ideal)

        # Guardar trayectoria real
        x_real.append(qp_real[0])
        y_real.append(qp_real[1])

        # Guardar trayectoria ideal
        x_ideal.append(qp_ideal[0])
        y_ideal.append(qp_ideal[1])

    return x_real, y_real, x_ideal, y_ideal


def graficar(x_real, y_real, x_ideal, y_ideal):
    """Grafica la trayectoria con ruido contra la trayectoria ideal."""
    plt.figure(figsize=(8, 6))

    plt.plot(
        x_ideal,
        y_ideal,
        label="Trayectoria estimada con odometría sin ruido",
        linewidth=1,
    )

    plt.plot(
        x_real,
        y_real,
        label="Trayectoria estimada con odometría con ruido",
        linewidth=1,
    )

    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.title("Comparación de trayectorias")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()

    # Error de posición contra el paso de integración: evidencia el crecimiento
    error = np.hypot(
        np.asarray(x_real) - np.asarray(x_ideal),
        np.asarray(y_real) - np.asarray(y_ideal),
    )
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, len(error) + 1), error, linewidth=2)
    plt.xlabel("Paso de integración")
    plt.ylabel("Error de posición [m]")
    plt.title("Crecimiento del error de odometría")
    plt.grid(True)


def main():
    print(V)
    graficar(*simular())
    plt.show()


if __name__ == "__main__":
    main()
