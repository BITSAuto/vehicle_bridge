# Legacy code these facts came from

We read but **do not modify** these repos. They're the only record of how the
cart was driven before this package.

| Script | What it does | Facts taken from it |
| --- | --- | --- |
| `cart_contorller/README.md` | Describes the controller and the motor | infinite run-on, 35 ms pulse, 0.45°/pulse, `MAX_STEER_DEG` 15, `MAX_SPEED_KMH` 7 |
| `cart_contorller/scripts/controller.py` | Older CARLA-oriented controller, open-loop pulse counting | `build_serial_command` copy |
| `road_segmentation/scripts/drivebywire.py` | Drive-by-wire test script | `build_serial_command` copy |
| `road_segmentation/scripts/rotary_encoder_driver.py` | Closed-loop vision-based steering on a real encoder, fixed throttle 75 | throttle semantics, `+right` convention, subscribes to `/steering/angle` and `/bitsauto/speed`, `SIM_DEG_PER_SEC = 12.0` |
| `road_segmentation/scripts/pwm_check.py`, `pwm_dir_check.py` | Hold the relay for a set time | confirms no self-stop |

`/steering/angle` and `/bitsauto/speed` were consumed by
`rotary_encoder_driver.py` but published by nothing in the workspace
(**Verified** by grepping both repos, 2026-09-09). `/steering/angle` is now
published by `encoder_node`; `/bitsauto/speed` still has no publisher on the
cart.
