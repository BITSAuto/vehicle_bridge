# Interfaces

## serial_bridge_node

| Direction | Topic | Type | Notes |
| --- | --- | --- | --- |
| in | `/cmd_ackermann` | `ackermann_msgs/AckermannDrive` | `speed` km/h (0 = coast, negative = reverse), `steering_angle` rad, + = right |
| in | `/steering/angle` | `std_msgs/Float32` | degrees, + = right. Required: without a fresh value the bridge holds neutral + stop |
| in | `/vehicle/emergency_brake` | `std_msgs/Bool` | `true` sets the brake flag with neutral throttle on every tick until `false` |
| out | serial | — | one frame per tick, at most every 30 ms |

| Parameter | Default | Meaning |
| --- | --- | --- |
| `serial_port` | `/dev/ttyUSB0` | drive-by-wire board |
| `dry_run` | `false` | compute and log, never touch the port |
| `encoder_timeout_s` | `0.5` | steering angle older than this is "lost" |

Constants in code: `CONTROL_TICK_S = 0.025` (40 Hz), `MIN_SERIAL_INTERVAL_S
= 0.030`, `MAX_SPEED_KMH = 7.0` (unverified throttle scale).

## encoder_node

| Direction | Name | Type | Notes |
| --- | --- | --- | --- |
| out | `/steering/angle` | `std_msgs/Float32` | degrees, + = right; nothing is published until a zero exists |
| out | `/steering/encoder_count` | `std_msgs/Int32` | raw count |
| service | `~/zero` (`/encoder_node/zero`) | `std_srvs/Trigger` | treat the current count as straight ahead |

| Parameter | Default | Meaning |
| --- | --- | --- |
| `serial_port` | `/dev/ttyACM0` | encoder MCU |
| `baud` | `115200` | must match the firmware |
| `line_regex` | `(-?\d+)` | first capture group is the count |
| `degrees_per_count` | `0.0` | **required**, positive; set in `config/encoder.yaml` (0.006 provisional) |
| `invert` | `false` | flip the sign so right is positive |
| `offset_deg` | `0.0` | added after scaling |
| `zero_on_start` | `true` | zero on the first reading after each connect |

## Launch arguments (`vehicle_bridge.launch.py`)

| Argument | Default |
| --- | --- |
| `serial_port` | `/dev/ttyUSB0` |
| `dry_run` | `false` |
| `encoder` | `true` (start `encoder_node`) |
| `encoder_port` | `/dev/ttyACM0` |
| `encoder_baud` | `115200` |
| `encoder_config` | this package's `config/encoder.yaml` |
