# Q-005 · What is the cart's real steering lock and rate?

- **Opened:** 2026-10-02 · **Status:** Open · **Priority:** medium

±15° is `cart_contorller`'s software limit, not a measured road-wheel angle.
The 12.86 °/s rate comes from documented pulse constants. **To resolve:**
during encoder calibration, measure the road-wheel angle at full lock both
ways (straightedge on the tyre, `atan(d/L)`), and time a lock-to-lock sweep.
Update `cart_driver`'s vehicle profile and tesla_sim's `maxSteeringDeg`.
