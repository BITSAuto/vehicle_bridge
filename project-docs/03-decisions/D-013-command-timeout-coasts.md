# D-013 · On a lost driver, coast with the steering stopped; clamp targets

- **Date:** 2026-10-15
- **Status:** Accepted (resolves [Q-006](../06-open-questions/Q-006-no-command-timeout.md), [Q-007](../06-open-questions/Q-007-no-steering-clamp.md))

- `cmd_timeout_s` (0.5 s): no `/cmd_ackermann` for that long → neutral throttle
  and steering relay stop (the wheels stay where they are). Never the brake
  ([D-009](D-009-emergency-brake-topic-is-the-only-brake.md)): a dead
  publisher is not an emergency, and the brake can damage the cart. An
  emergency brake already engaged stays engaged.
- Before any command has arrived the bridge sends the same neutral + stop.
- `max_steer_deg` (15°): steering targets are clamped at the bridge, so a
  manual `ros2 topic pub` cannot ask for more than the planner does.
