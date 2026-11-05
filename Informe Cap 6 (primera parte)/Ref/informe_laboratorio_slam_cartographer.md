# Informe de Laboratorio: Mapeo y Localización Simultánea (SLAM 2D) con ROS 2 Humble y Cartographer

**Asignatura:** Robótica / Robótica Móvil  
**Fecha:** 4 de noviembre de 2026  
**Entorno de Ejecución:** Docker (`ros2_turtlebot`) sobre Nobara Linux  

---

## 1. Resumen Ejecutivo
En esta práctica se implementó y validó de forma autónoma el pipeline de **Mapeo y Localización Simultánea (SLAM 2D)** en un entorno simulado de **Gazebo** utilizando el modelo **TurtleBot3 Burger**. Se utilizó **Cartographer** como nodo de SLAM para la generación probabilística de mapas de ocupación 2D, combinado con un controlador de evitación de colisiones desarrollado en **Python** para asegurar una navegación limpia y libre de colisiones.

---

## 2. Arquitectura del Sistema

La solución integra 4 nodos principales que se comunican concurrentemente mediante el middleware de ROS 2:

```
[Gazebo Simulation] ---> /scan, /tf, /odom ---> [Cartographer SLAM] ---> /map ---> [RViz2]
         ^                                              |
         |------------------ /cmd_vel <------------------|
                   [simple_controller.py]
```

### Componentes Clave:
1. **Simulación (Gazebo):** Simula la física del robot TurtleBot3 Burger y los sensores en el entorno `turtlebot3_world`. Publica los tópicos `/scan` (LiDAR 2D) y la odometría del robot.
2. **Nodo de SLAM (Cartographer):** Procesa los datos de distancia y transformaciones espaciales para generar submapas probabilísticos y construir la cuadrícula de ocupación global del entorno en `/map`.
3. **Controlador Autónomo (`simple_controller.py`):** Nodo programado en Python con lógica de evitación de obstáculos usando el rango frontal de 30° del LiDAR (`/scan`) a $< 0.5\text{ m}$, enviando comandos de velocidad angular y lineal a través de `/cmd_vel`.
4. **Visualizador (RViz2):** Renderiza las relaciones de transformación TF, la nube de puntos del escáner láser y la cuadrícula de ocupación de Cartographer en el Fixed Frame `map`.

---

## 3. Implementación del Controlador (`simple_controller.py`)

Para evitar que el robot patine o choque contra obstáculos (lo cual descompensa la odometría y distorsiona el mapa), se implementó la siguiente estructura en el paquete `localization_lab`:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class SimpleController(Node):
    def __init__(self):
        super().__init__('simple_controller')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription_ = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.obstacle_ahead = False

    def scan_callback(self, msg):
        # Evaluación del rango frontal (30° frontales del LiDAR)
        front_ranges = msg.ranges[:15] + msg.ranges[-15:]
        valid_ranges = [r for r in front_ranges if not float('inf') in (r,) and r > 0.05]
        
        if valid_ranges and min(valid_ranges) < 0.5:
            self.obstacle_ahead = True
        else:
            self.obstacle_ahead = False
            
        self.move_robot()

    def move_robot(self):
        msg = Twist()
        if self.obstacle_ahead:
            msg.linear.x = 0.0
            msg.angular.z = 0.5  # Giro en el sitio
        else:
            msg.linear.x = 0.15 # Avance seguro
            msg.angular.z = 0.05
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

---

## 4. Resultados y Evidencias

### 4.1. Archivos Guardados del Mapa
Utilizando la herramienta `nav2_map_server map_saver_cli`, se exportaron los siguientes archivos al directorio del sistema:

* **`my_map.yaml`:** Define la resolución del mapa ($0.05\text{ m/px}$), el origen y los umbrales de ocupación/espacio libre.
* **`my_map.pgm`:** Imagen matricial en escala de grises con la representación de paredes hexagonales, los 9 pilares internos y el espacio navegable explorado.

```bash
# Verificación de archivos generados
-rw-r--r-- 1 root root 22955 my_map.pgm
-rw-r--r-- 1 root root   123 my_map.yaml
```

### 4.2. Visualización en RViz2 y Gazebo
* **Grabación de Video:** Se registró en video el recorrido completo en vivo donde se observa la actualización progresiva por submapas de Cartographer mientras el robot navega esquivando los obstáculos autónomamente.
* **Mapa Resultante:** El mapa final delimitó claramente las geometrías del mundo sin desviaciones ni artefactos de odometría.

---

## 5. Conclusiones
1. **Comportamiento de Cartographer:** A diferencia de algoritmos que actualizan celda por celda de forma continua (`slam_toolbox`), Cartographer funciona acumulando submapas locales optimizados, lo que genera actualizaciones del mapa por bloques probabilísticos en la interfaz visual.
2. **Importancia de la Evitación de Obstáculos:** La incorporación de un controlador reactivo fue determinante para mantener limpia la odometría, evitando errores de desalineación en el mapeo producidos por patinajes o colisiones del chasis contra paredes.