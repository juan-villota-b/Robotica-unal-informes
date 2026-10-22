"""PARTE 2: CONTROL - IR A UN PUNTO - Actividad 2."""
import matplotlib.pyplot as plt
import numpy as np


def main():
    x, y, theta = 0, 0, 0
    goal = np.array([5, 5])

    Kv = 0.5
    Kh = 1.5

    dt = 0.1
    L = 2.0
    v = 0
    delta = 0
    distance = 10.0

    X, Y = [], []

    n = 0
    while distance > 0.1 and n < 10000:
        dx = goal[0] - x
        dy = goal[1] - y

        print(dx, dy)

        distance = np.sqrt(dx**2 + dy**2)
        theta_goal = np.arctan2(dy, dx)

        v = Kv * distance
        delta = Kh * (theta_goal - theta)

        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += v / L * np.tan(delta) * dt

        X.append(x)
        Y.append(y)
        n = n + 1

    plt.plot(X, Y)
    plt.scatter(goal[0], goal[1])
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    main()
