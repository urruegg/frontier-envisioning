# Copilot instructions: Frontier Envisioning

This repository builds **Frontier Envisioning**, a Copilot Cowork plugin (MIT) for Microsoft Innovation Hub solution engineers. It gathers customer context (Work IQ, workshop transcripts), builds the interactive **Frontier Company Blueprint** HTML along the Hub journey, writes the PRD, solution design, ADRs and IT readiness checklist, creates the agent identity kit and models the business value case and FinOps. `AGENTS.md` holds the full working agreement; read it before you change anything.

## Where things are

- `plugin/` is the packaged unit: `skills/` (seven skills with `SKILL.md`, `scripts/`, `references/`, `templates/`, `examples/`), `package/manifest.json`, `install/`, the user README, `MIT.md`, `THIRD-PARTY-NOTICES.md`.
- `src/renderer/` holds the sources of the blueprint HTML. The template in `plugin/skills/frontier-blueprint/templates/` is generated from it.
- `tools/` (task runner `dev.py`, build, package, release, checks), `tests/` (unit, pipeline, DOM, browser), `infra/` + `site/` + `azure.yaml` (showcase hosting), `docs/` (PRD, ADRs, engineering guides, plans), `backlog/`.

## Rules that always apply

1. **Customer-neutral.** Never write a real customer name. The demo company is the fictitious *Caldova Industrial AG*. `python tools/dev.py scan` checks.
2. **Plugin scripts use the Python standard library only** and run offline in the Cowork sandbox: `main(argv) -> int`, deterministic output, UTF-8, no network.
3. **Never hand-edit generated files**: the blueprint template (edit `src/renderer/*`, run `python tools/dev.py template`), `plugin/install/plugin-install.json` (`python tools/dev.py package`), anything in `dist/` or `build/`.
4. **Test first.** Write the failing test, make it pass, refactor. Renderer changes need DOM tests.
5. **Verify before you finish.** `python tools/dev.py check` must end with `ALL GATES PASSED`; paste its summary into the pull request.
6. **Versions.** A released version is immutable. The first change to `plugin/` after a release runs `python tools/dev.py bump X.Y.Z`.
7. **Microsoft product icons** are trademarks used under Microsoft's icon terms (architecture diagrams and documentation, unmodified); see `plugin/THIRD-PARTY-NOTICES.md`.
8. **Human-only:** merging, approvals, releases and tags, deployments, repository settings, the `status:ready` and `approved:*` labels, and `.github/hooks/`. Hooks enforce this.
9. Plain business English for users; British spelling as in the existing documents.

## Commands

`python tools/dev.py doctor | precommit | check | test | selftest | template | package | demo | dom | site | e2e | bump X.Y.Z`
