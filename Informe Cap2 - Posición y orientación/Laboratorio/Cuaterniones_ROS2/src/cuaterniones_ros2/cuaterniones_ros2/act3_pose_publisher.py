import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from scipy.spatial.transform import Rotation as R


class PosePublisher(Node):

    def __init__(self):
        super().__init__('pose_publisher')
        self.pub = self.create_publisher(Pose, 'pose', 10)
        self.timer = self.create_timer(0.5, self.publish_pose)

    def publish_pose(self):
        msg = Pose()

        # posición
        msg.position.x = 1.0
        msg.position.y = 2.0
        msg.position.z = 0.0

        # orientación (90° en Z)
        r = R.from_euler('z', 90, degrees=True)
        q = r.as_quat()

        msg.orientation.x = q[0]
        msg.orientation.y = q[1]
        msg.orientation.z = q[2]
        msg.orientation.w = q[3]

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = PosePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
