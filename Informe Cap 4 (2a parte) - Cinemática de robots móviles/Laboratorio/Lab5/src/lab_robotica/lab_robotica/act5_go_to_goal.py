"""ACTIVIDAD 5: nodo ROS2 go_to_goal para el TurtleBot3 (codigo base).

Control "ir a un punto" sobre el modelo diferencial del TurtleBot3:
  * se suscribe a /odom (nav_msgs/Odometry) para leer la pose,
  * publica en /cmd_vel (geometry_msgs/TwistStamped) las velocidades v y omega,
  * control proporcional:  v = Kv*distancia,  omega = Kh*error_de_rumbo.

Correcciones respecto al codigo de la guia:
  * se elimino el metodo pose_callback (usaba msg.x / msg.y / msg.theta, que no
    existen en Odometry y no se usaba en ningun suscriptor),
  * se corrigio la indentacion de main().

Ejecutar (terminal 1):
    ros2 launch turtlebot3_gazebo empty_world.launch.py
Ejecutar (terminal 2):
    ros2 run lab_robotica act5_go_to_goal
"""
import math

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.node import Node


class GoToGoal(Node):

    def __init__(self):
        super().__init__('go_to_goal')

        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.timer = self.create_timer(0.1, self.control)

        self.x = 0
        self.y = 0
        self.theta = 0
        self.Kv = 0.5
        self.Kh = 2.0

        self.goal = np.array([2.0, 2.0])

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.theta = math.atan2(siny_cosp, cosy_cosp)

    def control(self):
        # -----------------------------
        # Error de posicion
        # -----------------------------
        dx = self.goal[0] - self.x
        dy = self.goal[1] - self.y

        distance = np.sqrt(dx ** 2 + dy ** 2)
        angle = np.arctan2(dy, dx)

        # -----------------------------
        # Normalizacion angular
        # -----------------------------
        def wrap(a):
            return (a + np.pi) % (2 * np.pi) - np.pi

        error = wrap(angle - self.theta)

        # -----------------------------
        # Control
        # -----------------------------
        if distance < 0.05:
            v = 0.0
            w = 0.0
        else:
            # Control proporcional
            v = self.Kv * distance
            w = self.Kh * error

        # -----------------------------
        # Mensaje TwistStamped
        # -----------------------------
        msg = TwistStamped()

        # Header (obligatorio en muchos plugins)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Velocidades
        msg.twist.linear.x = v
        msg.twist.angular.z = w

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = GoToGoal()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
