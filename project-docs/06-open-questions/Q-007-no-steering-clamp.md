# Q-007 · The bridge doesn't clamp steering targets

- **Opened:** 2026-10-02 · **Status:** Resolved 2026-10-15 · **Priority:** medium

A target beyond the mechanical lock makes the relay drive into the lock until
the encoder reaches a value it can't reach. tesla_sim clamps to ±15°; the
bridge should too (`max_steer_deg` parameter, from Q-005).

**Resolved 2026-10-15:** [D-013](../03-decisions/D-013-command-timeout-coasts.md) (branch `fix/relay-overrun`).
