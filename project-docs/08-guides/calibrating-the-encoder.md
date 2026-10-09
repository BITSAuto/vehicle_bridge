# Calibrating the encoder

Calibration lives in `config/encoder.yaml` (`degrees_per_count`, `invert`,
`offset_deg`). Do this with the cart stationary, drive power off, wheels off
the ground if possible.

1. Temporarily set `degrees_per_count: 1.0` so the node starts.
2. Straighten the wheels and launch with `dry_run:=true` (zeroes there).
3. `ros2 topic echo /steering/encoder_count`. Steer to a measured angle to
   the right and note the count; do the same to the left. Full lock is
   convenient, but **measure** the road-wheel angle: hold a straightedge flat
   against the tyre sidewall, measure how far it moves sideways (`d`) over a
   length `L` compared with straight ahead; the angle is `atan(d / L)`.
4. `degrees_per_count = (right_angle + left_angle) / |right_count − left_count|`
   (using both sides averages out an off-centre zero).
5. Write it into `config/encoder.yaml`, relaunch, and check `/steering/angle`
   reads the measured angles. If right reads negative, set `invert: true`.
6. Record the measured lock angles and the date in
   [steering-hardware.md](../04-knowledge/steering-hardware.md) and close
   [Q-003](../06-open-questions/Q-003-real-encoder-mcu-format-and-scale.md)/[Q-005](../06-open-questions/Q-005-steering-lock-not-measured.md).

If the firmware prints something other than a bare integer (e.g.
`ENC:1234`), set `line_regex` (first group = the count).
