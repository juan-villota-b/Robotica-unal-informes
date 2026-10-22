import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from scipy.spatial.transform import Rotation as R


class TFPublisher(Node):

    def __init__(self):
        super().__init__('tf_publisher')
        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast_tf)
        self.t = 0

    def broadcast_tf(self):
        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'robot'

        # Movimiento circular
        t.transform.translation.x = 2.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        # Rotación progresiva
        r = R.from_euler('z', self.t)
        q = r.as_quat()

        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.br.sendTransform(t)
        self.t += 0.05


def main():
    rclpy.init()
    node = TFPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
