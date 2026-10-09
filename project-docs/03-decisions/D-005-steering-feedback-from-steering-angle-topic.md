# D-005 · Close the steering loop over `/steering/angle`, not the board's serial response

- **Date:** 2026-09-09
- **Status:** Accepted

## Context
The legacy controller already subscribed to `/steering/angle` (Float32,
degrees, + right). The drive-by-wire board's serial response format isn't
documented anywhere.

## Decision
`serial_bridge_node` subscribes to `/steering/angle` and only drains the
board's responses.

## Consequences
- Something must publish `/steering/angle` on the cart; that became
  `encoder_node` ([D-008](D-008-encoder-node-reads-a-separate-mcu.md)).
- tesla_sim publishes the same topic, so the bridge can be dry-run against
  the sim.
