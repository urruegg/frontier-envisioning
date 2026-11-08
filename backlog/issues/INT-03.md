---
id: INT-03
title: "Commit dependency lockfiles and pin the toolchain"
milestone: "M0"
labels: [type:chore, area:engineering, agent:copilot, priority:P1, size:S]
---
## Context

The development dependencies (pytest, ruff, PyYAML, happy-dom, Playwright, ESLint) are declared with version ranges; the starting point has no lockfile because it was prepared offline.

## Acceptance criteria

- [ ] `package-lock.json` committed; CI uses `npm ci`
- [ ] `requirements-dev.txt` pins exact versions
- [ ] Dependabot groups the updates weekly (pip, npm, GitHub Actions)
- [ ] `python tools/dev.py doctor` shows every tool on a fresh dev container
