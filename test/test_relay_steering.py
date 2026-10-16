"""RelaySteeringController against a simulated relay actuator."""
import pytest

from vehicle_bridge.relay_steering import (RATE_DEG_S, RELAY_LEFT, RELAY_RIGHT, RELAY_STOP,
                                           RelaySteeringController)

TICK = 0.025      # serial_bridge_node's control tick


def drive(targets, start_delay, stop_delay, rate_scale=1.0, lock_deg=30.0, ctrl=None, seconds_each=3.0):
    """Step through ``targets``; the wheels obey each relay value from
    send + start_delay (moves) or send + stop_delay (stops), and a stop that
    lands before its move cancels it. Returns (ctrl, relay log, angle log)."""
    ctrl = ctrl or RelaySteeringController()
    angle, t, sent = 0.0, 0.0, []          # sent: (time effective, relay)
    relays, angles = [], []
    for target in targets:
        for _ in range(int(seconds_each / TICK)):
            r = ctrl.update(target, angle, t)
            if not relays or r != relays[-1]:
                at = t + (stop_delay if r == RELAY_STOP else start_delay)
                sent = [s for s in sent if s[0] < at]
                sent.append((at, r))
            relays.append(r)
            for sub in range(5):            # actuator at 200 Hz
                now = t + sub * TICK / 5
                active = RELAY_STOP
                for at, v in sent:
                    if at <= now:
                        active = v
                step = RATE_DEG_S * rate_scale * TICK / 5
                if active == RELAY_RIGHT:
                    angle = min(lock_deg, angle + step)
                elif active == RELAY_LEFT:
                    angle = max(-lock_deg, angle - step)
            angles.append(angle)
            t += TICK
    return ctrl, relays, angles


def switches(relays):
    return sum(1 for a, b in zip(relays, relays[1:]) if a != b)


STEPS = [8.0, -6.0, 3.0, 0.0, 10.0, 4.0, -9.0, -2.0, 6.0, 0.0]


@pytest.mark.parametrize('start,stop,scale', [
    (0.0, 0.0, 1.0),
    (0.12, 0.12, 1.0),       # the cart, as described: ~0.1-0.15 s each way
    (0.15, 0.05, 1.0),       # slow start, quick stop: short pulses do nothing
    (0.05, 0.20, 1.0),       # run-on after a stop
    (0.12, 0.12, 0.7),       # slower wheels
])
def test_settles_without_hunting(start, stop, scale):
    ctrl, relays, angles = drive(STEPS * 2, start, stop, scale)
    # Second pass through the steps: the actuator has been learned by then.
    n = len(STEPS) * int(3.0 / TICK)
    for k, target in enumerate(STEPS):
        settled = angles[n + (k + 1) * int(3.0 / TICK) - 1]
        assert abs(settled - target) < 1.6, (k, target, settled)
    assert switches(relays[n:]) <= 4 * len(STEPS)          # ~one move + one stop per step, little hunting
    assert abs(ctrl.d_start - start) < 0.08 and abs(ctrl.d_stop - stop) < 0.15


def test_never_reverses_without_stopping():
    _, relays, _ = drive(STEPS, 0.12, 0.12)
    for a, b in zip(relays, relays[1:]):
        assert {a, b} != {RELAY_LEFT, RELAY_RIGHT}


def test_never_sends_a_pulse_too_short_to_move():
    ctrl, _, _ = drive(STEPS * 2, 0.2, 0.05)
    assert ctrl.min_hold_s >= 0.15


def test_stops_pushing_against_the_lock():
    # Target beyond the mechanical lock: the move must be stopped, not held forever.
    _, relays, angles = drive([20.0], 0.1, 0.1, lock_deg=12.0, seconds_each=4.0)
    assert angles[-1] == pytest.approx(12.0, abs=0.1)
    assert relays[-1] == RELAY_STOP


def test_beats_the_naive_controller_on_overrun():
    """Without compensation (initial delay 0, no learning) the stop goes out late."""
    naive = RelaySteeringController(initial_delay_s=0.0, adapt=False)
    _, _, a_naive = drive([8.0], 0.15, 0.15, ctrl=naive)
    _, _, a_comp = drive([8.0], 0.15, 0.15)
    overrun_naive = max(a_naive) - 8.0
    overrun_comp = max(a_comp) - 8.0
    assert overrun_naive > 1.5 and overrun_comp < 0.8
