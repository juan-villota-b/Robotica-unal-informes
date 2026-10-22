"""Métricas comunes para comparar los caminos de las partes A-D."""

import csv

import numpy as np

CAMPOS_CSV = ("parte", "metrica", "valor", "unidad", "nota")


def longitud_pasos(path):
    """Número de aristas del camino (un paso por arista)."""
    return max(len(path) - 1, 0)


def longitud_euclidiana(path):
    """Longitud euclidiana del camino, sumando las distancias entre puntos."""
    p = np.asarray(path, dtype=float)
    if len(p) < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))


def distancia_minima(path, goal):
    """Distancia mínima al objetivo a lo largo del camino."""
    p = np.asarray(path, dtype=float)
    if len(p) == 0:
        return float("nan")
    return float(np.min(np.linalg.norm(p - np.asarray(goal, dtype=float), axis=1)))


def distancia_final(path, goal):
    """Distancia al objetivo en el último punto del camino."""
    p = np.asarray(path, dtype=float)
    if len(p) == 0:
        return float("nan")
    return float(np.linalg.norm(p[-1] - np.asarray(goal, dtype=float)))


def resumen_camino(path, goal):
    """Resumen numérico de un camino para el informe."""
    p = np.asarray(path, dtype=float)
    if len(p) == 0:
        return {
            "pasos": 0,
            "longitud_euclidiana": 0.0,
            "distancia_minima": float("nan"),
            "distancia_final": float("nan"),
            "indice_minimo": None,
        }
    d = np.linalg.norm(p - np.asarray(goal, dtype=float), axis=1)
    return {
        "pasos": longitud_pasos(p),
        "longitud_euclidiana": longitud_euclidiana(p),
        "distancia_minima": float(np.min(d)),
        "distancia_final": float(d[-1]),
        "indice_minimo": int(np.argmin(d)) + 1,  # 1-based, como las iteraciones
    }


def escribir_csv(filas, ruta):
    """Escribe una lista de diccionarios con las columnas de ``CAMPOS_CSV``."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        for fila in filas:
            writer.writerow({campo: fila.get(campo, "") for campo in CAMPOS_CSV})
    return ruta
