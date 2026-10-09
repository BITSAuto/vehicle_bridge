# Fake MCU test (2026-10-02, Humble)

A pty-based fake MCU streamed counts (non-zero origin, boot banner, 100 Hz).

| Check | Result |
| --- | --- |
| `/steering/angle` rate | ~99 Hz |
| Zero on first reading | ✔ |
| `~/zero` re-zeroes | ✔ |
| Kill the MCU | serial I/O error logged, retry every second; `serial_bridge_node` (dry run) logged "forcing neutral+stop" within 0.5 s |
| Restart the MCU | reconnected and re-zeroed |
| Launch file | started both nodes and loaded `config/encoder.yaml` |

**Not verified:** real hardware, the real MCU's format/baud/port, Jazzy.
How to repeat: [testing-with-a-fake-mcu.md](../08-guides/testing-with-a-fake-mcu.md).
