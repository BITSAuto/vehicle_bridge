# Relay steering controller

`RelaySteeringController.update(target_deg, encoder_deg, now_s) -> relay`,
called once per control tick (every 10 ms in the bridge, every Webots step in
tesla_sim). *Rewritten 2026-10-15 ([D-012](../03-decisions/D-012-compensate-steering-actuation-delay.md));
the plain hysteresis version it replaced is described in the 2026-09-09 worklog.*

## What it does each tick
1. **Predict.** `predicted = encoder + committed_deg(now)`: the motion already
   commanded but not yet visible, from the command history and the learned
   actuator. This is what a stop sent now would still let happen.
2. **Decide on the predicted angle.**
   - STOP → RIGHT/LEFT when `target − predicted` exceeds ±1.0° (or ¾ of the
     smallest step a pulse can make, if larger) and the last state has been
     held for `min_hold_s`.
   - RIGHT/LEFT → STOP when the predicted angle is within 0.5° (or 0.35 of the
     smallest step) of the target, or the move has **stalled**.
   - No direct LEFT ↔ RIGHT: always through STOP.
3. **Learn** (once a second). Fit, over the last 5 s of commands and encoder
   readings, the actuator that explains them: `d_start` (move command → wheels
   moving), `d_stop` (stop command → wheels stopped; run-on if larger), `gain`
   (wheel speed / `RATE_DEG_S`). A delay is only updated when the window pins
   it down (moving it ±50 ms makes the fit clearly worse).

## Derived limits
- `min_hold_s = max(35 ms, d_start − d_stop + 35 ms)`: a pulse shorter than
  `d_start − d_stop` moves nothing, so none is ever sent.
- `min_step_deg`: the smallest movement a pulse can make; the deadband is
  widened to it so run-on cannot force a pulse back the other way.
- **Stall / lock:** a move with < 0.2° of progress for `d_start + 0.5 s` is
  stopped, its angle becomes a limit for that direction until `reset()`, and
  the history is dropped so the fit doesn't learn from motion that didn't
  happen.

`INITIAL_DELAY_S = 0.12` (the owner's ~100–150 ms) is used until the first fit.
`now_s` must be on the same clock as the encoder: wall clock on the cart,
simulation time in tesla_sim.

**Shared with tesla_sim** ([D-003](../03-decisions/D-003-share-the-relay-controller-with-tesla-sim.md)):
the sim feeds it its own rack angle, which has no delay, so there it learns
≈0 ms and behaves like the plain controller.
