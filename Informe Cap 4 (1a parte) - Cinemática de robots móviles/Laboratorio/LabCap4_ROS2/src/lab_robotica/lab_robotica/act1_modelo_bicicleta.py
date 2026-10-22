"""PARTE 1: MODELO CINEMATICO (BICICLETA) - Actividad 1: Simulacion basica."""
import matplotlib.pyplot as plt
import numpy as np


def main():
    L = 2.0
    v = 1.0
    delta = 0.3

    x, y, theta = 0, 0, 0
    dt = 0.1

    X, Y = [], []

    for _ in range(100):
        x_dot = v * np.cos(theta)
        y_dot = v * np.sin(theta)
        theta_dot = v / L * np.tan(delta)

        x += x_dot * dt
        y += y_dot * dt
        theta += theta_dot * dt

        X.append(x)
        Y.append(y)

    plt.plot(X, Y)
    plt.title('Trayectoria del robot')
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()
