# Setup and build

```bash
sudo apt install ros-$ROS_DISTRO-ackermann-msgs python3-serial
cd ~/ros2_ws/src && git clone https://github.com/BITSAuto/vehicle_bridge.git
cd ~/ros2_ws && PYTHONNOUSERSITE=1 colcon build --symlink-install --packages-select vehicle_bridge
```
- `PYTHONNOUSERSITE=1` avoids a newer `setuptools` in `~/.local` breaking
  `ament_python` builds (seen on the laptop).
- With `--symlink-install`, edits to `config/encoder.yaml` take effect on the
  next launch without rebuilding.
- Serial access: `sudo usermod -a -G dialout $USER`, then log out and in.
- tesla_sim needs this package in the same workspace (it imports
  `relay_steering`).
