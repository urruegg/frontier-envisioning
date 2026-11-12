# Documentation

| Field | Value |
|---|---|
| Version | 0.7 |
| Date | 2026-11-12 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained catalogue; approval not inferred |
| Scope | Using the plugin, engineering guidance and historical records; document revision, not product version |
| References | [Repository](../README.md), [Product requirements](prd.md), [Solution design](solution-design.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33), [Issue #35](https://github.com/urruegg/frontier-envisioning/issues/35), [SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md) |

## Using the plugin

Start here to evaluate the **1.9.2 unreleased internal candidate**. No repository
visibility change, published release or external sharing clearance is implied.
The sole human maintainer is [@urruegg](https://github.com/urruegg).

| Guide | For |
|---|---|
| [Getting started](getting-started.md) | Download/open the example, install in Cowork and prepare an evidence-led workshop |
| [Caldova gallery](demo/README.md) | Offline HTML and five screenshot views of the fictitious example; capture provenance and regeneration |
| [Starter prompts](starter-prompts.md) | Scoped, read-only preparation prompt and a synthetic Caldova variant |
| [Packaged plugin guide](../plugin/README.md) | Installation details, eight skills, outputs, data handling and the full FinOps Preview procedure |

## Engineering

| Document | Authority or purpose |
|---|---|
| [Product requirements](prd.md) | Approved 1.10.0 development-candidate requirements with integrated proof pending; prior candidate records and historical Part A are retained |
| [Solution design](solution-design.md) | Candidate architecture and scope-qualified verification; new integrated proof is pending and historical Part B is retained |
| [Architecture decisions](adr/README.md) | Repository/engineering rationale; Proposed status is not acceptance |
| [Engineering handbook](engineering/handbook.md) | Build, test, version, release and deployment practice |
| [Workstation setup](engineering/workstation-setup.md) | Existing dependency, dev-container and local setup instructions |
| [Testing strategy](engineering/testing-strategy.md) | What each test level proves and its limits |
| [Copilot and Superpowers](engineering/copilot-and-superpowers.md) | AI-assisted engineering, supported harnesses and guardrails |
| [GitHub setup](engineering/github-setup.md) | Repository configuration and sole-maintainer review model |
| [Deployment](engineering/deployment.md) | Controlled showcase hosting; not needed to inspect the offline example |

### Work-package catalogues

| Catalogue | Purpose |
|---|---|
| [ideas/](ideas/README.md) | Ideas for new work packages |
| [specs/](specs/README.md) | Governing specifications |
| [plans/](plans/README.md) | Test-first implementation plans |
| [sprints/](sprints/README.md) | Linked delivery records |

Baseline-first FinOps development is [#35](https://github.com/urruegg/frontier-envisioning/issues/35):
[approved plan](plans/2026-11-12-agent-finops-baseline-plan.md) and
[SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md). Approval and
in-progress implementation are not verified delivery or a release.

The version-only 1.9.2 preparation is [#33](https://github.com/urruegg/frontier-envisioning/issues/33):
[plan](plans/2026-11-12-version-1.9.2-plan.md) and
[SPRINT-006](sprints/SPRINT-006-version-1.9.2.md). This is not a release.

The reader-documentation baseline is [#31](https://github.com/urruegg/frontier-envisioning/issues/31):
[idea and execution direction](ideas/2026-11-12-internal-user-documentation.md),
[design](specs/2026-11-12-internal-user-documentation-design.md),
[plan](plans/2026-11-12-internal-user-documentation-plan.md) and
[SPRINT-005](sprints/SPRINT-005-internal-user-documentation.md).
Execution was directed in conversation. The sprint records actual local
verification; use #31 for current PR/CI status. Separate written-plan review
and protected ready/approval labels are not inferred.

## Historical evidence and internal analyses

These are source-qualified records, not a new reader's installation checklist.
The #25 D0–D5 local technical work was completed and human-merged in
[PR #29](https://github.com/urruegg/frontier-envisioning/pull/29) on 11 November.
That baseline is not new #31 validation, a release or manual tenant acceptance.

| Record | How to read it |
|---|---|
| [Original intake plan](engineering/intake-plan.md) | Received scope, phases and dated exit criteria |
| [1.9 receipt](intake/handover-1.9.0.md) and [SPRINT-004](sprints/SPRINT-004-handover-1.9-preview-finops.md) | Frozen source evidence and chronological execution checkpoints; earlier pending statements retain their original context |
| [1.7 receipt](intake/handover-1.7.0.md) and [SPRINT-003](sprints/SPRINT-003-handover-1.7-intake.md) | Earlier selective integration and its qualified technical evidence |
| [Documentation, governance and accessibility — SPRINT-001](sprints/SPRINT-001-docs-governance-and-accessibility.md) | Historical delivery, sign-off and accessibility evidence; protected routing and manual acceptance remain separately qualified |
| [Accessibility verification](intake/2026-11-10-accessibility-verification.md) | #7 implementation/catalogue correction and manual acceptance limits; not WCAG certification |
| [HubWorks analysis](analysis/hubworks-integration-analysis.md) | Microsoft-internal analysis; not a universal loader or a new sharing permission |
| [Visualisation and reuse evaluation](analysis/visualisation-and-reuse-evaluation.md) | Evaluation evidence, not proof of deployed integrations |

Use plural folders for all current records. Historical designs are catalogued
under specs and historical implementation plans under plans; their original
format and commit-qualified evidence are retained. Link directly to the
[PRD](prd.md) or [solution design](solution-design.md), not an obsolete combined index.
Protected routing [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
and release-cache [#30](https://github.com/urruegg/frontier-envisioning/issues/30)
remain human-owned; neither is needed to download and inspect the example.
