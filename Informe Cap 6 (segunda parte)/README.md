# Informe Cap 6 — Segunda parte

**Qué es:** la continuación del trabajo del Capítulo 6, centrada en la
**sección 8 de la guía** («Parte 5 — SLAM con Cartographer usando ROS2 Jazzy +
Turtlebot3 + Gazebo + RViz2», pp. 10–21 del PDF). La primera parte cubrió las
partes 1–4 (odometría, EKF, landmarks y SLAM con EKF en Python); esta cubre el
pipeline real en ROS 2.

## Contenido

```
Informe Cap 6 (segunda parte)/
├── Guia/
│   ├── GUÍA DE LABORATORIO CAP6.pdf            ← guía completa (21 pp.)
│   ├── GUIA_CAP6.md                            ← guía completa en Markdown
│   └── PARTE_8 - SLAM con Cartographer en ROS2.md  ← §8 extraída y renumerada 8.1–8.26
├── Laboratorio/
│   ├── README.md                               ← comandos exactos y verificación
│   ├── ros2_ws/src/localization_lab/           ← paquete compilado
│   └── evidencias/                             ← mapa, capturas y logs de la corrida
├── Informe/
│   └── INFORME_CAP6_P2.md                      ← informe redactado con resultados reales
└── Presentación y sustentación/                ← pendiente
```

## Qué pide la parte 8 (resumen)

| Bloque | Pasos | Contenido |
|---|---|---|
| Entorno | 8.1–8.6 | ROS 2, TurtleBot3, Gazebo Harmonic, Cartographer, Nav2 |
| Paquete | 8.7–8.12 | workspace, `ros2 pkg create`, nodo, `setup.py`, `package.xml` |
| Configuración | 8.13–8.14 | `cartographer.lua` y `cartographer.launch.py` |
| Ejecución | 8.15–8.24 | compilar, Gazebo, tópicos, controlador, SLAM, RViz2 |
| Cierre | 8.25–8.26 | guardar mapa (`.pgm` + `.yaml`) y concepto central |

## Estado

| Entregable | Estado |
|---|---|
| Guía extraída y renumerada | listo |
| Paquete + build | listo (`colcon build` OK) |
| Corrida del pipeline | lista (mapa 9.40 × 8.35 m, 90 s) |
| Evidencias (mapa, capturas, logs) | listas en `Laboratorio/evidencias/` |
| Informe | redactado (`Informe/INFORME_CAP6_P2.md`) |
| Presentación y sustentación | **pendiente** |

## Lo que hay que saber antes de correrlo

1. La distro de este equipo es **lyrical**, no jazzy: el paso 8.5 (Cartographer)
   no existe y se reemplaza por **SLAM Toolbox** (mismo `/map` y mismo TF).
2. Usar `turtlebot3_world.launch.py`, no `empty_world`: sin paredes el LiDAR
   entrega `inf` y el mapa queda vacío.
3. No cerrar la ventana de Gazebo mientras corre el SLAM: el launch apaga todo
   (`on_exit_shutdown`).
4. Todo el detalle está en `Laboratorio/README.md` y la tabla de anomalías en
   `Informe/INFORME_CAP6_P2.md` §7.
