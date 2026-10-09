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
