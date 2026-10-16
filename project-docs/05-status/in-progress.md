# In progress

## `fix/relay-overrun` (2026-10-15, not yet a PR)
- Delay-compensating relay controller that learns the actuator
  ([D-012](../03-decisions/D-012-compensate-steering-actuation-delay.md)).
- `/cmd_ackermann` timeout → coast, steering stopped; ±15° clamp
  ([D-013](../03-decisions/D-013-command-timeout-coasts.md)).
- Non-blocking reply drain (bug M-06), 10 ms tick (M-07), `tools/fake_cart.py`.
- Needs the matching one-line tesla_sim change (relay timed on sim time, M-08).
- Tested: [relay-overrun.md](../09-testing-and-results/relay-overrun.md).
