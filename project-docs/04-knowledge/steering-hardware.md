# Steering hardware

### The steering is a relay with infinite run-on
**Verified** (2026-09-09). `cart_contorller/README.md`: "the real cart motor
has infinite run-on and does not stop by itself until this `50` command is
explicitly received". Confirmed by `pwm_check.py` and `pwm_dir_check.py`
(hold a direction for a user-chosen time with no timeout) and by
`rotary_encoder_driver.py`'s header ("Motor 51 = turn right continuously
until 50 = stop").

### Timing: ~35 ms minimum pulse, ~0.45° per pulse
**Verified** from `cart_contorller/README.md`: `PULSE_MS = 35.0` ("the real
motor intrinsically takes 30ms to react"), `DEG_PER_PULSE = 0.45`.
Corroborated by `rotary_encoder_driver.py`'s `SIM_DEG_PER_SEC = 12.0`;
0.45 / 0.035 ≈ 12.86 °/s.

### Sign convention: + = right
**Verified**: `rotary_encoder_driver.py` documents `/steering/angle` as
"degrees (+right / -left)", and tesla_sim's commanded angle is + right too.
Converting between them is only `degrees()`/`radians()`; there is no sign
flip. This is the opposite of ROS REP 103, so don't "fix" it.

### Two legacy control strategies; the bridge follows the newer one
**Verified**: `cart_contorller`'s `MotorSteering` counts pulses open-loop
(CARLA-oriented, a simulated angle estimate); `rotary_encoder_driver.py`'s
`MotorController` is closed-loop on a real encoder with hysteresis. The owner
described `cart_contorller` as containing "a lot of deprecated stuff using
carla sim". `RelaySteeringController` follows the closed-loop one.

### Steering lock
**Assumed** ±15°: `cart_contorller`'s `MAX_STEER_DEG`, a software limit. The
real road-wheel angle at lock has never been measured
([Q-005](../06-open-questions/Q-005-steering-lock-not-measured.md)).
