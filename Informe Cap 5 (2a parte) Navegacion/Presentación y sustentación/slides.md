---
theme: default
title: Informe Cap 5 parte E — Navegación en ROS 2
info: |
  ## Parte E: Navegación Autónoma y Control Reactivo
  Robótica · UNAL Manizales · Semestre VIII · 2026-2
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
background: /cover.svg
---

<div class="pt-6">

<div class="etiqueta">Robótica · UNAL Manizales</div>

<h1 class="portada-titulo">Informe Cap 5 · Parte E</h1>

<div class="text-xl opacity-80 mt-1">Navegación autónoma y control reactivo en ROS 2 Humble</div>

<div class="flex gap-2 justify-center mt-6">
  <span class="chip">TurtleBot3 Burger</span>
  <span class="chip">Gazebo</span>
  <span class="chip">Nav2</span>
  <span class="chip">Nodo reactivo</span>
</div>

<div class="mt-10 text-base text-gray-600">
  Jhon Hesneydert Londoño · Juan David Villota
</div>

<div class="text-sm text-gray-500 mt-2">Semestre VIII · 2026-2</div>

</div>

---
layout: default
---

# E1 — Nav2 con mapa previo

<div class="flex gap-6 mt-2">

<div class="w-1/2">

Se lanza el TurtleBot3 en Gazebo con un mapa ya construido (`mapa_lab.yaml`,
0.05 m/celda). Nav2 localiza con AMCL, el planner traza la ruta y el controller
la sigue. En RViz se marca **2D Pose Estimate** y luego **Nav2 Goal**.

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 \
  navigation2.launch.py use_sim_time:=True \
  map:=/root/mapa_lab.yaml autostart:=True
```

</div>

<div class="w-1/2">
  <img src="/e1_rviz.png" class="w-full rounded shadow" />
</div>

</div>

---
layout: default
---

# E2 — Nodo reactivo

<div class="flex gap-6 mt-2">

<div class="w-1/2">

Va de `/scan` a `/cmd_vel` con control puramente reactivo: en cada lectura avanza
(0.2 m/s) o gira en el sitio (0.5 rad/s) si hay un obstáculo a menos de 0.5 m.
No usa mapa, odometría ni planificación.

```python
d = msg.ranges[0]
if 0.0 < d < 0.5:
    cmd.linear.x, cmd.angular.z = 0.0, 0.5
else:
    cmd.linear.x, cmd.angular.z = 0.2, 0.0
```

```bash
colcon build --packages-select mi_paquete_navegacion
ros2 run mi_paquete_navegacion nodo_reactivo
```

</div>

<div class="w-1/2">
  <img src="/e2_gazebo.png" class="w-full rounded shadow" />
</div>

</div>

---
layout: default
---

# Preguntas

<div class="space-y-4 mt-2">

<div class="tarjeta">

**1. Reactivo vs Nav2.** El reactivo acopla sensor y actuador: decide con la
lectura instantánea del LiDAR, sin mapa ni memoria, así que es rápido pero no
garantiza llegar y puede quedar atrapado en un obstáculo en "U". Nav2 es
jerárquico: localiza en el mapa (AMCL), planifica una ruta global, la sigue con
un controller local y se recupera con un árbol de comportamiento.

</div>

<div class="tarjeta">

**2. Función del planner.** Convierte la meta en una ruta (`nav_msgs/Path`) que
el controller pueda seguir: expande celdas sobre el mapa de costos minimizando
$g+h$ (NavFn con A\* o Dijkstra) y recalcula cuando la ruta se invalida o el
robot se desvía.

</div>

<div class="tarjeta">

**3. Ventajas de ROS 2.** Nodos desacoplados que se comunican por DDS, acciones
con progreso y cancelación, ciclo de vida para arrancar en orden, TF2 y RViz
como herramientas comunes, y la misma pila de navegación en simulación y en el
robot real.

</div>

</div>

---
layout: default
---

# Comparación

| Criterio | Reactiva | Nav2 |
| --- | --- | --- |
| Información | Solo `/scan` | Mapa + LiDAR + odometría |
| Memoria | Ninguna | Ruta y costmaps |
| Optimalidad | No | Sí (A\* / Dijkstra) |
| Obstáculo | Gira y sigue | Replanifica |
| Falla típica | Trampa local ("U") | Mapa incorrecto |

---
layout: default
---

# Visualizaciones en RViz

| Video | Tema | Enlace |
| --- | --- | --- |
| 1 | Navegación con Nav2 | <https://youtu.be/CKRkHOLL7Mo> |
| 2 | Navegación automática | <https://youtu.be/04T-c-QD1vQ> |
| 3 | Mapeado con navegación automática | <https://youtu.be/eLvfvaTScak> |
