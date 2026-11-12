# Parte 8 — SLAM con Cartographer en ROS 2

> **Qué es este documento.** Es la **sección 8** de la `GUÍA DE LABORATORIO CAP6`
> (pp. 10–21 del PDF), extraída y ordenada como documento de trabajo del
> **Informe Cap 6 — segunda parte**. La guía numera esta sección como
> «8. Parte 5» porque el capítulo tiene cinco partes; el paso 8.1 … 8.26 de acá
> corresponde exactamente a los §8.1–§8.10 y a los pasos 11–26 del PDF.
>
> **Qué pide la parte 8.** Montar el pipeline real de SLAM del TurtleBot3:
> LiDAR → SLAM → `/map` → RViz2, con TurtleBot3 + Gazebo Harmonic + Cartographer
> + RViz2, y guardar el mapa en `.pgm` + `.yaml`.
>
> **En este equipo** la distro es ROS 2 **lyrical**, no jazzy: los paquetes
> `ros-jazzy-*` se instalan como `ros-lyrical-*` y `cartographer_ros` **no está
> publicado para lyrical** (solo `cartographer-ros-msgs`). El paso 8.5 se
> resuelve con **SLAM Toolbox** (`ros-lyrical-slam-toolbox`), que produce el
> mismo `/map` y el mismo TF `map→odom`. Los archivos de Cartographer quedan en
> el paquete para reproducir la guía literal en un equipo con Jazzy. El detalle
> de cada diferencia está en `Laboratorio/README.md` y en
> `Informe/INFORME_CAP6_P2.md`.

## Procedimiento

Ajustado para:

- Ubuntu 24.04
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic
- TurtleBot3
- Cartographer ROS 2
- Nav2

> Si ya está todo instalado, saltar al paso 8.7.
> *El PDF numera §8.1–§8.10 y después salta a los pasos 11–26. Acá se
> normaliza todo como 8.1–8.26: 8.11–8.26 son los pasos 11–26 del PDF.*

> **En este equipo (ROS 2 lyrical):** `cartographer_ros` no está publicado, así
> que los pasos de Cartographer (8.5, 8.13 y 8.21) se resuelven con **SLAM
> Toolbox**, que ya está instalado. El launch del laboratorio replica la
> interfaz de la guía y publica `/map` + TF `map→odom`:
>
> ```bash
> ros2 launch localization_lab slam_toolbox.launch.py
> ```
>
> Los archivos `config/cartographer.lua` y `launch/cartographer.launch.py` se
> conservan para reproducir la guía en un equipo con Jazzy. Detalles y
> diferencias en `Laboratorio/README.md` (anomalías A3 y A16).

### 8.1 Verificar ROS 2 Jazzy

```bash
ros2 --version
```

Debe aparecer algo similar a:

```
ros2 0.32.x
```

Ver distribución:

```bash
echo $ROS_DISTRO
```

Resultado esperado:

```
jazzy
```

**Qué esperar:** si `echo $ROS_DISTRO` no imprime nada, el entorno no está
cargado: falta `source /opt/ros/<distro>/setup.bash` en la terminal.

### 8.2 Instalar dependencias

```bash
sudo apt update
```

### 8.3 Instalar TurtleBot3

> En este equipo los nombres `ros-jazzy-*` de los pasos 8.3–8.6 son
> `ros-lyrical-*`; el 8.5 no existe y se reemplaza por
> `sudo apt install ros-lyrical-slam-toolbox` (ya instalado junto con
> `navigation2`/`nav2-bringup`).

```bash
sudo apt install ros-jazzy-turtlebot3*
```

### 8.4 Instalar Gazebo Harmonic

En ROS 2 Jazzy ya **no** se usa Gazebo Classic. Se usa **Gazebo Harmonic**.

Simulador:

```bash
sudo apt install ros-jazzy-ros-gz
```

Bridge ROS ↔ Gazebo:

```bash
sudo apt install ros-jazzy-ros-gz-bridge
```

### 8.5 Instalar Cartographer

```bash
sudo apt install ros-jazzy-cartographer
sudo apt install ros-jazzy-cartographer-ros
```

### 8.6 Instalar Navigation2

```bash
sudo apt install ros-jazzy-navigation2
sudo apt install ros-jazzy-nav2-bringup
```

### 8.7 Crear workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 8.8 Crear paquete

```bash
cd src
ros2 pkg create localization_lab --build-type ament_python
```

### 8.9 Estructura final

```
localization_lab/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── localization_lab
├── localization_lab/
│   ├── __init__.py
│   └── simple_controller.py
├── launch/
│   └── cartographer.launch.py
├── config/
│   └── cartographer.lua
└── rviz/
    └── slam.rviz
```

*Las carpetas `launch/`, `config/` y `rviz/` no las crea `ros2 pkg create`:
hay que crearlas a mano en los pasos 8.13, 8.14 y 8.23.*

### 8.10 Nodo controlador

Se puede crear el siguiente `simple_controller.py` o reutilizar el controlador
reactivo de la práctica de ROS 2 del capítulo 5.

Crear el archivo:

```bash
cd localization_lab/localization_lab
touch simple_controller.py
```

Código completo:

```python
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped


class SimpleController(Node):

    def __init__(self):
        super().__init__('simple_controller')

        self.publisher_ = self.create_publisher(
            TwistStamped,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.move_robot
        )

    def move_robot(self):
        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        msg.twist.linear.x = 0.2
        msg.twist.angular.z = 0.1

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = SimpleController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**Qué esperar:** el nodo no imprime nada; su efecto se ve en el robot. Publica a
10 Hz una velocidad lineal de 0.2 m/s y angular de 0.1 rad/s, o sea una
circunferencia de radio $r = v/\omega = 2$ m.

*El tipo es `TwistStamped` (no `Twist`): incluye `header` con sello de tiempo.*

### 8.11 `setup.py` para Jazzy

```bash
gedit ~/ros2_ws/src/localization_lab/setup.py
```

Código completo:

```python
from setuptools import setup
from glob import glob
import os

package_name = 'localization_lab'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.lua')
        ),
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='docente',
    maintainer_email='docente@lab.com',
    description='Localization and SLAM laboratory',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_controller = localization_lab.simple_controller:main',
        ],
    },
)
```

*La guía deja `console_scripts` vacío; con la lista vacía el paso 8.20 falla
porque `ros2 run` no encuentra el ejecutable. Agregar esa línea es obligatorio.*

### 8.12 `package.xml`

```bash
gedit ~/ros2_ws/src/localization_lab/package.xml
```

Añadir dependencias:

```xml
<depend>rclpy</depend>
<depend>geometry_msgs</depend>
<depend>sensor_msgs</depend>
<depend>nav_msgs</depend>
<depend>cartographer_ros</depend>
```

### 8.13 Crear configuración de Cartographer

Crear la carpeta `config`:

```bash
mkdir ~/ros2_ws/src/localization_lab/config
```

> **IMPORTANTE.** Antes hay que copiar los `.lua` base del paquete:

```bash
cp /opt/ros/jazzy/share/cartographer/configuration_files/map_builder.lua \
   ~/ros2_ws/src/localization_lab/config/

cp /opt/ros/jazzy/share/cartographer/configuration_files/trajectory_builder.lua \
   ~/ros2_ws/src/localization_lab/config/

cp /opt/ros/jazzy/share/cartographer/configuration_files/pose_graph.lua \
   ~/ros2_ws/src/localization_lab/config/
```

Crear el archivo:

```bash
touch ~/ros2_ws/src/localization_lab/config/cartographer.lua
```

Código completo:

```lua
include "map_builder.lua"
include "trajectory_builder.lua"

options = {
    map_builder = MAP_BUILDER,
    trajectory_builder = TRAJECTORY_BUILDER,
    map_frame = "map",
    tracking_frame = "base_scan",
    published_frame = "base_footprint",
    odom_frame = "odom",
    provide_odom_frame = true,
    publish_frame_projected_to_2d = true,
    use_odometry = false,
    use_nav_sat = false,
    use_landmarks = false,
    num_laser_scans = 1,
    num_multi_echo_laser_scans = 0,
    num_subdivisions_per_laser_scan = 1,
    num_point_clouds = 0,
    lookup_transform_timeout_sec = 0.2,
    submap_publish_period_sec = 0.3,
    pose_publish_period_sec = 0.005,
    trajectory_publish_period_sec = 0.03,
    rangefinder_sampling_ratio = 1.0,
    odometry_sampling_ratio = 1.0,
    fixed_frame_pose_sampling_ratio = 1.0,
    imu_sampling_ratio = 1.0,
    landmarks_sampling_ratio = 1.0,
}

MAP_BUILDER.use_trajectory_builder_2d = true

TRAJECTORY_BUILDER_2D.use_imu_data = false
TRAJECTORY_BUILDER_2D.min_range = 0.12
TRAJECTORY_BUILDER_2D.max_range = 3.5
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 5.0

POSE_GRAPH.optimize_every_n_nodes = 35

return options
```

**Qué significan los tres parámetros que importan:**

| Parámetro | Valor | Por qué |
|---|---|---|
| `tracking_frame` | `base_scan` | frame del LiDAR: es el sensor con el que se hace el seguimiento |
| `provide_odom_frame` | `true` | Cartographer inventa `odom` a partir del escaneo, no de las ruedas |
| `use_odometry` | `false` | no se usa la odometría del TurtleBot3 como entrada |

### 8.14 Crear launch file

```bash
mkdir ~/ros2_ws/src/localization_lab/launch
touch ~/ros2_ws/src/localization_lab/launch/cartographer.launch.py
```

Código completo:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    config_dir = os.path.join(
        get_package_share_directory('localization_lab'),
        'config'
    )

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
        arguments=[
            '-configuration_directory',
            config_dir,
            '-configuration_basename',
            'cartographer.lua'
        ]
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
        arguments=[
            '-resolution',
            '0.05'
        ]
    )

    return LaunchDescription([
        cartographer_node,
        occupancy_grid_node
    ])
```

**Qué esperar:** son **dos** nodos. `cartographer_node` hace el SLAM y publica
`/submap_list` y el TF `map→odom`; `cartographer_occupancy_grid_node` convierte
los submapas en una grilla de ocupación `/map` de 5 cm/celda.

### 8.15 Compilar workspace

```bash
cd ~/ros2_ws
rm -rf build install log
colcon build
```

### 8.16 Cargar entorno

```bash
source install/setup.bash
```

*En `zsh` usar `source install/setup.zsh`: `setup.bash` falla en esa shell.*

### 8.17 Configurar TurtleBot3

```bash
export TURTLEBOT3_MODEL=burger
```

*Va en **todas** las terminales que lancen algo del robot; si falta, el launch
no encuentra el URDF.*

### 8.18 Lanzar Gazebo Harmonic

**Terminal 1:**

```bash
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

**Qué esperar:** Gazebo abre con un mundo vacío y el burger en el origen. En la
lista de tópicos aparecen `/scan`, `/odom`, `/tf` y `/cmd_vel`. El robot no se
mueve hasta el paso 8.20.

### 8.19 Verificar tópicos

**Terminal 2:**

```bash
source ~/ros2_ws/install/setup.bash
ros2 topic list
```

Verificar que estén:

```
/scan
/odom
/tf
/cmd_vel
```

**Qué esperar:** `/scan` debe publicar a ~5 Hz (`ros2 topic hz /scan`) y
`ros2 topic info /cmd_vel` debe decir `geometry_msgs/msg/TwistStamped`.

### 8.20 Ejecutar controlador

**Terminal 3:**

```bash
source ~/ros2_ws/install/setup.bash
ros2 run localization_lab simple_controller
```

**Qué esperar:** el robot empieza a moverse en círculos dentro de Gazebo. Si no
se mueve, revisar el paso 8.11 (`console_scripts`) y que `/cmd_vel` esté conectado.

### 8.21 Ejecutar Cartographer

> En este equipo (lyrical) el comando es
> `ros2 launch localization_lab slam_toolbox.launch.py`; publica `/map` y el TF
> `map→odom` (sin `/submap_list`). Ver el aviso al inicio de la Parte 5.

**Terminal 4:**

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch localization_lab cartographer.launch.py
```

**Qué esperar:** los dos nodos arrancan, se suscriben a `/scan` y empiezan a
publicar `/map`, `/submap_list` y el TF `map→odom`. Todavía no se ve nada: falta
RViz2.

### 8.22 Ejecutar RViz2

**Terminal 5:**

```bash
rviz2
```

### 8.23 Configurar RViz2

**Fixed Frame:** `map`

**Add → By Topic**, agregar:

- `/map`
- `/scan`
- `/tf`
- `/submap_list`

**Qué esperar:** con el robot moviéndose, el mapa crece en tiempo real alrededor
de la trayectoria. Si la pantalla queda vacía, casi siempre es el Fixed Frame mal
puesto en `map` o `use_sim_time` desincronizado.

### 8.24 Resultado esperado

En **Gazebo**:

- Robot moviéndose.

En **RViz2**:

- Nube LiDAR.
- Mapa construyéndose.
- Trayectoria.
- Submapas.
- Transformaciones TF.

### 8.25 Guardar mapa

Instalar el map saver:

```bash
sudo apt install ros-jazzy-nav2-map-server
```

Guardar:

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

**Qué esperar:** dos archivos en el directorio donde se ejecutó el comando:

- `my_map.pgm` — la imagen de la grilla de ocupación.
- `my_map.yaml` — resolución (0.05 m/celda), origen y umbrales de ocupación.

---

---

## Concepto central

El sistema implementa el pipeline real usado por TurtleBot3:

```
LiDAR → Cartographer → SLAM → Mapa → RViz2
```

En términos de tópicos:

```
/scan  ─┐
        ├→ cartographer_node → /map, /submap_list, TF map→odom → RViz2
/odom  ─┘         ↑
               /cmd_vel ← simple_controller
```

---

## Checklist de entrega (solo parte 8)

- [ ] Captura de Gazebo con el robot moviéndose.
- [ ] Captura de RViz2 con `/map`, `/scan`, `/tf` (y `/submap_list` si es
      Cartographer).
- [ ] `my_map.pgm` + `my_map.yaml` guardados con `map_saver_cli`.
- [ ] Tabla de anomalías de la guía (Jazzy → lyrical) en el informe.
