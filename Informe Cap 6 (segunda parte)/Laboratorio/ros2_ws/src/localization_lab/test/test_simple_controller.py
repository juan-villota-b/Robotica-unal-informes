"""Pruebas del nodo controlador. No requieren Gazebo ni RViz."""

import unittest

import rclpy
from geometry_msgs.msg import TwistStamped

from localization_lab.simple_controller import SimpleController


class TestSimpleController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def test_publica_en_cmd_vel(self):
        node = SimpleController()
        try:
            self.assertEqual(node.publisher_.topic_name, '/cmd_vel')
            self.assertEqual(node.publisher_.msg_type, TwistStamped)
        finally:
            node.destroy_node()

    def test_velocidades_por_defecto(self):
        node = SimpleController()
        try:
            self.assertAlmostEqual(
                node.get_parameter('linear_speed').value, 0.2)
            self.assertAlmostEqual(
                node.get_parameter('angular_speed').value, 0.1)
        finally:
            node.destroy_node()


if __name__ == '__main__':
    unittest.main()
