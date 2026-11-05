# Laboratorio Capítulo 6 — Localización y mapeo

Implementación de la **guía CAP6 (Corke, cap. 6)**. La guía tiene 5 partes y el
laboratorio las resuelve como 7 ejercicios:

| Ejercicio | Guía | Qué hace |
|---|---|---|
| 1 | Parte 1 | Odometría con y sin ruido |
| 2 | Parte 2 | EKF sin corrección externa |
| 3 | Parte 3 | EKF con landmarks (mapa conocido) |
| 4 | Parte 4 | SLAM con EKF (mapa desconocido) |
| 5 | §8.10 | Nodo ROS2 `simple_controller` |
| 6 | §13–§21 | SLAM con SLAM Toolbox (sustituto de Cartographer) + TurtleBot3 + Gazebo |
| 7 | §22–§25 | RViz2 + guardado del mapa |

## Contenido

```
Laboratorio/
├── simulaciones/
│   ├── parte1_odometria.py
│   ├── parte2_ekf.py
│   ├── parte3_ekf_landmarks.py
│   └── parte4_slam.py
└── ros2_ws/
    └── src/localization_lab/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/localization_lab
        ├── localization_lab/
        │   ├── __init__.py
        │   └── simple_controller.py
        ├── test/test_simple_controller.py
        ├── launch/cartographer.launch.py
        ├── launch/slam_toolbox.launch.py
        ├── config/cartographer.lua
        ├── config/slam_toolbox.yaml
        └── rviz/slam.rviz
```

## Entorno verificado

| Componente | Versión en este equipo |
|---|---|
| Ubuntu | 26.04 LTS (resolute) |
| ROS 2 | **lyrical** (`/opt/ros/lyrical`) |
| Gazebo | 10.5.0 (Harmonic) |
| Python | 3.14.4, venv `~/venvs/robotica` |
| roboticstoolbox-python | 1.4.2 |
| spatialmath-python | 1.1.17 |
| TurtleBot3 (apt) | `ros-lyrical-turtlebot3-*` 2.3.7 |
| SLAM Toolbox (apt) | `ros-lyrical-slam-toolbox` 2.10.0 (sustituto de Cartographer) |

> La guía está escrita para **Ubuntu 24.04 + ROS 2 Jazzy**. En este equipo la
> distro instalada es **lyrical**; todos los paquetes `ros-jazzy-*` se instalan
> como `ros-lyrical-*`. Las diferencias que afectan la ejecución están en
> [Anomalías](#anomalías-encontradas).

## Ejercicios 1–4 (Python)

Requieren el venv del curso (no se usa ROS 2):

```bash
cd "Informes/Informe Cap 6 (primera parte)/Laboratorio"
source ~/venvs/robotica/bin/activate

python simulaciones/parte1_odometria.py        # ejercicio 1
python simulaciones/parte2_ekf.py              # ejercicio 2
python simulaciones/parte3_ekf_landmarks.py    # ejercicio 3
python simulaciones/parte4_slam.py             # ejercicio 4
```

Cada script abre sus figuras con `plt.show()` y termina al cerrarlas. Sin
pantalla (SSH, CI) usar `MPLBACKEND=Agg` para que no intente abrir ventana.

Salidas esperadas, según la guía:

- **E1**: la trayectoria ideal es una circunferencia limpia; la ruidosa se
  desvía de forma acumulativa. La segunda figura grafica el error de posición
  contra el paso de integración.
- **E2**: la trayectoria estimada sigue a la real con deriva y la curva
  `get_Pnorm()` crece de forma monótona; las elipses de confianza se agrandan.
- **E3**: la incertidumbre baja en cada corrección con landmarks y vuelve a
  subir al alejarse; las elipses de confianza son pequeñas.
- **E4**: se estiman pose y landmarks a la vez (los estimados se dibujan como
  cruces). La incertidumbre de la guía (`sqrt(det(P))`) cae porque crece la
  dimensión del estado (ver anomalía A9); la curva de la pose 3×3 es la
  comparable con la parte 3. Con mapa conocido la pose termina en ~1.4e-5; en
  SLAM, en ~7.3e-3: más incertidumbre, como era de esperar.

## Ejercicios 5–7 (ROS 2 + Gazebo)

Dependencias de la guía (§8.2–§8.6) con los nombres de **lyrical**. En este
equipo ya están instalados TurtleBot3, `ros_gz`, el bridge y `nav2_map_server`
(verificado); Cartographer no existe para lyrical (A3):

```bash
sudo apt update

# TurtleBot3 + Gazebo Harmonic + bridge (ya instalados en este equipo)
sudo apt install ros-lyrical-turtlebot3-gazebo ros-lyrical-turtlebot3-simulations \
                 ros-lyrical-ros-gz ros-lyrical-ros-gz-bridge

# Servidor de mapa y map_saver (ya instalado)
sudo apt install ros-lyrical-nav2-map-server

# SLAM Toolbox: sustituto de Cartographer en lyrical (instalado, versión 2.10.0)
sudo apt install ros-lyrical-slam-toolbox

# Cartographer: no está publicado para lyrical (ver A3)

# §8.6 al pie de la letra (ya instalado)
sudo apt install ros-lyrical-navigation2 ros-lyrical-nav2-bringup
```

Compilar una sola vez (o después de mover la carpeta). No se usa
`rm -rf build install log`: este workspace es propio, pero ese comando borraría
los artefactos de todos los paquetes del workspace si se compartiera:

```bash
cd "Informes/Informe Cap 6 (primera parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.zsh        # en bash: setup.bash
colcon build --symlink-install
source install/setup.zsh
export TURTLEBOT3_MODEL=burger
```

Terminal 1 — Gazebo con el TurtleBot3:

```bash
source /opt/ros/lyrical/setup.zsh
export TURTLEBOT3_MODEL=burger

# Mundo de la guía (§18). Sin obstáculos: sirve para mover el robot, no para mapear.
ros2 launch turtlebot3_gazebo empty_world.launch.py

# Mundo con paredes y obstáculos: el que produce un mapa real en el ejercicio 6.
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Terminal 2 — ejercicio 5, el controlador:

```bash
cd "Informes/Informe Cap 6 (primera parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.zsh
source install/setup.zsh
ros2 run localization_lab simple_controller
```

El nodo usa `use_sim_time:=true` por defecto (reloj de Gazebo) y velocidades
`linear_speed=0.2`, `angular_speed=0.1`. Se pueden cambiar sin editar código:

```bash
# sin simulación (reloj de pared) o con otras velocidades
ros2 run localization_lab simple_controller --ros-args \
     -p use_sim_time:=false -p linear_speed:=0.3
```

Verificar los tópicos de la guía (§19):

```bash
ros2 topic list                 # /scan /odom /tf /cmd_vel
ros2 topic info /cmd_vel        # geometry_msgs/msg/TwistStamped
ros2 topic echo /cmd_vel --once # linear.x = 0.2, angular.z = 0.1
```

Terminal 3 — ejercicio 6, SLAM con SLAM Toolbox:

```bash
cd "Informes/Informe Cap 6 (primera parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.zsh
source install/setup.zsh
ros2 launch localization_lab slam_toolbox.launch.py
```

> `cartographer_ros` no está publicado para ROS 2 lyrical, así que el
> ejercicio se resuelve con **SLAM Toolbox** (ver anomalía **A3**). El launch
> mantiene la interfaz de la guía (`use_sim_time`, `resolution`) y publica
> `/map` más el TF `map→odom`.

> **Mapa vacío con `empty_world`**: ese mundo no tiene paredes ni obstáculos, y
> el LiDAR entrega `inf` en todos los haces, así que el mapa queda sin celdas
> ocupadas. Para ver un mapa real usar el mundo con obstáculos del paquete
> (anomalía **A16**):
>
> ```bash
> ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
> ```

Terminal 4 — ejercicio 7, RViz2 y guardado del mapa:

```bash
cd "Informes/Informe Cap 6 (primera parte)/Laboratorio/ros2_ws"
source /opt/ros/lyrical/setup.zsh
source install/setup.zsh
rviz2 -d src/localization_lab/rviz/slam.rviz   # Fixed Frame: map
ros2 run nav2_map_server map_saver_cli -f my_map
```

`map_saver_cli` (paquete `nav2_map_server`, ya instalado) deja `my_map.pgm` y
`my_map.yaml` en el directorio actual, tal como pide el §25 de la guía.

> El display **Submapas** de `slam.rviz` escucha `/submap_list`, que solo existe
> con Cartographer. Con SLAM Toolbox el equivalente es el `MarkerArray`
> `/slam_toolbox/graph_visualization`; añadirlo como display si se quiere ver el
> grafo. `/map`, `/scan` y el TF `map→odom` funcionan igual.

## Anomalías encontradas

Verificadas en este equipo. La numeración se usa en el resto del documento.

| # | Guía dice | Este equipo | Efecto / solución |
|---|---|---|---|
| A1 | Ubuntu 24.04, ROS 2 Jazzy | Ubuntu 26.04, ROS 2 **lyrical** | Todos los `sudo apt install ros-jazzy-*` se ejecutan como `ros-lyrical-*`. Nada más cambia. |
| A2 | `ros2 --version` → `ros2 0.32.x` | `ros2 --version` no existe: `error: unrecognized arguments: --version` | Comprobar la distro con `echo $ROS_DISTRO` (→ `lyrical`) y `ros2 --help`. |
| A3 | `sudo apt install ros-jazzy-cartographer ros-jazzy-cartographer-ros` | Solo existe `ros-lyrical-cartographer-ros-msgs`; no hay `ros-lyrical-cartographer` ni `-ros` | **Parte 5 (pasos §8.5, §13 y §21) migrada a SLAM Toolbox.** `cartographer_ros` no existe para lyrical, así que el laboratorio instala `ros-lyrical-slam-toolbox` (2.10.0) y añade `launch/slam_toolbox.launch.py` + `config/slam_toolbox.yaml` con la misma interfaz que la guía (`use_sim_time`, `resolution`). Comando: `ros2 launch localization_lab slam_toolbox.launch.py`. Publica `/map`, `/map_metadata` y el TF `map→odom`; `/submap_list` no existe. Los archivos de Cartographer quedan en el paquete para reproducir la guía en un equipo con Jazzy. |
| A4 | Copiar `map_builder.lua`, `trajectory_builder.lua` y `pose_graph.lua` desde `/opt/ros/jazzy/share/cartographer/configuration_files/` | Esa ruta no existe (no hay Cartographer) | Los `include` del `.lua` los resuelve el paquete `cartographer` al ejecutar; no se copiaron. |
| A5 | `setup.py` con `entry_points={'console_scripts': []}` y luego `ros2 run localization_lab simple_controller` | Con la lista vacía, `ros2 run` no encuentra el ejecutable | Se añadió `simple_controller = localization_lab.simple_controller:main`. Sin esto el §20 falla. |
| A6 | `tests_require=['pytest']` | setuptools actual lo marca obsoleto: `UserWarning: Unknown distribution option: 'tests_require'` | Cosmético: el build termina bien. En setuptools nuevos sería `extras_require={'test': ['pytest']}`. |
| A7 | `TwistStamped` en `/cmd_vel` | En lyrical `/cmd_vel` **es** `geometry_msgs/msg/TwistStamped` (`turtlebot3_burger_bridge.yaml`) | Compatible sin cambios. En configuraciones con `Twist` habría que cambiar el tipo del mensaje. |
| A8 | Parte 1 integra la pose ideal con `robot.f(...)` | Funciona, pero es el objeto equivocado: debería ser `robot_ideal.f(...)` | Como ambos robots comparten `L=1`, el resultado es idéntico. Se dejó literal y se documenta. |
| A9 | Parte 4: «reducción parcial de incertidumbre» | `get_Pnorm()` es `sqrt(det(P))` sobre todo el estado `3+2N`. Al añadir landmarks el determinante colapsa a ~1e-27 aunque la pose no mejore | La curva de la guía no mide la incertidumbre de la pose. Medido aquí: `sqrt(det(P_pose))` pasa de 3.3e-5 a 7.3e-3 (crece). Interpretar la curva como «incertidumbre global del estado», no de la pose. |
| A10 | Partes 3 y 4: `plt.figure(); mapa.plot(); ...` | `LandmarkMap.plot()` abre su propia figura (`plotvol2`) | En la guía original queda una ventana vacía adicional (3 ventanas). En esta implementación se quitó el `plt.figure()` previo y el tamaño se ajusta con `plt.gcf().set_size_inches(...)`: quedan 2 ventanas, sin cambios en los resultados. |
| A11 | Sin semilla explícita | `Vehicle`, `RandomPath`, `LandmarkMap` y `RangeBearingSensor` usan `seed=0` por defecto, y `np.random.seed()` no los afecta | La simulación es reproducible, pero siempre da lo mismo: para variar el ruido hay que pasar `seed=` al constructor (`Bicycle(covar=V, seed=n)`). |
| A12 | §18: `ros2 launch turtlebot3_gazebo empty_world.launch.py` | El launch de ROBOTIS siempre levanta `gzclient`; no acepta `gui:=false` | Necesita pantalla. En SSH: `export DISPLAY=:0` o correr Gazebo en el equipo local. |
| A13 | §8.3 `sudo apt install ros-jazzy-turtlebot3*` | `ros-lyrical-turtlebot3-*` sí está (2.3.7). `turtlebot3_bringup` y `teleop` no están en apt | No hacen falta en simulación: el launch de Gazebo ya incluye `robot_state_publisher` y el bridge. |
| A14 | Numeración §8.1–§8.10 y luego §11 | No existen los pasos 9 y 10 | Solo afecta la numeración del documento. |
| A15 | §8.6 `ros-jazzy-navigation2` y `ros-jazzy-nav2-bringup` | Existen como `ros-lyrical-navigation2` y `ros-lyrical-nav2-bringup`; quedaron instalados (1.5.2, junto con `nav2_amcl`). Los paquetes `nav2_*` que usa este laboratorio son `nav2_map_server` | El laboratorio solo usa `map_saver_cli` (§25), pero la instalación del §8.6 ya está hecha por si se sigue la guía al pie de la letra. |
| A16 | §18 `ros2 launch turtlebot3_gazebo empty_world.launch.py` y luego SLAM | `empty_world` no tiene paredes ni obstáculos: el LDS-01 entrega `inf` en los 360 haces y el mapa de ocupación sale **sin celdas ocupadas** (todo desconocido) | El pipeline funciona, pero no hay nada que mapear. Verificado con `turtlebot3_world.launch.py`: `/scan` con 360 haces finitos (0.9–2.8 m), `/map` con 103 celdas ocupadas y 942 libres, y `map_saver_cli` guarda el `.pgm`/`.yaml`. Para la demo de SLAM usar el mundo con obstáculos. |

## Notas de implementación

- El código de las partes 1–4 es el de la guía, reorganizado en constantes,
  una función `simular()` y una función `graficar()`. Los valores, el orden de
  las operaciones y los textos de las figuras se conservan.
- El paquete ROS2 replica el árbol, el `setup.py`, el `package.xml`, el
  `cartographer.lua` y el `cartographer.launch.py` de la guía, con la única
  corrección del entry point (A5) y el `.rviz` del §23 ya configurado.

### Mejoras aplicadas al código de la guía

Aprobadas en `../REPORTE_GUIA_CAP6.md`:

| ID | Cambio |
|---|---|
| M01 | Parte 1: `V` de velocidad `0.2` → `0.02` (igual que el libro y las partes 2–4). |
| M02 | Parte 1: la pose ideal se integra con `robot_ideal.f(...)`. |
| M03 | `setup.py` con el console script `simple_controller`. |
| M05 | `seed=0` explícito en `RandomPath`, `LandmarkMap` y `RangeBearingSensor`; `workspace=mapa`. |
| M06 | Parte 4: se dibujan los landmarks estimados con `slam.plot_map()`. |
| M07 | Parte 4: se imprime `slam.get_transform(mapa)` (mapa estimado → real). |
| M09 | Parte 4: segunda curva de incertidumbre `sqrt(det(P[:3, :3]))` y escala log. |
| M12 | Parte 4: se documenta que la incertidumbre de la pose en SLAM es mayor que con mapa conocido. |
| M13 | Partes 3 y 4: sin ventana vacía (`plt.gcf().set_size_inches`). |
| M14 | Parte 2: elipses de confianza (`filled=True`). |
| M15 | Partes 3 y 4: leyendas en las trayectorias. |
| M16 | Parte 1: segunda figura con el error de posición contra el paso. |
| M19 | Nodo: `use_sim_time:=true` por defecto, desactivable por CLI. |
| M20 | Nodo: `try/finally` en `main` para cerrar limpio con Ctrl+C. |
| M21 | Nodo: velocidades como parámetros `linear_speed` y `angular_speed`. |
| M22 | `package.xml`: `cartographer_ros` como `exec_depend`, sin `sensor_msgs`/`nav_msgs` sin uso, con `test_depend`. |
| M23 | `extras_require` en lugar de `tests_require`; test del nodo en `test/`. |
| M24 | No se usa `rm -rf build install log` (workspace propio). |
| M25 | Launch con argumentos `use_sim_time` y `resolution`. |
| M27 | Imports explícitos en las cuatro partes (ya estaban). |
| M28 | `np.pi` en lugar de `math.pi` en las partes 3 y 4. |
