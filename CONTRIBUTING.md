# Contributing

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Contribution workflow; document revision, not product version |
| References | [Documentation](docs/README.md), [Working agreement](AGENTS.md), [Engineering handbook](docs/engineering/handbook.md), [Work packages](docs/plan/README.md) |

Thank you for improving Frontier Envisioning. People and coding agents follow the same agreement: [AGENTS.md](AGENTS.md). The details are in the [engineering handbook](docs/engineering/handbook.md).

## In short

1. **Start from an issue** that meets the Definition of Ready (label `status:ready`). New ideas: open an issue with the *Feature or change* form; open questions: the *Decision* form.
2. **Spec and plan** for anything beyond a small fix: `docs/spec/YYYY-MM-DD-<topic>-design.md` and `docs/plan/YYYY-MM-DD-<topic>-plan.md`. Link the real issue, [idea](docs/idea/README.md), [spec](docs/spec/README.md), [plan](docs/plan/README.md) and [sprint](docs/sprint/README.md); [legacy plans](docs/plans/README.md) remain historical records.
3. **Branch** `feat/<issue-id>-<topic>` (or `fix/`, `chore/`, `docs/`), **test first**, small commits with conventional messages (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`).
4. **Verify**: `python tools/dev.py check` ends with `ALL GATES PASSED`; renderer changes also `python tools/dev.py site e2e`.
5. **Pull request** with the template filled in and the gate summary pasted. A code owner reviews; a person merges (squash).

## Rules you cannot skip

- No real customer names, people or engagement details anywhere: the demo company is the fictitious Caldova Industrial AG.
- Plugin scripts use the Python standard library only and run offline.
- Never hand-edit generated files (the blueprint template, `plugin/install/plugin-install.json`).
- The first change to `plugin/` after a release bumps the version (`python tools/dev.py bump X.Y.Z`).
- Microsoft product icons stay within Microsoft's icon terms.

## Set up

Dev container (recommended) or locally: Python 3.11+, Node.js 22+, Git; then `python tools/dev.py setup` and `pre-commit install`. See [workstation setup](docs/engineering/workstation-setup.md).
