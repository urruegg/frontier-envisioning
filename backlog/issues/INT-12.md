---
id: INT-12
title: "Turn on Copilot cloud agent, code review and hooks"
milestone: "M0"
labels: [type:chore, area:copilot, human-only, priority:P1, size:S]
---
## Context

The repository carries custom instructions, path instructions, custom agents, project skills, hooks and a setup-steps workflow for Copilot.

## Acceptance criteria

- [ ] Copilot cloud agent enabled for the repository
- [ ] Automatic Copilot code review on pull requests
- [ ] `copilot-setup-steps` workflow green
- [ ] Guard hook verified in a test session (for example a denied `gh pr merge`)
- [ ] MCP servers for the cloud agent configured if needed (Microsoft Learn)

## Source

docs/engineering/copilot-and-superpowers.md
