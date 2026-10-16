# D-012 · Compensate the steering actuation delay; learn the actuator

- **Date:** 2026-10-15
- **Status:** Accepted

**Context.** The owner reports ~100–150 ms from a command to the steering
starting to move, and about the same for a stop. The 2026-09-09 controller
stopped when the *encoder* reached the target, so the wheels ran on for the
stop delay: about 12.9 °/s × 0.15 s ≈ 2° past every target, more than the
1.0° restart threshold, so it pulsed back and hunted. Against a simulated
actuator with 0.12 s each way it switched the relay 159 times for 10 target
changes (19 with this decision).

**Decision.** A Smith predictor on the command history, with the start delay,
stop delay and wheel speed fitted online from the encoder
([relay-steering-controller.md](../02-architecture/relay-steering-controller.md)).
Not a configured delay: the real values are unmeasured, may differ between
start and stop, and change with load. Ported from road_follower's
`RelayDriver`, where it was developed against a closed-loop harness.

**Consequences.** Needs numpy. Pulses are never shorter than `d_start − d_stop`;
the deadband widens with run-on; a stall becomes a lock limit until restart.
