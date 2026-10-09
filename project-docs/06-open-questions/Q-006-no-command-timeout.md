# Q-006 · The bridge has no `/cmd_ackermann` timeout

- **Opened:** 2026-10-09 · **Status:** Open · **Priority:** **high (safety, before any powered test)**

`serial_bridge_node` stores the last commanded speed and steering target and
keeps sending them. If the publisher (e.g. `cart_driver`) crashes or the
network drops, the cart keeps its throttle on. The steering-angle staleness
check doesn't cover this. tesla_sim has `cmdTimeout` for the same reason.
**Proposed fix:** a `cmd_timeout_s` parameter (e.g. 0.5 s); when exceeded,
send neutral throttle and hold the steering target (or stop the relay), never
the brake. Add a unit test.
