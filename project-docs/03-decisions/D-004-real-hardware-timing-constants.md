# D-004 · Use the real motor's timing constants, not tuned values

- **Date:** 2026-09-09
- **Status:** Accepted

## Decision
`MIN_HOLD_S = 0.035` and `DEG_PER_MIN_HOLD = 0.45` come straight from
`cart_contorller/README.md` (the motor needs ~30 ms to react; one 35 ms pulse
turns the wheels ~0.45°). `RATE_DEG_S` ≈ 12.86 °/s follows. Hysteresis
thresholds 1.0° / 0.5° follow `rotary_encoder_driver.py`'s loop.

## Why
An independent constant in a different file (`SIM_DEG_PER_SEC = 12.0`) gives
nearly the same rate, which makes the "digital clone" claim mean something
for steering.
