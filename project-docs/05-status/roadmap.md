# Roadmap

In order. Items 1–2 can be done remotely; the rest need someone at the cart.

| # | Item | Why | Depends on |
| --- | --- | --- | --- |
| 1 | `/cmd_ackermann` timeout → neutral + stop | A dead publisher must not leave the throttle on | — ([Q-006](../06-open-questions/Q-006-no-command-timeout.md)) |
| 2 | Clamp steering targets to ±15°; unit tests for `relay_steering`, `encoder`, `serial_command` | Safety and regression protection | — |
| 3 | Connect the encoder MCU; confirm format, baud, sign; calibrate `degrees_per_count` | `/steering/angle` must be right before closing the loop | cart access ([Q-003](../06-open-questions/Q-003-real-encoder-mcu-format-and-scale.md)) |
| 4 | Measure the steering lock and rate on the cart | Planner limits | cart access ([Q-005](../06-open-questions/Q-005-steering-lock-not-measured.md)) |
| 5 | Calibrate throttle byte → speed at low speed; confirm what `J` does | Speed control | cart access ([Q-001](../06-open-questions/Q-001-throttle-mapping-unverified.md), [Q-002](../06-open-questions/Q-002-reverse-and-braking-range.md)) |
| 6 | A speed source on the cart publishing `/vehicle/speed` | `cart_driver` needs measured speed | hardware choice ([Q-004](../06-open-questions/Q-004-real-cart-speed-source.md)) |
| 7 | Build and run on Jazzy (the Orin) | The cart's computer | ([Q-008](../06-open-questions/Q-008-not-yet-built-on-jazzy.md)) |
