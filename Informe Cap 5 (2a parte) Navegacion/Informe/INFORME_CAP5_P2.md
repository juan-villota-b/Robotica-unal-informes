# Informe de Laboratorio - Parte E: Navegación Autónoma y Control Reactivo en ROS 2 Humble

**Estudiante:** Jhon Hesneydert Londoño · Juan David Villota
**Asignatura:** Robótica / Sistemas Embebidos
**Entorno de Ejecución:** ROS 2 Humble | TurtleBot3 (Burger) | Gazebo Simulation

---

## 1. Resumen Ejecutivo
El presente informe documenta el desarrollo y la validación práctica de la **Parte E** del laboratorio de robótica móvil. Se abordan e integran dos enfoques fundamentales para la movilidad autónoma:
1. **Navegación Global (Parte E1):** Uso de la pila de navegación **Nav2** para localización (AMCL) y planificación de trayectorias con mapa previo (`/root/mapa_lab.yaml`).
2. **Navegación Reactiva Local (Parte E2):** Desarrollo e integración del nodo personalizado `nodo_reactivo.py` en Python para la evasión autónoma de obstáculos mediante lecturas continuas del sensor LiDAR (`/scan`).

---

## 2. Parte E1: Navegación Global y Planificación de Rutas con Nav2

### 2.1 Descripción de la Configuración
Para llevar a cabo la navegación basada en mapa, se utilizó el mapa de ocupación previamente generado mediante Cartographer (SLAM). La configuración del mapa en formato YAML define los parámetros de resolución, origen y umbrales de ocupación empleados por el `map_server`.

#### Archivo de Configuración del Mapa (`mapa_lab.yaml`):
```yaml
image: mapa_lab.pgm
mode: trinary
resolution: 0.050000
origin: [-10.000000, -10.000000, 0.000000]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

### 2.2 Procedimiento y Comandos de Ejecución
El despliegue de Nav2 con auto-inicialización de nodos de ciclo de vida se realizó mediante el siguiente comando:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
    use_sim_time:=True \
    map:=/root/mapa_lab.yaml \
    autostart:=True
```

### 2.3 Operación en RViz2
1. **Estimación de la Pose Inicial (`2D Pose Estimate`):** Se estableció la posición del robot en la grilla para sincronizar el mapa estático con las lecturas de odometría y LiDAR mediante el filtro de partículas AMCL.
2. **Asignación de Objetivo (`Nav2 Goal`):** Se definió una coordenada de destino en el mapa, activando la planificación de trayectorias global (*Global Planner*) y la ejecución del controlador local (*Local Controller*).

*[Insertar aquí la captura de pantalla de RViz2 mostrando Navigation: active y la ruta planificada]*

---

## 3. Parte E2: Control Reactivo y Evasión Autónoma de Obstáculos

### 3.1 Arquitectura del Nodo Reactivo
Se implementó un nodo en ROS 2 denominado `nodo_reactivo.py` bajo una arquitectura Suscriptor-Publicador:
* **Suscripción:** Tópico `/scan` (`sensor_msgs/msg/LaserScan`) para obtener distancias de detección del LiDAR.
* **Publicación:** Tópico `/cmd_vel` (`geometry_msgs/msg/Twist`) para controlar la velocidad lineal y angular del robot.

### 3.2 Código Fuente (`nodo_reactivo.py`)

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class NodoReactivo(Node):
    def __init__(self):
        super().__init__('nodo_reactivo')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.get_logger().info('Nodo reactivo de evasión inicializado.')

    def scan_callback(self, msg):
        # Muestra la distancia frontal (0 grados)
        distancia_frontal = msg.ranges[0]

        cmd = Twist()
        # Umbral de seguridad: 0.5 metros
        if distancia_frontal < 0.5 and distancia_frontal > 0.0:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5  # Giro de evasión
            self.get_logger().info(f'Obstáculo detectado a {distancia_frontal:.2f}m. Rotando...')
        else:
            cmd.linear.x = 0.2   # Avance continuo
            cmd.angular.z = 0.0

        self.publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoReactivo()
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3.3 Integración en `setup.py` y Compilación
Para permitir la ejecución del nodo mediante `ros2 run`, se registró el punto de entrada en el archivo `setup.py`:

```python
entry_points={
    'console_scripts': [
        'nodo_reactivo = mi_paquete_navegacion.nodo_reactivo:main',
    ],
},
```

Compilación del entorno:
```bash
colcon build --packages-select mi_paquete_navegacion
source install/setup.bash
ros2 run mi_paquete_navegacion nodo_reactivo
```

*[Insertar aquí la captura de pantalla de Gazebo mostrando el robot esquivando un obstáculo]*

---

## 4. Análisis Teórico y Preguntas del Laboratorio

### A. Diferencias entre Navegación Reactiva y Nav2
* **Navegación Reactiva:** Bucle de control cerrado de respuesta inmediata basado únicamente en la información de sensores en tiempo real. No posee mapa ni memoria espacial, lo que la hace susceptible a trampas locales (como obstáculos en forma de "U").
* **Navegación con Nav2:** Pila jerárquica de navegación global que utiliza un mapa previo, algoritmos de localización (AMCL) y cálculo de rutas óptimas (A* o Dijkstra) para llevar al robot desde cualquier punto $A$ hasta un punto $B$ sin quedar atrapado.

### B. Función del Planner y del Controller en Nav2
* **Global Planner:** Taza una trayectoria completa y óptima libre de obstáculos estáticos desde el origen hasta el objetivo basándose en el mapa global.
* **Local Controller (DWB / TEB):** Modula la velocidad lineal ($v$) y angular ($\omega$) en ciclos de alta frecuencia para seguir la ruta global y evitar obstáculos no mapeados o dinámicos detectados por el LiDAR en tiempo real.

### C. Ventajas de la Arquitectura Modulated ROS 2
La arquitectura orientada a servicios de ROS 2 basada en DDS permite desacoplar nodos de percepción, control y planificación, garantizando comunicación de baja latencia y alta mantenibilidad.

---

## 5. Propuesta de Proyecto Final

**Título:** Sistema Híbrido de Inspección Industrial Autónoma con Nav2 y Capa de Seguridad Reactiva
**Descripción:**
Se propone desarrollar una aplicación de inspección autónoma para logística o almacenes. El sistema combinará la planificación global de **Nav2** para navegar eficientemente entre estaciones de trabajo (puntos de interés) con un **módulo reactivo de seguridad**, el cual intervendrá anulando temporalmente la trayectoria global en caso de detectar imprevistos o personas en el camino de manera intempestiva.
