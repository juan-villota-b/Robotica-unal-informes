# Informes — Robótica

Estructura: **una carpeta por capítulo/informe**, y dentro `Guia/` (guía, slides y lecturas) + `Laboratorio/` (el workspace ROS2 de cada práctica).

| Informe | Guía | Laboratorio |
|---|---|---|
| `Informe Cap2 - Posición y orientación` | `Guia/GUÍA DE LABORATORIO CAP2.pdf` | `Laboratorio/Cuaterniones_ROS2` (act 1–6) |
| `Informe Cap3 - Tiempo y movimiento` | `Guia/Guia_1.pdf` (Mini INS) + `ROS2_Mini_INS_Implementation.pdf` | `Laboratorio/ros2_wc` (paquete `imu_orientation`) |
| `Informe Cap 4 (1a parte) - Cinemática de robots móviles` | `Guia/GUÍA DE LABORATORIO CAP4.pdf` + slides «Robótica móvil: Vehículos» | `Laboratorio/LabCap4_ROS2` (act 1–4, simulación) |
| `Informe Cap 4 (2a parte) - Cinemática de robots móviles` | copia de la guía CAP4 + slides | `Laboratorio/Lab5` (act 3–5 en TurtleBot3 / Gazebo) + `INFORME_LAB5.md`, `PRESENTACION_LAB5.*` |
| `Informe Cap 5 (1a parte) Navegacion` | `Guia/GUÍA DE LABORATORIO CAP5.pdf` (reactivo, Bug2, A*, mapas de ocupación, ROS2 Nav2) | `Laboratorio/` (partes A–D en Python) + `Informe/INFORME_CAP5.md` (PDF) |

Extras:
- `Informe Cap2/Presentación y sustentación/` → presentación del Cap 2 (8 diapositivas). La sustentación y las instrucciones de las diapositivas quedaron dentro de `Cuaterniones_ROS2/`.
- La guía CAP4 es una sola para las dos partes; se copió en ambas carpetas.

## Importante tras mover los workspaces
Los `install/` de colcon guardan rutas absolutas, así que cada laboratorio debe recompilarse en su nueva ubicación:

```bash
cd "Informes/Informe Cap 4 (2a parte) - Cinemática de robots móviles/Laboratorio/Lab5"
colcon build --symlink-install && source install/setup.zsh
```

Lo mismo para `LabCap4_ROS2`, `Cuaterniones_ROS2` y `ros2_wc`.

Fuera de `Informes/` quedan los recursos del curso: `Clase_1_Instalacion_Robotica_2026_2.pdf`, `Libros/`, `RVC3-python/` (código de Corke), `Img/` y `log/`.
