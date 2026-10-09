# Encoder: counts to `/steering/angle`

`angle_deg = (count − zero_count) × degrees_per_count × (−1 if invert) + offset_deg`

1. `encoder_node` opens the MCU port. Opening usually resets an Arduino-class
   MCU, so the count origin moves on every connect.
2. The **first line after connecting is dropped** (it may start mid-number).
   Lines that don't match `line_regex` are ignored.
3. With `zero_on_start: true`, the first valid count becomes the zero:
   **the wheels must be straight at launch**. With `false`, nothing is
   published until `~/zero` is called.
4. Each valid line publishes `/steering/angle` and `/steering/encoder_count`.
5. On a serial error (e.g. `[Errno 5] Input/output error` when the USB
   device disappears), the node logs it, drops the zero, and retries every
   second; it re-zeroes on the first reading after reconnecting.

While no zero exists nothing is published, so `serial_bridge_node` holds
neutral + stop. `degrees_per_count` has no usable default: the node refuses
to start without a positive value, because a wrong scale drives the steering
past its target towards the lock.

Calibration procedure: [08-guides/calibrating-the-encoder.md](../08-guides/calibrating-the-encoder.md).
