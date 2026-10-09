# Glossary

| Term | Meaning |
| --- | --- |
| **Drive-by-wire (DBW)** | The cart's microcontroller that takes serial frames and drives throttle, steering relay, brake and lights |
| **Frame** | One serial command, `*A{a}B{throttle}C{c}D{steering}E{left}F{horn}G{light}H{right}I{brake}J{reverse}#` |
| **Relay** | The steering motor's three states: 49 left, 50 stop, 51 right |
| **Infinite run-on** | The steering motor keeps turning until it receives 50 |
| **Minimum hold** | A relay pulse, once started, is held at least 35 ms (the motor's ~30 ms reaction time) |
| **Hysteresis** | Start turning when the error exceeds 1.0°, stop when it falls below 0.5° |
| **Encoder MCU** | The separate microcontroller that reads the steering encoder and streams counts |
| **Zero** | The count treated as straight ahead; set on the first reading after each connect, or with `~/zero` |
| **Neutral** | Throttle byte 50: no drive, the cart coasts |
| **Dry run** | `dry_run:=true`: compute everything, never open or write the serial port |
| **Staleness** | No `/steering/angle` for `encoder_timeout_s` (0.5 s): the bridge forces neutral + stop |
