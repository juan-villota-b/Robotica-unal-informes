"""ACTIVIDAD 3 en el TurtleBot3: seguimiento de linea (modelo diferencial).

Es el controlador del seguimiento de linea llevado al TurtleBot3 en Gazebo:
la pose se lee de /odom y el angulo de direccion `delta` se envia como
velocidad angular `omega` (en el robot diferencial theta' = omega):

    distancia  = (a*x + b*y + c) / sqrt(a^2 + b^2)
    theta_line = atan2(a, -b)
    omega      = Kd * distancia + Kh * (theta_line - theta)
    v          = constante

Correcciones respecto al codigo de la guia:
  * el error de rumbo se normaliza a [-pi, pi] (el TurtleBot3 puede quedar en
    cualquier orientacion, no solo en el cuadrante inicial de la guia),
  * se publica TwistStamped (el tipo que espera el puente ros_gz del TurtleBot3).

Ejecutar (terminal 1):
    ros2 launch turtlebot3_gazebo empty_world.launch.py
Ejecutar (terminal 2):
    ros2 run lab_robotica act3_linea_turtlebot3
"""
import math

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node


class LineFollower(Node):

    def __init__(self):
        super().__init__('line_follower')

        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.timer = self.create_timer(0.1, self.control)

        # Linea objetivo: a*x + b*y + c = 0
        self.a = 1.0
        self.b = -2.0
        self.c = 4.0

        self.x = 0
        self.y = 0
        self.theta = 0
        self.Kd = 0.5
        self.Kh = 1.0
        self.v = 0.15

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.theta = math.atan2(siny_cosp, cosy_cosp)

    def control(self):
        # -----------------------------
        # Distancia a la linea y angulo de la linea
        # -----------------------------
        distance = (self.a * self.x + self.b * self.y + self.c) / \
            math.sqrt(self.a ** 2 + self.b ** 2)
        theta_line = math.atan2(self.a, -self.b)

        # -----------------------------
        # Normalizacion angular
        # -----------------------------
        def wrap(a):
            return (a + math.pi) % (2 * math.pi) - math.pi

        # -----------------------------
        # Control (modelo diferencial: omega = delta)
        # -----------------------------
        v = self.v
        w = self.Kd * distance + self.Kh * wrap(theta_line - self.theta)

        # -----------------------------
        # Mensaje TwistStamped
        # -----------------------------
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = v
        msg.twist.angular.z = w

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = LineFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
