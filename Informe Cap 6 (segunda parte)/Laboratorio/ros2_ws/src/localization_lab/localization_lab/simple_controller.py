import sys

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class SimpleController(Node):
    """Mueve el TurtleBot3 en círculos publicando en ``/cmd_vel``."""

    def __init__(self):
        super().__init__('simple_controller')

        # Velocidades configurables por parámetro.
        self.declare_parameter('linear_speed', 0.2)
        self.declare_parameter('angular_speed', 0.1)

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

        msg.twist.linear.x = self.get_parameter('linear_speed').value
        msg.twist.angular.z = self.get_parameter('angular_speed').value

        self.publisher_.publish(msg)


def main(args=None):
    # En simulación el reloj lo publica Gazebo en /clock. Se activa por
    # defecto y se puede desactivar con
    # ``ros2 run localization_lab simple_controller --ros-args -p use_sim_time:=false``.
    args = list(sys.argv[1:] if args is None else args)
    if not any('use_sim_time' in arg for arg in args):
        args += ['--ros-args', '-p', 'use_sim_time:=true']

    rclpy.init(args=args)

    node = SimpleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
