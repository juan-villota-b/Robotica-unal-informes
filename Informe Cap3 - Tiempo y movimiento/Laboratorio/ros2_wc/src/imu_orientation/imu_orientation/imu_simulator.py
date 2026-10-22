import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class IMUSimulator(Node):

    def __init__(self):
        super().__init__('imu_simulator')

        # Publicador del mensaje IMU
        self.pub = self.create_publisher(Imu, '/imu', 10)

        # Timer: ejecuta publish_imu cada 0.01 s = 100 Hz
        self.timer = self.create_timer(0.01, self.publish_imu)

    def publish_imu(self):
        msg = Imu()

        # Rotación constante alrededor del eje Z
        msg.angular_velocity.y = 4.0  # rad/s
        msg.angular_velocity.x = 1.0  # rad/s
        msg.angular_velocity.z = 4.0  # rad/s

        # Publicar mensaje
        self.pub.publish(msg)


def main():
    rclpy.init()

    node = IMUSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
