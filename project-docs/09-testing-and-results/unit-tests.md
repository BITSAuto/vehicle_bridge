# Unit tests

**There are none yet.** `relay_steering.py`, `encoder.py` and
`serial_command.py` are pure Python and easy to test. Worth adding:
- relay: thresholds, 35 ms minimum hold, no direct LEFT↔RIGHT, `reset()`;
- encoder: parsing with the default and a custom `line_regex`, zero, invert,
  offset, ignoring the first line;
- serial command: exact frame for known inputs; throttle never `<50`;
  e-brake forces neutral;
- bridge: staleness → neutral + stop; (once added) command timeout.

**Update 2026-10-15:** `test/test_relay_steering.py` (9 tests, `python3 -m pytest test`):
settling without hunting for five actuators (symmetric delay, slow start, run-on,
slow wheels), the learned delays, no direct LEFT↔RIGHT, no pulse too short to
move, stopping at a lock, and the overrun of the uncompensated controller.
Results: [relay-overrun.md](relay-overrun.md). Encoder and serial-command tests
are still to do.
