# 2026-09-09 · Serial bridge and shared relay controller

**Who:** project owner, with Claude Code
**Goal:** convert ROS commands to the cart's serial protocol, with steering closed over an encoder, and make tesla_sim steer the same way.

## What was done
- Read the three legacy protocol scripts and `cart_contorller`'s README
  ([legacy-code.md](../04-knowledge/legacy-code.md)).
- Wrote `serial_command.py`, `relay_steering.py`, `serial_bridge_node.py`
  ([D-001](../03-decisions/D-001-separate-package-for-real-vehicle-io.md)–[D-006](../03-decisions/D-006-hold-neutral-and-stop-without-fresh-feedback.md), [D-010](../03-decisions/D-010-brake-on-shutdown.md)).
- Caught a no-op in the "no encoder" branch before running it (M-01).
- tesla_sim switched to the shared controller.

## Results
- [sim-parity-dry-run.md](../09-testing-and-results/sim-parity-dry-run.md).
