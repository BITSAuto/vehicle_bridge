#!/usr/bin/env python3
"""Read the steering encoder MCU over USB serial and publish /steering/angle.

The rotary encoder on the steering column is an incremental encoder read by a
separate microcontroller, which streams its running count over its own USB
serial port (one integer per line by default; see encoder.py). This node turns
that count into the /steering/angle topic serial_bridge_node closes its relay
steering loop over -- the same topic tesla_sim publishes from its simulated
PositionSensor.

Publishes:
  /steering/angle          std_msgs/Float32  degrees, +right/-left
  /steering/encoder_count  std_msgs/Int32    raw count, for calibration
Services:
  ~/zero                   std_srvs/Trigger  treat the current count as straight ahead

Zeroing: an incremental count is relative to wherever the MCU powered up, and
opening the port usually resets an Arduino-class MCU (DTR toggles), so the
origin moves on every (re)connect. With zero_on_start=true the first complete
reading after each connect is taken as straight ahead -- park with the wheels
straight before starting, or call ~/zero once they are. Until a zero exists,
nothing is published, which makes serial_bridge_node hold neutral+stop.
"""
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32
from std_srvs.srv import Trigger

from vehicle_bridge.encoder import DEFAULT_LINE_REGEX, EncoderAngleConverter

try:
    import serial
except ImportError:
    serial = None

POLL_S = 0.005            # 200 Hz -- well above any sane MCU line rate
RECONNECT_S = 1.0
NO_DATA_WARN_S = 1.0
MAX_LINE_BYTES = 256      # guard against a stream with no newlines


class EncoderNode(Node):
    def __init__(self):
        super().__init__('encoder_node')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('line_regex', DEFAULT_LINE_REGEX)
        self.declare_parameter('degrees_per_count', 0.0)
        self.declare_parameter('invert', False)
        self.declare_parameter('offset_deg', 0.0)
        self.declare_parameter('zero_on_start', True)

        self._port = self.get_parameter('serial_port').value
        self._baud = int(self.get_parameter('baud').value)
        self._zero_on_start = bool(self.get_parameter('zero_on_start').value)
        degrees_per_count = float(self.get_parameter('degrees_per_count').value)
        if degrees_per_count <= 0.0:
            # No safe default: a wrong scale makes the steering loop drive past
            # its target toward the mechanical lock. Refuse to publish instead.
            raise ValueError(
                'degrees_per_count must be set to a positive, calibrated value '
                '(see the README calibration procedure)')
        self._converter = EncoderAngleConverter(
            degrees_per_count,
            invert=bool(self.get_parameter('invert').value),
            offset_deg=float(self.get_parameter('offset_deg').value),
            line_regex=self.get_parameter('line_regex').value)

        self._angle_pub = self.create_publisher(Float32, '/steering/angle', 10)
        self._count_pub = self.create_publisher(Int32, '/steering/encoder_count', 10)
        self.create_service(Trigger, '~/zero', self._on_zero)

        self._ser = None
        self._buf = b''
        self._skip_partial = True
        self._last_count = None
        self._last_data_s = None
        self._next_connect_s = 0.0

        if serial is None:
            raise RuntimeError('pyserial not installed')

        self.create_timer(POLL_S, self._poll)
        self.get_logger().info(
            f'Encoder node: {self._port} @ {self._baud}, {degrees_per_count} deg/count, '
            f'zero_on_start={self._zero_on_start}')

    def _connect(self):
        try:
            self._ser = serial.serial_for_url(self._port, baudrate=self._baud, timeout=0)
        except Exception as e:
            self.get_logger().warn(f'Cannot open {self._port}: {e}', throttle_duration_sec=5.0)
            self._ser = None
            return
        self._buf = b''
        self._skip_partial = True  # first line may start mid-number
        self._last_count = None
        self._last_data_s = time.monotonic()
        if self._zero_on_start:
            self._converter.set_zero(None)
        self.get_logger().info(f'Opened {self._port}.')

    def _disconnect(self, reason):
        self.get_logger().error(f'Encoder serial lost ({reason}); reconnecting.')
        try:
            self._ser.close()
        except Exception:
            pass
        self._ser = None
        # The MCU likely reset, so the old zero no longer refers to straight ahead.
        self._converter.set_zero(None)
        self._next_connect_s = time.monotonic() + RECONNECT_S

    def _poll(self):
        now = time.monotonic()
        if self._ser is None:
            if now >= self._next_connect_s:
                self._next_connect_s = now + RECONNECT_S
                self._connect()
            return

        try:
            data = self._ser.read(self._ser.in_waiting or 1)
        except Exception as e:
            self._disconnect(e)
            return

        if data:
            self._buf += data
            *lines, self._buf = self._buf.split(b'\n')
            if len(self._buf) > MAX_LINE_BYTES:
                self.get_logger().warn('Encoder line too long; discarding buffer.', throttle_duration_sec=5.0)
                self._buf = b''
            for raw in lines:
                if self._skip_partial:
                    self._skip_partial = False
                    continue
                self._handle_line(raw.decode('ascii', errors='replace').strip(), now)
        elif now - self._last_data_s > NO_DATA_WARN_S:
            self.get_logger().warn(
                f'No encoder data for {now - self._last_data_s:.1f}s.', throttle_duration_sec=2.0)

    def _handle_line(self, line, now):
        count = self._converter.parse_count(line)
        if count is None:
            if line:
                self.get_logger().debug(f'Ignoring encoder line: {line!r}')
            return
        self._last_count = count
        self._last_data_s = now
        self._count_pub.publish(Int32(data=count))

        if self._converter.zero_count is None:
            if not self._zero_on_start:
                self.get_logger().warn(
                    'No zero set -- call ~/zero with the wheels straight.', throttle_duration_sec=5.0)
                return
            self._converter.set_zero(count)
            self.get_logger().warn(f'Zeroed at count {count}: assuming wheels are straight now.')
        self._angle_pub.publish(Float32(data=float(self._converter.to_degrees(count))))

    def _on_zero(self, request, response):
        if self._last_count is None:
            response.success = False
            response.message = 'no encoder reading yet'
        else:
            self._converter.set_zero(self._last_count)
            response.success = True
            response.message = f'zeroed at count {self._last_count}'
            self.get_logger().info(response.message)
        return response

    def destroy_node(self):
        if self._ser is not None:
            self._ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = EncoderNode()
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
