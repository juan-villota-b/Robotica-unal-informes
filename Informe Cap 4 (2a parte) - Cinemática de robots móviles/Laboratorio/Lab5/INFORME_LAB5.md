# Laboratorio 5 — Cap. 4 (Corke): actividades 3, 4 y 5 en el TurtleBot3

**TurtleBot3 (modelo diferencial) · ROS2 Lyrical · Gazebo 10.5**

Los tres nodos usan la misma interfaz: leen la pose de **`/odom`** y actúan sobre
**`/cmd_vel`**, así que el mismo código sirve en simulación y en el robot real. Lo que cambia
entre las tres actividades es el **problema de control**, no la comunicación.

Preparación (una vez) — se usa el Python del sistema, **no** el venv `robotica`:

```bash
cd /home/juan-david/Documentos/Semestre_VIII/Robótica/Lab5
colcon build --symlink-install && source install/setup.zsh
```

## Cómo se lanza

Un solo comando por actividad (abre Gazebo con el robot, el nodo y RViz ya configurado):

```bash
ros2 launch lab_robotica lab5.launch.py actividad:=3    # seguimiento de línea
ros2 launch lab_robotica lab5.launch.py actividad:=4    # Pure Pursuit
ros2 launch lab_robotica lab5.launch.py actividad:=5    # ir a un punto
```

El lanzador exporta `TURTLEBOT3_MODEL=burger` por su cuenta, levanta el servidor y la GUI de
Gazebo como procesos independientes, y escalona los arranques: **RViz a los 6 s** y **el nodo
a los 10 s**, para que el rastro se dibuje completo desde el primer movimiento (en la
actividad 5 el robot llega al objetivo en pocos segundos).

Alternativa manual, en dos terminales (con `export TURTLEBOT3_MODEL=burger`):

```bash
ros2 launch turtlebot3_gazebo empty_world.launch.py    # terminal 1
ros2 run lab_robotica <nodo>                           # terminal 2
```

Para ver la trayectoria por separado: `rviz2 -d install/lab_robotica/share/lab_robotica/config/lab5.rviz --ros-args -p use_sim_time:=true`

---

## Actividad 3 — Seguimiento de línea en el TurtleBot3

**Lo implementado** (`act3_linea_turtlebot3.py`): el controlador de la actividad 3 sobre el
robot diferencial. Del controlador bicicleta se conserva el cálculo de la distancia y del
rumbo de la línea; el ángulo de dirección `δ` pasa a ser velocidad angular `ω`, porque en el
TurtleBot3 `θ' = ω`. La pose se lee de `/odom` y el comando se publica como `TwistStamped` en
`/cmd_vel` (no hay cámara: la recta es analítica, `a = 1`, `b = −2`, `c = 4`).

```
distance = (a·x + b·y + c)/√(a²+b²)      θ_line = atan2(a, −b) = 26.57°     (x − 2y + 4 = 0)
ω = Kd·distance + Kh·wrap(θ_line − θ)    con Kd = 0.5, Kh = 1.0
v = 0.15 m/s
```

Correcciones al código de la guía: el error de rumbo se normaliza a `[−π, π]` (el robot puede
quedar en cualquier orientación, no solo en el cuadrante inicial de la guía) y se publica
`TwistStamped`, que es el tipo que espera el puente `ros_gz` del TurtleBot3.

### Evidencia

![Actividad 3: Gazebo y RViz](act3.png)

Izquierda, la ventana de Gazebo con el TurtleBot3 en el mundo vacío. Derecha, RViz con el
display *Rastro de la trayectoria* sobre `/odom`.

**Análisis.** El rastro (rojo) describe un **arco que se va rectificando**: el robot parte del
origen a 1.789 m de la recta y con rumbo 0°, así que primero el término `Kh·(θ_line − θ)` lo
hace girar hasta alinearse con la dirección de la recta (26.57°) mientras el término
`Kd·distance` cierra la distancia transversal. Al final del rastro la curva es prácticamente
tangente a la recta: el robot quedó **viajando sobre la línea** (`ρ → 0`, rumbo ≈ 26.5°). Ese
tramo curvo de enganche es lo que no existe cuando `Kd = 0`: el robot se alinea igual pero
avanza paralelo, sin tocar nunca la recta.

---

## Actividad 4 — Pure Pursuit en el TurtleBot3

**Lo implementado** (`act4_pure_pursuit_turtlebot3.py`): el seguidor de trayectoria sobre el
robot diferencial, con los waypoints `(0,0) → (2,4) → (6,5) → (8,10)`. Cuando el waypoint
actual queda a menos de `lookahead` el índice avanza al siguiente; el control vuelve a ser
velocidad angular y el recorrido termina al alcanzar el último waypoint (la guía cortaba en
285 iteraciones, que no completan los ≈14 m del camino).

```
error = wrap(atan2(Δy, Δx) − θ)     ω = Kd·error   con Kd = 1.3 ;  v = 0.15 m/s
```

### Evidencia

![Actividad 4: Gazebo y RViz](act4.png)

**Análisis.** Aquí el rastro es **poligonal**: tramos rectos unidos por **dos esquinas
marcadas**, que son los dos waypoints intermedios (2, 4) y (6, 5). El robot apunta a cada
waypoint y gira al alcanzarlo, en lugar de describir una curva continua como en la actividad
3. Las esquinas se ven **suavemente redondeadas**, que es el efecto de que el índice avanza
por radio (`lookahead`) y no por paso exacto sobre el punto: el robot **corta la esquina**. Es
la manifestación directa de que Pure Pursuit persigue *un punto*, no la polilínea: entre dos
waypoints la ruta real es un arco, y corregir en lateral obliga a girar porque el robot es no
holonómico.

---

## Actividad 5 — Ir a un punto en el TurtleBot3

**Lo implementado** (`act5_go_to_goal.py`): el nodo de la guía corregido. Se suscribe a
`/odom`, calcula el error de posición y de rumbo al objetivo `(2, 2)` y publica el comando en
`/cmd_vel`, deteniéndose cuando `distance < 0.05`.

```
v = Kv·distance   (Kv = 0.5)        w = Kh·error   (Kh = 2.0)
```

**Correcciones aplicadas al código base** (venía con errores):

- Se **eliminó el método `pose_callback`**: usaba `msg.x`, `msg.y` y `msg.theta`, campos que
  **no existen** en `Odometry`, y no estaba suscrito a ningún tópico.
- Se corrigió la **indentación de `main()`**.

### Evidencia

![Actividad 5: Gazebo y RViz](act5.png)

**Análisis.** El rastro es **casi una recta**: un pequeño gancho al inicio —el giro para
apuntar al objetivo— y después un tramo recto hasta el robot, que aparece dibujado por el
display *RobotModel* **al final del rastro, detenido en el objetivo**. A diferencia de las
actividades 3 y 4, aquí la referencia es **un punto y no una trayectoria**, así que una vez
que el rumbo apunta al objetivo (`error → 0`) el robot ya no necesita girar y avanza en línea
recta. Además, como `v = Kv·distance`, la velocidad es proporcional a lo que le falta: arranca
a `0.5 × 2.83 = 1.41 m/s` y se va frenando sola hasta que `distance < 0.05 m`, que es la
condición de parada. Esa es la razón de que el recorrido sea tan corto y rápido comparado con
las otras dos actividades, donde `v` es constante (0.15 m/s).

### Preguntas

**1. ¿Qué tipo de información se publica en `/cmd_vel` y para qué se usa?**

Un `geometry_msgs/msg/TwistStamped`: es un **comando de velocidad**, no una posición.

| Campo | Uso en el laboratorio |
|---|---|
| `twist.linear.x` | velocidad lineal **v** hacia adelante (m/s) |
| `twist.angular.z` | velocidad angular **ω** de guinada (rad/s) |
| `header` | sello de tiempo y marco (`base_link`) |
| resto | no se usa: un robot diferencial no se desplaza de lado ni se inclina |

Sirve para **ordenar el movimiento a la base móvil**. El plugin diferencial lo reparte a las
ruedas (`v_l = v − ωW/2`, `v_r = v + ωW/2`), de donde `v = (v_r+v_l)/2` y `ω = (v_r−v_l)/W`.
Es el mismo tópico y el mismo mensaje que usa el TurtleBot3 real, por lo que el nodo funciona
sin cambios sobre el robot físico.

**2. ¿Qué información se utilizó para cerrar el lazo de control con `/odom`?**

La **pose completa** que trae `nav_msgs/msg/Odometry`: `position.x` y `position.y`, más el
rumbo extraído del cuaternión de orientación
(`yaw = atan2(2(w·z + x·y), 1 − 2(y² + z²))`). Con `(x, y, θ)` el nodo calcula la **distancia al
objetivo**, el **rumbo al objetivo** y el **error de rumbo**: esa es la señal de realimentación.
Sin `/odom` el robot solo publicaría comandos a ciegas. Es un lazo cerrado en posición: `v` es
proporcional al error de posición y `ω` al error de orientación.

Hay que tener en cuenta que la pose de `/odom` es **odométrica** —el simulador la obtiene
integrando el modelo cinemático (`x += v·cos θ·dt`, etc.) a partir de las velocidades de
rueda, no de un sensor externo—, por eso en un robot real acumula deriva.

**3. ¿Qué sensores serían necesarios en un sistema real?**

| Para qué | Sensor |
|---|---|
| medir las velocidades de rueda que alimentan la odometría `(v, ω)` | **encoders** |
| medir la velocidad de giro real y corregir el deslizamiento | **IMU** (giróscopo + acelerómetro) |
| saber **dónde está respecto al mundo** (la odometría sola deriva) | **LiDAR 2D** + SLAM/AMCL sobre un mapa, cámara (odometría visual), GPS/GNSS o balizas UWB |
| seguridad / evasión de obstáculos | LiDAR, ultrasonidos o *bumpers* |

Los encoders y la IMU sostienen el lazo que ya usa el laboratorio, pero para un objetivo
expresado en coordenadas del mundo hace falta además un sistema de localización externa,
porque `/odom` por sí sola no cierra el lazo contra el mundo. El TurtleBot3 simulado ya trae
`/scan` (LiDAR), `/imu`, `/joint_states` (encoders simulados) y `/odom`.

---

## Cierre

1. Las tres actividades comparten la misma interfaz ROS2 (`/odom` → nodo → `/cmd_vel`); lo que
   cambia es el problema: **seguir una recta**, **seguir un camino** o **llegar a un punto**.
2. Esa diferencia se ve directamente en las evidencias: rastro **curvo** en la 3, **poligonal**
   en la 4 y **recto con parada** en la 5.
3. El ángulo de dirección `δ` del modelo bicicleta de la guía se traduce en velocidad angular
   `ω` para el modelo diferencial del TurtleBot3.
4. `Kd` (o `Kv`) fija la rapidez de convergencia; en la 5, además, hace que el robot se frene
   solo al acercarse al objetivo.
