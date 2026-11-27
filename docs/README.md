# Documentation

| Field | Value |
|---|---|
| Version | 1.2 |
| Date | 2026-11-27 |
| Author | Original author not recorded; Copilot AI-assisted maintenance; AI assistant (AI-assisted #70 release evidence guidance) |
| Status | Maintained catalogue; approval not inferred |
| Scope | Using the plugin, engineering guidance and historical records; document revision, not product version |
| References | [Repository](../README.md), [Product requirements](prd.md), [Solution design](solution-design.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33), [Issue #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Guidance #39](https://github.com/urruegg/frontier-envisioning/issues/39), [SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md), [Maintenance #82](https://github.com/urruegg/frontier-envisioning/issues/82) |

## Using the plugin

Start here to evaluate the **unreleased 1.11.0 development candidate**.
Its download is **not yet published**; the
[release listing](https://github.com/urruegg/frontier-envisioning/releases)
may offer an older classic build, not this candidate. Use the
[candidate source-build/CI artefact route](getting-started.md#install-in-copilot-cowork)
until human publication. Build metadata is not publication or sharing clearance.
The sole human maintainer is [@urruegg](https://github.com/urruegg).
The approved source/issue/PR host, with intended private/internal classification, is
[urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning).
Observed repository visibility is public (`private:false`). That does not clear
unchanged internally marked material. The intended private/internal policy
discrepancy needs [human reconciliation](engineering/release-evidence-adoption.md#classification-and-access);
classifications and distribution restrictions remain unchanged.
The candidate distributes eight skills: seven existing GA wrappers, including
Business Value Case, plus optional Preview Envisioning Agent Factory.
Nine source folders remain, including FinOps retained as source-only: it is not
registered, copied or installed by the 1.11.0 ZIP. This does not remove an
older FinOps copy from a user's configuration.
Core workshops, ordinary value, identity and requested process/ontology work
need neither Factory nor FinOps; Fabric Preview caveats remain explicit.

Recorded local evidence covers completed package/receiver and full L1/L2
checks, with reviewed `7ad10f1` CI in the
[plugin guide](../plugin/README.md#engineering-evidence-and-remaining-checks).
Fresh real-host health in open
[#81](https://github.com/urruegg/frontier-envisioning/issues/81) and official
publication remain pending. Changed package prose needs a newly verified ZIP;
prior evidence is not a pass for this revision.

| Guide | For |
|---|---|
| [Getting started](getting-started.md) | Core-first example, 1.11.0 candidate installation and evidence-led workshop; retained source-only baseline history |
| [Caldova gallery](demo/README.md) | Offline core HTML and ten captures, including architecture/workshop views and requested ontology, no FinOps; actual capture version/hashes belong to the manifest |
| [Starter prompts](starter-prompts.md) | Scoped core preparation and synthetic Caldova variant; legacy/source-only baseline exercise is unavailable in the 1.11.0 ZIP |
| [Packaged plugin guide](../plugin/README.md) | Eight-skill candidate installation, optional offline Factory Preview, outputs, data handling and the absent-FinOps boundary |
| [Versioned FinOps procedure](../plugin/skills/frontier-finops/SKILL.md#quick-start--requested-versioned-baseline) | Retained source-only protocol, unavailable in the 1.11.0 ZIP: twelve-month scenarios, frozen-target external review and projected JSON/Markdown |
| [Complete baseline contract](../plugin/skills/frontier-finops/references/agent-finops-baseline.md) | Retained source-only CLI, decimal/currency, review and projection contract; not an installed 1.11.0 procedure |

**Legacy/source-only FinOps — unavailable in the 1.11.0 ZIP.**
Use ordinary Value Case and sourced cost assumptions with named budget gaps;
missing costs are not zero or verified ROI. Do not invoke an absent skill.
The retained financial protocol requires fresh actual scenario awareness before
cost operations or figures, not inferred from a prompt or installation. Decline
allows draft/core work with named gaps, not financial readiness. At financial
build handover, each agent in
scope needs the complete currently evidenced/priced baseline and exact-target
external owner/delegation review, with no conditional unpriced exception.
The separate synthetic Caldova baseline is not current pricing or real approval.

## Engineering

| Document | Authority or purpose |
|---|---|
| [Product requirements](prd.md) | Current 1.11.0 candidate requirements and eight-skill boundary; prior release/candidate records and historical Part A are retained |
| [Solution design](solution-design.md) | Current offline Factory architecture and scope-qualified verification; historical Part B is retained |
| [Architecture decisions](adr/README.md) | Repository/engineering rationale; Proposed status is not acceptance |
| [Engineering handbook](engineering/handbook.md) | Build, test, version, release and deployment practice |
| [Workstation setup](engineering/workstation-setup.md) | Existing dependency, dev-container and local setup instructions |
| [Testing strategy](engineering/testing-strategy.md) | What each test level proves and its limits |
| [Copilot and Superpowers](engineering/copilot-and-superpowers.md) | AI-assisted engineering, supported harnesses and guardrails |
| [GitHub setup](engineering/github-setup.md) | Repository configuration and sole-maintainer review model |
| [Release evidence adoption](engineering/release-evidence-adoption.md) | #67 exact-version evidence and dated 25 November adoption state; the current workflow read-access binding is present, with no routine manifest-retention PR |
| [Deployment](engineering/deployment.md) | Controlled showcase hosting; not needed to inspect the offline example |

### Work-package catalogues

| Catalogue | Purpose |
|---|---|
| [ideas/](ideas/README.md) | Ideas for new work packages |
| [specs/](specs/README.md) | Governing specifications |
| [plans/](plans/README.md) | Test-first implementation plans |
| [sprints/](sprints/README.md) | Linked delivery records |

Release-evidence simplification is
[#67](https://github.com/urruegg/frontier-envisioning/issues/67), with
[#70 guidance](https://github.com/urruegg/frontier-envisioning/issues/70):
[approved spec](specs/2026-11-24-release-evidence-simplification-design.md),
[plan](plans/2026-11-25-release-evidence-simplification-plan.md),
[SPRINT-012](sprints/SPRINT-012-release-evidence-simplification.md) and
[Proposed release evidence rationale](adr/0031-release-assets-as-evidence.md).
The current [release workflow](../.github/workflows/release.yml) already binds
L1 read access; adding another token binding is not a current adoption step.
The normal flow is human review/merge with truthful gates and actual manual
evidence, then the maintainer runs **Actions > release > Run workflow** on
`main` with the matching `version`, `manual_checks=true` and `publish=true`.
Both true values are preflight requirements, not build-only switches or
permission to attest to checks not performed. Automation verifies and publishes;
no manual tag-first or recurring SHA/manifest-retention ceremony is required.
The guidance's 25 November pending protected handover/PR #71 CI statements
remain dated adoption history, not current instructions. Actual #52 closure is
not established here; do not infer it or invent historical retention.

The current candidate uses the existing
[Factory design](specs/2026-11-25-agent-factory-handover-design.md),
[offline plan](plans/2026-11-25-agent-factory-offline-implementation-plan.md),
[health/distribution spec](specs/2026-11-26-plugin-health-and-finops-exclusion-design.md),
[amendment plan](plans/2026-11-26-plugin-health-and-finops-exclusion-plan.md) and
[SPRINT-013](sprints/SPRINT-013-agent-factory-handover.md).
Their dated evidence remains qualified; public-facing maintenance
[#82](https://github.com/urruegg/frontier-envisioning/issues/82) does not approve
internal/protected edits or publication.

Historical baseline-first FinOps is [#35](https://github.com/urruegg/frontier-envisioning/issues/35),
governed by the actual [decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36),
[approved design](specs/2026-11-12-agent-finops-baseline-design.md) and
[plan](plans/2026-11-12-agent-finops-baseline-plan.md).

| Work item | Scope |
|---|---|
| [#38](https://github.com/urruegg/frontier-envisioning/issues/38) | Offline profile/model, calculation, frozen records, external review and projection |
| [#37](https://github.com/urruegg/frontier-envisioning/issues/37) | Optional Blueprint source integration and per-agent financial handover criterion |
| [#39](https://github.com/urruegg/frontier-envisioning/issues/39) | Source guidance and candidate verification |

Use [SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md) for source-qualified
execution and validation evidence. Design/plan approval grants no financial
consent, authenticated review, release, publication or deployment authority.

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
