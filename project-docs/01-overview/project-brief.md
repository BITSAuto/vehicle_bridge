# Project brief

## What it is
The ROS 2 package that drives the **real BITSAuto cart**. It turns
`/cmd_ackermann` into the cart's serial drive-by-wire protocol, closes the
steering loop over a relay, reads the steering encoder, and provides the one
input that may brake (`/vehicle/emergency_brake`). Package `vehicle_bridge`,
`ament_python`, repository
[BITSAuto/vehicle_bridge](https://github.com/BITSAuto/vehicle_bridge).

It also owns `RelaySteeringController`, which `tesla_sim` imports so the
simulator's steering behaves exactly like the cart's.

## Why it exists
- **The cart has no proportional steering.** Its steering motor is a
  three-state relay (left / stop / right) that keeps turning until told to
  stop. Angle control has to be built in software from an encoder reading.
- **One copy of the protocol.** Before this package, the same
  `build_serial_command` function was copy-pasted in three scripts across
  `road_segmentation` and `cart_contorller`. It now lives here once.
- **Sim/real parity.** The same `/cmd_ackermann` stream and the same steering
  logic drive either the simulator or the cart; which one is a launch choice.

## Nodes
- `serial_bridge_node`: `/cmd_ackermann` + `/steering/angle` +
  `/vehicle/emergency_brake` → serial commands at 40 Hz.
- `encoder_node`: reads the steering encoder's microcontroller over USB serial
  → `/steering/angle` (degrees, + = right).

## How much is verified on the real cart
Very little so far. The protocol and the steering timing are verified from
existing scripts and docs; the encoder path is tested against a fake
microcontroller only; the throttle scaling, reverse and the encoder's real
format and scale are **unverified**. Treat the first powered test as a
calibration session ([08-guides/first-powered-test.md](../08-guides/first-powered-test.md)).

## Rules this package enforces
- Normal driving never brakes: speed 0 sends neutral throttle (coast); the
  braking throttle range (`<50`) is never sent.
- The brake flag is set only while `/vehicle/emergency_brake` is `true`, and
  once on shutdown as a fail-safe.
- With no fresh steering angle (0.5 s), it forces neutral throttle and relay
  stop rather than steering blind.
