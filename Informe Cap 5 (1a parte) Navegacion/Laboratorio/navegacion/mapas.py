"""Mapa de ocupación de la guía y utilidades de dibujo.

Convención de coordenadas
-------------------------
El mapa se indexa como ``grid[y, x]`` y las posiciones se expresan como
``(x, y)``. En las figuras se usa ``origin="lower"`` para que el eje y
crezca hacia arriba, como en el plano cartesiano.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Directorios de salida, relativos a Laboratorio/.
BASE_DIR = Path(__file__).resolve().parents[1]
FIGURAS_DIR = BASE_DIR / "figuras"
RESULTADOS_DIR = BASE_DIR / "resultados"

# Inicio y objetivo de la guía para las partes B y C.
START_B = (2, 2)
GOAL_B = (18, 18)

# La parte D de la guía usa el problema invertido.
START_D = (18, 18)
GOAL_D = (2, 2)


def crear_mapa_guia():
    """Mapa 20x20 de la guía: un obstáculo rectangular de 4x10 celdas."""
    grid = np.zeros((20, 20), dtype=int)
    grid[8:12, 5:15] = 1
    return grid


def is_free(grid, p):
    """True si la celda ``p = (x, y)`` está dentro del mapa y libre.

    La comprobación de límites no estaba en el código de la guía; se añade
    para que el seguidor de borde no consulte índices fuera de la matriz.
    """
    x, y = int(p[0]), int(p[1])
    return (
        0 <= x < grid.shape[1]
        and 0 <= y < grid.shape[0]
        and grid[y, x] == 0
    )


def dibujar_grid(
    ax,
    grid,
    path=None,
    start=None,
    goal=None,
    color_camino="#2ca02c",
    titulo="",
    mline=False,
    expandidos=None,
):
    """Dibuja el mapa, opcionalmente el camino, inicio, objetivo y m-line."""
    ax.imshow(grid, origin="lower", cmap="Greys", vmin=0, vmax=1, alpha=0.75)

    if expandidos is not None and len(expandidos) > 0:
        ex = [p[0] for p in expandidos]
        ey = [p[1] for p in expandidos]
        ax.scatter(
            ex,
            ey,
            c="0.82",
            s=14,
            marker="s",
            linewidths=0,
            label="nodos expandidos",
            zorder=2,
        )

    if path is not None and len(path) > 0:
        path = np.asarray(path)
        ax.plot(
            path[:, 0],
            path[:, 1],
            color=color_camino,
            lw=2.0,
            marker="o",
            ms=2.8,
            label="camino",
            zorder=4,
        )

    if start is not None:
        ax.scatter(
            start[0],
            start[1],
            c="tab:blue",
            s=80,
            edgecolors="black",
            linewidths=0.6,
            label="inicio",
            zorder=5,
        )

    if goal is not None:
        ax.scatter(
            goal[0],
            goal[1],
            c="tab:red",
            s=140,
            marker="*",
            edgecolors="black",
            linewidths=0.6,
            label="objetivo",
            zorder=5,
        )

    if mline and start is not None and goal is not None:
        ax.plot(
            [start[0], goal[0]],
            [start[1], goal[1]],
            "k--",
            lw=1.0,
            alpha=0.55,
            label="m-line",
            zorder=3,
        )

    ax.set_xlim(-0.5, grid.shape[1] - 0.5)
    ax.set_ylim(-0.5, grid.shape[0] - 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel("x (celdas)")
    ax.set_ylabel("y (celdas)")
    ax.set_xticks(np.arange(0, grid.shape[1], 2))
    ax.set_yticks(np.arange(0, grid.shape[0], 2))
    ax.grid(color="0.85", lw=0.4, alpha=0.6)
    if titulo:
        ax.set_title(titulo)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)


def guardar_figura(fig, nombre):
    """Guarda la figura en PNG (300 dpi) y SVG dentro de ``figuras/``."""
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    png = FIGURAS_DIR / f"{nombre}.png"
    svg = FIGURAS_DIR / f"{nombre}.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    return png, svg
