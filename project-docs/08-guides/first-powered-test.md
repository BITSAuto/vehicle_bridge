# First powered test: checklist

Nothing here has run on the powered cart yet. Treat the first session as
calibration, with a person at the physical kill switch and wheels off the
ground where possible.

**Before going to the cart**
- [x] Command timeout added ([Q-006](../06-open-questions/Q-006-no-command-timeout.md)) and steering clamp ([Q-007](../06-open-questions/Q-007-no-steering-clamp.md)) (2026-10-15, D-013)
- [x] Same bridge build tested against `tools/fake_cart.py` on the Orin ([relay-overrun.md](../09-testing-and-results/relay-overrun.md) — done 2026-10-15)
- [ ] Built and fake-MCU-tested on the Orin's Jazzy ([Q-008](../06-open-questions/Q-008-not-yet-built-on-jazzy.md))

**Wheels off the ground, drive power off**
- [ ] Encoder MCU format, baud and port confirmed; calibrated ([calibrating-the-encoder.md](calibrating-the-encoder.md))
- [ ] `+` steering command turns the wheels **right**
- [ ] Relay stops at the target without oscillating; time a lock-to-lock sweep
- [ ] Note the learned actuator from the log ("Steering actuator learned: start … ms, stop … ms") into `04-knowledge/steering-hardware.md`
- [ ] Stop publishing `/cmd_ackermann`: within 0.5 s the throttle goes neutral and the steering stops (no brake)
- [ ] Unplug the encoder: bridge logs "forcing neutral+stop" within 0.5 s

**Wheels off the ground, drive power on**
- [ ] Speed 0 → throttle 50, wheels don't turn
- [ ] Small speed → wheels turn forward; `/vehicle/emergency_brake` true → brake engages, throttle neutral
- [ ] Negative speed: does `J` engage reverse? ([Q-002](../06-open-questions/Q-002-reverse-and-braking-range.md))

**On the ground, walking pace, open area**
- [ ] Throttle byte → speed table ([Q-001](../06-open-questions/Q-001-throttle-mapping-unverified.md))
- [ ] Coast-down from 5 km/h: distance and time (tesla_sim's `coastDecel`)

Write up the session in `10-worklog/` and update the knowledge pages with
what was measured.
