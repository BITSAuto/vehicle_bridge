# Testing `encoder_node` with a fake MCU

A pseudo-terminal stands in for the encoder's USB serial port.

```python
# fake_mcu.py: prints its device path, then streams counts at 100 Hz
import os, pty, time, tty
master, slave = pty.openpty()
tty.setraw(slave)
print('fake encoder MCU on', os.ttyname(slave), flush=True)
count = 1234                      # non-zero power-up origin
os.write(master, b'BOOT encoder v1\r\n')
while True:
    os.write(master, f'{count}\r\n'.encode())
    count += 3                    # steering slowly to one side
    time.sleep(0.01)
```

```bash
python3 fake_mcu.py                         # note the /dev/pts/N it prints
ros2 launch vehicle_bridge vehicle_bridge.launch.py dry_run:=true encoder_port:=/dev/pts/N
ros2 topic hz /steering/angle               # ~100 Hz
ros2 service call /encoder_node/zero std_srvs/srv/Trigger
```
Things to check (what the 2026-10-02 test checked): the boot banner is
ignored; the first reading becomes zero; `~/zero` re-zeroes; killing the
fake makes `encoder_node` log a serial error and retry every second and the
bridge log "forcing neutral+stop" within 0.5 s; restarting the fake (same
path may change) reconnects and re-zeroes.

The script above was checked to emit the expected bytes (2026-10-09); the
original 2026-10-02 script wasn't kept.
