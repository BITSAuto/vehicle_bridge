"""Single source of truth for the vehicle's serial drive-by-wire protocol.

Wire format:
    *A{a}B{throttle}C{c}D{steering}E{left_ind}F{horn}G{light}H{right_ind}I{brake}J{reverse}#
9600 baud, 8N1, no flow control.

This exact function was independently copy-pasted four times before this
package existed: road_segmentation's drivebywire.py, rotary_encoder_driver.py,
and cart_controller's controller.py all define byte-for-byte the same
`build_serial_command`. This module replaces all of those call sites' need to
keep their own copy in sync -- see private-notes/tesla_sim/02-decision-log.md
for why a shared module was chosen over a fifth copy in vehicle_bridge itself.

Channel meanings, from reading the above three scripts:
    A            unused in every script read (always 0)
    B throttle   byte 0-100. 50 = neutral/coast, >50 = forward, <50 = braking
                 (per rotary_encoder_driver.py's own header comment). No
                 script read here ever exercises the <50 braking range or
                 ties it to a specific ROS input -- treat as unverified.
    C            unused in every script read (always 0)
    D steering   RELAY_LEFT (49) / RELAY_STOP (50) / RELAY_RIGHT (51). Not a
                 proportional value -- see relay_steering.py. The real motor
                 "has infinite run-on and does not stop by itself" until 50
                 is explicitly sent (cart_controller/README.md).
    E left indicator, F horn, G light, H right indicator   0/1, no ROS
                 mapping exists yet anywhere in this workspace.
    I brake      0/1, no ROS mapping exists yet.
    J reverse    0/1, gear-selection flag, separate from the throttle byte.
"""

SERIAL_BAUD = 9600

THROTTLE_NEUTRAL = 50  # a byte value (0-100), not a percent


def build_serial_command(
    a_val=0, b_throttle=THROTTLE_NEUTRAL, c_val=0, d_steering=50,
    e_left_indicator=0, f_horn=0, g_light=0,
    h_right_indicator=0, i_brake=0, j_reverse=0,
):
    return (
        f"*A{a_val}"
        f"B{b_throttle}"
        f"C{c_val}"
        f"D{d_steering}"
        f"E{e_left_indicator}"
        f"F{f_horn}"
        f"G{g_light}"
        f"H{h_right_indicator}"
        f"I{i_brake}"
        f"J{j_reverse}#"
    )
