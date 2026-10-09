# Unit tests

**There are none yet.** `relay_steering.py`, `encoder.py` and
`serial_command.py` are pure Python and easy to test. Worth adding:
- relay: thresholds, 35 ms minimum hold, no direct LEFT↔RIGHT, `reset()`;
- encoder: parsing with the default and a custom `line_regex`, zero, invert,
  offset, ignoring the first line;
- serial command: exact frame for known inputs; throttle never `<50`;
  e-brake forces neutral;
- bridge: staleness → neutral + stop; (once added) command timeout.
