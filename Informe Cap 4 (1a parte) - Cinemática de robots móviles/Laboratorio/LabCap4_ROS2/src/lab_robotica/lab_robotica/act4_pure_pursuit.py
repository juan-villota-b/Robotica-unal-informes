"""PARTE 4: SEGUIMIENTO DE TRAYECTORIA (PURE PURSUIT) - Actividad 4."""
import matplotlib.pyplot as plt
import numpy as np


def angle_wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def main():
    path = np.array([[0, 0], [2, 4], [6, 5], [8, 10]])
    lookahead = 0.5

    x, y, theta = 0, 0, 0

    current_index = 0

    Kd = 1.3

    dt = 0.1
    L = 2.0
    v = 0.5
    iteraciones = 285
    n = 0

    X, Y = [], []

    while n < iteraciones:
        # Distancia al punto actual
        dx = path[current_index][0] - x
        dy = path[current_index][1] - y
        dist = np.hypot(dx, dy)

        # Avanzar al siguiente punto si esta cerca
        if dist < lookahead and current_index < len(path) - 1:
            current_index += 1

        target = path[current_index]

        # Direccion al objetivo
        dx = target[0] - x
        dy = target[1] - y
        theta_goal = np.arctan2(dy, dx)

        # Error angular normalizado
        error = angle_wrap(theta_goal - theta)

        # Control
        delta = Kd * error

        # Modelo cinematico
        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += v / L * np.tan(delta) * dt

        X.append(x)
        Y.append(y)
        n = n + 1

    # -----------------------------
    # Grafica
    # -----------------------------
    plt.plot(path[:, 0], path[:, 1], 'r--', label='Trayectoria')
    plt.plot(X, Y, label='Robot')
    plt.axis('equal')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
