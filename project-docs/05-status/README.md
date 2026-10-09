# 05 · Status

| Page | Contents |
| --- | --- |
| [completed.md](completed.md) | Finished work, with PRs |
| [in-progress.md](in-progress.md) | Work started but not merged |
| [roadmap.md](roadmap.md) | Next steps and what they depend on |

## Snapshot (2026-10-09)
- `main` = `499afb2`: serial bridge, relay controller, encoder node,
  emergency-brake topic.
- **Never run on the powered cart.** Tested in dry run against tesla_sim and
  against a fake encoder MCU.
- **Before the first powered test:** add a command timeout
  ([Q-006](../06-open-questions/Q-006-no-command-timeout.md)), calibrate the
  encoder, and verify the throttle mapping at low speed.
