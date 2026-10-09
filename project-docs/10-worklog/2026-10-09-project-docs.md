# 2026-10-09 · Project docs

**Who:** project owner, with Claude Code
**Branch / PR:** `docs/project-docs`

- Created this book from tesla_sim's private notes (where vehicle_bridge's
  history lived), the README, git history and session records
  ([D-011](../03-decisions/D-011-project-docs.md)).
- Reviewing the code for it found that the bridge has **no `/cmd_ackermann`
  timeout** ([Q-006](../06-open-questions/Q-006-no-command-timeout.md), high
  priority) and a stale docstring (M-05, fixed).
- Code comments that referenced the private notes now point here.
