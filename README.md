# vehicle_bridge

ROS 2 to serial drive-by-wire bridge for the real vehicle, plus the shared
steering-relay controller that lets `tesla_sim` model the same hardware
behavior in simulation. The point of both living in one package: the same
`/cmd_ackermann` command stream, and the same steering-relay logic, drive
either the simulator or the real vehicle -- swapping which one you're talking
to is a launch-file choice, not a different control interface.

Design history, decisions, verified facts, open questions, known bugs and
status are in the [project docs](project-docs/README.md). Read them before
changing anything, and update them with every change.

## Why this needs to exist: the vehicle has no proportional steering input

The real vehicle steers via a three-state relay, not a servo:

| Serial value (`D` field) | Meaning |
| --- | --- |
| `49` | turn left, continuously |
| `50` | stop |
| `51` | turn right, continuously |

The relay **does not stop on its own** -- "the real cart motor has infinite
run-on and does not stop by itself until this `50` command is explicitly
received" (verified directly in `cart_controller/README.md`). There is no
"set steering to X degrees" primitive anywhere in the protocol. Closed-loop
angle control has to be built entirely in software: read a target angle, read
a real rotary-encoder angle back, and decide whether to hold the relay
left/right/stopped -- which is exactly what
`road_segmentation/rotary_encoder_driver.py`'s hysteresis controller already
does for its own vision-based steering. `relay_steering.py` factors that same
approach into a reusable class instead of it being written a third time.

## Modules

| File | What it does |
| --- | --- |
| `serial_command.py` | The wire protocol: `build_serial_command(...)` -> `*A...J...#`. Single source of truth -- this exact function existed as three separate copy-pasted versions before this package (`drivebywire.py`, `cart_controller/controller.py`, `rotary_encoder_driver.py`), all byte-for-byte identical. |
| `relay_steering.py` | `RelaySteeringController`: `(target_deg, encoder_deg, now_s) -> relay state`. Used identically by `serial_bridge_node.py` (real encoder) and `tesla_sim/tesla_driver.py` (Webots `PositionSensor`). |
| `serial_bridge_node.py` | The real-hardware ROS 2 node: `/cmd_ackermann` in, serial out. |
| `encoder.py` | `EncoderAngleConverter`: parses a count from one encoder-MCU line and converts it to degrees. No ROS/serial dependency. |
| `encoder_node.py` | Reads the steering encoder's MCU over its own USB serial port and publishes `/steering/angle`. |

## Running on the real vehicle

```bash
ros2 launch vehicle_bridge vehicle_bridge.launch.py \
  serial_port:=/dev/ttyUSB0 encoder_port:=/dev/ttyACM0
```

This starts two nodes:
- `encoder_node` reads the steering encoder MCU and publishes `/steering/angle`
  (`std_msgs/Float32`, degrees, `+right`/`-left`) plus the raw count on
  `/steering/encoder_count` (`std_msgs/Int32`). Pass `encoder:=false` if
  something else publishes `/steering/angle`.
- `serial_bridge_node` closes the relay steering loop over `/steering/angle`.
  If it has never received an angle, or the last one is older than
  `encoder_timeout_s` (0.5 s), it holds neutral throttle + steering stop and
  logs a warning every 2 s rather than driving blind.

Read/write permission on both serial ports is required
(`sudo usermod -a -G dialout $USER`, then re-login, is the usual fix).

### Steering encoder

The encoder is incremental and is read by a separate MCU that streams its
running count over USB serial. Assumed MCU output: one count per line,
e.g. `1234\r\n`, at 115200 baud. If the firmware prints something else
(e.g. `ENC:1234`), set the `line_regex` parameter; its first capture group
must be the integer count. Lines that don't match are ignored, and the first
line after connecting is always dropped because it may start mid-number.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `serial_port` | `/dev/ttyACM0` | Encoder MCU device (`encoder_port` in the launch file) |
| `baud` | `115200` | Must match the MCU firmware |
| `line_regex` | `(-?\d+)` | Extracts the count from each line |
| `degrees_per_count` | `0.0` | **Required**, set in `config/encoder.yaml`. The node refuses to start without a positive value, because a wrong scale drives the steering past its target toward the lock. |
| `invert` | `false` | Flip sign so that turning right is positive |
| `offset_deg` | `0.0` | Added after scaling, for a zero that isn't exactly straight |
| `zero_on_start` | `true` | Treat the first reading after each connect as straight ahead |

**Zeroing.** An incremental count only means something relative to its
power-up position, and opening the port usually resets an Arduino-class MCU,
so the origin moves on every connect. With `zero_on_start:=true`, park with
the wheels straight before launching. To re-zero later with the wheels
straight:

```bash
ros2 service call /encoder_node/zero std_srvs/srv/Trigger
```

If the port drops, the node reconnects every second and re-zeroes on the
first reading (or, with `zero_on_start:=false`, publishes nothing until
`~/zero` is called). Nothing is published while no zero exists, so the bridge
holds neutral.

**Calibrating `degrees_per_count`.** Calibration lives in
`config/encoder.yaml` (`degrees_per_count`, `invert`, `offset_deg`), which the
launch file loads by default. With a `--symlink-install` build, the installed
copy is a symlink back to the source file, so edits take effect on the next
launch without rebuilding. Commit the file so the calibration travels with
the repo, or pass a vehicle-specific copy with `encoder_config:=/path/to.yaml`.

Procedure (vehicle stationary, drive power off, wheels off the ground if
possible):
1. Temporarily set `degrees_per_count: 1.0` so the node starts.
2. Straighten the wheels and launch with `dry_run:=true`, which zeroes the
   count there.
3. Run `ros2 topic echo /steering/encoder_count`. Steer to a measured angle
   to the right and note the count, then do the same to the left. Full lock
   is convenient, but measure the actual road-wheel angle at lock rather
   than assuming it. To measure, hold a straightedge flat against the tyre
   sidewall. Measure how far it moves sideways (`d`) at a distance `L` along
   it, compared with the straight-ahead position. The angle is
   `atan(d / L)`.
4. Compute
   `degrees_per_count = (right_angle + left_angle) / |right_count - left_count|`.
   Using both sides averages out a slightly off-centre zero.
5. Write the value into `config/encoder.yaml`, relaunch, and check that
   `/steering/angle` reads about the measured angles at the same positions.
   If right reads negative, set `invert: true`.

`dry_run:=true` computes relay decisions and logs warnings normally but never
opens or writes to the serial port -- useful for testing the bridge against a
live `/cmd_ackermann` + `/steering/angle` stream (including from `tesla_sim`
itself, see below) with no hardware attached.

On shutdown (`Ctrl-C` or node death), the bridge sends one final
neutral-throttle, stop-steering, brake-on command before closing the port.

## What's calibrated against real hardware, and what isn't

**Verified directly against `cart_controller/README.md` and the three
protocol scripts:**
- The wire format itself.
- `MIN_HOLD_S = 0.035` and `DEG_PER_MIN_HOLD = 0.45` (the motor's ~30ms
  reaction time and per-pulse angular movement) -- corroborated
  independently by `rotary_encoder_driver.py`'s own `SIM_DEG_PER_SEC = 12.0`
  fallback constant, which works out to the same ~12.86 deg/s a different way.
- Throttle byte semantics: `50` = neutral/coast, `>50` = forward,
  `<50` = braking (from `rotary_encoder_driver.py`'s own header comment).

**Not verified -- flagged in code, don't treat as fact:**
- `MAX_SPEED_KMH = 7.0` (the speed-to-throttle-byte scale factor). Borrowed
  from `cart_controller`'s own constant of the same name as the best
  available reference; no script anywhere in this workspace actually
  calibrates a throttle byte against a measured real speed.
- The reverse-gear mapping (negative commanded speed -> `j_reverse=1` +
  forward-range throttle magnitude). No script read anywhere exercises the
  `j_reverse` flag or the `<50` braking range at all -- this bridge's
  interpretation is a reasonable reading of the protocol, not something
  confirmed against real hardware behavior.
- Lights, horn and indicators (`E`, `F`, `G`, `H`) have no ROS input wired to
  them yet -- always sent as `0`.

### Braking: emergency only

The cart's brake (`I`) can't modulate: it stops the vehicle instantly and can
damage it. Normal driving therefore never brakes. A commanded speed of 0 sends
the neutral throttle byte (`50`), and the cart **coasts** to a stop on
friction; the bridge never sends the `<50` braking range.

The brake has exactly one input: `/vehicle/emergency_brake` (`std_msgs/Bool`).
`True` sends `I1` with neutral throttle on every tick until `False` arrives.
It is meant for a safety monitor's last-resort stop, not for speed control.
`tesla_sim` exposes the same topic with the same semantics (instant stop). The
bridge also sends one brake command when it shuts down, as a fail-safe.

Before trusting this on a real, powered vehicle: verify the throttle mapping
at low speed first, and confirm reverse actually engages reverse rather than
regenerative braking.

## Using this with tesla_sim (the "digital clone" side)

`tesla_sim/tesla_driver.py` imports `RelaySteeringController` from this
package and applies the exact same relay/hysteresis logic to a Webots
steering motor, using a Webots `PositionSensor` as the encoder. It publishes
`/steering/angle` and `/bitsauto/speed` under these same global topic names
(not namespaced under `/vehicle/...` the way tesla_sim's other topics are) --
deliberately, so that a control script written against the real vehicle can
run against the simulator with zero code changes, only a different launch
file. See `src/tesla_sim/README.md`'s Sensing and Troubleshooting sections
for what tesla_sim publishes and how its relay steering behaves.
