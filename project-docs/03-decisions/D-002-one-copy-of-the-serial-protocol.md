# D-002 · One copy of the serial protocol: `serial_command.py`

- **Date:** 2026-09-09
- **Status:** Accepted

## Context
`build_serial_command` existed byte-for-byte identical in
`road_segmentation/scripts/drivebywire.py`,
`road_segmentation/scripts/rotary_encoder_driver.py` and
`cart_contorller/scripts/controller.py`.

## Decision
`vehicle_bridge/serial_command.py` is the single source of truth. Other code
should import it rather than keep a copy.

## Consequences
- The legacy repos still have their own copies (we don't modify
  `road_segmentation`); any protocol change must be checked against them.
