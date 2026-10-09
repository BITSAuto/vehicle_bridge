# D-006 · Without fresh steering feedback, actively command neutral + stop

- **Date:** 2026-09-09 (initial "never received" case); extended 2026-10-02 to stale feedback
- **Status:** Accepted

## Context
The relay keeps turning until told to stop. Skipping a tick when feedback is
missing would leave the last relay state (possibly mid-turn) engaged with
nothing correcting it. Before 2026-10-02 a single old message also kept the
bridge steering forever.

## Decision
If `/steering/angle` was never received or is older than
`encoder_timeout_s` (0.5 s), send throttle 50 and relay 50 every tick, reset
the controller, and warn every 2 s.

## Consequences
- A disconnected encoder stops the steering and the drive (the cart coasts).
- See [safety-behaviour.md](../02-architecture/safety-behaviour.md) for the
  gaps this doesn't cover (no command timeout).
