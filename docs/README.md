# Documentation

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-10 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained catalogue; approval not inferred |
| Scope | Active documentation and historical record routing; document revision, not product version |
| References | [Repository](../README.md), [Product requirements](prd.md), [Solution design](solution-design.md), [Work-package approval](https://github.com/urruegg/frontier-envisioning/issues/6) |

| Document | For |
|---|---|
| [prd.md](prd.md) | Authoritative product requirements, shared product context, release plan and open product decisions (Part A) |
| [solution-design.md](solution-design.md) | Authoritative solution design, technical decisions and sources (Part B), with the historical 1.6.0 file inventory |
| [adr/](adr) | Architecture decisions of the repository and engineering setup (ADR-0017 onwards) |
| [engineering/intake-plan.md](engineering/intake-plan.md) | The intake: what was handed over, phases, exit criteria, decisions |
| [engineering/handbook.md](engineering/handbook.md) | How we build, test, version, release and deploy |
| [engineering/copilot-and-superpowers.md](engineering/copilot-and-superpowers.md) | AI-assisted engineering: GitHub Copilot surfaces, Superpowers, agents, skills, hooks |
| [engineering/workstation-setup.md](engineering/workstation-setup.md) | Dev container, local setup, VS Code, Copilot CLI |
| [engineering/testing-strategy.md](engineering/testing-strategy.md) | Test levels, what each gate proves |
| [intake/2026-11-10-accessibility-verification.md](intake/2026-11-10-accessibility-verification.md) | New #7 implementation handoff; catalogue AA blocker and pending human acceptance, not the original audit |
| [engineering/deployment.md](engineering/deployment.md) | Showcase hosting on Azure Static Web Apps with azd, Bicep and OpenID Connect |
| [engineering/github-setup.md](engineering/github-setup.md) | Creating and configuring the GitHub repository |
| [analysis/hubworks-integration-analysis.md](analysis/hubworks-integration-analysis.md) | HubWorks integration analysis (Microsoft internal, sharing copy) |
| [analysis/visualisation-and-reuse-evaluation.md](analysis/visualisation-and-reuse-evaluation.md) | Visualisation and reuse evaluation (diagrams, CAT agent skills, GitHub harness) |
| [ideas/](ideas/README.md) | Ideas for new work packages |
| [specs/](specs/README.md) | Governing specifications |
| [plans/](plans/README.md) | Test-first implementation plans |
| [sprints/](sprints/README.md) | Linked delivery records |

## Linked work packages

| Work package | Records | State |
|---|---|---|
| [Documentation, governance and accessibility (#6)](https://github.com/urruegg/frontier-envisioning/issues/6) | [Idea](ideas/README.md), [spec](specs/README.md), [plans](plans/README.md), [SPRINT-001](sprints/SPRINT-001-docs-governance-and-accessibility.md) | User-approved design, plans and readiness on [#6](https://github.com/urruegg/frontier-envisioning/issues/6); delivery evidence remains separate |
| [Plural documentation layout (#18)](https://github.com/urruegg/frontier-envisioning/issues/18) | [Governing idea](ideas/2026-11-09-docs-governance-and-accessibility.md#plural-layout-amendment-2026-11-10), [spec](specs/2026-11-10-documentation-layout-design.md), [plan](plans/2026-11-10-documentation-layout-plan.md), [SPRINT-001](sprints/SPRINT-001-docs-governance-and-accessibility.md) | Maintainer-directed naming/removal amendment; validation and delivery tracked separately |

Use plural folders for all current records. Historical designs are catalogued
under specs and historical implementation plans under plans; their original
format and commit-qualified evidence are retained. The combined product-document
index is removed: link directly to the PRD or solution design and its own anchor.
Protected hook routing still needs human #8 action.
