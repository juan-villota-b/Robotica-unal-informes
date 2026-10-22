"""Experimento C: A* de la guía con heurística euclidiana.

Genera:
  figuras/C1_astar.png|svg
  resultados/metricas_c.csv (si se ejecuta este script solo)
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

from navegacion.c_astar import astar
from navegacion.mapas import (
    GOAL_B,
    START_B,
    crear_mapa_guia,
    dibujar_grid,
    guardar_figura,
)
from navegacion.metricas import escribir_csv, longitud_pasos
from navegacion.mapas import RESULTADOS_DIR


def _figura(path, expandidos, grid):
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    dibujar_grid(
        ax,
        grid,
        path=path,
        start=START_B,
        goal=GOAL_B,
        color_camino="#d62728",
        titulo="Parte C — A* con heurística euclidiana",
        expandidos=sorted(set(expandidos)),
    )
    ax.text(
        0.98,
        0.02,
        f"pasos = {longitud_pasos(path)}\n"
        f"nodos extraídos = {len(expandidos)}\n"
        f"nodos únicos = {len(set(expandidos))}",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6", alpha=0.9),
    )
    ruta = guardar_figura(fig, "C1_astar")
    plt.close(fig)
    return ruta


def ejecutar():
    """Corre A* en el mapa de la guía y devuelve filas y resumen."""
    grid = crear_mapa_guia()

    t0 = time.perf_counter()
    path, extraidos, encolados, expandidos, costo = astar(grid, START_B, GOAL_B)
    tiempo = time.perf_counter() - t0

    exito = bool(path) and tuple(path[-1]) == GOAL_B
    pasos = longitud_pasos(path)
    unicos = len(set(expandidos))

    filas = [
        {
            "parte": "C",
            "metrica": "longitud_camino",
            "valor": pasos,
            "unidad": "pasos",
            "nota": "A*, (2,2) -> (18,18)",
        },
        {
            "parte": "C",
            "metrica": "costo",
            "valor": costo if costo is not None else -1,
            "unidad": "aristas",
            "nota": "costo g(objetivo)",
        },
        {
            "parte": "C",
            "metrica": "nodos_extraidos",
            "valor": extraidos,
            "unidad": "nodos",
            "nota": "heappop, puede incluir duplicados",
        },
        {
            "parte": "C",
            "metrica": "nodos_unicos",
            "valor": unicos,
            "unidad": "nodos",
            "nota": "nodos distintos extraídos",
        },
        {
            "parte": "C",
            "metrica": "nodos_encolados",
            "valor": encolados,
            "unidad": "nodos",
            "nota": "heappush total",
        },
        {
            "parte": "C",
            "metrica": "exito",
            "valor": int(exito),
            "unidad": "booleano",
            "nota": "1 = llegó al objetivo",
        },
        {
            "parte": "C",
            "metrica": "tiempo_s",
            "valor": round(tiempo, 6),
            "unidad": "s",
            "nota": "medición local, indicativa",
        },
    ]

    _figura(path, expandidos, grid)

    resumen = {
        "path": path,
        "pasos": pasos,
        "costo": costo,
        "extraidos": extraidos,
        "unicos": unicos,
        "encolados": encolados,
        "exito": exito,
        "tiempo_s": tiempo,
    }
    return filas, resumen


def main():
    filas, resumen = ejecutar()
    ruta = escribir_csv(filas, RESULTADOS_DIR / "metricas_c.csv")

    print("Parte C — A*")
    print(
        f"  camino: {resumen['pasos']} pasos, costo={resumen['costo']}, "
        f"éxito={resumen['exito']}"
    )
    print(
        f"  extraídos={resumen['extraidos']}, únicos={resumen['unicos']}, "
        f"encolados={resumen['encolados']}, tiempo={resumen['tiempo_s']:.4f} s"
    )
    print(f"  Métricas en {ruta}")


if __name__ == "__main__":
    main()
