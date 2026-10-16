"""Shared steering-relay hysteresis controller.

The vehicle has no proportional steering input. Steering is driven by a
three-state relay -- turn left / stop / turn right -- that runs continuously
in whichever direction it's told until explicitly stopped: "the real cart
motor has infinite run-on and does not stop by itself until this 50 command
is explicitly received" (cart_controller/README.md). Closed-loop angle
control has to be built entirely in software on top of that primitive plus a
rotary-encoder angle reading -- this is exactly what road_segmentation's
rotary_encoder_driver.py already does for its vision-based controller, and
what this module does more generally so it isn't reimplemented a third time.

This class is meant to be used identically by two callers:
  - vehicle_bridge's serial_bridge_node.py: encoder angle from the real
    rotary encoder (/steering/angle), relay decision sent over serial.
  - tesla_sim's tesla_driver.py: encoder angle from a Webots PositionSensor
    on the steering joint, relay decision drives a velocity-mode Motor.
Same class, same thresholds -- a controller (or a human tuning by feel)
validated against one sees the same step response from the other.
"""

import numpy as np

RELAY_LEFT = 49
RELAY_STOP = 50
RELAY_RIGHT = 51

# Real hardware timing, from cart_controller/README.md (independently
# verified against that file directly -- see
# project-docs/04-knowledge/steering-hardware.md): the motor takes ~30ms to
# physically react, so a pulse must be held >=35ms once started, and one such
# hold moves the real steering ~0.45 degrees. Corroborated independently by
# road_segmentation/rotary_encoder_driver.py's own SIM_DEG_PER_SEC=12.0
# fallback constant (0.45deg / 0.035s = ~12.86 deg/s -- the same figure,
# derived a different way in a different file).
MIN_HOLD_S = 0.035
DEG_PER_MIN_HOLD = 0.45
RATE_DEG_S = DEG_PER_MIN_HOLD / MIN_HOLD_S  # ~12.86 deg/s while the relay is engaged

# Hysteresis thresholds, same shape as rotary_encoder_driver.py's inner loop:
# start moving once |error| exceeds HIGH, stop once it drops below LOW. LOW <
# HIGH avoids chatter right at the setpoint. LOW should not be smaller than
# roughly one MIN_HOLD_S worth of motion (~0.45 deg), or the controller will
# ask to stop before a single pulse could have gotten there and can overshoot
# by a full pulse every time instead of settling.
ANGLE_THRESHOLD_HIGH_DEG = 1.0
ANGLE_THRESHOLD_LOW_DEG = 0.5

# Actuation delay before anything is learned. The cart's is ~0.1-0.15 s from
# command to the wheels starting to move (owner, 2026-10-15); the controller
# measures its own once the wheels have moved.
INITIAL_DELAY_S = 0.12


class RelaySteeringController:
    """Relay controller with actuation-delay compensation:
    ``(target_deg, encoder_deg, now_s) -> relay``.

    The wheels act on a command only some time after it is sent, and may keep
    moving for some time after a stop. A controller that stops when the
    *encoder* reaches the target therefore overruns by rate x stop delay
    (~2 deg at 150 ms), restarts the other way and hunts. This one keeps the
    history of what it sent, adds the motion already commanded but not yet
    visible to the encoder reading (a Smith predictor), and decides from that
    predicted angle, so the stop goes out early by the right amount.

    The actuator is learned, not assumed. Once a second it fits, to the last
    few seconds of commands and encoder readings:
      d_start  delay from a move command to the wheels moving,
      d_stop   delay from a stop command to the wheels stopping (run-on),
      gain     wheel speed relative to RATE_DEG_S.
    A pulse shorter than d_start - d_stop would move nothing, so pulses are
    never shorter; and the deadband is widened to the smallest step a pulse
    can make, so run-on cannot force a pulse back the other way.

    Also:
      * direction never reverses without a stop in between;
      * a move whose wheels stop responding (mechanical lock, stalled motor)
        is stopped after STALL_S rather than driven into the stop forever, and
        targets beyond that angle are limited to it from then on.

    ``now_s`` must be monotonic seconds on the same clock as the encoder
    readings (wall clock on the cart, simulation time in tesla_sim).
    """

    HISTORY_S = 6.0
    FIT_WINDOW_S = 5.0
    FIT_GRID = np.arange(0.0, 0.51, 0.025)
    STALL_S = 0.5            # a move with less than STALL_DEG of motion for this long has stalled
    STALL_DEG = 0.2

    def __init__(self, initial_delay_s=INITIAL_DELAY_S, adapt=True):
        self.d_start = initial_delay_s
        self.d_stop = initial_delay_s
        self.gain = 1.0
        self.adapt = adapt
        self.fits = 0
        self.reset()

    @property
    def relay(self):
        return self._relay

    def reset(self):
        self._relay = RELAY_STOP
        self._dir = 0
        self._changed = -1e9
        self._hist = []                  # (time, encoder deg, direction in force from then on)
        self._last_fit = -1e9
        self._progress = None            # (time, encoder deg) of the current move's last real progress
        self.limits = {}                 # direction -> angle where a move stalled (lock)

    # -- actuator model ----------------------------------------------------
    @property
    def min_hold_s(self):
        """Shortest pulse certain to move the wheels."""
        return max(MIN_HOLD_S, self.d_start - self.d_stop + MIN_HOLD_S)

    @property
    def min_step_deg(self):
        """Smallest wheel movement one pulse can produce."""
        return RATE_DEG_S * self.gain * max(self.min_hold_s + self.d_stop - self.d_start, 0.0)

    def _pulses(self, now):
        """[(start, end, dir)] of commanded moves; the one in progress ends at ``now``."""
        out, cur = [], None
        for t, _, d in self._hist:
            if cur is not None and d == cur[2]:
                continue
            if cur is not None:
                out.append((cur[0], t, cur[2]))
            cur = (t, None, d) if d != 0 else None
        if cur is not None:
            out.append((cur[0], now, cur[2]))
        return out

    def committed_deg(self, now):
        """Wheel motion already commanded but not yet seen, if a stop were sent now."""
        total = 0.0
        for a, b, d in self._pulses(now):
            lo, hi = max(now, a + self.d_start), b + self.d_stop
            if hi > lo:
                total += d * (hi - lo)
        return total * RATE_DEG_S * self.gain

    def _fit(self, now):
        hist = [e for e in self._hist if e[0] >= now - self.FIT_WINDOW_S]
        if len(hist) < 20:
            return
        t = np.array([e[0] for e in hist])
        enc = np.array([e[1] for e in hist])
        if np.ptp(enc) < 1.0:
            return                                       # too little motion to learn from
        pulses = self._pulses(now)
        if not pulses:
            return
        step = max(1, len(t) // 100)                     # <= ~100 samples: cheap enough at 1 Hz
        t, enc = t[::step], enc[::step]
        a = np.array([p[0] for p in pulses])
        b = np.array([p[1] for p in pulses])
        d = np.array([p[2] for p in pulses], dtype=float)
        g = self.FIT_GRID
        lo = a[None, None, :, None] + g[:, None, None, None]          # (S, 1, N, 1)
        hi = b[None, None, :, None] + g[None, :, None, None]          # (1, P, N, 1)
        moved = np.clip(np.minimum(t[None, None, None, :], hi) - lo, 0.0, None)   # (S, P, N, K)
        model = (moved * d[None, None, :, None]).sum(axis=2) * RATE_DEG_S          # (S, P, K)
        model -= model[..., :1]
        enc0 = enc - enc[0]
        den = (model * model).sum(axis=2)
        gain = np.clip((model * enc0).sum(axis=2) / np.maximum(den, 1e-9), 0.4, 1.6)
        cost = ((gain[..., None] * model - enc0) ** 2).mean(axis=2)
        cost[den < 1e-6] = np.inf
        i, j = np.unravel_index(np.argmin(cost), cost.shape)
        best = cost[i, j]
        if best >= 0.5 * float(np.var(enc)):              # the model does not explain the motion
            return

        def pinned(curve, idx):
            """Is the minimum sharp? Moving 50 ms either way must cost clearly more;
            otherwise this window says nothing about that delay (e.g. the move's
            start lies before the window) and it is left alone."""
            near = [curve[idx + o] for o in (-2, 2) if 0 <= idx + o < len(curve)]
            return min(near) > 1.2 * best + 1e-6
        k = 0.5
        if pinned(cost[:, j], i):
            self.d_start = (1 - k) * self.d_start + k * float(g[i])
        if pinned(cost[i, :], j):
            self.d_stop = (1 - k) * self.d_stop + k * float(g[j])
        self.gain = (1 - k) * self.gain + k * float(gain[i, j])
        self.fits += 1

    # -- control -----------------------------------------------------------
    def update(self, target_deg, encoder_deg, now_s):
        while self._hist and self._hist[0][0] < now_s - self.HISTORY_S:
            self._hist.pop(0)
        if self.adapt and now_s - self._last_fit >= 1.0:
            self._last_fit = now_s
            self._fit(now_s)

        for d, lim in self.limits.items():
            target_deg = min(target_deg, lim) if d > 0 else max(target_deg, lim)
        predicted = encoder_deg + self.committed_deg(now_s)
        held = (now_s - self._changed) >= self.min_hold_s
        hi = max(ANGLE_THRESHOLD_HIGH_DEG, 0.75 * self.min_step_deg)
        lo = max(ANGLE_THRESHOLD_LOW_DEG, 0.35 * self.min_step_deg)
        if self._dir == 0:
            err = target_deg - predicted
            if held and err > hi:
                self._set(+1, now_s, encoder_deg)
            elif held and err < -hi:
                self._set(-1, now_s, encoder_deg)
        else:
            remaining = self._dir * (target_deg - predicted)
            stalled = self._stalled(encoder_deg, now_s)
            if stalled:
                # ponytail: any stall becomes a permanent limit until reset(); a
                # transient motor hiccup would cap the range. Fine while the lock
                # is the only thing that stalls it.
                self.limits[self._dir] = encoder_deg
                # The commanded motion did not happen: that history would teach
                # the fit nonsense (a slow, late actuator). Start learning afresh.
                self._hist = []
            if held and (remaining <= lo or stalled):
                self._set(0, now_s, encoder_deg)
        # the command in force from now on, stamped with when it is sent
        self._hist.append((now_s, encoder_deg, self._dir))
        return self._relay

    def _stalled(self, encoder_deg, now_s):
        t0, e0 = self._progress
        if self._dir * (encoder_deg - e0) >= self.STALL_DEG:
            self._progress = (now_s, encoder_deg)
            return False
        return now_s - t0 > self.d_start + self.STALL_S

    def _set(self, d, now_s, encoder_deg):
        self._dir = d
        self._relay = RELAY_RIGHT if d > 0 else RELAY_LEFT if d < 0 else RELAY_STOP
        self._changed = now_s
        self._progress = (now_s, encoder_deg) if d else None
