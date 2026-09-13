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

RELAY_LEFT = 49
RELAY_STOP = 50
RELAY_RIGHT = 51

# Real hardware timing, from cart_controller/README.md (independently
# verified against that file directly -- see
# private-notes/tesla_sim/03-established-facts.md): the motor takes ~30ms to
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


class RelaySteeringController:
    """Hysteresis relay controller: (target_deg, encoder_deg, now_s) -> relay.

    Call `update()` once per control tick. `now_s` must be a monotonic
    seconds value (e.g. `time.monotonic()`, or a ROS/Webots clock's seconds)
    -- used only to enforce MIN_HOLD_S, matching the real relay's minimum
    reaction time. Direction reversal always passes through RELAY_STOP first
    (the state machine below has no LEFT->RIGHT or RIGHT->LEFT edge at all,
    both must go through STOP) -- this is a deliberate safety property carried
    over from rotary_encoder_driver.py's MotorController, not an oversight.
    """

    def __init__(self):
        self._relay = RELAY_STOP
        self._last_change_s = None

    @property
    def relay(self):
        return self._relay

    def reset(self):
        self._relay = RELAY_STOP
        self._last_change_s = None

    def update(self, target_deg, encoder_deg, now_s):
        error = target_deg - encoder_deg

        if self._relay == RELAY_STOP:
            # Starting a new pulse has no minimum-wait -- only an already-
            # engaged pulse has a minimum hold before it may stop or reverse.
            if error > ANGLE_THRESHOLD_HIGH_DEG:
                self._set(RELAY_RIGHT, now_s)
            elif error < -ANGLE_THRESHOLD_HIGH_DEG:
                self._set(RELAY_LEFT, now_s)
        else:
            held_long_enough = (now_s - self._last_change_s) >= MIN_HOLD_S
            if not held_long_enough:
                return self._relay
            if self._relay == RELAY_RIGHT and error < ANGLE_THRESHOLD_LOW_DEG:
                self._set(RELAY_STOP, now_s)
            elif self._relay == RELAY_LEFT and error > -ANGLE_THRESHOLD_LOW_DEG:
                self._set(RELAY_STOP, now_s)

        return self._relay

    def _set(self, relay, now_s):
        self._relay = relay
        self._last_change_s = now_s
