# Running on the cart

```bash
ros2 launch vehicle_bridge vehicle_bridge.launch.py serial_port:=/dev/ttyUSB0 encoder_port:=/dev/ttyACM0
```
- Prefer `/dev/serial/by-id/...` paths so the two boards can't swap.
- **Wheels straight at launch**: `encoder_node` zeroes on its first reading.
  Re-zero later with `ros2 service call /encoder_node/zero std_srvs/srv/Trigger`.
- Pass `encoder:=false` if something else publishes `/steering/angle`;
  `dry_run:=true` to never touch the drive-by-wire port.
- Only one vehicle per ROS domain: never run tesla_sim on the same domain.

## Commanding it
```bash
ros2 topic pub -r 10 /cmd_ackermann ackermann_msgs/msg/AckermannDrive "{speed: 5.0, steering_angle: 0.0}"
ros2 topic pub --once /vehicle/emergency_brake std_msgs/msg/Bool "{data: true}"   # emergencies only
```
- Speed is km/h; 0 coasts. Steering is radians, + = right.
- If `/cmd_ackermann` stops for 0.5 s (`cmd_timeout_s`), the bridge coasts:
  neutral throttle, steering stopped, no brake ([D-013](../03-decisions/D-013-command-timeout-coasts.md)).
  A one-shot `ros2 topic pub --once` therefore only acts for 0.5 s: publish
  with `-r 10`.
- Steering targets are clamped to ±15° (`max_steer_deg`).
- **Stopping the bridge brakes the cart** (one brake frame at shutdown).
  Bring it to rest by coasting first.
