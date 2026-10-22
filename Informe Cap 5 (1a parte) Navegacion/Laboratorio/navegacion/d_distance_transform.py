"""Parte D: distance transform iterativo de la guía.

El código de la guía usa 4 vecinos y costo unitario, es decir, calcula una
distance transform Manhattan (L1), no la euclidiana que usa el toolbox de
Corke por defecto. Se conserva la actualización iterativa y el orden de
barrido de la guía.
"""

import numpy as np


def distance_transform(grid, goal, n_iter=100):
    """Calcula el mapa de distancias al objetivo.

    Devuelve ``(dist, barridos_estabilizacion)``. Se ejecutan siempre
    ``n_iter`` barridos, como en la guía; ``barridos_estabilizacion`` es el
    primer barrido que no cambió ningún valor (incluye el barrido de
    verificación), o ``n_iter`` si no se estabilizó.
    """
    alto, ancho = grid.shape
    dist = np.full((alto, ancho), np.inf, dtype=float)

    gx, gy = int(goal[0]), int(goal[1])
    dist[gy, gx] = 0.0

    barridos_estabilizacion = None

    for it in range(n_iter):
        cambio = False

        for x in range(ancho):
            for y in range(alto):
                if grid[y, x] != 0:
                    continue

                mejor = dist[y, x]
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < ancho and 0 <= ny < alto:
                        candidato = dist[ny, nx] + 1.0
                        if candidato < mejor:
                            mejor = candidato

                if mejor < dist[y, x]:
                    dist[y, x] = mejor
                    cambio = True

        if not cambio and barridos_estabilizacion is None:
            barridos_estabilizacion = it + 1

    if barridos_estabilizacion is None:
        barridos_estabilizacion = n_iter

    return dist, barridos_estabilizacion


def extraer_camino(dist, start, goal, max_iter=200):
    """Baja por el mapa de distancias eligiendo el vecino de menor valor."""
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))

    pos = start
    path = [pos]
    alto, ancho = dist.shape

    for _ in range(max_iter):
        if pos == goal:
            break

        x, y = pos
        mejor = None
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < ancho and 0 <= ny < alto:
                valor = dist[ny, nx]
                if mejor is None or valor < mejor[1]:
                    mejor = ((nx, ny), valor)

        if mejor is None or not np.isfinite(mejor[1]):
            break

        pos = mejor[0]
        path.append(pos)

    return np.asarray(path, dtype=int)
