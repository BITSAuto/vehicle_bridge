# Completed

Newest first.

## 2026-10-09 · Project docs
This book ([D-011](../03-decisions/D-011-project-docs.md)).

## 2026-10-08 · Emergency brake — [PR #1](https://github.com/BITSAuto/vehicle_bridge/pull/1) into `feature/steering-encoder`, then [PR #2](https://github.com/BITSAuto/vehicle_bridge/pull/2) into `main` (`499afb2`)
- `/vehicle/emergency_brake` as the only brake; speed 0 always coasts
  ([D-009](../03-decisions/D-009-emergency-brake-topic-is-the-only-brake.md)), `cc8a29c`.
- Fixed a crash on brake release (rclpy log severity).

## 2026-10-02 · Steering encoder — `e97d88f` (merged with PR #2)
- `encoder_node`, `encoder.py`, `config/encoder.yaml`, launch file starts both
  nodes ([D-008](../03-decisions/D-008-encoder-node-reads-a-separate-mcu.md)).
- Bridge treats a stale angle (0.5 s) as lost ([D-006](../03-decisions/D-006-hold-neutral-and-stop-without-fresh-feedback.md)).
- Tested end to end against a fake MCU.

## 2026-09-13 · Own repository — `c45b82c`
[D-007](../03-decisions/D-007-own-repository.md).

## 2026-09-09 · Serial bridge and relay controller
- `serial_command.py`, `relay_steering.py`, `serial_bridge_node.py`
  ([D-001](../03-decisions/D-001-separate-package-for-real-vehicle-io.md) to
  [D-006](../03-decisions/D-006-hold-neutral-and-stop-without-fresh-feedback.md),
  [D-010](../03-decisions/D-010-brake-on-shutdown.md)).
- Dry-run parity check against tesla_sim.
