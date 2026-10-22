"""Ejecuta las cuatro actividades A-D y escribe resultados/metricas.csv."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from navegacion.mapas import FIGURAS_DIR, RESULTADOS_DIR
from navegacion.metricas import escribir_csv
from experimentos import run_a, run_b, run_c, run_d


def main():
    filas = []
    resumenes = {}

    for nombre, modulo in (("A", run_a), ("B", run_b), ("C", run_c), ("D", run_d)):
        print(f"\n=== Parte {nombre} ===")
        filas_parte, resumen = modulo.ejecutar()
        filas.extend(filas_parte)
        resumenes[nombre] = resumen

    ruta = escribir_csv(filas, RESULTADOS_DIR / "metricas.csv")

    print("\n=== Resumen ===")
    a = resumenes["A"]
    print(
        "A: "
        f"T=222 d_min={a[222]['distancia_minima']:.3f}; "
        f"T=500 d_final={a[500]['distancia_final']:.3f}; "
        f"T=1000 d_final={a[1000]['distancia_final']:.3f}; "
        f"T=2000 d_min={a[2000]['distancia_minima']:.3f}"
    )
    b = resumenes["B"]
    print(
        f"B: {b['pasos']} pasos, éxito={b['exito']}; "
        f"prueba inversa: éxito={b['prueba_inversa']['exito']}, "
        f"celdas únicas={b['prueba_inversa']['celdas_unicas']}"
    )
    c = resumenes["C"]
    print(
        f"C: {c['pasos']} pasos, costo={c['costo']}, "
        f"extraídos={c['extraidos']}, encolados={c['encolados']}"
    )
    d = resumenes["D"]
    print(
        f"D: {d['pasos']} pasos, dist[inicio]={d['dist_inicio']:.0f}, "
        f"estabiliza en {d['barridos_estabilizacion']} barridos; "
        f"comparación DT={d['comparacion_dt_pasos']} vs Bug2={d['comparacion_bug2_pasos']}"
    )

    print(f"\nMétricas: {ruta} ({len(filas)} filas)")
    print(f"Figuras:  {FIGURAS_DIR}")


if __name__ == "__main__":
    main()
