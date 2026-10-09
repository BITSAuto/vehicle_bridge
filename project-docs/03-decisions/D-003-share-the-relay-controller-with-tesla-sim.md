# D-003 · Share `RelaySteeringController` with tesla_sim

- **Date:** 2026-09-09
- **Status:** Accepted

## Context
The owner wanted the sim to "simulate how the vehicle actually works", and
the bridge to convert Ackermann commands into 49/50/51 "taking into account
the readings of a rotary encoder".

## Decision
One `RelaySteeringController` class, imported by both
`serial_bridge_node` (real encoder) and tesla_sim's driver (simulated rack
angle).

## Alternatives considered
- **Separate implementations in sim and bridge:** rejected; they would drift,
  and parity would need re-testing after every change.
- **Continuous steering in the sim:** rejected; the sim would be easier than
  the cart, so controllers tuned there wouldn't transfer.

## Consequences
- Parity is guaranteed by the import graph (confirmed working by a dry-run
  against the live sim, [09-testing-and-results/sim-parity-dry-run.md](../09-testing-and-results/sim-parity-dry-run.md)).
- Any change here changes both the sim and the cart.
- Modelled on the newer closed-loop `rotary_encoder_driver.py`
  `MotorController` (encoder feedback, hysteresis), not on `cart_contorller`'s
  older open-loop pulse counting.
