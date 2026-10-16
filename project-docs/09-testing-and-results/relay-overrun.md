# 2026-10-15 · Relay controller against simulated actuators

**Unit tests** (`test/test_relay_steering.py`, 9 tests): ten target steps,
twice; second pass scored. Simulated actuator at 200 Hz, 25 ms control tick.

| Start / stop delay | Old controller: relay switches | New: switches | New: max settle error |
| --- | --- | --- | --- |
| 0.03 / 0.03 s | 19 | 19 | 0.61° |
| 0.12 / 0.12 s (the cart, as described) | **159** | 19 | 0.51° |
| 0.15 / 0.10 s | 59 | 19 | 0.47° |
| 0.05 / 0.20 s (run-on) | 183 | 19 | 0.76° |

Learned delays match the true ones to ≤ 5 ms in these runs, also after a long
move to a target held for many seconds (an earlier version drifted there; the
"only update a delay the window pins down" rule fixed it).

**Bridge end to end** (`tools/fake_cart.py`: fake board replying continuously,
0.12 s delay each way, lock ±20°; fake encoder at 100 Hz; bridge not in dry run):
- targets +8, −6, +3 (×2): each reached monotonically, no overshoot, settled
  0.16–0.61° short (inside the deadband);
- +30° → held at 14.92° (clamp);
- publishing stopped → throttle 71 → 50, relay 50, brake 0 within the timeout;
- 27–28 frames/s, worst gap 42 ms; no stall from the replies;
- learned start 127–150 ms, stop 125–148 ms (true 120 ms + the bridge's own
  send latency).
- With the fake left at +14.8° from a previous run, the encoder zeroed there and
  the fake's lock appeared at +5.2°: the bridge stopped at it and logged
  "Steering stalled at +5.2 deg". That run is why stalled history is now dropped.
