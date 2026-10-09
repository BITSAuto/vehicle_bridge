# Q-001 · What speed does each throttle byte give?

- **Opened:** 2026-09-09 · **Status:** Open · **Priority:** high (before driving)

`MAX_SPEED_KMH = 7.0` (from `cart_contorller`) scales speed linearly onto
bytes 50–100, so 5 km/h sends ≈86. Nothing ever calibrated this. **To
resolve:** at the cart, on a flat road, step the byte (e.g. 55, 60, 65, …)
and measure steady speed (GPS, a phone, or timing over marked distance);
replace the linear guess with a table. `cart_driver`'s speed controller
corrects with measured speed, but only once a speed source exists (Q-004).
