# 2026-10-08 · Emergency brake topic

**Who:** project owner, with Claude Code
**Branch / PR:** `feat/emergency-brake`, [PR #1](https://github.com/BITSAuto/vehicle_bridge/pull/1) → `feature/steering-encoder`, then [PR #2](https://github.com/BITSAuto/vehicle_bridge/pull/2) → `main` (`499afb2`)
**Goal:** braking only through an explicit emergency input, as part of `cart_driver`'s step 1.

## What was done
- `/vehicle/emergency_brake` → `I1` with neutral throttle; speed 0 always
  coasts; README "Braking: emergency only"
  ([D-009](../03-decisions/D-009-emergency-brake-topic-is-the-only-brake.md)).
- Fixed the brake-release crash (M-03).
