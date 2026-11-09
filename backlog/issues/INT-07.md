---
id: INT-07
title: "Pin GitHub Actions to commit SHAs"
milestone: "M0"
labels: [type:chore, area:engineering, agent:copilot, priority:P2, size:S]
---
## Context

Workflows reference actions by major version tag. Pinning to a full commit SHA protects the supply chain.

## Acceptance criteria

- [ ] Every `uses:` pinned to a 40-character SHA with the version in a comment
- [ ] Dependabot updates the pins
- [ ] `tools/check_repo.py` still passes
