"""ACTIVIDAD 4 en el TurtleBot3: Pure Pursuit (modelo diferencial).

Es el seguidor de trayectoria Pure Pursuit llevado al TurtleBot3: la pose se lee
de /odom y el control se publica como velocidades v y omega:

    error angular = wrap(atan2(dy, dx) - theta)   al waypoint actual
    omega         = Kd * error
    v             = constante

El waypoint actual avanza cuando el robot esta a menos de `lookahead` de el.
Cuando se alcanza el ultimo waypoint el robot se detiene.

Correcciones respecto al codigo de la guia:
  * el error angular se normaliza (el robot puede apuntar en cualquier direccion),
  * el recorrido termina al alcanzar el ultimo waypoint en vez de cortar por un
    numero fijo de iteraciones.

Ejecutar (terminal 1):
    ros2 launch turtlebot3_gazebo empty_world.launch.py
Ejecutar (terminal 2):
    ros2 run lab_robotica act4_pure_pursuit_turtlebot3
"""
import math

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node

PATH = [(0.0, 0.0), (2.0, 4.0), (6.0, 5.0), (8.0, 10.0)]


class PurePursuit(Node):

    def __init__(self):
        super().__init__('pure_pursuit')

        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.timer = self.create_timer(0.1, self.control)

        self.path = PATH
        self.lookahead = 0.5
        self.current_index = 0
        self.Kd = 1.3
        self.v = 0.15

        self.x = 0
        self.y = 0
        self.theta = 0

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.theta = math.atan2(siny_cosp, cosy_cosp)

    def control(self):
        # -----------------------------
        # Distancia y avance al siguiente waypoint
        # -----------------------------
        target = self.path[self.current_index]
        distance = math.hypot(target[0] - self.x, target[1] - self.y)

        if distance < self.lookahead and self.current_index < len(self.path) - 1:
            self.current_index += 1
            target = self.path[self.current_index]
        elif distance < self.lookahead and self.current_index == len(self.path) - 1:
            self.publicar(0.0, 0.0)
            self.get_logger().info('camino completado')
            return

        # -----------------------------
        # Error angular normalizado
        # -----------------------------
        def wrap(a):
            return (a + math.pi) % (2 * math.pi) - math.pi

        theta_goal = math.atan2(target[1] - self.y, target[0] - self.x)
        error = wrap(theta_goal - self.theta)

        # -----------------------------
        # Control
        # -----------------------------
        self.publicar(self.v, self.Kd * error)

    def publicar(self, v, w):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = v
        msg.twist.angular.z = w
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = PurePursuit()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
