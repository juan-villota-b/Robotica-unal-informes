"""Parte C: A* en un grid de 4 vecinos, como en la guía.

La heurística es la distancia euclidiana. Se añade un contador de nodos
extraídos de la cola y la lista de nodos expandidos para poder analizar el
papel de la heurística; el algoritmo es el de la guía.
"""

import heapq

import numpy as np


def heuristic(a, b):
    """Distancia euclidiana entre dos celdas ``(x, y)``."""
    return float(np.linalg.norm(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))


def astar(grid, start, goal):
    """A* de la guía.

    Devuelve ``(path, extraidos, encolados, expandidos, costo)``.
    ``extraidos`` cuenta cada ``heappop`` (puede incluir duplicados);
    ``expandidos`` es la lista de nodos extraídos, útil para la figura.
    Si no hay camino, ``path`` es una lista vacía y ``costo`` es ``None``.
    """
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))

    open_list = []
    heapq.heappush(open_list, (0.0, start))

    came_from = {}
    cost = {start: 0}
    expandidos = []
    encolados = 1

    while open_list:
        _, current = heapq.heappop(open_list)
        expandidos.append(current)

        if current == goal:
            break

        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor = (current[0] + dx, current[1] + dy)

            # x se compara con el ancho (columnas) y con el alto (filas).
            if (
                0 <= neighbor[0] < grid.shape[1]
                and 0 <= neighbor[1] < grid.shape[0]
                and grid[neighbor[1], neighbor[0]] == 0
            ):
                new_cost = cost[current] + 1

                if neighbor not in cost or new_cost < cost[neighbor]:
                    cost[neighbor] = new_cost
                    priority = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current
                    encolados += 1

    if goal != start and goal not in came_from:
        return [], len(expandidos), encolados, expandidos, None

    # Reconstruir el camino.
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = came_from[node]
    path.append(start)
    path.reverse()

    return path, len(expandidos), encolados, expandidos, cost.get(goal)
