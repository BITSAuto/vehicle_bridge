# Testing without hardware

## A fake MCU on a pseudo-terminal exercised the whole encoder path
On 2026-10-02 a fake MCU streamed counts over a pty (with a non-zero
power-up origin, a boot banner line and 100 Hz output). It tested parsing,
zeroing, `~/zero`, reconnects and the bridge's staleness stop with no
hardware. Killing the fake also reproduced the real failure mode of a
disappearing USB device (`[Errno 5] Input/output error`, then the path
vanishing), which the reconnect loop now handles. The script lived in a
scratch directory and wasn't kept; [08-guides/testing-with-a-fake-mcu.md](../08-guides/testing-with-a-fake-mcu.md)
describes how to recreate it.

## Dry run against tesla_sim
`dry_run:=true` against the live sim's `/cmd_ackermann` and
`/steering/angle` tests everything except the serial port. Parity of relay
decisions is guaranteed by the shared class, not by that test.

## What these can't tell you
The real MCU's format and scale, the throttle mapping, the board's replies,
real motor timing. Those need the cart.
