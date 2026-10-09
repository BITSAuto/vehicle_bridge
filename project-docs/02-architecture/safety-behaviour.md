# Safety behaviour

| Situation | What the bridge sends |
| --- | --- |
| normal | throttle from the commanded speed (≥ 50), relay from the controller, brake 0 |
| commanded speed 0 | throttle **50** (coast), never a braking value |
| `/steering/angle` never received, or older than 0.5 s | throttle 50, relay **50** (stop), brake as commanded; warns every 2 s; controller reset |
| `/vehicle/emergency_brake` true | throttle 50, brake **1**, every tick, until false |
| node shutdown (Ctrl-C or death) | one final frame: throttle 50, relay 50, brake **1**, then closes the port |
| serial port can't open | runs as dry run and logs an error |

**Known gaps** (not yet handled):
- **No `/cmd_ackermann` timeout.** If the publisher (e.g. `cart_driver`)
  dies, the bridge keeps sending the last throttle and steering target
  ([Q-006](../06-open-questions/Q-006-no-command-timeout.md), high priority).
- **No steering clamp** to ±15° in the bridge
  ([Q-007](../06-open-questions/Q-007-no-steering-clamp.md)).
- The shutdown brake is deliberate, but it means stopping the bridge stops
  the cart instantly, which can damage it if moving.
