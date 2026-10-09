# Speed and throttle

### Throttle scaling is unverified
**Assumed**: `MAX_SPEED_KMH = 7.0` (borrowed from `cart_contorller`)
maps linearly to bytes 50–100, so the team's 5 km/h cruise sends byte
≈86. Nothing in the workspace ever calibrated a byte against a measured
speed ([Q-001](../06-open-questions/Q-001-throttle-mapping-unverified.md)).

### Braking behaviour
**Documented** by the team (2026-10-08): the brake stops the cart instantly
and can damage it; it is for emergencies only. Normal stops are by coasting.
How far the cart coasts from 5 km/h is unknown (tesla_sim uses 0.4 m/s² as a
placeholder).

### No speed measurement on the cart yet
**Verified** absence: nothing in the workspace publishes `/vehicle/speed` or
`/bitsauto/speed` on the real cart. An early message from the owner
(2026-10-08) also said the cart has no wheel encoders; that version of the
message was later rewritten, so treat it as likely but unconfirmed
([Q-004](../06-open-questions/Q-004-real-cart-speed-source.md)). `cart_driver`
needs a speed source to drive the real cart.
