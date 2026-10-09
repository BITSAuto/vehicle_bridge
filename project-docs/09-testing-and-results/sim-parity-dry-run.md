# Sim parity dry run (2026-09-09)

`serial_bridge_node` with `dry_run:=true` against a live tesla_sim, on the
sim's own `/cmd_ackermann` and `/steering/angle`, for 12 s of continuous
commands: **no** missing-angle warnings, so the bridge received and used the
sim's feedback throughout. Relay decisions weren't logged and diffed; parity
rests on both sides importing the same `RelaySteeringController`.
