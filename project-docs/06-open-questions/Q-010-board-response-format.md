# Q-010 · What does the drive-by-wire board reply?

- **Opened:** 2026-09-09 · **Status:** Open · **Priority:** low

The bridge drains and discards responses. If the board echoes state or
errors, parsing them would let the bridge detect a dead link. Capture the raw
replies at the cart.

**Update 2026-10-15:** still unknown, but no longer dangerous: the bridge used to
drain replies with a blocking `readline()` loop, which would never have
returned against a board that keeps replying
([bridge-bugs.md M-06](../07-bugs-and-lessons/bridge-bugs.md)). It now reads
only what is waiting, without blocking.
