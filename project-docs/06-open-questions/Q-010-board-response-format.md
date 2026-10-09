# Q-010 · What does the drive-by-wire board reply?

- **Opened:** 2026-09-09 · **Status:** Open · **Priority:** low

The bridge drains and discards responses. If the board echoes state or
errors, parsing them would let the bridge detect a dead link. Capture the raw
replies at the cart.
