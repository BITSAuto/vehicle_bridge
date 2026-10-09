# Encoder facts

### It is incremental and read by a separate MCU over USB serial
**Documented** (owner, 2026-10-02). Not yet seen connected.

### Assumed line format and port
**Assumed**: one integer per line (e.g. `1234\r\n`), 115200 baud,
`/dev/ttyACM0`. See [Q-003](../06-open-questions/Q-003-real-encoder-mcu-format-and-scale.md).

### Provisional scale
**Assumed**: ±15° at ±2500 counts → `degrees_per_count: 0.006` (owner's
estimate). An earlier README draft cited "~15° per cart_controller" as a lock
angle; that is a software limit, and the claim was removed.

### Angle formula
**Verified** by reading `encoder.py` and in the fake-MCU test (2026-10-02):
`(count − zero_count) × degrees_per_count`, then `invert`, then
`+ offset_deg`.

### Behaviour on disconnect
**Verified** with a fake MCU on a pseudo-terminal (2026-10-02): killing the
MCU produced `[Errno 5] Input/output error`, then the device path vanished;
the node logged it, retried every second, reconnected and re-zeroed when the
fake came back. A restart moves the origin silently, so the re-zero is only
correct if the wheels are straight at that moment.
