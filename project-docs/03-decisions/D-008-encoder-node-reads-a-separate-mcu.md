# D-008 · `encoder_node` reads the steering encoder from its own MCU over USB serial

- **Date:** 2026-10-02
- **Status:** Accepted (merged in [PR #2](https://github.com/BITSAuto/vehicle_bridge/pull/2), 2026-10-08)

## Context
The owner asked for the encoder to be read and mapped to `/steering/angle`
inside vehicle_bridge. Their answers: the encoder is on a **separate MCU over
USB serial** (not the drive-by-wire board), and it is **incremental**
(counts).

## Decision
A second node, `encoder_node`, on its own port, publishing
`/steering/angle` (deg, + right) and `/steering/encoder_count`.

## Sub-decisions
- **Zero on every connect** (`zero_on_start`, default true) plus a `~/zero`
  service, because an incremental count is relative to power-up and opening
  the port usually resets the MCU. Nothing is published until a zero exists.
- **`degrees_per_count` has no default;** the node refuses to start without a
  positive value, because a wrong scale overshoots towards the lock. The
  value lives in `config/encoder.yaml`.
- **Provisional calibration** from the owner: ±15° at ±2500 counts
  (0.006 °/count). Not measured.
- **Assumed MCU format:** one integer per line, 115200 baud, `/dev/ttyACM0`;
  `line_regex` lets the real format be matched without code changes.

## Consequences
- Answers the earlier question of who publishes `/steering/angle` on the
  cart. Only tested against a fake MCU ([09-testing-and-results/fake-mcu-test.md](../09-testing-and-results/fake-mcu-test.md)).
