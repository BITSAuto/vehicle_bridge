# Serial protocol facts

### The frame, byte for byte
**Verified** (2026-09-09) from three independent, byte-identical copies of
`build_serial_command` (`road_segmentation/scripts/drivebywire.py`,
`road_segmentation/scripts/rotary_encoder_driver.py`,
`cart_contorller/scripts/controller.py`):
`*A{a}B{throttle}C{c}D{steering}E{left_ind}F{horn}G{light}H{right_ind}I{brake}J{reverse}#`,
**9600 baud, 8N1**.

### Throttle byte semantics
**Documented** in `rotary_encoder_driver.py`'s header: "Throttle byte: 50 =
neutral/coast, >50 = forward, <50 = braking." No script exercises `<50` or
`J` with real input behind it; the legacy scripts only ever send a fixed
throttle of 75.

### Steering field
**Verified**: `D` = 49 left, 50 stop, 51 right (see
[steering-hardware.md](steering-hardware.md)).

### Unused and unmapped fields
**Verified** from the scripts: `A` and `C` are always 0; `E`–`H` (indicators,
horn, light) have no ROS mapping anywhere in the workspace.

### Board responses
**Assumed unknown:** the board replies, but no script documents or parses the
format. The bridge drains and discards it.
