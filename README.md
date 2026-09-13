# vehicle_bridge

ROS 2 to serial drive-by-wire bridge for the real vehicle, plus the shared
steering-relay controller that lets `tesla_sim` model the same hardware
behavior in simulation. The point of both living in one package: the same
`/cmd_ackermann` command stream, and the same steering-relay logic, drive
either the simulator or the real vehicle -- swapping which one you're talking
to is a launch-file choice, not a different control interface.

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

## Running on the real vehicle

```bash
ros2 launch vehicle_bridge vehicle_bridge.launch.py serial_port:=/dev/ttyUSB0
```

Requires:
- Something already publishing `/steering/angle` (`std_msgs/Float32`, degrees,
  `+right`/`-left`) from the real rotary encoder. This bridge does **not**
  read that value from the Arduino's serial response -- it subscribes to the
  topic directly, the same way `rotary_encoder_driver.py --cart` already
  does. If nothing publishes it yet, the bridge holds the relay at neutral
  and logs a warning every 2s rather than driving blind.
- Read/write permission on the serial port (`sudo usermod -a -G dialout $USER`,
  then re-login, is the usual fix if you get a permissions error).

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
- Brake, lights, horn, indicators (`I`, `E`, `F`, `G`, `H`) have no ROS input
  wired to them at all yet -- always sent as `0`.

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
