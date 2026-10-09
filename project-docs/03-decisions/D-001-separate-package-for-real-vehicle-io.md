# D-001 · A separate package for real-vehicle I/O

- **Date:** 2026-09-09
- **Status:** Accepted

## Context
Commands from ROS needed converting to the cart's serial protocol, with
steering closed over an encoder. tesla_sim was being rewritten to steer like
the same relay.

## Decision
Create `vehicle_bridge`, holding the real serial bridge and the shared relay
controller. tesla_sim depends on vehicle_bridge, not the other way round.

## Alternatives considered
- **Fold it into tesla_sim:** rejected. Real hardware I/O has no reason to
  depend on Webots, and the cart's computer shouldn't need the simulator.
