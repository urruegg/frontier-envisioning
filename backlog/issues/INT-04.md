---
id: INT-04
title: "Browser tests baseline and required check"
milestone: "M0"
labels: [type:chore, area:engineering, priority:P1, size:M]
---
## Context

Real-browser tests (Playwright, Chromium) run against the showcase site served with the hosting headers. They were written offline and have not yet run in a browser.

## Acceptance criteria

- [ ] `L2 browser tests` green in CI on the import commit
- [ ] Screenshots of all 14 views attached to the run
- [ ] No Content-Security-Policy violation and no console error
- [ ] The job is a required status check on main

## Source

tests/e2e/blueprint.spec.mjs; docs/engineering/testing-strategy.md
