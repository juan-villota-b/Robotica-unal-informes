"""Experimento D: distance transform iterativo de la guía.

Genera:
  figuras/D1_distance_transform.png|svg
  resultados/metricas_d.csv (si se ejecuta este script solo)
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

from navegacion.b_bug2 import bug2
from navegacion.d_distance_transform import distance_transform, extraer_camino
from navegacion.mapas import (
    GOAL_B,
    GOAL_D,
    START_B,
    START_D,
    crear_mapa_guia,
    guardar_figura,
)
from navegacion.metricas import escribir_csv, longitud_pasos
from navegacion.mapas import RESULTADOS_DIR


def _figura(dist, path, grid, barridos_estabilizacion):
    dist_plot = np.where(np.isfinite(dist), dist, np.nan)

    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    cmap = plt.get_cmap("hot").copy()
    cmap.set_bad("0.55")  # obstáculos: gris, distinto del blanco de distancia alta
    im = ax.imshow(dist_plot, origin="lower", cmap=cmap)
    fig.colorbar(im, ax=ax, label="distancia al objetivo (celdas)")

    obs_y, obs_x = np.where(grid == 1)
    ax.scatter(
        obs_x,
        obs_y,
        c="black",
        s=22,
        marker="s",
        label="obstáculos",
        zorder=3,
    )

    ax.plot(
        path[:, 0],
        path[:, 1],
        color="cyan",
        lw=2.4,
        marker=".",
        ms=4,
        label="trayectoria",
        zorder=4,
    )
    ax.scatter(
        START_D[0],
        START_D[1],
        c="tab:blue",
        s=90,
        edgecolors="black",
        linewidths=0.6,
        label="inicio",
        zorder=5,
    )
    ax.scatter(
        GOAL_D[0],
        GOAL_D[1],
        c="lime",
        s=160,
        marker="*",
        edgecolors="black",
        linewidths=0.6,
        label="objetivo",
        zorder=5,
    )

    ax.text(
        0.98,
        0.33,
        f"dist[inicio] = {dist[START_D[1], START_D[0]]:.0f}\n"
        f"pasos = {longitud_pasos(path)}\n"
        f"barridos = 100 (estabiliza en {barridos_estabilizacion})",
        transform=ax.transAxes,
        va="center",
        ha="right",
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6", alpha=0.95),
    )

    ax.set_xlim(-0.5, grid.shape[1] - 0.5)
    ax.set_ylim(-0.5, grid.shape[0] - 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel("x (celdas)")
    ax.set_ylabel("y (celdas)")
    ax.set_xticks(np.arange(0, grid.shape[1], 2))
    ax.set_yticks(np.arange(0, grid.shape[0], 2))
    ax.set_title("Parte D — Distance transform iterativo (Manhattan)")
    ax.legend(loc="lower right", fontsize=8, framealpha=0.95)

    ruta = guardar_figura(fig, "D1_distance_transform")
    plt.close(fig)
    return ruta


def ejecutar():
    """Corre D con el problema invertido de la guía y compara con Bug2."""
    grid = crear_mapa_guia()

    t0 = time.perf_counter()
    dist, barridos_estabilizacion = distance_transform(grid, GOAL_D, n_iter=100)
    path = extraer_camino(dist, START_D, GOAL_D)
    tiempo = time.perf_counter() - t0

    pasos = longitud_pasos(path)
    dist_inicio = float(dist[START_D[1], START_D[0]])
    libres = int(np.sum(grid == 0))
    obstaculos = int(np.sum(grid == 1))

    # Comparación justa: mismo problema (2,2) -> (18,18) para D y para Bug2.
    dist_b, _ = distance_transform(grid, GOAL_B, n_iter=100)
    path_b = extraer_camino(dist_b, START_B, GOAL_B)
    path_bug2, exito_bug2, _ = bug2(grid, START_B, GOAL_B)

    filas = [
        {
            "parte": "D",
            "metrica": "longitud_camino",
            "valor": pasos,
            "unidad": "pasos",
            "nota": "DT, (18,18) -> (2,2), como la guía",
        },
        {
            "parte": "D",
            "metrica": "dist_inicio",
            "valor": round(dist_inicio, 4),
            "unidad": "celdas",
            "nota": "dist[start] del mapa de distancias",
        },
        {
            "parte": "D",
            "metrica": "barridos_ejecutados",
            "valor": 100,
            "unidad": "barridos",
            "nota": "n_iter de la guía",
        },
        {
            "parte": "D",
            "metrica": "barridos_estabilizacion",
            "valor": barridos_estabilizacion,
            "unidad": "barridos",
            "nota": "primer barrido sin cambios (incluye verificación)",
        },
        {
            "parte": "D",
            "metrica": "celdas_libres",
            "valor": libres,
            "unidad": "celdas",
            "nota": "grid == 0",
        },
        {
            "parte": "D",
            "metrica": "obstaculos",
            "valor": obstaculos,
            "unidad": "celdas",
            "nota": "grid == 1",
        },
        {
            "parte": "D",
            "metrica": "tiempo_s",
            "valor": round(tiempo, 6),
            "unidad": "s",
            "nota": "medición local, indicativa",
        },
        {
            "parte": "D",
            "metrica": "comparacion_dt_pasos",
            "valor": longitud_pasos(path_b),
            "unidad": "pasos",
            "nota": "DT con (2,2) -> (18,18)",
        },
        {
            "parte": "D",
            "metrica": "comparacion_bug2_pasos",
            "valor": longitud_pasos(path_bug2),
            "unidad": "pasos",
            "nota": "Bug2 con (2,2) -> (18,18)",
        },
        {
            "parte": "D",
            "metrica": "comparacion_bug2_exito",
            "valor": int(exito_bug2),
            "unidad": "booleano",
            "nota": "Bug2 con (2,2) -> (18,18)",
        },
    ]

    _figura(dist, path, grid, barridos_estabilizacion)

    resumen = {
        "pasos": pasos,
        "dist_inicio": dist_inicio,
        "barridos_estabilizacion": barridos_estabilizacion,
        "libres": libres,
        "obstaculos": obstaculos,
        "tiempo_s": tiempo,
        "comparacion_dt_pasos": longitud_pasos(path_b),
        "comparacion_bug2_pasos": longitud_pasos(path_bug2),
        "comparacion_bug2_exito": bool(exito_bug2),
    }
    return filas, resumen


def main():
    filas, resumen = ejecutar()
    ruta = escribir_csv(filas, RESULTADOS_DIR / "metricas_d.csv")

    print("Parte D — Distance transform")
    print(
        f"  camino: {resumen['pasos']} pasos, dist[inicio]={resumen['dist_inicio']:.0f}, "
        f"barridos hasta estabilizar={resumen['barridos_estabilizacion']}"
    )
    print(
        f"  comparación: DT={resumen['comparacion_dt_pasos']} pasos, "
        f"Bug2={resumen['comparacion_bug2_pasos']} pasos "
        f"(éxito={resumen['comparacion_bug2_exito']})"
    )
    print(f"  Métricas en {ruta}")


if __name__ == "__main__":
    main()
