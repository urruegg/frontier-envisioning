# AGENTS.md: working agreement for coding agents

This file is for every coding agent working in this repository (GitHub Copilot in VS Code, Copilot CLI, Copilot cloud agent and code review, and any other agent that reads `AGENTS.md`). People follow the same agreement; see also `CONTRIBUTING.md` and `docs/engineering/handbook.md`.

## 1. What this repository is

**Frontier Envisioning** is a Copilot Cowork plugin (MIT) used by Microsoft Innovation Hub solution engineers for Frontier solution envisioning and architecture design. Seven skills:

| Skill | Purpose |
|---|---|
| `frontier-envisioning` | Orchestrates the method from frame to handover |
| `frontier-context-discovery` | Customer context from Work IQ and workshop transcripts, evidence register |
| `frontier-blueprint` | The interactive Frontier Company Blueprint HTML (14 views along the Hub journey) |
| `frontier-solution-design` | PRD, solution design, ADRs, IT readiness checklist |
| `frontier-agent-identity` | Agent identity kit: names, colours, icons, cards, validators, pipelines |
| `frontier-value-case` | Business value case in CHF: value tree, assumption register, NPV, ROI |
| `frontier-finops` | What the agents cost: credits, licences, Azure, people, purchase options |

The plugin runs inside Copilot Cowork. This repository adds the engineering around it: source control, tests, builds, releases, a hosted showcase and AI-assisted engineering with guardrails.

## 2. Repository map: where to edit

| Path | Edit? | Notes |
|---|---|---|
| `plugin/skills/**` | yes | Skill procedures, scripts (stdlib only), references, canon data, examples |
| `plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html` | **no, generated** | Edit `src/renderer/*`, then `python tools/dev.py template` |
| `plugin/install/plugin-install.json` | **no, generated** | `python tools/dev.py package` |
| `plugin/package/manifest.json`, `plugin/.claude-plugin/plugin.json` | via `bump` | Versions change with `python tools/dev.py bump X.Y.Z` |
| `src/renderer/**` | yes | Blueprint HTML sources |
| `tools/**`, `tests/**` | yes | Python 3.11+, stdlib; tests are `unittest` classes, DOM tests use `node:test` |
| `infra/**`, `site/**`, `azure.yaml` | yes | Showcase hosting; deployment runs in the workflow, not in agent sessions |
| `docs/**`, `backlog/**` | yes | Plans in `docs/plans/`, decisions in `docs/adr/` |
| `.github/hooks/**`, `.github/CODEOWNERS`, `LICENSE`, `plugin/MIT.md`, `releases/**`, `.github/workflows/release.yml`, `.github/workflows/azure-dev.yml`, `tools/neutrality-denylist.txt`, `.agents/skills/**` | **no, people only** | The guard hook denies agent edits; propose the change in the PR description |
| `dist/`, `build/` | **no** | Build output (ignored by Git) |

## 3. The engineering method (Superpowers with this repository's gates)

Use the Superpowers skills when they are available (see `docs/engineering/copilot-and-superpowers.md`); the steps below are the same with or without them.

1. **Start from an issue that is ready** (label `status:ready`, set by a person). Definition of Ready: problem and outcome stated, acceptance criteria testable, open decisions resolved, affected areas named, customer-neutral sample data available.
2. **Brainstorm and write the spec** (`brainstorming`): ask, play back, agree. Save `docs/plans/YYYY-MM-DD-<topic>-design.md`. A person approves it (label `approved:design`) before planning big changes.
3. **Plan** (`writing-plans`): bite-sized tasks with exact files, tests and commands. Save `docs/plans/YYYY-MM-DD-<topic>-plan.md`.
4. **Work on a branch** (`using-git-worktrees` where available): `feat/<issue-id>-<topic>`, `fix/...`, `chore/...`, `docs/...`.
5. **Test first** (`test-driven-development`): failing test, minimal code, passing test, refactor, commit. Conventional commit messages (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`), the issue id in the body.
6. **Debug systematically** (`systematic-debugging`): reproduce, find the root cause, then fix. No guesses.
7. **Verify before claiming done** (`verification-before-completion`): run `python tools/dev.py check`; it must end with `ALL GATES PASSED`. For renderer changes also `python tools/dev.py site e2e` when Playwright is installed.
8. **Review** (`requesting-code-review`): open a draft pull request with the template filled in, the gate summary pasted, screenshots for visual changes. Address every finding (`receiving-code-review`).
9. **Finish** (`finishing-a-development-branch`): the pull request is merged by a person. Never merge, approve, tag or release yourself.

## 4. Definition of Done

- Acceptance criteria of the issue met and ticked in the PR.
- Tests added or updated; `python tools/dev.py check` passes locally and in CI (`L1 quality gate`), browser tests pass (`L2 browser tests`).
- Generated files regenerated and committed; no hand edits to them.
- Documentation updated: `SKILL.md` and references for behaviour, the PRD for requirements, an ADR for an architectural decision, `CHANGELOG.md` under the version in development.
- Customer-neutral (scan passes), no secrets, product icons used within their terms.
- If `plugin/` changed after a release: the version was bumped first.

## 5. Rules

- **Customer neutrality.** Never write a real customer name, person, or engagement detail. Use the fictitious Caldova Industrial AG. The neutrality scan uses hashed terms (`tools/neutrality-denylist.txt`).
- **Offline, deterministic plugin.** Plugin scripts use the Python standard library only, no network, deterministic output (the release check compares artefacts byte for byte).
- **Single sources.** Canon content lives in `plugin/skills/frontier-blueprint/templates/blueprint-defaults.json`; rates in `plugin/skills/frontier-finops/rates/`; shared formulas in `fv_expr.py` (identical copies in two skills).
- **Security.** No secrets in code, logs or outputs. Do not read tokens or secret environment variables. No `curl | sh`. Azure changes only through the `azure-dev` workflow.
- **Licences.** Plugin code and docs are MIT. Microsoft product icons are trademarks under Microsoft's icon terms (see `plugin/THIRD-PARTY-NOTICES.md`). Third-party skills (Superpowers, MIT) keep their licence notice.
- **Scope.** Change only what the issue asks. Propose follow-ups as new issues instead of widening the pull request.

## 6. Human-only actions (enforced by `.github/hooks/`)

Merging and approving pull requests; creating releases and release tags; force pushes and pushes to `main`; repository settings, rulesets, secrets and variables; labels `status:ready`, `approved:design`, `approved:release`; running deployments or workflows by hand; `azd`/`az` changes (agents may run `az bicep build`); editing the guardrails, `CODEOWNERS`, the licence, release manifests, the neutrality denylist and vendored third-party skills; bypassing commit hooks.

## 7. Commands

| Command | What it does | Gate |
|---|---|---|
| `python tools/dev.py doctor` | Which tools are installed | |
| `python tools/dev.py precommit` | Template drift, lint, repository rules, neutrality | L0 |
| `python tools/dev.py check` | L0 + unit tests + plugin self-test + package + demo + release reproduction + DOM tests | L1 |
| `python tools/dev.py site e2e` | Showcase site and browser tests (Playwright) | L2 |
| `python tools/dev.py template` | Assemble the blueprint template from `src/renderer` | |
| `python tools/dev.py package demo` | Plugin package into `dist/`, Caldova demo into `build/demo/` | |
| `python tools/dev.py bump X.Y.Z` | New version everywhere | |

## 8. When something fails

| Symptom | Fix |
|---|---|
| `DRIFT: ... differs from src/renderer` | Run `python tools/dev.py template` and commit the template |
| `plugin-install.json was stale` | Run `python tools/dev.py package` and commit the file |
| `CUSTOMER NAME: ...` | Replace it with Caldova content; never add the name elsewhere |
| `The sources no longer reproduce the released X` | You changed the plugin after a release: `python tools/dev.py bump <next>` first |
| `description has N UTF-16 units` | Shorten the skill description (routing quality) |
| Guard hook denied a call | Read the reason; it names what to do instead |
