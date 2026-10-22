"""PARTE 3: SEGUIMIENTO DE LINEA - Actividad 3."""
import matplotlib.pyplot as plt
import numpy as np


def main():
    # Linea: ax + by + c = 0
    a, b, c = 1, -2, 4

    # Pose inicial
    x, y, theta = 8, 5, np.pi / 2

    Kd = 0.5
    Kh = 1.0

    dt = 0.1
    L = 2.0
    v = 1
    delta = 0
    iteraciones = 200
    n = 0

    X, Y = [], []

    while n < iteraciones:
        # Distancia a la linea
        distance = (a * x + b * y + c) / np.sqrt(a**2 + b**2)
        # Angulo de la linea
        theta_line = np.arctan2(a, -b)

        # Controlador
        delta = Kd * distance + Kh * (theta_line - theta)

        # Modelo cinematico
        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += v / L * np.tan(delta) * dt

        X.append(x)
        Y.append(y)
        n = n + 1

    # -----------------------------
    # Graficar linea homogenea
    # -----------------------------
    x_line = np.linspace(3, 25, 100)

    if b != 0:
        y_line = (-a * x_line - c) / b
    else:
        # Linea vertical
        x_line = np.full(100, -c / a)
        y_line = np.linspace(-5, 10, 100)

    # -----------------------------
    # Grafica
    # -----------------------------
    plt.plot(X, Y, label='Trayectoria del robot')
    plt.plot(x_line, y_line, 'r--', label='Linea objetivo')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Seguimiento de linea')
    plt.axis('equal')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
