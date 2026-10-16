"""Fake drive-by-wire board + steering encoder MCU, for testing the bridge with no hardware.

    python3 tools/fake_cart.py    # prints the two /dev/pts paths for serial_port:= and encoder_port:=

Two ptys.
Board: parses *A..B<thr>..D<relay>..I<brake>..J..#, streams 'OK' replies nonstop,
applies relay moves after DELAY s, integrates the wheel angle at 12.86 deg/s, lock +/-20.
Encoder: streams count = angle / 0.006 at 100 Hz. Logs one line per second to stdout."""
import os, pty, re, time, tty
DELAY, RATE, LOCK, DPC = 0.12, 12.86, 20.0, 0.006
bm, bs = pty.openpty(); em, es = pty.openpty()
for fd in (bs, es): tty.setraw(fd)
os.set_blocking(bm, False)
print('BOARD', os.ttyname(bs), 'ENCODER', os.ttyname(es), flush=True)
angle, pending, active = 0.0, [], 50
buf, frames, last_frame_t, max_gap = b'', 0, None, 0.0
thr = brake = 50
t_prev = t_log = t_enc = time.monotonic()
while True:
    now = time.monotonic()
    try:
        buf += os.read(bm, 4096)
    except (BlockingIOError, OSError):
        pass
    for m in re.finditer(rb'\*A\d+B(\d+)C\d+D(\d+)E\d+F\d+G\d+H\d+I(\d+)J\d+#', buf):
        thr, relay, brake = int(m.group(1)), int(m.group(2)), int(m.group(3))
        pending.append((now + DELAY, relay)); frames += 1
        if last_frame_t is not None:
            max_gap = max(max_gap, now - last_frame_t)
        last_frame_t = now
    buf = buf[buf.rfind(b'#') + 1:] if b'#' in buf else buf
    try:
        os.write(bm, b'OK\r\n')                      # a board that never stops replying
    except OSError:
        pass
    while pending and pending[0][0] <= now:
        active = pending.pop(0)[1]
    dt = now - t_prev; t_prev = now
    if active == 51: angle = min(LOCK, angle + RATE * dt)
    elif active == 49: angle = max(-LOCK, angle - RATE * dt)
    if now - t_enc >= 0.01:
        t_enc = now
        try: os.write(em, f'{round(angle / DPC)}\r\n'.encode())
        except OSError: pass
    if now - t_log >= 1.0:
        print(f'{now:.1f} angle={angle:+6.2f} relay={active} throttle={thr} brake={brake} frames/s={frames} max_gap_ms={max_gap*1000:.0f}', flush=True)
        t_log, frames, max_gap = now, 0, 0.0
    time.sleep(0.002)
