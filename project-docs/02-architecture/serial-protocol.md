# Serial protocol

Frame: `*A{a}B{throttle}C{c}D{steering}E{left_ind}F{horn}G{light}H{right_ind}I{brake}J{reverse}#`,
9600 baud, 8N1, no flow control. Built only by `serial_command.build_serial_command`.

| Field | Meaning | What the bridge sends |
| --- | --- | --- |
| `A` | unused in every script read | 0 |
| `B` throttle | byte 0–100: 50 neutral/coast, >50 forward, <50 braking | `50 + min(abs(speed) / 7.0, 1) × 50`, so 5 km/h ≈ **86**; 0 km/h = 50; **never <50**; 50 while the e-brake is on |
| `C` | unused | 0 |
| `D` steering | relay: 49 left, 50 stop, 51 right | from `RelaySteeringController`; 50 when the angle is stale |
| `E`, `F`, `G`, `H` | left indicator, horn, light, right indicator | always 0 (no ROS input) |
| `I` brake | 0/1 | 1 only while `/vehicle/emergency_brake` is true, and once at shutdown |
| `J` reverse | 0/1 | 1 when the commanded speed is negative (unverified meaning) |

Responses from the board are read and discarded; their format isn't known
([Q-010](../06-open-questions/Q-010-board-response-format.md)).

The throttle scaling (`MAX_SPEED_KMH = 7.0`) and the meaning of `J` are
unverified ([Q-001](../06-open-questions/Q-001-throttle-mapping-unverified.md),
[Q-002](../06-open-questions/Q-002-reverse-and-braking-range.md)).
