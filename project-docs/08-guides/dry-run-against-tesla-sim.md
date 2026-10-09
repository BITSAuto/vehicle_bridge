# Dry run against tesla_sim

With the sim running (see tesla_sim's guides) on your domain:
```bash
ros2 run vehicle_bridge serial_bridge_node --ros-args -p dry_run:=true
```
The bridge consumes the sim's `/cmd_ackermann` and `/steering/angle`,
computes relay decisions and throttle bytes, and never opens a port. Expect
no "No /steering/angle within 0.5s" warnings while the sim runs. Don't start
`encoder_node` (the sim already publishes `/steering/angle`).
