---
id: INT-08
title: "Ratchet the lint rules (ruff, ESLint)"
milestone: "M0"
labels: [type:chore, area:engineering, agent:copilot, priority:P3, size:M]
---
## Context

The starting point runs ruff with the error rules only (syntax errors, undefined names) and ESLint with the recommended rules, where unused variables and needless escapes are warnings. ESLint reports 7 warnings in the renderer: three unused functions, one unused variable and three needless escapes.

## Acceptance criteria

- [ ] ruff rule set extended (E, F, W, I, B, UP) with the fixes, tools/ and tests/ first
- [ ] Renderer findings fixed and the warnings turned into errors
- [ ] Changes to plugin/ or src/renderer/ ship with the next approved release (version bump first)
