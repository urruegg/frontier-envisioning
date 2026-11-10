# Intake plan: Frontier Envisioning into controlled engineering

| Field | Value |
|---|---|
| Version | 1.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Retained exporter proposal; historical assertions are not current approval |
| Scope | Intake record metadata and routing; document revision, not product version; original proposal and evidence retained below |
| References | [Documentation](../README.md), [M0 plan](../plans/2026-11-08-cowork-m0-implementation-plan.md), [Intake evidence](../intake/m0-evidence.md), [Current work packages](../plans/README.md) |

This is the retained exporter proposal and its historical validation assertions. For current execution, use the [approved M0 plan](../plans/2026-11-08-cowork-m0-implementation-plan.md) and [actual intake evidence](../intake/m0-evidence.md). Release approval is now separate from showcase `prod`; `RELEASE_ENABLED` remains disabled until all recorded blockers and policy checks are resolved. Do not execute the old first-week tag/publish checklist as an intake shortcut.

| | |
|---|---|
| Version | 1.0, 8 November 2026 |
| Product owner and maintainer | Urs Rüegg, Microsoft Innovation Hub Switzerland |
| Baseline | Frontier Envisioning 1.4.0, built and validated in Copilot Cowork on 8 November 2026 |
| Target | A GitHub repository where people and GitHub Copilot (with Superpowers) refine and extend the plugin through pull requests, automated quality gates, infrastructure as code and reproducible releases |

## 1. Outcome

At the end of the intake (milestone **M0 · Intake baseline**):

- the repository is on GitHub, `main` is protected, and every change arrives through a reviewed pull request;
- the gates L0 (commit), L1 (pull request), L2 (browser, deployment to dev) and L3 (release) run automatically and are green;
- the repository rebuilds the published 1.4.0 artefacts byte for byte, so nothing was lost in the move;
- GitHub Copilot (VS Code, CLI, cloud agent, code review) works with the repository's instructions, agents, skills and guardrails, and the Superpowers method is available on every surface the team uses;
- the showcase (Caldova blueprint, identity catalogue, plugin download) is deployable to Azure from the repository;
- the backlog for 1.5.0 is triaged and the first issues are ready.

## 2. What is handed over

| Component | Content | Size |
|---|---|---|
| Plugin (`plugin/`) | 7 skills: envisioning, context discovery, blueprint, solution design, agent identity, value case, FinOps; manifest, install check, user guide, MIT licence, third-party notices | 79 files; 31 Python scripts (about 7,400 lines, standard library only) |
| Renderer (`src/renderer/`) | Blueprint HTML sources: page shell, CSS, JavaScript (14 views) | 3 files, about 2,800 lines |
| Canon and examples | Innovation Hub canon (Agent Factory, landing zone, ADRs, IT readiness), Caldova examples for every skill, rates 2026-11 | in `plugin/skills/*/templates`, `examples`, `rates` |
| Product documentation | PRD and solution design 1.4.0, HubWorks integration analysis (sharing copy), visualisation and reuse evaluation | `docs/` |
| Engineering added for the intake | Task runner, build, release and check tools; unit, pipeline, DOM and browser tests; workflows; Copilot configuration; hooks; infrastructure; engineering guides; ADR-0017 to ADR-0022; seed backlog of 50 issues | `tools/`, `tests/`, `.github/`, `infra/`, `docs/engineering/`, `backlog/` |
| Release record | Hashes of the published 1.4.0 artefacts | `releases/1.4.0/manifest.json` |

### Evidence prepared before the hand-over

| Check | Result |
|---|---|
| Plugin package rebuilt from the new layout | Byte-identical to the published `frontier-envisioning-plugin-1.4.0.zip` |
| Caldova demo rebuilt (blueprint, identity kit, catalogue) | Identical to the published files (the blueprint after normalising its build date) |
| Blueprint template assembled from `src/renderer` | Byte-identical to the template in the package |
| Plugin self-test | 29 of 29 |
| Unit tests (tools, hooks, site, release tools, backlog) | 39 of 39 |
| DOM tests (happy-dom) on the 1.4.0 demo | 12 of 12 |
| Renderer lint (ESLint, recommended rules) | 0 errors, 7 warnings (INT-08) |
| Pipeline tests (self-test wrapper; release reproduction built in a temporary folder) | 2 of 2 |
| Showcase built and served locally with the hosting headers | Smoke check passed; the CSP hash matches the blueprint's inline script; Entra configuration protects every route |
| Release bundle | Built (12 entries) with checksums |
| Python static checks (undefined names, syntax warnings) | 0 findings |
| Customer-neutrality scan (repository and every archive) | 0 findings |
| GitHub bootstrap dry run | 30 labels, 4 milestones, 50 issues planned |

Not run before the hand-over (no network or tools in the preparation environment): ruff, pytest (the tests ran with unittest), Playwright browser tests, Bicep compilation, `azd`, the GitHub workflows themselves, and Superpowers installation. These are the first checks of Phase 1.

## 3. Target engineering model

- **Flow**: issue that meets the Definition of Ready, spec and plan in `docs/plans/`, branch, test-first implementation, `python tools/dev.py check`, pull request with evidence, code owner review, squash merge by a person.
- **Gates**: L0 pre-commit, L1 `L1 quality gate`, L2 `L2 browser tests` and deployment to dev, L3 tag-driven release with SBOM, provenance and an approval before the draft release.
- **AI-assisted engineering**: GitHub Copilot with repository instructions, path instructions, five custom agents (planner, builder, renderer, reviewer, release manager), five repository skills and the Superpowers method; deterministic hooks deny human-only actions.
- **Infrastructure as code**: the showcase on Azure Static Web Apps (Bicep, Azure Developer CLI, OpenID Connect, Microsoft Entra sign-in). The customer-facing IaC track (landing zone for the agents a customer builds) is the epic BUILD-01.

Details: [handbook](handbook.md), [Copilot and Superpowers](copilot-and-superpowers.md), [testing strategy](testing-strategy.md), [deployment](deployment.md).

## 4. Phases

| Phase | Goal | Issues | Exit criteria | Who |
|---|---|---|---|---|
| 0 Bootstrap | Repository exists and is protected | INT-01, ENG-D1 | Ruleset active, labels, milestones and issues created | Maintainer |
| 1 Baseline green | Gates run on GitHub; 1.4.0 reproduced | INT-02, INT-03, INT-04, INT-12, INT-14 | `L1 quality gate` and `L2 browser tests` green and required; lockfiles committed; Copilot cloud agent and code review on; release workflow drafted v1.4.0 from the import commit | Maintainer, Copilot builder |
| 2 Harden | Supply chain and test depth | INT-06 (ENG-D2), INT-07, INT-08, INT-11, INT-15, ENG-D4 | Superpowers available on every surface used; actions pinned; lint ratchet plan; unit tests per plugin script; release checklist in place | Maintainer, Copilot builder and reviewer |
| 3 Showcase | Deployable showcase | ENG-D3, INT-05 | `azure-dev` deploys dev on merge, prod after approval; sign-in enforced; smoke check green | Maintainer, Azure owner |
| 4 First feature release | 1.5.0 through the new flow | EPIC-HW (F-01 to F-06, F-08), INT-09, INT-10, then the operate loop | 1.5.0 released from a tag with provenance; installed in Cowork from the release asset | Maintainer, Copilot agents, Hub leadership for decisions |

Proposal: Phases 0 to 2 by 20 November 2026 (milestone M0). The HubWorks analysis targets Frontier 1.5 (F-01 to F-06, F-08) by the same date for the pilot; with the intake first, agree the 1.5.0 scope and date at the M0 review.

## 5. Roles

| Role | Responsibility |
|---|---|
| Product owner and maintainer | Backlog, Definition of Ready, design approvals (`approved:design`), merges, releases and tags, repository settings |
| Code owners | Review every pull request (`.github/CODEOWNERS`) |
| Release manager | Tags, approves the `prod` environment, publishes the draft release, records the release manifest |
| Hub leadership and Hub solution engineering | Product decisions D-01 to D-08 (PRD A.13) |
| Azure owner | Subscription, cost, app registration for the showcase sign-in |
| Copilot agents | Plan, build, review and prepare releases through pull requests; never merge, release or deploy |

## 6. Decisions to take

| Id | Decision | Recommendation | Needed for |
|---|---|---|---|
| ENG-D1 | Repository home and visibility | Private repository under the maintainer's account until the open-source question is settled; the HubWorks analysis is Microsoft internal | Phase 0 |
| ENG-D2 | How Superpowers reaches each Copilot surface | Both: personal installs for VS Code and Copilot CLI, and vendored pinned skills for the cloud agent | Phase 2 |
| ENG-D3 | Showcase hosting | Azure Static Web Apps Standard with Microsoft Entra sign-in | Phase 3 |
| ENG-D4 | Release immutability and versioning | Released versions are immutable; the first plugin change after a release bumps the version | Phase 2 |
| D-01 to D-08 | Product decisions from the PRD | as in the PRD | 1.5.0 and later |

## 7. Risks

| Risk | Mitigation |
|---|---|
| A real customer name enters the repository | Hashed denylist scan in L0 and L1, agent hook on every edit, private repository |
| The move loses or changes behaviour | Release reproduction against `releases/1.4.0/manifest.json` in L1 while the version is 1.4.0 |
| Browser tests and IaC were not run before the hand-over | First tasks of Phase 1 (INT-04, INT-05); expect small fixes |
| Agents take human-only actions | Hooks deny them deterministically; rulesets and environment approvals stop the rest |
| Plan limits (private repository on a personal plan) block rulesets, environments or secret scanning | Bootstrap reports what was not applied; ENG-D1 decides the home |
| Microsoft product icon terms | Notice and opt-out exist; E-02 replaces deck copies with the official sets (D-07) |
| Superpowers changes upstream | Pinned version (v7.0.2) with a lock file; upgrades through a pull request |

## 8. First week

1. Unzip the repository package, read `README.md` and this plan.
2. `python tools/bootstrap_github.py --owner <owner>` (dry run), then `--apply` (or `tools/Initialize-GitHubRepo.ps1`). Follow [github-setup.md](github-setup.md) for the web settings.
3. Open the dev container (or run `python tools/dev.py setup`), run `python tools/dev.py check` locally.
4. Commit `package-lock.json` and pinned `requirements-dev.txt` (INT-03) in the first pull request; watch `L1 quality gate` and `L2 browser tests`.
5. Install Copilot CLI and Superpowers (`copilot plugin marketplace add obra/superpowers-marketplace`, `copilot plugin install superpowers@superpowers-marketplace`); try the planner agent on INT-11.
6. Tag `v1.4.0` on the import commit (INT-14) to prove the release pipeline.
7. M0 review: close Phase 1, confirm the decisions, agree the 1.5.0 scope.
