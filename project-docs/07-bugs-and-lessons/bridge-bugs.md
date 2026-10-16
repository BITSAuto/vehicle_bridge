# Bridge bugs

## M-01: A no-op line in the "no encoder yet" branch
- **Found:** 2026-09-09, by re-reading the code before running it
- **Bug:** the first draft had `relay = self._steering.relay = self._steering.relay`
  in the branch for "no `/steering/angle` yet". It sent nothing, leaving
  whatever relay state was last sent (possibly mid-turn) engaged on real
  hardware.
- **Fix:** send an explicit neutral + stop frame every tick in that branch
  ([D-006](../03-decisions/D-006-hold-neutral-and-stop-without-fresh-feedback.md)).

## M-02: One old steering angle kept the bridge steering forever
- **Found:** 2026-10-02
- **Bug:** the bridge only checked that an angle had *ever* arrived. If the
  encoder stopped, it kept closing the loop on a frozen value.
- **Fix:** `encoder_timeout_s` (0.5 s) staleness check.

## M-03: Releasing the emergency brake crashed the bridge
- **Found:** 2026-10-08 (same bug in tesla_sim)
- **Bug:** one log call site used `warn` on engage and `info` on release;
  rclpy raises "Logger severity cannot be changed between calls".
- **Fix:** two separate log calls (`cc8a29c`).

## M-04: A software limit cited as a measured lock angle
- **Found:** 2026-10-02
- **Bug:** a README draft said "~15° per cart_controller" as if it were the
  measured lock. It's `MAX_STEER_DEG`, a software limit.
- **Fix:** removed; tracked as [Q-005](../06-open-questions/Q-005-steering-lock-not-measured.md).

## M-05: The protocol docstring still says the brake has no ROS mapping
- **Found:** 2026-10-09
- **Bug:** `serial_command.py` says "I brake 0/1, no ROS mapping exists yet",
  written before `/vehicle/emergency_brake`.
- **Fix:** docstring updated with this book.

## M-06: The reply drain could stall the bridge forever
- **Found:** 2026-10-15, by reading the code (not seen on hardware)
- **Bug:** after every frame, `while self._ser.readline(): pass` with a 50 ms
  read timeout. Every tick blocked ≥ 50 ms (the "40 Hz" loop ran at ≤ 20 Hz and
  delayed the encoder callbacks with it), and against a board that keeps
  replying the loop never ends: the bridge stops ticking with the last relay
  state engaged, and the motor's infinite run-on takes the steering to the lock.
- **Fix:** read only `in_waiting` bytes. Checked with `tools/fake_cart.py`, a
  fake board that replies continuously.
- **Rule:** nothing in a control tick may block on I/O.

## M-07: Frames went out every 50 ms, not every 30 ms
- **Found:** 2026-10-15, counting frames at a fake board
- **Bug:** a 25 ms tick against a 30 ms minimum frame interval skips every
  other tick.
- **Fix:** 10 ms tick; frames now go out every ~30–40 ms (27–28/s measured).

## M-08: tesla_sim timed the relay controller with the wall clock
- **Found:** 2026-10-15
- **Bug:** `tesla_driver.py` passed `time.monotonic()` while the sim runs at
  ~0.3× real time (headless on the Orin), so the 35 ms hold and anything
  timing-based was wrong in sim; a learning controller would have learned a
  3× slow actuator.
- **Fix (in tesla_sim):** pass `robot.getTime()`.
