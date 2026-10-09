# D-009 · `/vehicle/emergency_brake` is the only way to brake; normal driving coasts

- **Date:** 2026-10-08
- **Status:** Accepted ([PR #1](https://github.com/BITSAuto/vehicle_bridge/pull/1), merged via PR #2)

## Context
The cart's brake can't modulate: it stops the cart instantly and can damage
it. The team drives at 5 km/h with throttle only and slows by coasting.
Previously the brake was only sent on shutdown, and the braking throttle range
(`<50`) was reachable in principle.

## Decision
- A `std_msgs/Bool` topic `/vehicle/emergency_brake`: `true` sends `I1` with
  neutral throttle on every tick until `false`.
- Speed 0 always sends neutral (50); the bridge never sends `<50`.
- tesla_sim has the same topic with the same semantics.

## Consequences
- Only `cart_driver`'s safety monitor publishes it.
- Engage and release are logged from separate calls (an rclpy restriction;
  [bridge-bugs.md](../07-bugs-and-lessons/bridge-bugs.md)).
