---
id: INT-01
title: "Bootstrap the GitHub repository and protect main"
milestone: "M0"
labels: [type:chore, area:engineering, human-only, priority:P1, size:S]
---
## Context

The repository starting point was prepared in Copilot Cowork from release 1.4.0. It must become a protected GitHub repository before anyone, person or agent, changes it.

## Acceptance criteria

- [ ] Repository created (visibility per ENG-D1) with the import commit on main
- [ ] Ruleset on main: pull request required, status check `L1 quality gate`, no force push, no deletion, code owner review
- [ ] Squash merge only, branches deleted after merge
- [ ] Labels, milestones and the seed issues created from `backlog/`
- [ ] Dependabot alerts and security updates on; secret scanning and push protection on where the plan allows
- [ ] Environments `dev` and `prod` exist; `prod` requires a reviewer

## Notes

Run `python tools/bootstrap_github.py --owner <owner>` (dry run) and then with `--apply`. The script reports settings your GitHub plan does not allow.

## Source

docs/engineering/github-setup.md
