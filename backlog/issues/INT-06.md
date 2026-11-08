---
id: INT-06
title: "Decide how Superpowers reaches every Copilot surface (ENG-D2)"
milestone: "M0"
labels: [type:decision, area:copilot, human-only, priority:P1, size:S]
---
## Context

Superpowers (obra/superpowers, MIT) is the engineering method of this repository. Copilot CLI installs it as a plugin; VS Code and the CLI read personal skills from ~/.copilot/skills; Copilot cloud agent sessions on GitHub Actions read only project skills (.github/skills, .claude/skills or .agents/skills).

## Acceptance criteria

- [ ] Option chosen: (a) personal installs only, (b) vendor the pinned skills into .agents/skills with a lock file, or (c) both (recommended)
- [ ] ADR-0021 accepted or amended
- [ ] If vendored: `python tools/superpowers.py vendor` run by a person, licence notice added, `superpowers.py verify` passes in CI

## Source

docs/engineering/copilot-and-superpowers.md; docs/adr/0021-ai-assisted-engineering.md
