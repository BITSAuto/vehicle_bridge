# D-010 · Send one brake command when the bridge shuts down

- **Date:** 2026-09-09
- **Status:** Accepted (deliberate fail-safe; revisit with Q-006)

## Decision
On shutdown or node death, send throttle 50, relay 50, brake 1, then close
the port.

## Why
If the bridge goes away, nothing will keep commanding the cart; stopping it
is the safe default.

## Trade-off
The brake is an instant stop that can damage the cart. Stopping the bridge
while moving therefore stops the cart hard. Keep that in mind during tests:
stop the cart first (command 0 and let it coast), then the bridge.
