# Hardware and environment

| Item | What we know | Confidence |
| --- | --- | --- |
| Drive-by-wire controller | Arduino-class board on USB serial, default `/dev/ttyUSB0`, **9600 baud 8N1**, frames `*A..B..C..D..E..F..G..H..I..J..#` | Verified from three existing scripts |
| Throttle | byte 0–100; 50 neutral/coast, >50 forward, <50 braking | Documented in an existing script's header; `<50` never exercised |
| Brake | flag `I` (0/1); stops the cart instantly and can damage it | Behaviour reported by the team; Verified as protocol field |
| Reverse | flag `J` (0/1) | Assumed meaning; never exercised |
| Steering motor | relay: `D` = 49 left, 50 stop, 51 right; infinite run-on; ~30 ms reaction; 0.45° per 35 ms pulse (≈12.86 °/s) | Verified from `cart_contorller`'s README and scripts |
| Steering lock | ±15° | Assumed: a software limit in `cart_contorller`, not a measurement |
| Steering encoder | incremental, read by a separate MCU streaming counts over USB serial, default `/dev/ttyACM0`, assumed 115200 baud, one integer per line | Format **Assumed**; separate MCU and incremental: stated by the owner |
| Encoder scale | provisional 0.006 °/count (±15° at ±2500 counts) | **Assumed** (owner-provided, unmeasured) |
| Speed sensor | none publishing on the real cart | Verified absence in this workspace; see [Q-004](../06-open-questions/Q-004-real-cart-speed-source.md) |
| Computer | Nvidia Jetson Orin AGX, Ubuntu 24.04, ROS 2 Jazzy | Verified |

Serial ports need read/write permission (`dialout` group, then log in
again). Use `/dev/serial/by-id/...` paths once both boards are connected so
the two ports can't swap.

Development and the fake-MCU tests ran on the laptop (ROS 2 Humble in a
distrobox). The package uses nothing Humble-specific but has not been built
on Jazzy yet ([Q-008](../06-open-questions/Q-008-not-yet-built-on-jazzy.md)).
