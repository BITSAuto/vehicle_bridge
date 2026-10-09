# 2026-10-02 · Steering encoder node

**Who:** project owner, with Claude Code
**Branch:** `feature/steering-encoder` (`e97d88f`), later merged via [PR #2](https://github.com/BITSAuto/vehicle_bridge/pull/2)
**Goal:** publish `/steering/angle` on the real cart.

## What was done
- `encoder_node` + `encoder.py` + `config/encoder.yaml`; launch starts both
  nodes ([D-008](../03-decisions/D-008-encoder-node-reads-a-separate-mcu.md)).
- Staleness check in the bridge (M-02).
- Removed a README claim that 15° was a measured lock (M-04).

## Results
- [fake-mcu-test.md](../09-testing-and-results/fake-mcu-test.md).

## Left for next time
- Real MCU format and calibration (Q-003), lock angle (Q-005), steering clamp (Q-007), Jazzy (Q-008).
