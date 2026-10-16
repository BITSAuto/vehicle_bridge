# 2026-10-15 · Steering overrun, command timeout, clamp

**Who:** with Claude Code
**Branch / PR:** `fix/relay-overrun` (no PR yet)
**Goal:** make the bridge safe to power: stop steering overrun with the cart's
~100–150 ms actuation delay, add the command timeout and steering clamp.

## What was done
- Relay controller rewritten with a Smith predictor and an online fit of the
  start delay, stop delay and wheel speed ([D-012](../03-decisions/D-012-compensate-steering-actuation-delay.md),
  [relay-steering-controller.md](../02-architecture/relay-steering-controller.md)); stall → lock limit.
- `cmd_timeout_s` and `max_steer_deg` in `serial_bridge_node` ([D-013](../03-decisions/D-013-command-timeout-coasts.md)); Q-006, Q-007 resolved.
- Blocking `readline()` drain replaced (M-06); tick 25 → 10 ms (M-07).
- `tools/fake_cart.py`; `test/test_relay_steering.py` (9 tests).
- tesla_sim: relay timed on simulation time (M-08) — separate change in that repo.

## Results
[relay-overrun.md](../09-testing-and-results/relay-overrun.md): 159 → 19 relay
switches for ten target changes at 0.12 s each way; bridge vs fake cart settles
without overshoot, clamps, times out to coast.

## Problems hit
- The first fit let a delay drift after long moves whose start lay before the
  fit window: delays are now only updated when the window pins them down.
- A stall against the lock taught the fit a slow actuator: the history is now
  dropped on a stall.

## Next
Encoder and serial-command unit tests; then the powered checklist
([first-powered-test.md](../08-guides/first-powered-test.md)).
