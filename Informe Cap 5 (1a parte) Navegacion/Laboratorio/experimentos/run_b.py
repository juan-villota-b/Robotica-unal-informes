"""Experimento B: Bug2 simplificado de la guía.

Genera:
  figuras/B1_bug2.png|svg
  resultados/metricas_b.csv (si se ejecuta este script solo)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

from navegacion.b_bug2 import bug2
from navegacion.mapas import (
    GOAL_B,
    START_B,
    crear_mapa_guia,
    dibujar_grid,
    guardar_figura,
)
from navegacion.metricas import (
    escribir_csv,
    longitud_euclidiana,
    longitud_pasos,
    resumen_camino,
)
from navegacion.mapas import RESULTADOS_DIR


def _figura(path, grid):
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    dibujar_grid(
        ax,
        grid,
        path=path,
        start=START_B,
        goal=GOAL_B,
        color_camino="#2ca02c",
        titulo="Parte B — Bug2 simplificado (mapa 20×20)",
        mline=True,
    )
    ax.text(
        0.98,
        0.02,
        f"pasos = {longitud_pasos(path)}\n"
        f"éxito = {'sí' if np.linalg.norm(path[-1] - np.array(GOAL_B)) < 1 else 'no'}",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6", alpha=0.9),
    )
    ruta = guardar_figura(fig, "B1_bug2")
    plt.close(fig)
    return ruta


def ejecutar():
    """Corre B en el mapa de la guía y una prueba con inicio/objetivo invertidos."""
    grid = crear_mapa_guia()

    path, exito, iteraciones = bug2(grid, START_B, GOAL_B)
    res = resumen_camino(path, GOAL_B)

    # Prueba de estrés con el mismo código y el mismo mapa, pero invertido.
    # Sirve para mostrar que el seguimiento de borde simplificado puede ciclar.
    path_inv, exito_inv, iter_inv = bug2(grid, GOAL_B, START_B)
    celdas_inv = len({tuple(p) for p in path_inv})

    filas = [
        {
            "parte": "B",
            "metrica": "longitud_camino",
            "valor": res["pasos"],
            "unidad": "pasos",
            "nota": "Bug2, (2,2) -> (18,18)",
        },
        {
            "parte": "B",
            "metrica": "longitud_euclidiana",
            "valor": round(longitud_euclidiana(path), 4),
            "unidad": "celdas",
            "nota": "Bug2, suma de distancias entre puntos",
        },
        {
            "parte": "B",
            "metrica": "exito",
            "valor": int(exito),
            "unidad": "booleano",
            "nota": "1 = llegó al objetivo",
        },
        {
            "parte": "B",
            "metrica": "iteraciones",
            "valor": iteraciones,
            "unidad": "iteraciones",
            "nota": "hasta llegar o agotar max_iter=500",
        },
        {
            "parte": "B",
            "metrica": "prueba_inversa_exito",
            "valor": int(exito_inv),
            "unidad": "booleano",
            "nota": "mismo mapa, (18,18) -> (2,2)",
        },
        {
            "parte": "B",
            "metrica": "prueba_inversa_iteraciones",
            "valor": iter_inv,
            "unidad": "iteraciones",
            "nota": "se agotan las 500 iteraciones",
        },
        {
            "parte": "B",
            "metrica": "prueba_inversa_celdas_unicas",
            "valor": celdas_inv,
            "unidad": "celdas",
            "nota": "ciclo entre dos celdas",
        },
    ]

    _figura(path, grid)

    resumen = {
        "path": path,
        "exito": bool(exito),
        "iteraciones": iteraciones,
        "pasos": res["pasos"],
        "longitud_euclidiana": res["longitud_euclidiana"],
        "prueba_inversa": {
            "exito": bool(exito_inv),
            "iteraciones": iter_inv,
            "celdas_unicas": celdas_inv,
            "final": tuple(int(v) for v in path_inv[-1]),
        },
    }
    return filas, resumen


def main():
    filas, resumen = ejecutar()
    ruta = escribir_csv(filas, RESULTADOS_DIR / "metricas_b.csv")

    print("Parte B — Bug2 simplificado")
    print(
        f"  camino: {resumen['pasos']} pasos, éxito={resumen['exito']}, "
        f"longitud euclidiana={resumen['longitud_euclidiana']:.3f}"
    )
    inv = resumen["prueba_inversa"]
    print(
        f"  prueba inversa: éxito={inv['exito']}, iteraciones={inv['iteraciones']}, "
        f"celdas únicas={inv['celdas_unicas']}, final={inv['final']}"
    )
    print(f"  Métricas en {ruta}")


if __name__ == "__main__":
    main()
