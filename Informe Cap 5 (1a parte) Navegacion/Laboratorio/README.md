# Laboratorio Capítulo 5 — Navegación de robots móviles

Simulaciones en Python de las **partes A, B, C y D** de la guía del Capítulo 5
de Corke. La parte E (ROS2/Nav2) no está incluida: la instrucción de esta
sesión cubre únicamente las actividades A–D.

## Contenido

```
Laboratorio/
├── navegacion/
│   ├── mapas.py                 # mapa 20×20, convención grid[y,x], dibujo
│   ├── metricas.py              # longitud, distancias, CSV
│   ├── a_braitenberg.py         # parte A
│   ├── b_bug2.py                # parte B
│   ├── c_astar.py               # parte C
│   └── d_distance_transform.py  # parte D
├── experimentos/
│   ├── run_a.py                 # corre A y guarda figuras + métricas
│   ├── run_b.py                 # corre B
│   ├── run_c.py                 # corre C
│   ├── run_d.py                 # corre D
│   └── run_all.py               # corre A–D y escribe resultados/metricas.csv
├── figuras/                     # PNG 300 dpi + SVG
└── resultados/                  # metricas.csv
```

## Requisitos e instalación

Se necesita Python 3.10 o superior con `numpy`, `scipy` y `matplotlib`. En este
equipo el entorno del curso ya tiene esas librerías:

```bash
source ~/venvs/robotica/bin/activate
```

Alternativa con un entorno local:

```bash
cd "Informes/Informe Cap 5 (1a parte) Navegacion/Laboratorio"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No se necesita ROS2 ni `roboticstoolbox` para las partes A–D.

## Cómo ejecutar

Desde la carpeta `Laboratorio/`:

```bash
# Todas las partes: figuras + resultados/metricas.csv
python experimentos/run_all.py

# Una parte concreta
python experimentos/run_a.py
python experimentos/run_b.py
python experimentos/run_c.py
python experimentos/run_d.py
```

Cada script guarda sus figuras en `figuras/` y un CSV parcial
(`metricas_a.csv`, etc.). `run_all.py` genera el consolidado
`resultados/metricas.csv`.

## Salidas

| Archivo | Contenido |
|---|---|
| `figuras/A1_braitenberg_trayectoria.png|svg` | Campo escalar y trayectoria de la parte A |
| `figuras/A2_braitenberg_distancia.png|svg` | Distancia al objetivo para T = 222, 500, 1000 y 2000 |
| `figuras/B1_bug2.png|svg` | Mapa, camino y m-line del Bug2 |
| `figuras/C1_astar.png|svg` | Camino de A* y nodos expandidos |
| `figuras/D1_distance_transform.png|svg` | Mapa de distancias y trayectoria |
| `resultados/metricas.csv` | Tabla completa de métricas |

## Convenciones

- El mapa se indexa como `grid[y, x]` y las posiciones se escriben `(x, y)`.
- En las figuras se usa `origin="lower"`, con el eje y hacia arriba.
- Las partes B, C y D usan 4 vecinos y costo unitario por arista.
- El mapa de la guía es de 20×20 celdas, con `grid[8:12, 5:15] = 1`.
- B y C usan `start = (2,2)` y `goal = (18,18)`. D usa el problema invertido
  de la guía: `goal = (2,2)` y `start = (18,18)`.

## Notas sobre el código de la guía

- **Parte A:** se conserva la ley `v = -Kv·(sL + sR)` y `ω = Ks·(sR - sL)`.
  No es la ley del libro (`v = 2 - sR - sL`), y por eso el vehículo no se
  detiene en el objetivo. El informe analiza esa diferencia.
- **Parte B:** se conserva el Bug2 simplificado, sin m-line ni condición de
  salida. En el mapa de la guía llega en 32 pasos; con inicio y objetivo
  invertidos puede quedar en un ciclo. El informe lo discute.
- **Parte C:** se añadió un contador de nodos extraídos/encolados y se
  corrigió la comparación de `x` con el ancho y de `y` con el alto.
- **Parte D:** el código de la guía usa 4 vecinos y costo 1, así que calcula
  una distance transform Manhattan (no la euclidiana del toolbox). Se registra
  el barrido de estabilización, pero se ejecutan los 100 barridos de la guía.
- Se eliminaron los `print` de los bucles y se añadió la comprobación de
  límites en `is_free` para evitar índices fuera de la matriz.

## Informe

El informe completo está en `../Informe/INFORME_CAP5.md`. Para generar el PDF:

```bash
~/venvs/robotica/bin/python ../Informe/md_a_pdf.py
```

El script convierte el Markdown a HTML, aplica estilos de impresión y usa
Google Chrome en modo headless para escribir `../Informe/INFORME_CAP5.pdf`.
