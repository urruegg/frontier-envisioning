---
id: INT-09
title: "Reproducible blueprint builds (SOURCE_DATE_EPOCH)"
milestone: "1.7.0"
labels: [type:chore, area:plugin, agent:copilot, priority:P2, size:S]
---
## Context

`build_blueprint.py` writes today's date into `meta.generated`, so the demo HTML differs from day to day; the release check normalises the date.

## Acceptance criteria

- [ ] `build_blueprint.py` uses SOURCE_DATE_EPOCH when set
- [ ] The release workflow sets SOURCE_DATE_EPOCH from the tag commit
- [ ] `verify_release.py` compares the demo without normalisation for 1.7.0 manifests
