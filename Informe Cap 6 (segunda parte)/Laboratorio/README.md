# Laboratorio — Parte 8: SLAM con Cartographer / SLAM Toolbox en ROS 2

Implementación de la **sección 8** de la `GUÍA DE LABORATORIO CAP6`
(«Parte 5 — SLAM con Cartographer usando ROS2 Jazzy + Turtlebot3 + Gazebo +
RViz2», pp. 10–21 del PDF). El paso a paso comentado está en
[`../Guia/PARTE_8 - SLAM con Cartographer en ROS2.md`](../Guia/PARTE_8%20-%20SLAM%20con%20Cartographer%20en%20ROS2.md).

Pipeline que se monta:

```
/scan  ─┐
        ├→ SLAM → /map + TF map→odom → RViz2
/odom  ─┘           ↑
                 /cmd_vel ← simple_controller
```

## Estructura

```
Laboratorio/
├── ros2_ws/
│   └── src/localization_lab/
│       ├── package.xml                  # dependencias (§8.12)
│       ├── setup.py                     # entry point del nodo (§8.11)
│       ├── setup.cfg
│       ├── resource/localization_lab
│       ├── localization_lab/
│       │   ├── __init__.py
│       │   ├── simple_controller.py     # nodo controlador (§8.10)
│       │   └── patrol_controller.py     # patrulla cuadrada (agregado)
│       ├── test/test_simple_controller.py
│       ├── launch/
│       │   ├── cartographer.launch.py   # guía literal (§8.14)
│       │   ├── slam_toolbox.launch.py   # sustituto en lyrical
│       │   └── lab_world.launch.py      # mundo + modelo estabilizado
│       ├── config/
│       │   ├── cartographer.lua         # guía literal (§8.13)
│       │   └── slam_toolbox.yaml        # parámetros equivalentes
│       ├── models/turtlebot3_burger/    # modelo con caster y fricción corregidos
│       └── rviz/slam.rviz               # RViz ya configurado (§8.23)
└── evidencias/
    ├── mapa_turtlebot3.pgm / .yaml      # mapa guardado (§8.25)
    ├── mapa_turtlebot3.png              # vista rápida del .pgm
    ├── gazebo_slam.png                  # captura de Gazebo
    ├── rviz_slam.png                    # captura de RViz2 con /map, /scan y TF
    ├── patrulla/                        # corrida con patrol_controller
    └── logs/                            # salidas de la corrida de verificación
```

## Entorno verificado

| Componente | Versión en este equipo |
|---|---|
| Ubuntu | 26.04 LTS |
| ROS 2 | **lyrical** (`/opt/ros/lyrical`) — la guía está escrita para Jazzy |
| Gazebo | 10.5.0 (Harmonic) |
| TurtleBot3 (apt) | `ros-lyrical-turtlebot3-*` 2.3.7 |
| SLAM Toolbox (apt) | `ros-lyrical-slam-toolbox` 2.10.0 |
| `nav2_map_server` | instalado (`map_saver_cli`, §8.25) |
| Cartographer | **no publicado para lyrical** (solo `cartographer-ros-msgs`) |

## Dependencias

```bash
sudo apt update
sudo apt install ros-lyrical-turtlebot3-gazebo ros-lyrical-turtlebot3-simulations \
                 ros-lyrical-ros-gz ros-lyrical-ros-gz-bridge \
                 ros-lyrical-slam-toolbox ros-lyrical-nav2-map-server \
                 ros-lyrical-navigation2 ros-lyrical-nav2-bringup
```

`ros-jazzy-cartographer` / `ros-jazzy-cartographer-ros` (§8.5) no existen para
lyrical: el papel de Cartographer lo cumple SLAM Toolbox (ver anomalías A3/A4).

## Compilar

Cada vez que se mueve la carpeta (los `install/` guardan rutas absolutas):

```bash
cd "Informes/Informe Cap 6 (segunda parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.bash      # en zsh: setup.zsh
colcon build --symlink-install
```

## Ejecutar (5 terminales)

**En cada terminal**, primero esto (la ruta es absoluta: no depende de dónde
estés parado):

```bash
cd "$HOME/Documentos/Semestre_VIII/Robótica/Informes/Informe Cap 6 (segunda parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.bash      # en zsh: setup.zsh
source install/setup.bash               # en zsh: setup.zsh
export TURTLEBOT3_MODEL=burger
```

Si falta cualquiera de los tres, el error aparece más tarde y disfrazado:
`localization_lab` "no existe", Gazebo abre sin robot o RViz queda vacío.

**T1 — Gazebo** (mundo con paredes y obstáculos; con `empty_world` el LiDAR
entrega `inf` y el mapa sale vacío, anomalía A16):

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**T1 con el modelo estabilizado** (recomendado; mismo mundo, mismo bridge,
pero el burger no se mece ni se vuelca al girar):

```bash
ros2 launch localization_lab lab_world.launch.py
```

**T2 — SLAM** (sustituto de `ros2 launch localization_lab cartographer.launch.py`,
§8.21):

```bash
ros2 launch localization_lab slam_toolbox.launch.py
```

**T3 — Controlador** (§8.20):

```bash
ros2 run localization_lab simple_controller
# velocidades por parámetro:
# ros2 run localization_lab simple_controller --ros-args -p angular_speed:=0.5
```

**T3 alternativo — patrulla** (`patrol_controller`, no está en la guía):

Recorre un cuadrado de 2 m y en cada esquina gira 360° en el lugar, que es lo
que llena el mapa sin acercarse a los obstáculos. Mide con `/odom`, así que no
se desfasa si el robot patina.

```bash
# desde el spawn de turtlebot3_world (2 m de lado, en la franja libre de la
# izquierda): gira 180° para mirar hacia -x y recorre el cuadrado en sentido
# horario, que es la zona sin cilindros
ros2 run localization_lab patrol_controller --ros-args \
     -p start_turn:=3.1416 -p turn_direction:=-1.0

# si el robot arranca en otro lado o el cuadrado no cabe, achicá el lado
ros2 run localization_lab patrol_controller --ros-args \
     -p side_length:=1.5 -p linear_speed:=0.12
```

Parámetros: `linear_speed` (0.15), `angular_speed` (0.5), `side_length`
(2.0), `laps` (1), `start_turn` (0.0), `turn_direction` (1.0, +1 izquierda),
`phase_timeout` (120 s).

**T4 — RViz2** (§8.22–§8.23; el `.rviz` ya trae Fixed Frame `map`, `/map`,
`/scan`, `/tf`, TF y RobotModel):

```bash
# la ruta la resuelve ROS, así funciona desde cualquier carpeta
rviz2 -d "$(ros2 pkg prefix localization_lab)/share/localization_lab/rviz/slam.rviz"
```

Si en cambio ves RViz vacío, revisá `Global Options → Fixed Frame = map` y que
`ros2 run tf2_ros tf2_echo map odom` imprima una matriz (sin ese TF, el display
`Map` no dibuja nada).

**T5 — Guardar el mapa** (§8.25), con el robot todavía mapeando:

```bash
ros2 run nav2_map_server map_saver_cli -f mapa_turtlebot3 \
       --ros-args -p use_sim_time:=true
```

Deja `mapa_turtlebot3.pgm` y `mapa_turtlebot3.yaml` en el directorio actual.

> **`rm -rf build install log`** del §8.15 no se usa acá: borra los artefactos
> de todos los paquetes del workspace. `colcon build` ya recompila lo que cambió.

## Verificación hecha en este equipo

Corrida del 2026-11-11 sobre `turtlebot3_world`, 90 s de mapeo con
`v = 0.2 m/s`, `ω = 0.1 rad/s` (círculo de 2 m de radio):

| Qué | Resultado | Evidencia |
|---|---|---|
| `/scan` publicado | 4.31–4.39 Hz, 360 haces | `evidencias/logs/hz_scan.txt` |
| Nodos del pipeline | `slam_toolbox`, `simple_controller`, `robot_state_publisher`, `parameter_bridge` | `evidencias/logs/topics.txt` + `slam_toolbox.log` |
| `/map` | `nav_msgs/OccupancyGrid`, 1 publicador (QoS *transient local*) | `evidencias/logs/map_info.txt` |
| TF `map→odom` | publicada por SLAM (ej.: `t = (−0.319, 2.214)`, `yaw = 41.4°`) | `evidencias/logs/tf_map_odom.txt` |
| Mapa guardado | 188 × 167 celdas @ 0.05 m → **9.40 × 8.35 m** | `evidencias/mapa_turtlebot3.yaml` |
| Celdas | 2308 ocupadas (7.4 %), 9560 libres (30.4 %), 19528 desconocidas (62.2 %) | conteo sobre el `.pgm` |
| Capturas | Gazebo y RViz2 | `evidencias/gazebo_slam.png`, `evidencias/rviz_slam.png` |

## Anomalías de la parte 8 en este equipo

| # | Guía dice | Este equipo | Efecto / solución |
|---|---|---|---|
| A1 | Ubuntu 24.04, ROS 2 Jazzy | Ubuntu 26.04, ROS 2 **lyrical** | Los `ros-jazzy-*` se instalan como `ros-lyrical-*`. |
| A2 | `ros2 --version` → `ros2 0.32.x` | `ros2 --version` no existe | Verificar con `echo $ROS_DISTRO` (→ `lyrical`). |
| A3 | `ros-jazzy-cartographer` y `-cartographer-ros` | solo `cartographer-ros-msgs`; no hay `cartographer_ros` | §8.5, §8.13 y §8.21 se resuelven con **SLAM Toolbox**. El launch y el `.lua` de Cartographer quedan en el paquete para un equipo con Jazzy. |
| A4 | Copiar `map_builder.lua`, `trajectory_builder.lua` y `pose_graph.lua` desde `/opt/ros/jazzy/share/cartographer/` | esa ruta no existe | Los `include` los resuelve el paquete `cartographer` al ejecutar; no se copiaron. |
| A5 | `setup.py` con `console_scripts: []` | con la lista vacía `ros2 run` no encuentra el nodo | Se agregó `simple_controller = localization_lab.simple_controller:main`. |
| A7 | `/cmd_vel` tipo `Twist` | en lyrical es `geometry_msgs/msg/TwistStamped` | El nodo ya publica `TwistStamped`: compatible. |
| A12 | Gazebo con GUI | el launch de ROBOTIS levanta `gzclient` y usa `on_exit_shutdown` | **No matar el cliente**: al morir, el launch apaga también el servidor y el SLAM se queda sin `/scan`. |
| A14 | Numeración §8.1–§8.10 y salto a §11 | no existen los pasos 9 y 10 | En `Guia/PARTE_8…md` se numeró 8.1–8.26. |
| A16 | §8.18 `empty_world` | mundo sin paredes: `/scan` todo `inf` | Mapa sin celdas ocupadas. Para la demo usar `turtlebot3_world.launch.py`. |
| A17 | §8.23 display `/submap_list` | solo existe con Cartographer | Con SLAM Toolbox no hay submapas; el equivalente es `/slam_toolbox/graph_visualization` (MarkerArray). `/map`, `/scan` y `/tf` funcionan igual. |

## Problemas típicos

- **RViz vacío** → Fixed Frame en `map` y `use_sim_time` activo en todos los nodos.
- **El mapa no crece** → el controlador no está publicando: `ros2 topic echo /cmd_vel --once`.
- **`ros2 run localization_lab …` no encuentra el ejecutable** → falta el
  `console_scripts` en `setup.py` (A5) o no se recompiló después de mover la carpeta.
- **Poco mapa** → 60–90 s dan para ~9 × 8 m; para el mundo completo hay que
  dejarlo girar más tiempo o usar `angular_speed` menor (radio mayor).
