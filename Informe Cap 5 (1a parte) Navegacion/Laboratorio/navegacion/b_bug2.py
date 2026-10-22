"""Parte B: Bug2 simplificado de la guía.

Se conserva la lógica de la guía: avanzar por el eje de mayor diferencia y,
si la celda siguiente está ocupada, probar los vecinos en el orden
derecha-arriba-izquierda-abajo. No se añade la m-line ni la condición de
salida del Bug2 completo; el informe discute esa limitación.
"""

import numpy as np

from .mapas import is_free


def bug2(grid, start, goal, max_iter=500):
    """Ejecuta el Bug2 simplificado y devuelve ``(path, exito, iteraciones)``."""
    pos = np.array(start, dtype=int)
    goal_arr = np.array(goal, dtype=int)
    path = [pos.copy()]
    exito = False
    iteraciones = 0

    for iteraciones in range(1, max_iter + 1):
        direction = goal_arr - pos

        # La guía elige el eje con mayor diferencia; así evita diagonales.
        if abs(direction[0]) > abs(direction[1]):
            step = np.array([int(np.sign(direction[0])), 0], dtype=int)
        else:
            step = np.array([0, int(np.sign(direction[1]))], dtype=int)

        next_pos = pos + step

        if is_free(grid, next_pos):
            pos = next_pos
        else:
            # Seguimiento de borde simplificado de la guía.
            for move in (
                np.array([1, 0], dtype=int),
                np.array([0, 1], dtype=int),
                np.array([-1, 0], dtype=int),
                np.array([0, -1], dtype=int),
            ):
                if is_free(grid, pos + move):
                    pos = pos + move
                    break

        path.append(pos.copy())

        if np.linalg.norm(pos - goal_arr) < 1:
            exito = True
            break

    return np.asarray(path), exito, iteraciones
