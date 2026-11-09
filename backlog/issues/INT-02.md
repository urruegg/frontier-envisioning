---
id: INT-02
title: "L1 quality gate green on the import commit; release 1.4.0 reproduced"
milestone: "M0"
labels: [type:chore, area:engineering, priority:P1, size:S]
---
## Context

The import must prove that nothing was lost: the repository rebuilds the published 1.4.0 artefacts.

## Acceptance criteria

- [ ] `ci` workflow green on main
- [ ] `verify-release`: 4 of 4 artefacts reproduced (plugin package, demo blueprint, identity kit, catalogue)
- [ ] Self-test 29 of 29, DOM tests and unit tests pass; neutrality scan 0 findings
- [ ] Build artefacts (package, demo) attached to the run

## Source

releases/1.4.0/manifest.json; docs/engineering/intake-plan.md
