# vehicle_bridge · Project docs

The shared engineering record for **vehicle_bridge**, the ROS 2 interface to
the real BITSAuto cart: serial drive-by-wire, relay steering, the steering
encoder and the emergency brake. Everything someone joining the project
needs should be findable from here. The usage summary is the top-level
[README](../README.md).

## Start here

| If you are... | Read |
| --- | --- |
| new to the project | [01-overview](01-overview/README.md), then [05-status](05-status/README.md) |
| going to the cart | [first-powered-test.md](08-guides/first-powered-test.md) and the [open questions](06-open-questions/README.md) |
| about to change code | the [decisions](03-decisions/README.md), [safety behaviour](02-architecture/safety-behaviour.md) and [bugs-and-lessons](07-bugs-and-lessons/README.md) |
| an AI agent | [AGENTS.md](../AGENTS.md), then this page |

## Status at a glance (2026-10-09)

Serial bridge, shared relay controller, encoder node and emergency-brake
topic are on `main`. **Never run on the powered cart**; tested in dry run
against tesla_sim and with a fake encoder MCU. Before the first powered test:
add a command timeout (Q-006), calibrate the encoder (Q-003), check the
throttle mapping (Q-001). The cart also has no speed source yet (Q-004).

## Contents

1. **[Overview](01-overview/README.md)** —
   [project brief](01-overview/project-brief.md) ·
   [system map](01-overview/system-map.md) ·
   [hardware and environment](01-overview/hardware-and-environment.md) ·
   [glossary](01-overview/glossary.md)
2. **[Architecture](02-architecture/README.md)** —
   [components](02-architecture/components.md) ·
   [interfaces](02-architecture/interfaces.md) ·
   [serial protocol](02-architecture/serial-protocol.md) ·
   [relay steering controller](02-architecture/relay-steering-controller.md) ·
   [encoder](02-architecture/encoder.md) ·
   [safety behaviour](02-architecture/safety-behaviour.md)
3. **[Decisions](03-decisions/README.md)** — D-001 to D-011
4. **[Knowledge](04-knowledge/README.md)** —
   [serial protocol facts](04-knowledge/serial-protocol-facts.md) ·
   [steering hardware](04-knowledge/steering-hardware.md) ·
   [encoder facts](04-knowledge/encoder-facts.md) ·
   [legacy code](04-knowledge/legacy-code.md) ·
   [speed and throttle](04-knowledge/speed-and-throttle.md)
5. **[Status](05-status/README.md)** —
   [completed](05-status/completed.md) ·
   [in progress](05-status/in-progress.md) ·
   [roadmap](05-status/roadmap.md)
6. **[Open questions](06-open-questions/README.md)** — Q-001 to Q-010
7. **[Bugs and lessons](07-bugs-and-lessons/README.md)** —
   [bridge bugs](07-bugs-and-lessons/bridge-bugs.md) ·
   [testing without hardware](07-bugs-and-lessons/testing-without-hardware.md)
8. **[Guides](08-guides/README.md)** —
   [setup and build](08-guides/setup-and-build.md) ·
   [running on the cart](08-guides/running-on-the-cart.md) ·
   [calibrating the encoder](08-guides/calibrating-the-encoder.md) ·
   [first powered test](08-guides/first-powered-test.md) ·
   [dry run against tesla_sim](08-guides/dry-run-against-tesla-sim.md) ·
   [testing with a fake MCU](08-guides/testing-with-a-fake-mcu.md)
9. **[Testing and results](09-testing-and-results/README.md)** —
   [unit tests](09-testing-and-results/unit-tests.md) ·
   [fake MCU test](09-testing-and-results/fake-mcu-test.md) ·
   [sim parity dry run](09-testing-and-results/sim-parity-dry-run.md) ·
   [real hardware results](09-testing-and-results/real-hardware-results.md)
10. **[Worklog](10-worklog/README.md)** — one page per work session

## How to keep this book current

This book is only useful if it is never stale. **Every piece of work updates
it in the same branch or PR** as the work itself: code, experiments,
debugging, field tests, measurements, and decisions made in a meeting or a
chat. A PR without a docs update is incomplete (the PR template has the
checklist).

| When you... | Update |
| --- | --- |
| do any work at all | add a page to `10-worklog/` (copy the template in its README) and adjust `05-status/` |
| decide something (including "we won't do X") | add `03-decisions/D-NNN-slug.md` and a row in its index. To reverse a decision, add a new one that supersedes it and mark the old one *Superseded by D-NNN*; don't delete it |
| verify a fact (measurement, datasheet, reading source code, a live test) | add it to the right page in `04-knowledge/` with a confidence tag and *how* it was checked |
| hit something unknown that matters | add `06-open-questions/Q-NNN-slug.md` and a row in its index |
| answer an open question | set its status to *Resolved*, say what resolved it and link to where the answer now lives; keep the page |
| find a bug (yours or anyone's) | record it in `07-bugs-and-lessons/`: symptom, root cause, fix, and the rule that would have prevented it |
| change how to build, run, deploy or calibrate | update `08-guides/` |
| get a new test or scenario result | update `09-testing-and-results/` |
| change architecture, topics, parameters or conventions | update `02-architecture/` |

**Writing rules**
- **Append, don't rewrite history.** If something written here turns out to be
  wrong, add a dated *Correction (YYYY-MM-DD):* under it. Knowing that
  something was believed and then disproved is useful.
- **Say how you know.** Confidence tags: **Verified** (checked directly
  against source code, a live system or a measurement; say which),
  **Documented** (from a datasheet or other docs, not re-checked here),
  **Assumed** (a guess, placeholder or inference; must also appear in open
  questions if it matters). Never let repetition upgrade an assumption.
- **Date everything** (YYYY-MM-DD) and link PRs, commits and issues.
- **One topic per page.** Add pages rather than growing one page forever.
  Each chapter's `README.md` lists its pages; keep that list in sync.
- **Link, don't duplicate.** Facts about another repo's component belong in
  that repo's book; link to it.
- **No secrets or personal details.** No passwords, tokens, private IPs,
  personal machine configs or e-mail addresses. Three of our repos are
  public.
- **Write for someone who wasn't there.** Spell out the why, not just the
  what.
