# Instrucción: Presentación de la guía "Representación de Pose y Cuaterniones en ROS2"

**Objetivo:** Generar `presentacion_cuaterniones.pptx` (16:9) con **exactamente 8 diapositivas**

---

## Estética visual (aplicar a TODAS las diapositivas)

- **Fondo:** blanco puro (`#FFFFFF`). Sin degradados, sin imágenes de fondo.
- **Tipografía:** una sola fuente sans-serif (Calibri o Arial).
  - Títulos: 24–28 pt, color negro `#1A1A1A`, negrita.
  - Cuerpo: 14–16 pt, color gris oscuro `#333333`, regular.
- **Paleta mínima:** solo negro/gris + un único acento discreto (azul apagado `#2C5F8A` o gris azulado) para el número de diapositiva o un filete fino. Nada más de color.
- **Espaciado:** márgenes amplios (≥ 1.5 cm), mucho aire/espacio en blanco. Nunca saturar la diapositiva.
- **Textos:** máximo **2–3 líneas** por bloque. Frases cortas, sin párrafos largos.
- **Sin elementos decorativos:** no usar iconos, emojis, sombras, bordes gruesos ni cliparts.
- **Numeración discreta** en esquina inferior derecha (ej. "2 / 8"), gris claro 10 pt.

---

## Diapositiva 1 — Portada
- **Universidad Nacional de Colombia** (arriba, centrado, negrita)
- Facultad de Ingeniería — Curso: Robótica
- Espacio en blanco
- Título grande: *Representación de Pose y Cuaterniones en ROS2 (Cap. 2 – Corke)*
- Espacio en blanco
- **Integrantes:**
  - [NOMBRE 1]
  - [NOMBRE 2]
  - [NOMBRE 3]

---

## Diapositivas 2 a 7 — Una por actividad

**Layout (dos columnas):**
- **Izquierda (~55%):** **cuadrado/rectángulo vacío de marcador de posición** (borde gris fino `#CCCCCC`, fondo gris muy claro `#F5F5F5`, con texto centrado gris `EVIDENCIA actN`). NO insertar imágenes reales; es un espacio en blanco reservado.
- **Derecha (~45%):**
  - Número pequeño de actividad + título en negrita.
  - **Máximo 2 líneas** de interpretación.

| Diap | Título | Texto (máx. 2 líneas) |
|------|--------|------------------------|
| 2 | Act 1 — Conversión | 90° en Z como cuaternión y como matriz. Ambos aplicados a un mismo vector dan el mismo resultado → equivalentes. |
| 3 | Act 2 — No conmutatividad | Rz·Rx ≠ Rx·Rz. El orden de las rotaciones cambia el resultado: no conmutan. |
| 4 | Act 3 — Publicador de pose | Nodo que publica posición (1,2,0) + orientación (90° Z) en `/pose` cada 0.5 s. |
| 5 | Act 4 — TF2 | Transformación world→robot (2 m en X, rotando) 10 veces/s. Visible en RViz. |
| 6 | Act 5 — Error de orientación | Error entre deseada (90° Z) y actual (45° Z) = 45° en Z. |
| 7 | Act 6 — SLERP | Interpola 0°→90° en Z en pasos uniformes de 15°, 5 puntos intermedios. |

---

## Diapositiva 8 — Discusión final
Tres preguntas, **respuesta muy breve (1–2 líneas c/u)**, separadas por espacio en blanco:

1. **¿Por qué cuaterniones y no Euler?** → Sin gimbal lock ni singularidades; permiten interpolar suavemente (SLERP).

2. **¿Qué problema evitan?** → El bloqueo de guiñada: con Euler se pierde un grado de libertad al alinear ejes; el cuaternión es continuo y único.

3. **TF2 y transformaciones del Cap. 2** → TF2 implementa las transformaciones SE(3) (rotación + traslación) encadenadas en un árbol en tiempo real.

---

## Importante
- Sin imágenes: solo formas de marcador de posición (cuadrados vacías) donde iría cada evidencia.
