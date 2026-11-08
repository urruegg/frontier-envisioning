---
id: INT-11
title: "Unit tests per plugin script"
milestone: "M0"
labels: [type:chore, area:engineering, agent:copilot, priority:P2, size:L]
---
## Context

The plugin scripts are tested end to end by `tools/selftest.py` (29 checks). Focused unit tests make failures easier to locate and enable a coverage floor.

## Acceptance criteria

- [ ] Unit tests for context_pack, parse_transcript, canon, merge_feedback, value_calc, finops_calc and seed_identity
- [ ] Coverage measured in CI (pytest-cov); a floor agreed after the first measurement
- [ ] `tools/selftest.py` stays the end-to-end test
