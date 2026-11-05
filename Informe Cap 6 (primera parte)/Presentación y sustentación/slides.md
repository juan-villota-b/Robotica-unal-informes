---
theme: default
title: Localización y mapeo — Capítulo 6
info: |
  ## Robótica · Capítulo 6
  Odometría, EKF, landmarks y SLAM
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

# Localización y mapeo

Odometría · EKF · Landmarks · SLAM

<div class="pt-10 opacity-70 text-sm">
  Robótica — Capítulo 6 · Corke, <em>Robotics, Vision and Control</em>
</div>

<div class="abs-br m-6 flex gap-2">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover:bg="white op-10">
    Presiona <kbd>espacio</kbd> para avanzar <carbon:arrow-right class="inline" />
  </span>
</div>

---
layout: default
---

# La ruta: siete puntos de la guía

<div class="text-sm opacity-70 mb-4">
  Un solo hilo conductor: estimar la pose y medir cuánto se sabe de ella.
</div>

<div class="grid grid-cols-3 gap-4 text-sm">

<div class="p-3 rounded bg-blue-500/10 border-l-4 border-blue-400">
<strong>1 · Odometría</strong><br>
Integrar el movimiento y ver cómo se acumula el error.
</div>

<div class="p-3 rounded bg-blue-500/10 border-l-4 border-blue-400">
<strong>2 · EKF</strong><br>
Propagar también la covarianza: la incertidumbre crece.
</div>

<div class="p-3 rounded bg-blue-500/10 border-l-4 border-blue-400">
<strong>3 · Landmarks</strong><br>
Corregir con un mapa conocido: la incertidumbre se acota.
</div>

<div class="p-3 rounded bg-red-500/10 border-l-4 border-red-400">
<strong>4 · SLAM</strong><br>
Pose y mapa a la vez: sin mapa previo.
</div>

<div class="p-3 rounded bg-green-500/10 border-l-4 border-green-400">
<strong>5–7 · ROS 2</strong><br>
Controlador, Cartographer y mapa guardado.
</div>

<div class="p-3 rounded bg-gray-500/10 border-l-4 border-gray-400">
<strong>Variables</strong><br>
<code>V</code> odometría · <code>P₀</code> inicial · <code>W</code> sensor.
</div>

</div>

<div class="mt-4 text-xs opacity-60">
  Las partes 1–4 salen del mismo experimento (semilla fija), así que las figuras son comparables entre sí.
</div>

---
layout: default
zoom: 0.92
---

# Parte 1 · Odometría: el error se acumula

<div class="text-sm opacity-70 mb-1">
  ← Punto de partida de todas las partes: un robot que solo integra su propia odometría.
</div>

<img src="/p1.png" class="w-full max-h-[260px] object-contain" />

<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs mt-2">

<div>

**¿Por qué la trayectoria presenta error?**
Cada paso suma ruido gaussiano; al integrarlo, el error se acumula y no se corrige nunca.

</div>

<div>

**¿Qué representa `V`?**
La covarianza del ruido de odometría: varianzas de velocidad y de timón.

</div>

<div>

**¿Qué ocurre si aumenta el ruido?**
La curva con ruido se separa antes y el error final crece.

</div>

<div>

**Dato:** 200 pasos de (1.0 m/s, 0.2 rad); error final ≈ 1 m.

</div>

</div>

---
layout: default
zoom: 0.92
---

# Parte 2 · EKF sin sensores: la incertidumbre crece

<div class="text-sm opacity-70 mb-1">
  ← Si la Parte 1 acumulaba error, aquí además se propaga la covarianza del filtro.
</div>

<img src="/p2.png" class="w-full max-h-[260px] object-contain" />

<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs mt-2">

<div>

**¿Por qué el EKF no corrige el error?**
No hay observaciones: sin innovación, el filtro solo propaga la odometría.

</div>

<div>

**¿Qué mide la curva de la derecha?**
`sqrt(det P)`: crece de 3.3e-5 a 1.6e-2, unas 470 veces en 20 s.

</div>

<div>

**¿Qué ocurre si aumenta `V`?**
La covarianza crece más rápido; la curva se empina.

</div>

<div>

**Dato:** `T = 20 s` con `dt = 0.1` → 200 pasos.

</div>

</div>

---
layout: default
zoom: 0.92
---

# Parte 3 · Landmarks: la incertidumbre se acota

<div class="text-sm opacity-70 mb-1">
  ← Frente a la Parte 2, ahora hay mediciones externas que corrigen la pose.
</div>

<img src="/p3.png" class="w-full max-h-[260px] object-contain" />

<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs mt-2">

<div>

**¿Qué es la innovación?**
La diferencia entre lo medido y lo predicho: `z − h(x)`.

</div>

<div>

**¿Por qué disminuye la incertidumbre?**
Cada landmark aporta información y reduce la covarianza; los dientes de sierra son esas correcciones.

</div>

<div>

**¿Qué ocurre sin landmarks?**
Vuelve al caso de la Parte 2: la incertidumbre crece sin freno.

</div>

<div>

**Dato:** 20 landmarks, alcance 4 m, apertura 180°.

</div>

</div>

---
layout: default
zoom: 0.92
---

# Parte 4 · SLAM: el mapa también se estima

<div class="text-sm opacity-70 mb-1">
  ← La Parte 3 conocía el mapa; aquí hay que estimar pose <em>y</em> mapa a la vez.
</div>

<img src="/p4_slam.png" class="w-full max-h-[250px] object-contain" />

<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs mt-2">

<div>

**¿Por qué es más complejo?**
El estado crece `3 + 2N` y hay que asociar cada observación con su landmark.

</div>

<div>

**¿Por qué no desaparece la incertidumbre?**
Los landmarks también son incógnitas: solo se reduce al revisitar zonas conocidas.

</div>

<div>

**Comparación con la Parte 3:** la incertidumbre de la pose pasa de 1.4e-5 a 7.3e-3.

</div>

<div>

**Ventaja:** no necesita mapa previo; construye el mapa mientras se localiza.

</div>

</div>

---
layout: default
zoom: 0.9
---

# Parte 5 · SLAM en ROS 2 con Cartographer

<div class="text-sm opacity-70 mb-1">
  ← Lo que en Python era un EKF, en ROS 2 es un pipeline de nodos sobre el TurtleBot3.
</div>

<img src="/p5.png" class="w-full max-h-[235px] object-contain" />

<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs mt-2">

<div>

**Pipeline:** Gazebo → `/scan`, `/odom`, `/tf` → Cartographer → `/map` → RViz2.

</div>

<div>

**Controlador reactivo:** si el LiDAR frontal detecta &lt; 0.5 m, gira en el sitio; si no, avanza.

</div>

<div>

**Mapa guardado:** `my_map.pgm` + `my_map.yaml` a 0.05 m/celda con `map_saver_cli`.

</div>

<div>

**Evidencia:** 110 s de grabación. El paquete del laboratorio usa ROS 2 lyrical con `TwistStamped`.

</div>

</div>

---
layout: end
---

# Referencias

<div class="text-left text-sm leading-relaxed mt-6">

- **Guía:** *Guía de laboratorio Capítulo 6 — Localización y mapeo*, 21 pp. (carpeta Guia/).
- **Libro:** P. Corke, *Robotics, Vision and Control*, 3.ª ed., Springer 2023, cap. 6.
- **Código del libro:** RVC3-python/notebooks/scripts/chap6.py.
- **Evidencia ROS 2:** Ref/informe_laboratorio_slam_cartographer.md y Ref/Mapeado con cartografher.webm.
- **Librerías:** roboticstoolbox-python 1.4.2 y spatialmath-python 1.1.17.
- **Revisión del código:** REPORTE_GUIA_CAP6.md.

</div>

<div class="mt-8 opacity-60 text-xs">
  Todas las figuras provienen de los scripts del laboratorio; no hay simulaciones en vivo.
</div>
