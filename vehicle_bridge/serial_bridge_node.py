#!/usr/bin/env python3
"""ROS 2 <-> serial drive-by-wire bridge for the real vehicle.

Subscribes the same /cmd_ackermann interface tesla_sim uses, so the identical
command stream that drives the simulator also drives real hardware -- that
interchangeability is the whole point of tesla_sim being a "digital clone"
rather than an unrelated simulation with its own bespoke control API.

Steering is closed-loop: /steering/angle (real rotary-encoder feedback, degrees,
+right/-left) plus the commanded target angle go through the same
RelaySteeringController tesla_sim's driver uses, producing one of the three
relay states (49/50/51) the real motor actually accepts -- see
relay_steering.py for why this can't be a proportional value.

Throttle is open-loop (no ROS input maps to brake/lights/indicators yet; see
README). /steering/angle comes from encoder_node, which reads the steering
encoder's own MCU over a separate USB serial port. If it stops arriving for
encoder_timeout_s, the bridge treats feedback as lost and holds neutral+stop.
"""
import math
import time

import rclpy
from ackermann_msgs.msg import AckermannDrive
from rclpy.node import Node
from std_msgs.msg import Float32

from vehicle_bridge.relay_steering import RelaySteeringController
from vehicle_bridge.serial_command import THROTTLE_NEUTRAL, SERIAL_BAUD, build_serial_command

try:
    import serial
except ImportError:
    serial = None

# Unverified -- see serial_command.py's module docstring and this package's
# README. Best available reference is cart_controller's MAX_SPEED_KMH=7.0;
# no script read anywhere in this workspace actually calibrates throttle-byte
# against real measured speed.
MAX_SPEED_KMH = 7.0

MIN_SERIAL_INTERVAL_S = 0.030  # matches cart_controller's own bus-protection interval
CONTROL_TICK_S = 0.025         # 40 Hz -- responsive; relay's own 35ms hold still gates transitions


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('dry_run', False)
        self.declare_parameter('encoder_timeout_s', 0.5)
        port = self.get_parameter('serial_port').value
        dry_run = self.get_parameter('dry_run').value
        self._encoder_timeout_s = float(self.get_parameter('encoder_timeout_s').value)

        self._steering = RelaySteeringController()
        self._target_deg = 0.0
        self._encoder_deg = 0.0
        self._last_encoder_s = None
        self._commanded_speed_kmh = 0.0
        self._last_serial_time = 0.0

        self._ser = None
        if dry_run:
            self.get_logger().warn('dry_run=true -- relay decisions computed but nothing written to serial.')
        elif serial is None:
            self.get_logger().error("pyserial not installed -- can't talk to hardware. Running as dry_run.")
        else:
            try:
                self._ser = serial.Serial(port=port, baudrate=SERIAL_BAUD, timeout=0.05)
                self.get_logger().info(f'Serial port {port} opened at {SERIAL_BAUD} baud.')
            except Exception as e:
                self.get_logger().error(f'Could not open {port}: {e}. Running as dry_run.')

        self.create_subscription(AckermannDrive, 'cmd_ackermann', self._on_cmd_ackermann, 1)
        self.create_subscription(Float32, 'steering/angle', self._on_encoder, 10)

        self._timer = self.create_timer(CONTROL_TICK_S, self._control_tick)

        self.get_logger().info(
            'Serial bridge ready: /cmd_ackermann in, relay steering closed over '
            '/steering/angle, MAX_SPEED_KMH={} (unverified, see README)'.format(MAX_SPEED_KMH))

    def _on_cmd_ackermann(self, msg):
        self._target_deg = math.degrees(msg.steering_angle)
        self._commanded_speed_kmh = msg.speed

    def _on_encoder(self, msg):
        self._encoder_deg = float(msg.data)
        self._last_encoder_s = time.monotonic()

    def _throttle_byte(self):
        # Unverified linear mapping -- see MAX_SPEED_KMH's comment above.
        magnitude = min(abs(self._commanded_speed_kmh) / MAX_SPEED_KMH, 1.0) * 50.0
        reverse = 1 if self._commanded_speed_kmh < 0 else 0
        throttle = int(round(THROTTLE_NEUTRAL + magnitude))
        return max(0, min(100, throttle)), reverse

    def _control_tick(self):
        now = time.monotonic()

        if self._last_encoder_s is None or now - self._last_encoder_s > self._encoder_timeout_s:
            # No fresh angle feedback -- actively command neutral+stop rather
            # than silently skip a tick, which would leave whatever relay
            # state was last sent (possibly mid-turn) engaged on real hardware
            # with nothing correcting it.
            self._steering.reset()
            self.get_logger().warn(
                'No /steering/angle within {}s -- forcing neutral+stop.'.format(self._encoder_timeout_s),
                throttle_duration_sec=2.0)
            if self._ser is not None and (now - self._last_serial_time) >= MIN_SERIAL_INTERVAL_S:
                self._last_serial_time = now
                cmd = build_serial_command(b_throttle=THROTTLE_NEUTRAL, d_steering=50)
                try:
                    self._ser.write(cmd.encode())
                except Exception as e:
                    self.get_logger().warn(f'Serial write failed: {e}')
            return

        relay = self._steering.update(self._target_deg, self._encoder_deg, now)
        throttle, reverse = self._throttle_byte()

        if (now - self._last_serial_time) < MIN_SERIAL_INTERVAL_S:
            return
        self._last_serial_time = now

        cmd = build_serial_command(b_throttle=throttle, d_steering=relay, j_reverse=reverse)
        if self._ser is not None:
            try:
                self._ser.write(cmd.encode())
                while self._ser.readline():
                    pass  # drain any response; not parsed (see module docstring)
            except Exception as e:
                self.get_logger().warn(f'Serial write failed: {e}')

    def destroy_node(self):
        if self._ser is not None and self._ser.is_open:
            try:
                self._ser.write(build_serial_command(b_throttle=THROTTLE_NEUTRAL, d_steering=50, i_brake=1).encode())
                time.sleep(0.05)
            finally:
                self._ser.close()
                self.get_logger().info('Serial port closed, vehicle commanded to neutral+brake.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
