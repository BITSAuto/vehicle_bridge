# Q-004 · Where will the real cart's measured speed come from?

- **Opened:** 2026-09-09 (as "who publishes `/bitsauto/speed`") · **Status:** Open · **Priority:** high (blocks real-cart driving)

Nothing publishes `/vehicle/speed` or `/bitsauto/speed` on the cart.
`cart_driver` needs measured speed for its speed hold, odometry, memory map
and its coast-distance safety check. An early message from the owner said the
cart has no wheel encoders (unconfirmed). Options, roughly best first: a
wheel or motor-shaft sensor (hall effect or encoder); visual(-inertial)
odometry from the D435i; GNSS velocity (noisy at 5 km/h). Whatever is chosen
should publish `/vehicle/speed` (Float32, m/s).
