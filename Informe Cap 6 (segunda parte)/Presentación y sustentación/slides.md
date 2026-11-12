---
theme: default
title: SLAM en ROS 2 — Capítulo 6, parte 8
info: |
  ## Robótica · Capítulo 6 · Parte 8
  Del simulador al mapa: TurtleBot3, Gazebo y SLAM Toolbox
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
---

<img src="/cover-crema.png" class="absolute inset-0 w-full h-full object-cover -z-10" />

<div class="relative text-[#2a2620]">

# Del simulador al mapa

<div class="text-lg opacity-80 mt-2">SLAM en ROS 2 con TurtleBot3 y Gazebo</div>

<div class="mx-auto mt-5 h-1 w-24 rounded bg-[#1f3a5f]"></div>

<div class="pt-8 text-base opacity-80">
  Jhon Hesneydert Londoño · Juan David Villota
</div>

<div class="pt-2 opacity-60 text-sm">
  Robótica — Capítulo 6 · Parte 8 · UNAL Manizales
</div>

<div class="pt-1 opacity-50 text-xs">
  github.com/juan-villota-b
</div>

</div>


---

# Las preguntas de esta simulación

<div class="text-sm opacity-70 mb-5">
  <code>simple_controller</code> de la guía: publica 0.2 m/s y 0.1 rad/s a 10 Hz. No se suscribe a nada.
</div>

<div class="grid grid-cols-3 gap-3 text-sm">

<div class="p-3 rounded bg-red-500/10 border-l-4 border-red-400">
<div class="font-bold mb-1">¿Y si choca?</div>
Sigue mandando la misma velocidad. El plugin retiene el último comando: no hay <em>timeout</em>.
</div>

<div class="p-3 rounded bg-red-500/10 border-l-4 border-red-400">
<div class="font-bold mb-1">¿Y si se vuelca?</div>
Las ruedas giran en el aire, la odometría reporta avance y RViz sigue “mapeando” un robot caído.
</div>

<div class="p-3 rounded bg-red-500/10 border-l-4 border-red-400">
<div class="font-bold mb-1">¿Cubre el mapa?</div>
El círculo de 2 m se queda en una franja: la arena mide 5.6 m y es hexagonal.
</div>

</div>

<div class="mt-7 grid grid-cols-3 gap-4 items-center text-sm">

<div class="col-span-2 p-3 rounded bg-gray-500/10 border-l-4 border-gray-400">
<strong>Medido antes de tocar nada</strong><br>
<span class="opacity-70">pitch oscilando 75° → 89° (rango 14.75°) · giroscopio en 0 con comando de 0.5 rad/s · altura del modelo 0.038 m</span>
</div>

<div class="text-center">
<div class="text-4xl font-bold text-[#1f3a5f]">90°</div>
<div class="text-xs opacity-60">robot volcado</div>
</div>

</div>

<div class="mt-6 p-3 rounded bg-amber-500/10 border-l-4 border-amber-400 text-sm">
Con el LiDAR mirando al piso, cada barrido era un corte distinto del mundo: el mapa no podía salir bien.
</div>

---
layout: two-cols
---

# El LiDAR mide un plano

El LDS-01 lanza el láser en **un plano horizontal** a 17 cm del piso y devuelve 360 distancias. No hay altura ni volumen: es **una rebanada** del mundo.

Si el robot se inclina un ángulo $\phi$, el haz que va a distancia $d$ se desvía:

$$d\tan\phi$$

Y el piso se vuelve un obstáculo fantasma a:

$$d=\frac{h}{\tan\phi}\approx 1.4\ \text{m}\quad(\phi=7^\circ)$$

::right::

<div class="pl-6 pt-2">

| Distancia | Desvío a 7° |
|---|---|
| 1 m | 12 cm |
| 2 m | 25 cm |
| 3.5 m | **43 cm** |

<div class="mt-5 p-3 rounded bg-red-500/10 border-l-4 border-red-400 text-sm">
El <em>scan matching</em> solo puede trasladar y girar: <strong>no tiene variable para la inclinación</strong>. Con cada barrido distinto elige la transformación “menos mala” y el mapa se ensucia.
</div>

</div>

---

# Modificación 1 · La física del robot

<div class="text-sm opacity-70 mb-5">
  El modelo oficial de Gazebo deja el caster <strong>1 mm en el aire</strong>: el robot se sostiene en dos ruedas y se mece.
</div>

<div class="grid grid-cols-2 gap-7 text-sm">

<div>

<div class="p-3 rounded bg-gray-500/10 border-l-4 border-gray-400 mb-4 text-xs">
<strong>Archivos nuevos</strong><br>
<code>models/turtlebot3_burger/model.sdf</code><br>
<code>launch/lab_world.launch.py</code>
</div>

| Parámetro | Antes | Ahora |
|---|---|---|
| caster `z` | −0.004 | **−0.006** |
| ruedas `mu` | 100 000 | **1.0** |
| `min_depth` | 0.001 | **0.0** |

</div>

<div>

<div class="grid grid-cols-2 gap-3 mb-4">
<div class="p-3 rounded bg-red-500/10 text-center">
<div class="text-3xl font-bold text-red-700">14.75°</div>
<div class="text-xs opacity-60">balanceo antes</div>
</div>
<div class="p-3 rounded bg-green-500/10 text-center">
<div class="text-3xl font-bold text-green-700">0.00°</div>
<div class="text-xs opacity-60">después</div>
</div>
</div>

<div class="p-3 rounded bg-green-500/10 border-l-4 border-green-500">
Con el caster apoyado y fricción real, el plano del LiDAR queda horizontal y <strong>cada barrido vuelve a ser válido</strong>.
</div>

</div>

</div>

---
layout: two-cols
---

# Del lazo abierto al seguidor de pared

El controlador de la guía no controla: **genera comandos**. Para mapear hacía falta algo que mirara el entorno.

La regla es mantener la pared de la derecha a 0.9 m:

$$\omega=-k\,(d-0.9)$$

con $\omega$ saturado a $\pm 0.35$ rad/s.

- Si el frente ve menos de 0.45 m: gira en el lugar.
- Si ve menos de 1.0 m: baja a 0.06 m/s.

::right::

<div class="pl-6 pt-4">

```python
right = self.right_range
error = right - self.wall_distance
omega = max(-0.35, min(0.35, -0.9 * error))

speed = 0.14 if self.front_range > 1.0 else 0.06
self.publish(speed, omega)
```

<div class="mt-4 text-xs opacity-70">
Mide con <code>/odom</code>, no con el reloj, y se adapta a la forma real de la arena en vez de seguir coordenadas fijas.
</div>

</div>


---

# Modificación 3 · Cartographer no está: SLAM Toolbox

<div class="grid grid-cols-2 gap-6 text-[0.7rem] leading-snug">

<div>

<div class="p-3 rounded bg-red-500/8 border-l-4 border-red-400 mb-3">
<strong>El problema de empaquetado</strong><br>
Para <em>lyrical</em> solo existe <code>cartographer-ros-msgs</code>. No hay <code>cartographer_ros</code>: los pasos 8.5, 8.13 y 8.21 no se pueden ejecutar.
</div>

<div class="p-3 rounded bg-green-500/8 border-l-4 border-green-500 mb-3">
<strong>La alternativa</strong><br>
<code>ros-lyrical-slam-toolbox</code> 2.10.0: grafo de poses + matcher Karto + optimizador Ceres. Modo <em>online</em> y <em>lifelong</em>.
</div>

<div class="p-2 rounded bg-gray-500/8 border-l-4 border-gray-400">
La interfaz observable es la misma: <code>/map</code>, TF <code>map→odom</code> y el mismo <code>map_saver_cli</code>.
</div>

</div>

<div>

| | Cartographer | SLAM Toolbox |
|---|---|---|
| Origen | Google | comunidad ROS 2 |
| Estructura | submapas + grafo | poses + barridos |
| Matcher | correlación *branch-and-bound* | Karto |
| Config | <code>.lua</code> | <code>.yaml</code> |
| Extra | <code>/submap_list</code> | grafo en MarkerArray |

<div class="mt-3 p-2 rounded bg-blue-500/8 border-l-4 border-blue-400">
<strong>Qué se conservó:</strong> <code>cartographer.lua</code> y <code>cartographer.launch.py</code> quedan en el paquete para reproducir la guía literal en Jazzy. El <code>.yaml</code> replica sus números: 0.05 m/celda, rango 0.12–3.5 m, frames <code>map</code>/<code>odom</code>/<code>base_footprint</code>.
</div>

</div>

</div>

<div class="mt-3 text-[0.65rem] opacity-70">
Además: RViz sin el panel <code>Displays</code> y Gazebo sin <code>EntityTree</code>, para que la grabación muestre solo el mapa y el mundo.
</div>

---

# Las 5 terminales y el paquete

<div class="grid grid-cols-2 gap-6 text-[0.68rem] leading-snug mt-2">

<div>

<div class="font-bold text-[0.75rem] mb-2 text-[#1f3a5f]">Qué corre en cada una</div>

<div class="space-y-2">

<div class="p-2 rounded bg-orange-500/8 border-l-4 border-orange-400">
<strong>T1 · Gazebo</strong> — <code>ros2 launch localization_lab lab_world.launch.py</code><br>
<span class="opacity-70">Simula el mundo y el burger; publica <code>/scan</code>, <code>/odom</code> y <code>/clock</code>.</span>
</div>

<div class="p-2 rounded bg-purple-500/8 border-l-4 border-purple-400">
<strong>T2 · SLAM</strong> — <code>ros2 launch localization_lab slam_toolbox.launch.py</code><br>
<span class="opacity-70">Alinea barridos y publica <code>/map</code> + TF <code>map→odom</code>.</span>
</div>

<div class="p-2 rounded bg-blue-500/8 border-l-4 border-blue-400">
<strong>T3 · Control</strong> — <code>ros2 run localization_lab patrol_controller</code><br>
<span class="opacity-70">Lee <code>/scan</code> y <code>/odom</code>; decide la velocidad y la publica en <code>/cmd_vel</code>.</span>
</div>

<div class="p-2 rounded bg-green-500/8 border-l-4 border-green-500">
<strong>T4 · RViz2</strong> — <code>rviz2 -d .../rviz/slam.rviz</code><br>
<span class="opacity-70">Dibuja el mapa, el barrido y los frames; no calcula nada.</span>
</div>

<div class="p-2 rounded bg-gray-500/8 border-l-4 border-gray-400">
<strong>T5 · Mapa</strong> — <code>map_saver_cli -f mapa</code><br>
<span class="opacity-70">Congela <code>/map</code> en <code>.pgm</code> + <code>.yaml</code>.</span>
</div>

</div>

</div>

<div>

<div class="font-bold text-[0.75rem] mb-2 text-[#1f3a5f]">Cómo está organizado el paquete</div>

```text
localization_lab/
├── package.xml          dependencias
├── setup.py             entry points
├── localization_lab/
│   ├── simple_controller.py    la guía
│   └── patrol_controller.py    seguidor
├── launch/   lab_world · slam_toolbox
├── config/   cartographer.lua · slam_toolbox.yaml
├── models/   turtlebot3_burger
└── rviz/     slam.rviz
```

<div class="mt-3 p-2 rounded bg-blue-500/8 border-l-4 border-blue-400">
Cada nodo declara sus parámetros (<code>linear_speed</code>, <code>wall_distance</code>, <code>duration</code>), así el comportamiento se cambia sin editar código.
</div>

<div class="mt-2 p-2 rounded bg-gray-500/8 border-l-4 border-gray-400">
Un solo <code>colcon build --symlink-install</code> compila el paquete y deja los dos ejecutables.
</div>

</div>

</div>

---

# Resultado · el mapa

<div class="grid grid-cols-2 gap-8 items-center">

<div>

<div class="text-xs opacity-70 mb-2">Salida de <code>map_saver_cli</code> + conversión a PNG</div>

<img src="/mapa.png" class="w-full rounded border border-gray-300" />

</div>

<div class="text-sm">

<div class="grid grid-cols-2 gap-3 mb-5">
<div class="p-3 rounded bg-blue-500/10">
<div class="text-2xl font-bold text-[#1f3a5f]">112 × 103</div>
<div class="text-xs opacity-60">celdas</div>
</div>
<div class="p-3 rounded bg-blue-500/10">
<div class="text-2xl font-bold text-[#1f3a5f]">5.6 × 5.15 m</div>
<div class="text-xs opacity-60">a 0.05 m/celda</div>
</div>
</div>

- Hexágono cerrado, sin paredes dobles.
- Los **9 cilindros** del centro en su grilla de 3 × 3.
- Recorrido por el anillo libre, sin tocar obstáculos.

<div class="mt-5 p-3 rounded bg-green-500/10 border-l-4 border-green-500 text-xs">
El mapa es el insumo de AMCL y Nav2: cierra el ciclo del capítulo.
</div>

</div>

</div>

---

# Arranque y final de la corrida

<div class="grid grid-cols-2 gap-5">

<div>
<img src="/arranque.png" class="w-full rounded border border-gray-300" />
<div class="text-xs opacity-70 mt-2 text-center">Primeros barridos: solo el sector que el LiDAR alcanza a ver.</div>
</div>

<div>
<img src="/final.png" class="w-full rounded border border-gray-300" />
<div class="text-xs opacity-70 mt-2 text-center">Al detenerse: la arena completa, con paredes y cilindros.</div>
</div>

</div>

<div class="mt-5 p-3 rounded bg-gray-500/10 border-l-4 border-gray-400 text-sm">
Lo que cambia entre las dos no es el algoritmo: es la <strong>cobertura</strong>. El primer barrido ya es válido porque el plano del LiDAR está horizontal.
</div>

---

# Respuestas · problemas y soluciones

<div class="text-sm mt-2">

| Problema | Causa | Solución |
|---|---|---|
| `cartographer_ros` no instala | no está publicado para *lyrical* | SLAM Toolbox, mismo `/map` y TF `map→odom` |
| El robot se mecía y se volcaba | caster 1 mm en el aire + fricción infinita | modelo propio: caster −0.006 y `mu` 1.0 |
| El mapa salía borroso | plano del LiDAR inclinado | consecuencia del anterior |
| El cuadrado no cubría la arena | arena hexagonal de 5.6 m | seguidor de pared con `/scan` |
| El robot no se movía | simulación en pausa: `/clock` no avanzaba | reanudar con `/world/default/control` |
| Se cerraba todo al cerrar Gazebo | `on_exit_shutdown` en el cliente | no cerrar la GUI durante la demo |
| `ros2 run` no encontraba el nodo | `console_scripts` vacío en la guía | entry point en `setup.py` |

</div>

<div class="mt-4 text-xs opacity-60">
Todas las diferencias están documentadas en el README del laboratorio, con el número de anomalía.
</div>

---

# Demostración en video

<div class="mt-8 text-center">

<div class="text-sm opacity-70 mb-8">Recorrido completo del seguidor de pared, con RViz y Gazebo en paralelo.</div>

<a href="https://youtu.be/JArwIEL_Rsk" target="_blank" class="inline-block px-14 py-9 rounded-xl border-2 border-[#1f3a5f]/30 bg-blue-500/5">

<div class="text-2xl font-bold text-[#1f3a5f] mb-2">▶ Ver grabación</div>

<div class="text-sm opacity-70">youtu.be/JArwIEL_Rsk</div>

</a>

<div class="mt-8 text-xs opacity-60">240 s de recorrido · 4:27 de video · mapa guardado en <code>.pgm</code> + <code>.yaml</code></div>

</div>

---

# Conclusiones

<div class="grid grid-cols-3 gap-4 text-sm mt-8">

<div class="p-4 rounded bg-blue-500/10 border-l-4 border-blue-400">
<div class="text-4xl font-bold text-[#1f3a5f] mb-3">01</div>
No se depura el algoritmo: se depura la <strong>suposición física</strong>. Un LiDAR 2D exige un plano horizontal.
</div>

<div class="p-4 rounded bg-blue-500/10 border-l-4 border-blue-400">
<div class="text-4xl font-bold text-[#1f3a5f] mb-3">02</div>
El control de la guía es de <strong>lazo abierto</strong>. Cambiarlo por uno que mire el sensor permitió recorrer toda la arena.
</div>

<div class="p-4 rounded bg-blue-500/10 border-l-4 border-blue-400">
<div class="text-4xl font-bold text-[#1f3a5f] mb-3">03</div>
El mapa es una <strong>estimación</strong>: se corrige, se ensucia y se reacomoda. Guardarlo bien es lo que lo vuelve útil.
</div>

</div>

<div class="mt-10 text-center text-xs opacity-60">
<a href="https://github.com/juan-villota-b/Robotica-unal-informes">github.com/juan-villota-b/Robotica-unal-informes</a>
</div>
