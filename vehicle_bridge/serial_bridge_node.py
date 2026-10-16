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

Throttle is open-loop and never brakes: speed 0 sends the neutral throttle
byte (50), so the cart coasts to a stop on friction. The cart's brake stops it
instantly and can damage it, so the only way to apply it is
/vehicle/emergency_brake (std_msgs/Bool, True = brake held). Lights and
indicators have no ROS input yet (see README). /steering/angle comes from encoder_node, which reads the steering
encoder's own MCU over a separate USB serial port. If it stops arriving for
encoder_timeout_s, the bridge treats feedback as lost and holds neutral+stop.
If /cmd_ackermann stops arriving for cmd_timeout_s (a crashed or disconnected
driver), it sends neutral throttle and stops the steering where it is -- it
coasts, it never brakes. Steering targets are clamped to +/-max_steer_deg.
"""
import math
import time

import rclpy
from ackermann_msgs.msg import AckermannDrive
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

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
CONTROL_TICK_S = 0.010         # 100 Hz, so a frame goes out as soon as MIN_SERIAL_INTERVAL_S allows (~33/s);
                               # at 25 ms every other tick was skipped and frames went out every 50 ms


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('dry_run', False)
        self.declare_parameter('encoder_timeout_s', 0.5)
        self.declare_parameter('cmd_timeout_s', 0.5)
        self.declare_parameter('max_steer_deg', 15.0)
        port = self.get_parameter('serial_port').value
        dry_run = self.get_parameter('dry_run').value
        self._encoder_timeout_s = float(self.get_parameter('encoder_timeout_s').value)
        self._cmd_timeout_s = float(self.get_parameter('cmd_timeout_s').value)
        self._max_steer_deg = float(self.get_parameter('max_steer_deg').value)

        self._steering = RelaySteeringController()
        self._target_deg = 0.0
        self._encoder_deg = 0.0
        self._last_encoder_s = None
        self._commanded_speed_kmh = 0.0
        self._last_cmd_s = None
        self._limits_logged = {}
        self._emergency_brake = False
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
        self.create_subscription(Bool, 'vehicle/emergency_brake', self._on_emergency_brake, 10)

        self._timer = self.create_timer(CONTROL_TICK_S, self._control_tick)

        self.get_logger().info(
            'Serial bridge ready: /cmd_ackermann in, relay steering closed over '
            '/steering/angle, MAX_SPEED_KMH={} (unverified, see README)'.format(MAX_SPEED_KMH))

    def _on_cmd_ackermann(self, msg):
        target = math.degrees(msg.steering_angle)
        self._target_deg = max(-self._max_steer_deg, min(self._max_steer_deg, target))
        self._commanded_speed_kmh = msg.speed
        self._last_cmd_s = time.monotonic()

    def _on_emergency_brake(self, msg):
        if msg.data and not self._emergency_brake:
            self.get_logger().warn('EMERGENCY BRAKE ENGAGED')
        elif not msg.data and self._emergency_brake:
            self.get_logger().info('Emergency brake released')
        self._emergency_brake = bool(msg.data)

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
        if self._steering.fits:
            st = self._steering
            self.get_logger().info(f'Steering actuator learned: start {st.d_start * 1000:.0f} ms, '
                                   f'stop {st.d_stop * 1000:.0f} ms, speed x{st.gain:.2f}',
                                   throttle_duration_sec=10.0)

        if self._last_encoder_s is None or now - self._last_encoder_s > self._encoder_timeout_s:
            # No fresh angle feedback -- actively command neutral+stop rather
            # than silently skip a tick, which would leave whatever relay
            # state was last sent (possibly mid-turn) engaged on real hardware
            # with nothing correcting it.
            self._steering.reset()
            self.get_logger().warn(
                'No /steering/angle within {}s -- forcing neutral+stop.'.format(self._encoder_timeout_s),
                throttle_duration_sec=2.0)
            self._send(now, THROTTLE_NEUTRAL, 50, 0)
            return

        if self._last_cmd_s is None or now - self._last_cmd_s > self._cmd_timeout_s:
            # No driver: coast and stop the steering where it is (never brake).
            self._steering.reset()
            if self._last_cmd_s is not None:
                self.get_logger().warn(
                    'No /cmd_ackermann within {}s -- coasting, steering stopped.'.format(self._cmd_timeout_s),
                    throttle_duration_sec=2.0)
            self._send(now, THROTTLE_NEUTRAL, 50, 0)
            return

        relay = self._steering.update(self._target_deg, self._encoder_deg, now)
        for d, lim in self._steering.limits.items():
            if self._limits_logged.get(d) != lim:
                self._limits_logged[d] = lim
                self.get_logger().warn(f'Steering stalled at {lim:+.1f} deg: treating it as the lock until restart.')
        throttle, reverse = self._throttle_byte()
        if self._emergency_brake:
            throttle, reverse = THROTTLE_NEUTRAL, 0      # never drive against the brake

        self._send(now, throttle, relay, reverse)

    def _send(self, now, throttle, relay, reverse):
        if self._ser is None or (now - self._last_serial_time) < MIN_SERIAL_INTERVAL_S:
            return
        self._last_serial_time = now
        cmd = build_serial_command(b_throttle=throttle, d_steering=relay, j_reverse=reverse,
                                   i_brake=int(self._emergency_brake))
        try:
            self._ser.write(cmd.encode())
            # Drain replies without waiting: a blocking readline() loop stalled the
            # tick >= 50 ms every time, and forever if the board streams replies --
            # leaving the last relay state (possibly mid-turn) engaged.
            if self._ser.in_waiting:
                self._ser.read(self._ser.in_waiting)
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
