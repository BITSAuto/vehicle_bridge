# Q-002 · What do `J` (reverse) and throttle `<50` actually do?

- **Opened:** 2026-09-09 · **Status:** Open · **Priority:** medium

The bridge maps a negative speed to `J=1` with a forward-range throttle. No
script ever exercised `J` or the `<50` "braking" range. **To resolve:** at
walking pace with the wheels off the ground first, confirm `J=1` engages
reverse (not regenerative braking or nothing). The bridge never sends `<50`
by design ([D-009](../03-decisions/D-009-emergency-brake-topic-is-the-only-brake.md)).
