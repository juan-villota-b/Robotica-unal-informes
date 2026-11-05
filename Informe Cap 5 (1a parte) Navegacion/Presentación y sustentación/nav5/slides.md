---
theme: seriph
title: Navegación de robots móviles — Capítulo 5
info: |
  ## De lo reactivo al mapa global
  Braitenberg · Bug2 · A* · distance transform
  Robótica — UNAL Manizales — 2026-2
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
aspectRatio: 16/9
canvasWidth: 980
colorSchema: light
comark: true
background: '#fbfaf8'
---

<style>
.cover-motif {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.slidev-layout.cover h1,
.slidev-layout.cover p,
.slidev-layout.cover .cover-meta {
  position: relative;
  z-index: 2;
}
.slidev-layout.cover h1 {
  color: #33424a;
}
.slidev-layout.cover .cover-copy {
  position: relative;
  z-index: 2;
  text-align: left;
  max-width: 60%;
  padding-left: 4.5rem;
}
</style>

<img src="/cover.svg" class="cover-motif" />

<div class="cover-copy">

<h1>Navegación de robots móviles</h1>

<p>Capítulo 5 — de lo reactivo al mapa global</p>

<div class="pt-10 text-sm opacity-60">
  Juan David · Ingeniería Electrónica · UNAL Manizales<br/>
  Robótica · Semestre VIII · 2026-2
</div>

</div>

<!--
Presentación del laboratorio del Capítulo 5: cuatro algoritmos, un mismo mapa, una misma pregunta:
¿qué le falta a un robot para llegar a su objetivo?
-->

---
layout: default
---

# Agenda

<div class="grid grid-cols-2 gap-x-10 gap-y-2 text-lg mt-6">

<div>

**1. Contexto y banco de pruebas**

**2. Parte A** — Braitenberg

**3. Parte B** — Bug2

</div>
<div>

**4. Parte C** — A*

**5. Parte D** — distance transform

**6. Síntesis y conclusiones**

</div>
</div>

<div class="mt-10 p-4 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392] text-sm">
  La pregunta que atraviesa las cuatro partes: <strong>qué información necesita el robot</strong> —y qué paga por tenerla— para llegar al objetivo.
</div>

<!--
Recorrido: de menos a más información. A no tiene mapa ni memoria; D tiene el mapa completo y la solución para todas las celdas.
-->

---
layout: section
---

# 1. Contexto

La guía cubre cinco partes; esta entrega resuelve cuatro

---
layout: default
---

# Alcance del laboratorio

<div class="grid grid-cols-[1.15fr_0.85fr] gap-8 mt-4">

<div>

| Parte | Método | Estado |
| --- | --- | --- |
| **A** | Braitenberg | ✅ Implementada |
| **B** | Bug2 simplificado | ✅ Implementada |
| **C** | A* | ✅ Implementada |
| **D** | Distance transform | ✅ Implementada |
| **E** | ROS2 / Nav2 | ⏳ Entrega posterior |

</div>

<div class="text-sm">

**Por qué la parte E queda fuera**

Integrar Nav2 exige el stack de ROS2, `nav2_bringup` y un robot simulado. La instrucción de esta sesión cubre A–D.

**Consecuencia práctica**

Las cuatro simulaciones son locales: `numpy` + `matplotlib`, sin ROS2 y reproducibles con un solo comando.

</div>
</div>

<div class="mt-6 p-3 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392] text-sm">
  Doce preguntas de análisis respondidas con los resultados de las corridas y el texto de Corke.
</div>

<!--
El alcance lo fijó el profesor: A–D. No es una omisión, es un recorte explícito del enunciado.
-->

---
layout: default
---

# El banco de pruebas común

<div class="grid grid-cols-2 gap-10 mt-6 text-sm">

<div>

**Mapa**

- Grid de **20 × 20** celdas
- Obstáculo `grid[8:12, 5:15] = 1` → 4 × 10 celdas
- **360** celdas libres, **40** ocupadas

**Coordenadas**

- Celda `(x, y)` ↔ `grid[y, x]`
- Figuras con `origin="lower"`: $y$ crece hacia arriba

</div>

<div>

**Grafo de búsqueda**

- **4 vecinos** (arriba, abajo, izquierda, derecha)
- Costo unitario por arista, **sin diagonales**
- Inicio $(2,2)$, objetivo $(18,18)$

**La cota que usaremos como referencia**

$$
d_{\text{Manhattan}} = |18-2| + |18-2| = 32
$$

</div>
</div>

<div class="mt-6 p-4 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392] text-sm">
  Ningún camino de 4 vecinos puede medir menos de 32 pasos. Ese número es el árbitro de optimalidad en este mapa.
</div>

<!--
Todo el laboratorio usa el mismo mapa, así que las cuatro partes son comparables directamente.
La cota de Manhattan es la referencia: 32 pasos.
-->

---
layout: section
---

# 2. Parte A — Braitenberg

Dos sensores, una resta, ninguna memoria

---
layout: default
---

# Una ley de control puramente reactiva

<div class="grid grid-cols-[1fr_1fr] gap-8 mt-2">

<div class="text-sm">

**El campo escalar** tiene su máximo en $(60, 90)$:

$$
s(x,y) = \frac{1000}{(x-60)^2 + (y-90)^2 + 50}
$$

**Dos sensores** separados $d = 2$ respecto al eje del robot:

$$
\begin{aligned}
v &= -K_v\,(s_L + s_R)\\
\omega &= K_s\,(s_R - s_L)
\end{aligned}
$$

</div>

<div class="text-sm">

**Parámetros**

| Parámetro | Valor |
| --- | ---: |
| $K_s$ | 17 |
| $K_v$ | 14 |
| $dt$ | 0.1 s |
| Estado inicial | $(10, 10, 0°)$ |
| Iteraciones | $T = 222$ |

**Cinemática** del robot diferencial simplificado:

$$
\begin{aligned}
x &\leftarrow x + v\cos\theta\,dt\\
y &\leftarrow y + v\sin\theta\,dt\\
\theta &\leftarrow \theta + \omega\,dt
\end{aligned}
$$

</div>
</div>

<div class="mt-4 p-3 rounded bg-orange-500/10 border-l-4 border-orange-400 text-sm">
  Ojo: esta es la ley de la <strong>guía</strong> (v = −Kv·(sL+sR)), no la del libro (v = 2 − sR − sL). La diferencia es el objeto del análisis.
</div>

<!--
El robot no tiene mapa, no tiene memoria, no tiene condición de parada. Solo dos sensores y una resta.
-->

---
layout: two-cols-header
---

# Trayectoria: un arco, no una recta

::left::

<div class="text-sm">

- Parte de $(10,10)$ con $\theta = 0$
- Se mueve **hacia la izquierda**: en $x$ se aleja del objetivo
- Describe un arco amplio y termina en $(51.36,\ 85.82)$
- Distancia final con $T=222$: **9.60 celdas**
- Nunca apunta directamente al objetivo

<div class="mt-4 text-xs opacity-70">
Figura A1 — campo del sensor y trayectoria para T = 222
</div>
</div>

::right::

<img src="/fig/A1_braitenberg_trayectoria.png" class="h-[400px] w-auto mx-auto rounded shadow-md" />

<!--
El color es el campo, la línea blanca la trayectoria. El robot "huele" el gradiente pero no lo sigue bien: la ley empuja hacia adelante sin frenar.
-->

---
layout: two-cols-header
---

# Más iteraciones no arreglan la ley

::left::

<div class="text-sm">

| $T$ | $d_{\min}$ | Iter. del mín. | $d_{\text{final}}$ |
| ---: | ---: | ---: | ---: |
| 222 | 9.596 | 222 | 9.596 |
| 500 | 9.570 | 223 | **131.62** |
| 1000 | 9.570 | 223 | **165.92** |
| 2000 | 1.642 | 1819 | 117.95 |

La curva completa: el robot **pasa cerca** del objetivo y sigue de largo. El mínimo global (1.64 en la iteración 1819) es una casualidad de la órbita, no una llegada.

<div class="mt-3 text-xs opacity-70">
Figura A2 — distancia al objetivo sobre la trayectoria completa
</div>
</div>

::right::

<img src="/fig/A2_braitenberg_distancia.png" class="h-[260px] w-auto mx-auto rounded shadow-md" />

<!--
Los puntos marcan el corte de cada T sobre la MISMA curva. Aumentar T solo alarga la órbita.
-->

---
layout: default
---

# Diagnóstico: por qué no converge

<div class="grid grid-cols-3 gap-5 mt-6 text-sm">

<div class="p-4 rounded border border-[#5d8392]/30">

**1. El signo**

$v = -K_v(s_L+s_R)$ crece en magnitud como $1/r^2$ al acercarse. En el paso siguiente a la mejor posición, $|v| \approx 192$ → salto de **19.2 celdas** en un solo $dt$.

</div>

<div class="p-4 rounded border border-[#5d8392]/30">

**2. No hay frenado ni parada**

Cerca del objetivo $s_L \approx s_R$, así que $\omega \to 0$: el robot deja de girar, pero **no de avanzar**. Sobrepasa y se aleja.

</div>

<div class="p-4 rounded border border-[#5d8392]/30">

**3. No hay mapa ni evasión**

El campo es global y conocido. Un obstáculo físico lo bloquearía: no hay sensores de proximidad ni comportamiento de evasión.

</div>
</div>

<div class="mt-8 p-4 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392]">

**La ley del libro sí converge:** $v = 2 - s_R - s_L$. En el objetivo $s_R = s_L = 1$, entonces $v \to 0$ y el robot frena de forma asintótica. La guía cambió el signo y perdió esa propiedad.

</div>

<!--
Tres causas independientes. La más grave es la ausencia de saturación: el paso de integración se vuelve enorme cerca del objetivo.
-->

---
layout: section
---

# 3. Parte B — Bug2

Estado y evasión de obstáculos, todavía sin mapa

---
layout: default
---

# El algoritmo, en cuatro pasos

<div class="grid grid-cols-[1fr_1fr] gap-8 mt-2 text-sm">

<div>

1. Calcular la dirección al objetivo
2. Avanzar por el **eje de mayor diferencia** (sin diagonales)
3. Si la celda siguiente está ocupada, probar los vecinos en orden **derecha → arriba → izquierda → abajo** y moverse al primero libre
4. Registrar la posición; terminar a menos de 1 celda del objetivo

<div class="mt-4 p-3 rounded bg-orange-500/10 border-l-4 border-orange-400 text-xs">
  <strong>Versión simplificada:</strong> no calcula la m-line ni usa la condición de salida del Bug2 completo. Esa omisión explica todo lo que falla después.
</div>

</div>

<div>

```python {3|5-9|11-19|all}
for it in range(1, max_iter + 1):
    direction = goal - pos

    # eje dominante: nunca diagonal
    if abs(direction[0]) > abs(direction[1]):
        step = (sign(direction[0]), 0)
    else:
        step = (0, sign(direction[1]))

    nxt = pos + step
    if is_free(grid, nxt):
        pos = nxt
    else:
        # fallback fijo: derecha, arriba,
        # izquierda, abajo
        for move in moves:
            if is_free(grid, pos + move):
                pos = pos + move
                break
```

</div>
</div>

<!--
La regla de desempate es fija y no verifica si el robot se acerca al objetivo. Ahí está la semilla del ciclo.
-->

---
layout: two-cols-header
---

# Rodea el obstáculo y llega

::left::

<div class="text-sm">

| Métrica | Valor |
| --- | ---: |
| Longitud del camino | **32 pasos** |
| Longitud euclidiana | 32.0 celdas |
| ¿Llegó? | Sí, 32 iteraciones |
| Cota inferior de Manhattan | 32 |

El camino baja hasta $y = 7$ (justo debajo del obstáculo) y sube por $x = 15$ (justo a la derecha). La m-line punteada se dibuja **solo como referencia**: el código no la usa.

<div class="mt-3 text-xs opacity-70">
Figura B1 — camino del Bug2 simplificado
</div>
</div>

::right::

<img src="/fig/B1_bug2.png" class="h-[390px] w-auto mx-auto rounded shadow-md" />

<!--
La coincidencia con la cota no es suerte del todo: el obstáculo permite una escalera monótona. Pero eso es geometría, no una garantía del algoritmo.
-->

---
layout: default
---

# ¿Es óptimo? Sí aquí, no en general

<div class="grid grid-cols-2 gap-6 mt-4 text-sm">

<div class="p-4 rounded border border-[#5d8392]/30">

**En este mapa, sí**

Cada paso cambia una coordenada en una unidad, así que cualquier camino necesita al menos $|18-2| + |18-2| = 32$ pasos. El camino mide exactamente 32: alcanza la cota y es óptimo.

</div>

<div class="p-4 rounded border border-[#5d8392]/30">

**Pero no es una propiedad del algoritmo**

Bug2 es local: sigue el borde sin visión global. En la casa del libro recorre **1307** puntos frente a **338** del distance transform — casi cuatro veces más.

</div>
</div>

**La prueba que lo delata** — mismo mapa, inicio y objetivo invertidos $(18,18) \to (2,2)$:

<v-clicks>

- Se agotan las 500 iteraciones: **no llega**
- Visita solo **13 celdas distintas**
- Queda ciclando entre $(12,12)$ y $(13,12)$

</v-clicks>

<div class="mt-4 p-3 rounded bg-orange-500/10 border-l-4 border-orange-400 text-sm">
  En (12,12) el empate |Δx| = |Δy| hace que intente bajar —obstáculo—; el fallback lo manda a la derecha y desde allí el paso dominante lo devuelve. Sin condición de salida, el ciclo es inevitable.
</div>

<!--
El Bug2 completo evita el ciclo con la m-line: abandona el borde solo cuando vuelve a la línea en un punto más cercano al objetivo. Sigue siendo subóptimo.
-->

---
layout: default
---

# A contra B: la diferencia es el estado

<table class="text-sm">
<thead>
<tr><th>Aspecto</th><th>A — Braitenberg</th><th>B — Bug2 simplificado</th></tr>
</thead>
<tbody>
<tr><td>¿Mapa global?</td><td>No</td><td>No</td></tr>
<tr><td>¿Memoria / estado?</td><td>No</td><td>Sí: camino y detección de obstáculos</td></tr>
<tr><td>¿Detecta obstáculos?</td><td>No</td><td>Sí: consulta celdas vecinas</td></tr>
<tr><td>¿Llega al objetivo?</td><td>No (mínimo 9.57)</td><td>Sí, en 32 pasos</td></tr>
<tr><td>Trayectoria</td><td>Continua, orbital</td><td>Discreta, en escalera</td></tr>
<tr><td>Optimalidad</td><td>No</td><td>Aquí sí; en general no</td></tr>
<tr><td>Entornos complejos</td><td>Se bloquea con un obstáculo</td><td>Puede ciclar (versión simplificada)</td></tr>
</tbody>
</table>

<div class="mt-5 p-3 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392] text-sm">
  El Braitenberg conecta sensores y motores <strong>sin memoria</strong>. El Bug2 añade una máquina de estados (avanzar / seguir borde) y recuerda el camino. Esa memoria resuelve obstáculos, pero sigue siendo navegación reactiva.
</div>

<!--
La progresión conceptual: sensores → + estado. Todavía sin planificación global.
-->

---
layout: section
---

# 4. Parte C — A*

El mapa como grafo y una heurística que dirige la búsqueda

---
layout: default
---

# A*: costo recorrido + costo estimado

<div class="grid grid-cols-[0.95fr_1.05fr] gap-8 mt-2 text-sm">

<div>

**Criterio de expansión**

$$
f(n) = g(n) + h(n)
$$

- $g(n)$: costo acumulado desde el inicio
- $h(n)$: estimación del costo restante
- Cola de prioridad por $f$
- $h$ euclidiana: $h(n) = \lVert n - \text{goal} \rVert_2$

**Detalle de implementación**

No usa conjunto cerrado: si encuentra un costo mejor, **vuelve a encolar** el nodo. Eso lo hace robusto ante heurísticas inconsistentes.

</div>

<div>

```python {2|5-9|11-20|all}
def astar(grid, start, goal):
    push(open_list, (0.0, start))
    cost = {start: 0}

    while open_list:
        _, current = heappop(open_list)
        if current == goal:
            break
        for dx, dy in FOUR_NEIGHBORS:
            neighbor = current + (dx, dy)
            if not free(grid, neighbor):
                continue
            new_cost = cost[current] + 1
            if neighbor not in cost \
               or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                priority = new_cost + h(neighbor, goal)
                push(open_list, (priority, neighbor))
                came_from[neighbor] = current
```

</div>
</div>

<!--
A* es UCS con una guía: la heurística no cambia el costo, cambia el orden en que se exploran los nodos.
-->

---
layout: two-cols-header
---

# Treinta y dos pasos, 305 nodos expandidos

::left::

<div class="text-sm">

| Métrica | Valor |
| --- | ---: |
| Longitud del camino | **32 pasos** |
| $g(\text{objetivo})$ | 32 aristas |
| Nodos extraídos | **305** |
| Nodos encolados | 347 |
| Tiempo (indicativo) | ≈ 1.2 ms |

A* sube por $x = 4$ hasta $y = 12$, cruza **por encima** del obstáculo y avanza en escalera hasta $(18,18)$.

Es una ruta distinta de la de Bug2 —que pasa por debajo— pero mide lo mismo: **32 pasos**.

<div class="mt-3 text-xs opacity-70">
Figura C1 — camino y nodos expandidos (gris)
</div>
</div>

::right::

<img src="/fig/C1_astar.png" class="h-[330px] w-auto mx-auto rounded shadow-md" />

<!--
Mismo costo óptimo, camino distinto: el óptimo no es único. Lo que cambia es cuánto se paga por encontrarlo.
-->

---
layout: default
---

# BFS, UCS y A*: tres formas de ordenar la cola

| Algoritmo | Criterio de expansión | Qué garantiza | Comentario |
|---|---|---|---|
| **BFS** | Cola FIFO por número de aristas | Menos aristas, si todas cuestan lo mismo | Ignora costos; explora mucho |
| **UCS** | Cola de prioridad por $g(n)$ | Costo mínimo con costos no negativos | Onda en todas las direcciones |
| **A\*** | Cola de prioridad por $f = g + h$ | Costo mínimo si $h$ es admisible | Dirige la búsqueda; expande menos |

<div class="mt-6 grid grid-cols-2 gap-6 text-sm">

<div class="p-3 rounded bg-[#5d8392]/10">

**Relaciones**

BFS es UCS cuando todas las aristas cuestan 1.  
UCS es A* cuando $h(n) = 0$.

</div>

<div class="p-3 rounded bg-[#5d8392]/10">

**Evidencia del libro**

Mismo camino óptimo de costo 1659: UCS explora **19** vértices, A\* explora **12**.

</div>
</div>

<!--
Tres algoritmos, un mismo esqueleto: lo único que cambia es la función de prioridad.
-->

---
layout: default
---

# La heurística: admisible, consistente, y aun así floja

<div class="grid grid-cols-2 gap-6 mt-4 text-sm">

<div>

**Qué exige la optimalidad**

- **Admisible:** $h(n) \le h^*(n)$, nunca sobreestima
- **Consistente:** $h(n) \le c(n,n') + h(n')$

La euclidiana cumple ambas en un grid de 4 vecinos.

</div>

<div>

**Por qué no basta con ser correcta**

En 4-conectividad la euclidiana **subestima mucho**: un desplazamiento diagonal cuesta 2 pasos, no $\sqrt{2}$. Muchos nodos empatan en $f$.

Resultado: A* expande **305 de 360** celdas libres — el **85 %**.

</div>
</div>

<div class="mt-5 p-4 rounded border border-[#5d8392]/30 text-sm">

**Qué pasaría con otra heurística**

| Heurística | Efecto |
| --- | --- |
| Manhattan | Admisible y más ajustada: menos expansiones |
| $h = 0$ | A* se degrada a UCS: explora más |
| Sobreestimada | Pierde la optimalidad: puede devolver un camino peor |
| Exacta $h^*$ | Expande solo el camino óptimo (pero eso es lo que queremos calcular) |

</div>

<!--
La heurística es el único parámetro de diseño de A*. Correcta pero floja = correcto pero lento.
-->

---
layout: section
---

# 5. Parte D — Mapas de ocupación

Calcular la distancia al objetivo para todas las celdas

---
layout: default
---

# Distance transform: la solución en todo el mapa

<div class="grid grid-cols-[1fr_1fr] gap-8 mt-2 text-sm">

<div>

**Inicialización**

$$
D(\text{meta}) = 0, \qquad D(c) = \infty \ \ \text{para } c \neq \text{meta}
$$

**Actualización por barridos**

$$
D(y,x) \leftarrow \min\Big(D(y,x),\ 1 + \min_{n \in N(y,x)} D(n)\Big)
$$

**Punto fijo: ecuación de Bellman**

$$
D(\text{meta}) = 0, \qquad D(c) = 1 + \min_{n} D(n)
$$

</div>

<div>

**Cómo se lee**

Cada celda guarda **cuántos pasos le faltan** para llegar a la meta. Al llegar al punto fijo, basta con bajar por el gradiente: desde cada celda, ir al vecino con menor $D$.

**Detalles de la guía**

- 4 vecinos, costo 1 → métrica **Manhattan** ($L_1$)
- Obstáculos quedan en $\infty$
- **100 barridos fijos**, sin verificar convergencia

<div class="mt-3 p-3 rounded bg-orange-500/10 border-l-4 border-orange-400 text-xs">
  El mapa de distancias se calcula <strong>una vez</strong> y sirve para cualquier inicio: es la diferencia con A*, que busca por consulta.
</div>

</div>
</div>

<!--
Es programación dinámica: resolver el problema para todos los estados posibles, no solo para el que necesitamos.
-->

---
layout: two-cols-header
---

# Un mapa de calor de distancias

::left::

<div class="text-sm">

| Métrica | Valor |
| --- | ---: |
| Longitud del camino | **32 pasos** |
| $D(\text{inicio})$ | **32 celdas** |
| Barridos ejecutados | 100 |
| Barrido de estabilización | **5** |
| Celdas libres / obstáculos | 360 / 40 |
| Tiempo (indicativo) | ≈ 31 ms |

La trayectoria sale de $(18,18)$, recorre el borde superior hasta $(2,18)$ y baja por el borde izquierdo hasta $(2,2)$.

Coincide con $D(\text{inicio}) = 32$: la distancia almacenada **es** la longitud del camino.

<div class="mt-3 text-xs opacity-70">
Figura D1 — mapa de distancias Manhattan y trayectoria óptima
</div>
</div>

::right::

<img src="/fig/D1_distance_transform.png" class="h-[330px] w-auto mx-auto rounded shadow-md" />

<!--
32 por dos vías independientes: la ecuación de Bellman y la cota geométrica de Manhattan.
-->

---
layout: default
---

# Por qué el resultado es óptimo

<div class="text-sm mt-2">

Sea $L$ la longitud de cualquier camino desde $c$ hasta la meta. Por inducción en los pasos:

</div>

$$
D(c) = 1 + \min_{n} D(n) \;\le\; 1 + D(n') \;\le\; 1 + (L-1) = L
$$

<div class="text-sm mt-1">

Es decir, $D(c)$ es una **cota inferior** de cualquier camino. Además, el camino que baja por el vecino de menor $D$ reduce $D$ exactamente en 1 en cada paso, así que alcanza la cota: **es óptimo**.

</div>

<div class="mt-6 grid grid-cols-2 gap-6 text-sm">

<div class="p-4 rounded border border-[#5d8392]/30">

**Por qué la guía dice "NO ÓPTIMO"**

1. Con 4 vecinos optimiza **Manhattan**, no la distancia euclidiana.
2. Ejecuta **100 barridos fijos** sin verificar convergencia.

</div>

<div class="p-4 rounded border border-[#5d8392]/30">

**La lectura correcta**

La optimalidad es del **punto fijo** y de la **métrica modelada**. En este mapa se alcanza en 5 barridos y el camino de 32 pasos es óptimo en $L_1$ — no la ruta euclidiana más corta para un robot con diagonales.

</div>
</div>

<!--
La etiqueta de la guía se refiere a las limitaciones de la implementación, no a la teoría de Bellman.
-->

---
layout: default
---

# Costo: bueno en 20 × 20, insuficiente en la casa

<div class="grid grid-cols-[1fr_1fr] gap-8 mt-4 text-sm">

<div>

**Complejidad**

- Cada barrido: $O(N^2)$ (una visita por celda, 4 vecinos)
- Barridos: al menos $O(N)$ para propagar la información
- Costo típico: $O(N^3)$; peor caso (laberinto): $O(N^4)$
- Memoria: $O(N^2)$

**En este mapa**

100 barridos × 400 celdas × 4 vecinos ≈ $1.6 \times 10^5$ actualizaciones ≈ 31 ms. **95 de los 100 barridos no cambian nada**: el mapa se estabiliza en 5.

</div>

<div class="p-4 rounded border border-[#5d8392]/30">

**La casa del libro (397 × 596)**

| Dato | Valor |
| --- | ---: |
| Barridos necesarios | **571** |
| Celdas inalcanzables | 9925 |
| Bug2 (completo) | 1307 pasos |
| Distance transform | **338 pasos** |

Con el límite fijo de 100 barridos, el código de la guía **ni siquiera convergería**. El número de barridos debe adaptarse al mapa o detectar la convergencia y detenerse.

</div>
</div>

<div class="mt-4 p-3 rounded bg-orange-500/10 border-l-4 border-orange-400 text-sm">
  Es el precio de la solución global: el DT paga cómputo por adelantado, pero no cicla, es completo y devuelve la ruta óptima para cualquier inicio.
</div>

<!--
Este es el argumento central de D frente a B: optimalidad a cambio de cómputo previo y de necesitar el mapa completo.
-->

---
layout: default
---

# Síntesis: el precio de saber más

| Parte | Método | ¿Mapa? | ¿Memoria? | ¿Óptimo? | Resultado 20×20 |
|---|---|---|---|---|---|
| **A** | Braitenberg | No | No | No | d-mín = 9.57; no llega |
| **B** | Bug2 simplificado | No | Sí (camino) | Aquí 32; en general no | 32 pasos |
| **C** | A\* | Sí | Sí (cola y costos) | Sí, con h admisible | 32 pasos; 305 expansiones |
| **D** | Distance transform | Sí | Sí (mapa de D) | Sí (Bellman, L1) | 32 pasos; D(inicio) = 32 |

<div class="grid grid-cols-3 gap-4 mt-6 text-sm">

<div class="p-3 rounded bg-[#5d8392]/10">
  <strong>A → B</strong><br/>
  Se añade <strong>estado</strong>: aparece la evasión de obstáculos.
</div>

<div class="p-3 rounded bg-[#5d8392]/10">
  <strong>B → C/D</strong><br/>
  Se añade <strong>mapa global</strong>: aparece la optimalidad.
</div>

<div class="p-3 rounded bg-[#5d8392]/10">
  <strong>C ↔ D</strong><br/>
  A* busca solo lo necesario; el DT resuelve <strong>para todas</strong> las celdas.
</div>
</div>

<!--
La progresión no es de "mejores algoritmos", es de más información y más cómputo. Cada paso paga algo.
-->

---
layout: default
---

# Conclusiones (1/2)

<div class="text-sm mt-2 space-y-3">

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**1. La ley de Braitenberg de la guía no converge.** Velocidad negativa sin saturación + ausencia de condición de parada = sobrepaso. Con T = 500 termina a 131.62 celdas; con T = 2000, a 117.95. Aumentar iteraciones solo alarga la órbita. La ley del libro (v = 2 − sR − sL) sí frena porque v → 0 en el objetivo.

</div>

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**2. El Bug2 simplificado es óptimo aquí, pero no en general.** 32 pasos alcanza la cota de Manhattan en este mapa. Sin embargo, al invertir inicio y objetivo cicla entre dos celdas durante 500 iteraciones. El Bug2 completo evita el ciclo con la m-line, pero sigue siendo subóptimo (1307 vs 338 en la casa).

</div>

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**3. A\* y el distance transform coinciden en longitud, no en camino.** Ambos dan 32 pasos por rutas distintas (arriba vs borde superior-izquierdo). A\* busca solo lo necesario; el DT precomputa la solución para todas las celdas.

</div>

</div>

<!--
Tres conclusiones que responden directamente a las preguntas de la guía.
-->

---
layout: default
---

# Conclusiones (2/2)

<div class="text-sm mt-2 space-y-3">

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**4. La heurística euclidiana es admisible pero poco informativa en 4-conectividad.** A\* expande el 85 % de las celdas libres. Una heurística Manhattan seguiría siendo admisible y expandiría menos, sin perder optimalidad.

</div>

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**5. El límite fijo de 100 barridos no escala.** En 20 × 20 sobran 95 barridos; en la casa del libro (397 × 596) se necesitan 571. Hay que detectar la convergencia o adaptar el número de barridos al tamaño del mapa.

</div>

<div class="p-3 rounded border-l-4 border-[#5d8392] bg-[#5d8392]/5">

**6. La parte E (ROS2 / Nav2) queda fuera de esta entrega.** A–D cubren navegación reactiva, evasión, planificación y mapas de ocupación. La integración en el stack de Nav2 se deja para una entrega posterior.

</div>

</div>

<div class="mt-5 p-3 rounded bg-[#5d8392]/10 text-sm">
  <strong>Idea de cierre:</strong> no hay un algoritmo "mejor". Hay un compromiso entre información disponible, cómputo y garantías — y cada parte del laboratorio mueve una de esas tres piezas.
</div>

<!--
Cierre: el hilo del laboratorio es el compromiso información ↔ cómputo ↔ garantías.
-->

---
layout: default
---

# Trabajo futuro

<div class="grid grid-cols-2 gap-6 mt-6 text-sm">

<div>

**Corto plazo**

- Parte E: llevar A\* y el DT a **Nav2** con un robot simulado
- Repetir A con la ley del libro y comparar la convergencia
- Heurística Manhattan en A\*: medir cuántas expansiones ahorra

</div>

<div>

**Mediano plazo**

- Detección de convergencia en el DT en lugar de 100 barridos fijos
- Extender la métrica a **8 vecinos** (Chebyshev / euclidiana)
- Bug2 completo con m-line y comparación cuantitativa

</div>
</div>

<div class="mt-8 grid grid-cols-3 gap-4 text-center text-sm">

<div class="p-4 rounded border border-[#5d8392]/30">
  <div class="text-2xl font-bold" style="color:#5d8392">4</div>
  <div class="opacity-60">actividades implementadas</div>
</div>

<div class="p-4 rounded border border-[#5d8392]/30">
  <div class="text-2xl font-bold" style="color:#5d8392">12</div>
  <div class="opacity-60">preguntas respondidas</div>
</div>

<div class="p-4 rounded border border-[#5d8392]/30">
  <div class="text-2xl font-bold" style="color:#5d8392">1</div>
  <div class="opacity-60">comando para reproducir todo</div>
</div>
</div>

<!--
Cierre del alcance y de lo que sigue. El comando es `python experimentos/run_all.py`.
-->

---
layout: default
---

# Referencias

<div class="text-sm mt-6 space-y-4">

**Corke, P.** (2023). *Robotics, Vision and Control: Fundamental Algorithms in Python* (3rd ed.). Springer.
Capítulo 5: §5.1.1 (Braitenberg), §5.1.2 (Bug2), §5.3 (A*), §5.4.1 (distance transform).

**Guía de laboratorio de simulación, Capítulo 5 — Corke.** Universidad Nacional de Colombia, sede Manizales, 2026.

**Corke, P.** *RVC3-python*: notebook `notebooks/chap5.ipynb` y modelo `RVC3/models/braitenberg.py`.

**Resultados locales:** `Laboratorio/resultados/metricas.csv` y `Laboratorio/figuras/`.

</div>

<div class="mt-10 p-4 rounded bg-[#5d8392]/10 border-l-4 border-[#5d8392] text-sm">

**Reproducir todo** (desde `Laboratorio/`, con el entorno del curso):

```bash
source ~/venvs/robotica/bin/activate
python experimentos/run_all.py
```

</div>

<!--
Todo el material está en el repositorio del curso, con figuras a 300 dpi y métricas en CSV.
-->

---
layout: end
class: text-center
---

# ¿Preguntas?

Gracias

<div class="pt-8 text-sm opacity-60">
  Juan David · Robótica · UNAL Manizales · 2026-2
</div>

<!--
Fin. Aceptar preguntas sobre cualquiera de las cuatro partes.
-->
