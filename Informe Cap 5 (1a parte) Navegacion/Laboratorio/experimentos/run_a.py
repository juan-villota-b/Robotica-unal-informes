"""Experimento A: vehículo Braitenberg de la guía.

Genera:
  figuras/A1_braitenberg_trayectoria.png|svg
  figuras/A2_braitenberg_distancia.png|svg
  resultados/metricas_a.csv (si se ejecuta este script solo)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

from navegacion.a_braitenberg import GOAL, KS, KV, X0, Y0, sensorfield, simular
from navegacion.mapas import FIGURAS_DIR, RESULTADOS_DIR, guardar_figura
from navegacion.metricas import escribir_csv

T_VALORES = (222, 500, 1000, 2000)
COLORES = {
    222: "#1f77b4",
    500: "#ff7f0e",
    1000: "#2ca02c",
    2000: "#d62728",
}


def _figura_trayectoria(sim):
    """Campo escalar y trayectoria de la guía (T=222)."""
    r = sim[222]
    xmin = min(r["x"].min(), X0, GOAL[0]) - 8.0
    xmax = max(r["x"].max(), X0, GOAL[0]) + 8.0
    ymin = min(r["y"].min(), Y0, GOAL[1]) - 8.0
    ymax = max(r["y"].max(), Y0, GOAL[1]) + 8.0

    xs = np.linspace(xmin, xmax, 320)
    ys = np.linspace(ymin, ymax, 320)
    X, Y = np.meshgrid(xs, ys)
    S = sensorfield(X, Y)

    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    cf = ax.contourf(X, Y, S, levels=28, cmap="viridis")
    fig.colorbar(cf, ax=ax, label="campo s(x, y)")

    # Sombra para que la trayectoria se vea sobre el campo.
    ax.plot(r["x"], r["y"], color="black", lw=4.0, alpha=0.45, zorder=3)
    ax.plot(r["x"], r["y"], color="white", lw=2.2, zorder=4, label="trayectoria")

    ax.scatter(
        X0,
        Y0,
        c="tab:blue",
        s=90,
        edgecolors="black",
        linewidths=0.7,
        label="inicio",
        zorder=6,
    )
    ax.scatter(
        GOAL[0],
        GOAL[1],
        c="tab:red",
        s=180,
        marker="*",
        edgecolors="black",
        linewidths=0.7,
        label="objetivo (60, 90)",
        zorder=6,
    )

    ax.set_xlabel("x (celdas)")
    ax.set_ylabel("y (celdas)")
    ax.set_aspect("equal")
    ax.set_title("Parte A — Braitenberg de la guía (T = 222)")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    ruta = guardar_figura(fig, "A1_braitenberg_trayectoria")
    plt.close(fig)
    return ruta


def _figura_distancia(sim):
    """Distancia al objetivo sobre la trayectoria completa (T=2000).

    Las corridas con T menor son prefijos de la misma trayectoria, así que
    se marca el punto de corte de cada T sobre una sola curva.
    """
    T_max = max(T_VALORES)
    r = sim[T_max]
    d = r["distancia"]

    fig, ax = plt.subplots(figsize=(8.2, 4.9))
    ax.plot(
        np.arange(1, T_max + 1),
        d,
        color="#1f77b4",
        lw=1.2,
        label="distancia al objetivo",
    )

    ax.axvline(
        222,
        color="black",
        ls=":",
        lw=1.1,
        label="corte de la guía (T = 222)",
    )

    # Punto de corte de cada T sobre la misma trayectoria.
    desplazamientos = {
        222: (-62, 12),
        500: (10, 12),
        1000: (10, 12),
        2000: (-10, 18),
    }
    for T in T_VALORES:
        valor = d[T - 1]
        ax.scatter(T, valor, color=COLORES[T], s=42, zorder=5)
        ax.annotate(
            f"T={T}\nd={valor:.2f}",
            xy=(T, valor),
            xytext=desplazamientos[T],
            textcoords="offset points",
            fontsize=7.5,
            color=COLORES[T],
            ha="right" if T in (222, 2000) else "left",
            va="bottom",
        )

    imin = int(np.argmin(d))
    ax.scatter(
        imin + 1,
        d[imin],
        color="tab:red",
        marker="*",
        s=150,
        zorder=6,
        label=f"mínimo: {d[imin]:.2f} (iter {imin + 1})",
    )

    ax.set_yscale("log")
    ax.set_ylim(1.2, 300.0)
    ax.set_xlabel("iteración")
    ax.set_ylabel("distancia al objetivo (celdas, escala log)")
    ax.set_title("Parte A — La distancia no converge a cero al aumentar T")
    ax.grid(True, which="both", ls=":", lw=0.5, alpha=0.5)
    ax.legend(
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        frameon=False,
    )
    fig.subplots_adjust(bottom=0.24)

    ruta = guardar_figura(fig, "A2_braitenberg_distancia")
    plt.close(fig)
    return ruta


def ejecutar():
    """Corre A para T = 222, 500, 1000 y 2000. Devuelve filas y resumen."""
    sim = {T: simular(T=T) for T in T_VALORES}
    filas = []
    resumen = {}

    for T in T_VALORES:
        r = sim[T]
        d = r["distancia"]
        imin = int(np.argmin(d))
        resumen[T] = {
            "distancia_minima": float(d[imin]),
            "iteracion_minimo": imin + 1,
            "distancia_final": float(d[-1]),
            "x_final": float(r["x"][-1]),
            "y_final": float(r["y"][-1]),
        }
        filas += [
            {
                "parte": "A",
                "metrica": "distancia_minima",
                "valor": round(float(d[imin]), 4),
                "unidad": "celdas",
                "nota": f"T={T}; mínimo en la iteración {imin + 1}",
            },
            {
                "parte": "A",
                "metrica": "distancia_final",
                "valor": round(float(d[-1]), 4),
                "unidad": "celdas",
                "nota": f"T={T}",
            },
            {
                "parte": "A",
                "metrica": "iteracion_minimo",
                "valor": imin + 1,
                "unidad": "iteraciones",
                "nota": f"T={T}",
            },
            {
                "parte": "A",
                "metrica": "x_final",
                "valor": round(float(r["x"][-1]), 4),
                "unidad": "celdas",
                "nota": f"T={T}",
            },
            {
                "parte": "A",
                "metrica": "y_final",
                "valor": round(float(r["y"][-1]), 4),
                "unidad": "celdas",
                "nota": f"T={T}",
            },
        ]

    _figura_trayectoria(sim)
    _figura_distancia(sim)

    resumen["parametros"] = {"Ks": KS, "Kv": KV, "dt": 0.1}
    return filas, resumen


def main():
    filas, resumen = ejecutar()
    ruta = escribir_csv(filas, RESULTADOS_DIR / "metricas_a.csv")

    print("Parte A — Braitenberg")
    for T in T_VALORES:
        r = resumen[T]
        print(
            f"  T={T:4d}: d_min={r['distancia_minima']:.3f} "
            f"(iter {r['iteracion_minimo']}), d_final={r['distancia_final']:.3f}, "
            f"pos_final=({r['x_final']:.2f}, {r['y_final']:.2f})"
        )
    print(f"  Figuras en {FIGURAS_DIR}")
    print(f"  Métricas en {ruta}")


if __name__ == "__main__":
    main()
