# 07 · Bugs and lessons

| Page | Bugs |
| --- | --- |
| [bridge-bugs.md](bridge-bugs.md) | M-01 no-op in the "no encoder" branch · M-02 one old angle kept steering forever · M-03 crash on brake release · M-04 lock angle cited as measured · M-05 stale protocol docstring |
| [testing-without-hardware.md](testing-without-hardware.md) | Lessons from testing serial peripherals with no hardware |

## Rules that came out of these
- The "not ready / no data" branch of a hardware control loop runs for real
  on every start-up and disconnect. Review it as carefully as the main path.
- Every input that controls actuators needs a freshness check.
- In rclpy, one log call site may only ever use one severity.
- Label every hardware number as measured or not.
