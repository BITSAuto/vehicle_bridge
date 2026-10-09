# Q-003 · What does the real encoder MCU send, and what is the real scale?

- **Opened:** 2026-10-02 · **Status:** Open · **Priority:** high (before closing the steering loop)

Assumed: one integer per line, 115200 baud, `/dev/ttyACM0`, 0.006 °/count,
right = positive, MCU resets when the port opens. **To resolve:** plug it in,
check `ls -l /dev/serial/by-id/` and the raw output (`cat` or `screen`), set
`line_regex`/`baud` if needed, then follow
[calibrating-the-encoder.md](../08-guides/calibrating-the-encoder.md) and
replace the provisional scale. Confirm `invert` and the reset-on-open
behaviour.
