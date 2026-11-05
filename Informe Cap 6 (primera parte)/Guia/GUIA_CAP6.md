# Guía de laboratorio de simulación — Capítulo 6

## Localización y mapeo

> **Fuente:** `GUÍA DE LABORATORIO CAP6.pdf` (21 pp.).
> Conversión a Markdown para lectura y copia de código.
> Los bloques **Qué hacer** y **Qué esperar** condensan lo que en el PDF queda
> implícito; el resto del contenido es el de la guía.
> Diferencias de entorno de este equipo (ROS 2 *lyrical* en lugar de *jazzy*):
> ver `Laboratorio/README.md`.

---

## Índice

1. [Introducción](#1-introducción)
2. [Objetivos de aprendizaje](#2-objetivos-de-aprendizaje)
3. [Resultados esperados](#3-resultados-esperados)
4. [Parte 1 — Odometría (dead reckoning)](#4-parte-1--odometría-dead-reckoning)
5. [Parte 2 — Estimación con EKF](#5-parte-2--estimación-con-ekf)
6. [Parte 3 — EKF con landmarks](#6-parte-3--ekf-con-landmarks)
7. [Parte 4 — Introducción a SLAM](#7-parte-4--introducción-a-slam)
8. [Parte 5 — SLAM con Cartographer en ROS 2](#8-parte-5--slam-con-cartographer-en-ros-2)
9. [Concepto central](#9-concepto-central)
10. [Checklist de entrega](#10-checklist-de-entrega)

---

## 1. Introducción

En esta guía se estudian los conceptos fundamentales de **localización y mapeo**
en robótica móvil usando Python, Robotics Toolbox y ROS 2.

Durante la práctica se implementan:

- Odometría
- Estimación con EKF (*Extended Kalman Filter*)
- Corrección con landmarks
- SLAM con ROS 2
- Visualización en RViz2

---

## 2. Objetivos de aprendizaje

- Explicar y modelar la localización por odometría y sus limitaciones.
- Implementar EKF para estimación de pose.
- Integrar observaciones de landmarks para corrección.
- Comprender SLAM y su complejidad.
- Implementar pipelines reales en ROS 2 (EKF, AMCL, SLAM).

---

## 3. Resultados esperados

Al finalizar, se debe poder:

- Mostrar trayectorias **real vs estimada**.
- Evidenciar el **crecimiento de incertidumbre** sin sensores.
- Demostrar la **reducción de incertidumbre** con landmarks.
- Ejecutar localización/SLAM en ROS 2 con visualización en RViz2.

---

## 4. Parte 1 — Odometría (dead reckoning)

### Objetivo

Implementar una simulación básica de odometría y analizar el crecimiento del error.

**Qué hacer:** comparar un robot con ruido contra uno ideal, ambos obedeciendo
exactamente la misma orden de movimiento durante 200 pasos, y graficar las dos
trayectorias superpuestas.

### Código base

```python
from roboticstoolbox import Bicycle
import numpy as np
import matplotlib.pyplot as plt

# Covarianza del ruido: incertidumbre para estimación de pose
V = np.diag([0.2, np.deg2rad(0.5)])**2
print(V)

# Robot con ruido
robot = Bicycle(covar=V)

# Robot ideal (sin ruido)
robot_ideal = Bicycle(covar=np.zeros((2, 2)))

# Variables para almacenar trayectorias
x_real = []
y_real = []

x_ideal = []
y_ideal = []

qp_real = [0, 0, 0]
qp_ideal = [0, 0, 0]

# Simulación
for _ in range(200):
    # Movimiento robot real
    odo_real = robot.step((1.0, 0.2))
    qp_real = robot.f(qp_real, odo_real)

    # Movimiento robot ideal
    odo_ideal = robot_ideal.step((1.0, 0.2))
    qp_ideal = robot.f(qp_ideal, odo_ideal)

    # Guardar trayectoria real
    x_real.append(qp_real[0])
    y_real.append(qp_real[1])

    # Guardar trayectoria ideal
    x_ideal.append(qp_ideal[0])
    y_ideal.append(qp_ideal[1])

# Graficar trayectorias
plt.figure(figsize=(8, 6))

plt.plot(
    x_ideal,
    y_ideal,
    label='Trayectoria estimada con odometría sin ruido',
    linewidth=1
)

plt.plot(
    x_real,
    y_real,
    label='Trayectoria estimada con odometría con ruido',
    linewidth=1
)

plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.title('Comparación de trayectorias')
plt.grid(True)
plt.axis('equal')
plt.legend()

plt.show()
```

### Gráfica esperada

- Trayectoria suave pero con **desviación acumulada**.
- **Error creciente** con el tiempo.

**Qué esperar:** la curva ideal es una circunferencia limpia (orden constante
$v=1.0$ m/s, dirección $0.2$ rad); la curva con ruido la sigue al principio y se
va abriendo como espiral. Las dos trayectorias se separan cada vez más: no
vuelven a juntarse nunca.
*En una corrida típica, tras 10 m recorridos la pose real queda a ~3 m de la ideal.*

### Indicadores de logro

- Identifica el crecimiento del error.
- Relaciona el error con el ruido.

### Preguntas de análisis

1. ¿Por qué la trayectoria presenta error?
2. ¿Qué representa la matriz de covarianza `V`?
3. ¿Qué ocurre si aumenta el ruido?

---

## 5. Parte 2 — Estimación con EKF

### Objetivo

Implementar estimación probabilística de pose usando un filtro de Kalman extendido.

**Qué hacer:** envolver el mismo robot ruidoso en un `EKF`, pero **sin ningún
sensor externo**. La trayectoria la genera `RandomPath`, no una orden constante.
Graficar dos cosas: trayectorias superpuestas y evolución de la incertidumbre.

### Código

```python
from roboticstoolbox import Bicycle, EKF, RandomPath
import numpy as np
import matplotlib.pyplot as plt

# Covarianza odometría
V = np.diag([0.02, np.deg2rad(0.5)])**2

# Robot
robot = Bicycle(covar=V, animation=None)

# Trayectoria "aleatoria"
robot.control = RandomPath(workspace=10)

# Covarianza inicial
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)])**2

# EKF
ekf = EKF(robot=(robot, V), P0=P0)

# Ejecutar simulación
ekf.run(T=20)

# Trayectoria
plt.figure(figsize=(8, 6))
robot.plot_xy(color='blue')
ekf.plot_xy(color='red')
plt.title('Trayectoria real vs estimada')
plt.grid(True)

# Incertidumbre
plt.figure(figsize=(8, 6))
plt.plot(ekf.get_t(), ekf.get_Pnorm(), linewidth=2)
plt.xlabel('Tiempo [s]')
plt.ylabel('Incertidumbre')
plt.title('Crecimiento de incertidumbre')
plt.grid(True)

plt.show()
```

### Resultado esperado

Se debe observar:

- Divergencia entre trayectoria real y estimada.
- Crecimiento **continuo** de la incertidumbre.
- Ausencia de corrección de pose.

**Qué esperar:** la curva de incertidumbre es **monótona creciente**: sube y no
baja en ningún instante, porque no hay medición que la corrija. Que el filtro sea
"EKF" no lo salva: sin sensor externo solo está integrando su propia ignorancia.
*En una corrida típica pasa de $3\times10^{-5}$ a $1.6\times10^{-2}$ en 20 s.*

### Preguntas de análisis

1. ¿Por qué el EKF no logra corregir el error?
2. ¿Qué representa la curva de incertidumbre?
3. ¿Qué ocurre si aumenta el valor de `V`?

---

## 6. Parte 3 — EKF con landmarks

### Objetivo

Corregir la pose usando observaciones externas del entorno.

**Qué hacer:** repetir la Parte 2 pero dándole al filtro **el mapa conocido**
(`map=mapa`) y un sensor de rango/ángulo tipo LiDAR. Ahora el EKF puede comparar
lo que mide con lo que esperaba medir.

### Código

```python
from roboticstoolbox import *
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Covarianza odometría
V = np.diag([0.02, np.deg2rad(0.5)])**2

# Robot
robot = Bicycle(covar=V, animation=None)
robot.control = RandomPath(workspace=10)

# Mapa de landmarks
mapa = LandmarkMap(20, workspace=10)

# Covarianza sensor de rango
W = np.diag([0.1, np.deg2rad(1)])**2

# Sensor de rango, tipo Lidar
sensor = RangeBearingSensor(
    robot=robot,
    map=mapa,
    covar=W,
    angle=[-pi/2, pi/2],
    range=4
)

# Covarianza inicial
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)])**2

# EKF
ekf = EKF(
    robot=(robot, V),
    P0=P0,
    map=mapa,                    # Conoce el mapa de landmarks previamente
    sensor=(sensor, W)
)

# Simulación
ekf.run(T=40)

# Trayectorias
plt.figure(figsize=(8, 6))
mapa.plot()
robot.plot_xy(color='blue')
ekf.plot_xy(color='red')
ekf.plot_ellipse()
plt.title('EKF con landmarks')
plt.grid(True)

# Incertidumbre
plt.figure(figsize=(8, 6))
plt.plot(ekf.get_t(), ekf.get_Pnorm(), linewidth=2)
plt.xlabel('Tiempo [s]')
plt.ylabel('Incertidumbre')
plt.title('Incertidumbre con correcciones')
plt.grid(True)

plt.show()
```

### Resultado esperado

Se debe observar:

- Mejor ajuste entre trayectoria real y estimada.
- Reducción **periódica** de la incertidumbre.
- Elipses de confianza más pequeñas.

**Qué esperar:** la curva de incertidumbre ya **no crece**: oscila como dientes de
sierra — sube al alejarse de los landmarks y cae en cada observación. Esa caída
periódica es la innovación entrando al filtro. Las elipses dibujadas sobre la
trayectoria deben achicarse donde el robot ve landmarks.
*En una corrida típica se mantiene entre $1.0\times10^{-3}$ y $1.4\times10^{-5}$,
sin crecer sin límite.*

### Preguntas de análisis

1. ¿Qué es la innovación?
2. ¿Por qué disminuye la incertidumbre?
3. ¿Qué ocurre cuando no se observan landmarks?

---

## 7. Parte 4 — Introducción a SLAM

### Objetivo

Comprender el problema de localización y mapeo simultáneo (SLAM) mediante una
simulación en Python.

**Qué hacer:** idéntico a la Parte 3 pero con `map=None`. El robot **no conoce**
el mapa: debe descubrir los landmarks mientras se localiza.

### Código

```python
from roboticstoolbox import *
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# ==============================
# Covarianza de odometría
# ==============================

V = np.diag([
    0.02,
    np.deg2rad(0.5)
])**2

# ==============================
# Robot
# ==============================

robot = Bicycle(
    covar=V,
    animation=None
)

robot.control = RandomPath(workspace=10)

# ==============================
# Mapa real
# ==============================

mapa = LandmarkMap(20, workspace=10)

# ==============================
# Sensor
# ==============================

W = np.diag([
    0.1,
    np.deg2rad(1)
])**2

sensor = RangeBearingSensor(
    robot=robot,
    map=mapa,
    covar=W,
    angle=[-pi/2, pi/2],
    range=4
)

# ==============================
# Covarianza inicial
# ==============================

P0 = np.diag([
    0.05,
    0.05,
    np.deg2rad(0.5)
])**2

# ==============================
# EKF SLAM
# ==============================

slam = EKF(
    robot=(robot, V),
    P0=P0,
    sensor=(sensor, W),
    map=None                        # No conoce el mapa de landmarks previamente
)

# ==============================
# Ejecutar simulación
# ==============================

slam.run(T=40)

# ==============================
# Graficar resultados
# ==============================

plt.figure(figsize=(10, 8))

# Mapa real
mapa.plot()

# Trayectoria real
robot.plot_xy(
    color='blue',
    label='Trayectoria real'
)

# Trayectoria estimada
slam.plot_xy(
    color='red',
    label='Trayectoria estimada'
)

# Elipses de confianza
slam.plot_ellipse()

plt.title('SLAM usando EKF')
plt.grid(True)
plt.axis('equal')

# ==============================
# Incertidumbre
# ==============================

plt.figure(figsize=(8, 6))

plt.plot(
    slam.get_t(),
    slam.get_Pnorm(),
    linewidth=2
)

plt.xlabel('Tiempo [s]')
plt.ylabel('Incertidumbre')
plt.title('Evolución de incertidumbre en SLAM')
plt.grid(True)

plt.show()
```

### Resultado esperado

Se debe observar:

- Construcción progresiva del mapa.
- Corrección de trayectoria.
- Estimación simultánea de pose y landmarks.
- Reducción parcial de incertidumbre.
- Diferencia entre trayectoria real y estimada.
- Comparación con el resultado de la simulación anterior (EKF con mapa conocido).

**Qué esperar:** el estado del filtro ya no es de 3 variables sino de $3 + 2N$:
cada landmark nuevo agrega dos incógnitas. Los landmarks aparecen en la gráfica
**a medida que el robot los detecta**, no todos de entrada, y la pose se corrige
con esos landmarks que acaba de estimar.

> **Ojo al interpretar la curva:** `get_Pnorm()` es $\sqrt{\det P}$ sobre **todo**
> el estado. Al agregar landmarks el determinante se hace muy chico aunque la
> pose no mejore, así que esa curva **no** mide la incertidumbre de la pose. Para
> eso hay que mirar el bloque $3\times3$ de la pose.

### Conceptos importantes

**¿Qué está resolviendo SLAM?** El robot debe estimar simultáneamente:

- su pose,
- el mapa,

sin conocer previamente ninguno de los dos.

### Preguntas de análisis

1. ¿Por qué SLAM es más complejo que localización?
2. ¿Qué ocurre si aumenta el ruido del sensor?
3. ¿Por qué la incertidumbre no desaparece completamente?
4. ¿Qué ventajas ofrece SLAM frente a usar un mapa conocido?
5. ¿Qué aplicaciones industriales podrían usar SLAM?
6. ¿Cómo es la comparación de los resultados obtenidos, conociendo y sin conocer
   el mapa de landmarks previamente?

---

## 8. Parte 5 — SLAM con Cartographer en ROS 2

Procedimiento ajustado para:

- Ubuntu 24.04
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic
- TurtleBot3
- Cartographer ROS 2
- Nav2

> Si ya está todo instalado, saltar al paso 5.7.
> *La numeración original del PDF (§8.1–§8.26, con un salto entre §8.10 y §11) se
> normaliza acá como 5.1–5.26: §8.x pasa a 5.x y §11–§26 a 5.11–5.26.*

> **En este equipo (ROS 2 lyrical):** `cartographer_ros` no está publicado, así
> que los pasos de Cartographer (5.5, 5.13 y 5.21) se resuelven con **SLAM
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

### 5.1 Verificar ROS 2 Jazzy

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

### 5.2 Instalar dependencias

```bash
sudo apt update
```

### 5.3 Instalar TurtleBot3

> En este equipo los nombres `ros-jazzy-*` de los pasos 5.3–5.6 son
> `ros-lyrical-*`; el 5.5 no existe y se reemplaza por
> `sudo apt install ros-lyrical-slam-toolbox` (ya instalado junto con
> `navigation2`/`nav2-bringup`).

```bash
sudo apt install ros-jazzy-turtlebot3*
```

### 5.4 Instalar Gazebo Harmonic

En ROS 2 Jazzy ya **no** se usa Gazebo Classic. Se usa **Gazebo Harmonic**.

Simulador:

```bash
sudo apt install ros-jazzy-ros-gz
```

Bridge ROS ↔ Gazebo:

```bash
sudo apt install ros-jazzy-ros-gz-bridge
```

### 5.5 Instalar Cartographer

```bash
sudo apt install ros-jazzy-cartographer
sudo apt install ros-jazzy-cartographer-ros
```

### 5.6 Instalar Navigation2

```bash
sudo apt install ros-jazzy-navigation2
sudo apt install ros-jazzy-nav2-bringup
```

### 5.7 Crear workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 5.8 Crear paquete

```bash
cd src
ros2 pkg create localization_lab --build-type ament_python
```

### 5.9 Estructura final

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
hay que crearlas a mano en los pasos 5.13, 5.14 y 5.23.*

### 5.10 Nodo controlador

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

### 5.11 `setup.py` para Jazzy

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

*La guía deja `console_scripts` vacío; con la lista vacía el paso 5.20 falla
porque `ros2 run` no encuentra el ejecutable. Agregar esa línea es obligatorio.*

### 5.12 `package.xml`

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

### 5.13 Crear configuración de Cartographer

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

### 5.14 Crear launch file

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

### 5.15 Compilar workspace

```bash
cd ~/ros2_ws
rm -rf build install log
colcon build
```

### 5.16 Cargar entorno

```bash
source install/setup.bash
```

*En `zsh` usar `source install/setup.zsh`: `setup.bash` falla en esa shell.*

### 5.17 Configurar TurtleBot3

```bash
export TURTLEBOT3_MODEL=burger
```

*Va en **todas** las terminales que lancen algo del robot; si falta, el launch
no encuentra el URDF.*

### 5.18 Lanzar Gazebo Harmonic

**Terminal 1:**

```bash
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

**Qué esperar:** Gazebo abre con un mundo vacío y el burger en el origen. En la
lista de tópicos aparecen `/scan`, `/odom`, `/tf` y `/cmd_vel`. El robot no se
mueve hasta el paso 5.20.

### 5.19 Verificar tópicos

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

### 5.20 Ejecutar controlador

**Terminal 3:**

```bash
source ~/ros2_ws/install/setup.bash
ros2 run localization_lab simple_controller
```

**Qué esperar:** el robot empieza a moverse en círculos dentro de Gazebo. Si no
se mueve, revisar el paso 5.11 (`console_scripts`) y que `/cmd_vel` esté conectado.

### 5.21 Ejecutar Cartographer

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

### 5.22 Ejecutar RViz2

**Terminal 5:**

```bash
rviz2
```

### 5.23 Configurar RViz2

**Fixed Frame:** `map`

**Add → By Topic**, agregar:

- `/map`
- `/scan`
- `/tf`
- `/submap_list`

**Qué esperar:** con el robot moviéndose, el mapa crece en tiempo real alrededor
de la trayectoria. Si la pantalla queda vacía, casi siempre es el Fixed Frame mal
puesto en `map` o `use_sim_time` desincronizado.

### 5.24 Resultado esperado

En **Gazebo**:

- Robot moviéndose.

En **RViz2**:

- Nube LiDAR.
- Mapa construyéndose.
- Trayectoria.
- Submapas.
- Transformaciones TF.

### 5.25 Guardar mapa

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

## 9. Concepto central

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

## 10. Checklist de entrega

- [ ] Parte 1: gráfica con las dos trayectorias y el error visible.
- [ ] Parte 2: gráfica de incertidumbre **creciente**.
- [ ] Parte 3: gráfica con elipses y la incertidumbre acotada (dientes de sierra).
- [ ] Parte 4: mapa construido progresivamente + comparación con la Parte 3.
- [ ] Parte 5: captura de Gazebo con el robot moviéndose.
- [ ] Parte 5: captura de RViz2 con `/map`, `/scan`, `/tf` y submapas.
- [ ] Parte 5: `my_map.pgm` + `my_map.yaml` guardados.
- [ ] Respuestas a las 15 preguntas de análisis (3 + 3 + 3 + 6).
