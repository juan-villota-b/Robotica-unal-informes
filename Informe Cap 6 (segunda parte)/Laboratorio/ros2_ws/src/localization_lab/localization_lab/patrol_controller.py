"""Patrulla de mapeo: recorrido por waypoints o cuadrado con giros de 360°.

Dos patrones:

``tour`` (por defecto)
    Recorre un rectángulo de ``width`` x ``height`` centrado en
    (``center_x``, ``center_y``), en coordenadas de ``/odom``. Navega punto a
    punto: gira en el lugar hasta apuntar al waypoint y avanza corrigiendo el
    rumbo. Con los valores por defecto da la vuelta completa a la zona libre
    del mundo ``turtlebot3_world`` (el anillo entre el grupo de cilindros y las
    paredes), en vez de quedarse en una franja.

``square``
    El patrón original: avanza ``side_length``, gira 360° en la esquina y gira
    90°, cuatro veces.

En los dos casos mide con ``/odom`` (no con el reloj) y vigila el LiDAR: si el
cono frontal ve un obstáculo más cerca que ``min_obstacle_distance``, corta la
pierna y pasa al waypoint siguiente en vez de empujar.

Uso típico desde el spawn de ``turtlebot3_world`` (odom = (0,0) en (-2, -0.5)):

    ros2 run localization_lab patrol_controller

    # el cuadrado de la guía, en la franja libre de la izquierda
    ros2 run localization_lab patrol_controller --ros-args \
         -p pattern:=square -p start_turn:=3.1416 -p turn_direction:=-1.0
"""

import math
import sys

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

# Estados
IDLE, TURN_START, FORWARD, SPIN, TURN, ROTATE, DRIVE, WALL, DONE = range(9)


def wrap(angle):
    """Normaliza un ángulo a (-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


class PatrolController(Node):
    """Recorre el entorno para que el LiDAR lo mapee."""

    def __init__(self):
        super().__init__('patrol_controller')

        self.pattern = self.declare_parameter('pattern', 'wall').value
        self.wall_distance = self.declare_parameter(
            'wall_distance', 0.9).value
        self.duration = self.declare_parameter('duration', 240.0).value
        self.linear_speed = self.declare_parameter(
            'linear_speed', 0.2).value
        self.angular_speed = self.declare_parameter(
            'angular_speed', 0.6).value
        self.tolerance = self.declare_parameter('tolerance', 0.25).value
        self.min_obstacle = self.declare_parameter(
            'min_obstacle_distance', 0.35).value
        self.spin_at_corner = self.declare_parameter(
            'spin_at_corner', 0.0).value
        self.phase_timeout = self.declare_parameter(
            'phase_timeout', 240.0).value

        # Patrón tour
        self.center = (
            self.declare_parameter('center_x', 2.0).value,
            self.declare_parameter('center_y', 0.5).value,
        )
        self.width = self.declare_parameter('width', 8.0).value
        self.height = self.declare_parameter('height', 7.2).value
        self.waypoints = self.build_waypoints()
        self.index = 0

        # Patrón square
        self.side_length = self.declare_parameter(
            'side_length', 2.0).value
        self.laps = self.declare_parameter('laps', 1).value
        self.start_turn = self.declare_parameter(
            'start_turn', 0.0).value
        self.turn_direction = self.declare_parameter(
            'turn_direction', 1.0).value
        self.side = 0
        self.lap = 0

        self.publisher_ = self.create_publisher(
            TwistStamped, '/cmd_vel', 10)
        self.create_subscription(Odometry, '/odom', self.on_odom, 10)
        self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.create_timer(0.05, self.step)      # 20 Hz

        self.pose_xy = None
        self.yaw = 0.0
        self.distance = 0.0
        self.turned = 0.0
        self.front_range = float('inf')
        self.right_range = float('inf')
        self.target = 0.0
        self.direction = 1.0
        self.phase_start = self.get_clock().now()
        self.wall_start = self.get_clock().now()

        if self.pattern == 'square':
            if self.start_turn:
                self.state = TURN_START
                self.target = abs(self.start_turn)
                self.direction = math.copysign(1.0, self.start_turn)
            else:
                self.state = FORWARD
            self.get_logger().info(
                'Patrulla cuadrada: lado %.2f m, %d vuelta(s)'
                % (self.side_length, self.laps))
        elif self.pattern == 'tour':
            self.state = ROTATE
            self.get_logger().info(
                'Recorrido: %d waypoints, rectángulo %.1f x %.1f m'
                % (len(self.waypoints), self.width, self.height))
        else:
            self.state = WALL
            self.get_logger().info(
                'Seguidor de pared: %.2f m, %.0f s'
                % (self.wall_distance, self.duration))

    # ------------------------------------------------------------ waypoints
    def build_waypoints(self):
        """Cuatro esquinas del rectángulo, en orden de recorrido."""
        cx, cy = self.center
        hw, hh = self.width / 2.0, self.height / 2.0
        return [
            (cx - hw, cy - hh),
            (cx + hw, cy - hh),
            (cx + hw, cy + hh),
            (cx - hw, cy + hh),
            (cx - hw, cy - hh),
        ]

    # ---------------------------------------------------------------- sensores
    def on_odom(self, msg):
        p = msg.pose.pose.position
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)

        if self.pose_xy is not None:
            self.distance += math.hypot(
                p.x - self.pose_xy[0], p.y - self.pose_xy[1])
            self.turned += abs(wrap(yaw - self.yaw))

        self.pose_xy = (p.x, p.y)
        self.yaw = yaw

    def range_at(self, msg, degrees):
        """Distancia en un ángulo dado (grados), con índice circular."""
        n = len(msg.ranges)
        i = int(round((math.radians(degrees) - msg.angle_min)
                      / msg.angle_increment)) % n
        r = msg.ranges[i]
        return r if math.isfinite(r) and r > 0.05 else float('inf')

    def on_scan(self, msg):
        """Rango mínimo al frente (+-25°) y a la derecha (-70°..-110°)."""
        self.front_range = min(
            self.range_at(msg, d) for d in range(-25, 26, 5))
        self.right_range = min(
            self.range_at(msg, d) for d in (-110, -100, -90, -80, -70))

    # -------------------------------------------------------------- máquina
    def start_phase(self, state, target=0.0, direction=1.0):
        self.state = state
        self.target = target
        self.direction = direction
        self.distance = 0.0
        self.turned = 0.0
        self.phase_start = self.get_clock().now()

    def step(self):
        if self.state == DONE:
            self.publish(0.0, 0.0)
            return

        if self.pose_xy is None:
            self.publish(0.0, 0.0)
            return

        elapsed = (self.get_clock().now() - self.phase_start).nanoseconds * 1e-9
        if self.phase_timeout > 0.0 and elapsed > self.phase_timeout:
            self.get_logger().warning(
                'Fase %d sin terminar después de %.0f s: me detengo'
                % (self.state, self.phase_timeout))
            self.state = DONE
            self.publish(0.0, 0.0)
            return

        if self.state == ROTATE:
            self.do_rotate()
        elif self.state == DRIVE:
            self.do_drive()
        elif self.state == WALL:
            self.do_wall()
        elif self.state == FORWARD:
            self.do_square_forward()
        elif self.state == TURN_START:
            self.do_turn(self.FORWARD)
        elif self.state == SPIN:
            if self.pattern == 'square':
                self.do_turn(self.TURN, math.pi / 2.0, self.turn_direction)
            else:
                self.do_turn(ROTATE)
        elif self.state == TURN:
            self.do_square_turn()

    # ------------------------------------------------------- seguidor de pared
    def do_wall(self):
        elapsed = (self.get_clock().now() - self.wall_start).nanoseconds * 1e-9
        if self.duration > 0.0 and elapsed > self.duration:
            self.get_logger().info(
                'Recorrido terminado: %.0f s, %.1f m' % (elapsed, self.distance))
            self.finish()
            return

        if self.front_range < 0.45:
            # obstáculo al frente: gira a la izquierda sin avanzar
            self.publish(0.0, self.angular_speed)
            return

        # pared a la derecha: si está lejos giro a la derecha, si está cerca
        # giro a la izquierda
        error = self.right_range - self.wall_distance
        omega = max(-0.35, min(0.35, -0.9 * error))
        speed = 0.14 if self.front_range > 1.0 else 0.06
        self.publish(speed, omega)

    # --------------------------------------------------------- patrón tour
    def target_point(self):
        if self.index >= len(self.waypoints):
            return None
        return self.waypoints[self.index]

    def do_rotate(self):
        target = self.target_point()
        if target is None:
            self.finish()
            return
        dx = target[0] - self.pose_xy[0]
        dy = target[1] - self.pose_xy[1]
        err = wrap(math.atan2(dy, dx) - self.yaw)
        if abs(err) < 0.12 or self.turned > 2.0 * math.pi:
            self.start_phase(DRIVE)
        else:
            self.publish(0.0, max(-self.angular_speed,
                                  min(self.angular_speed, 1.5 * err)))

    def do_drive(self):
        target = self.target_point()
        if target is None:
            self.finish()
            return
        dx = target[0] - self.pose_xy[0]
        dy = target[1] - self.pose_xy[1]
        dist = math.hypot(dx, dy)
        err = wrap(math.atan2(dy, dx) - self.yaw)

        if self.front_range < self.min_obstacle:
            self.get_logger().warning(
                'Obstáculo a %.2f m: salto al waypoint %d'
                % (self.front_range, self.index + 1))
            self.next_waypoint()
            return

        if dist < self.tolerance:
            self.get_logger().info(
                'Waypoint %d alcanzado (%.2f m)' % (self.index, dist))
            self.next_waypoint()
            return

        # avanza y corrige el rumbo; frena cerca del objetivo
        speed = self.linear_speed
        if dist < 0.8:
            speed = max(0.05, self.linear_speed * dist / 0.8)
        omega = max(-self.angular_speed, min(self.angular_speed, 1.5 * err))
        self.publish(speed, omega)

    def next_waypoint(self):
        self.index += 1
        if self.spin_at_corner > 0.0 and self.index < len(self.waypoints):
            self.start_phase(SPIN, self.spin_at_corner, 1.0)
        elif self.index >= len(self.waypoints):
            self.finish()
        else:
            self.start_phase(ROTATE)

    def finish(self):
        self.get_logger().info('Recorrido terminado.')
        self.state = DONE
        self.publish(0.0, 0.0)

    # ------------------------------------------------------- patrón square
    def do_square_forward(self):
        if self.distance >= self.side_length:
            self.get_logger().info(
                'Lado %d listo (%.2f m): giro 360°'
                % (self.side + 1, self.distance))
            self.start_phase(SPIN, 2.0 * math.pi, 1.0)
        else:
            self.publish(self.linear_speed, 0.0)

    def do_turn(self, next_state, target=None, direction=None):
        if target is not None:
            self.target = target
        if direction is not None:
            self.direction = direction
        if self.turned >= self.target:
            self.start_phase(next_state)
        else:
            self.publish(0.0, self.direction * self.angular_speed)

    def do_square_turn(self):
        if self.turned >= self.target:
            self.side += 1
            if self.side < 4:
                self.start_phase(FORWARD)
            else:
                self.side = 0
                self.lap += 1
                if self.lap < self.laps:
                    self.get_logger().info(
                        'Vuelta %d de %d' % (self.lap, self.laps))
                    self.start_phase(FORWARD)
                else:
                    self.finish()
        else:
            self.publish(0.0, self.direction * self.angular_speed)

    # ------------------------------------------------------------- comando
    def publish(self, linear, angular):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = linear
        msg.twist.angular.z = angular
        self.publisher_.publish(msg)


def main(args=None):
    args = list(sys.argv[1:] if args is None else args)
    if not any('use_sim_time' in arg for arg in args):
        if '--ros-args' in args:
            i = args.index('--ros-args')
            args[i + 1:i + 1] = ['-p', 'use_sim_time:=true']
        else:
            args += ['--ros-args', '-p', 'use_sim_time:=true']

    rclpy.init(args=args)
    node = PatrolController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
