# Implementation-plan catalogue

| Field | Value |
|---|---|
| Version | 1.9 |
| Date | 2026-11-25 |
| Author | Original catalogue author not recorded; Copilot SDK in VS Code, AI-assisted consolidation |
| Status | Maintained catalogue; approval belongs to the linked records, not this guide |
| Scope | Current and historical implementation plans; specifications live in docs/specs |
| References | [Docs](../README.md), [Ideas](../ideas/README.md), [Specs](../specs/README.md), [Sprints](../sprints/README.md), [Layout issue](https://github.com/urruegg/frontier-envisioning/issues/18) |

| Plan | Owner during execution | Tracking and delivery evidence |
|---|---|---|
| [Agent Factory handover](2026-11-25-agent-factory-handover-plan.md) | `@urruegg` accountable; written spec `7f650c4` and actual W0 plan `c8cc5bb` approved | [#72](https://github.com/urruegg/frontier-envisioning/issues/72), bounded [#73](https://github.com/urruegg/frontier-envisioning/issues/73), [idea](../ideas/2026-11-25-agent-factory-handover.md), [spec](../specs/2026-11-25-agent-factory-handover-design.md), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md); actual Cowork unavailable, host-gate amendment Proposed; no downstream code readiness or host pass |
| [Release evidence simplification](2026-11-25-release-evidence-simplification-plan.md) | `@urruegg` accountable; written spec at `67dc9a5` and subsequent actual plan/execution at `22f512f` approved | [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [idea](../ideas/2026-11-24-release-evidence-simplification.md), [spec](../specs/2026-11-24-release-evidence-simplification-design.md), [SPRINT-012](../sprints/SPRINT-012-release-evidence-simplification.md); bounded #68/#69/#70 implementation, results pending |
| [Process governance and SAP grounding](2026-11-17-process-governance-sap-grounding-plan.md) | `@urruegg` accountable; written spec and subagent-driven plan/readiness at `35ad763` approved | [#59](https://github.com/urruegg/frontier-envisioning/issues/59), [parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [SPRINT-011](../sprints/SPRINT-011-process-grounding-and-optional-systems.md); bounded runtime #60 handoff, no implementation or full-gate result yet |
| [PR-gated operating model](2026-11-14-pr-gated-operating-model-plan.md) | `@urruegg` accountable; spec `8de16ca`, subagent plan/readiness `e8ea6bd` | [#48](https://github.com/urruegg/frontier-envisioning/issues/48), [SPRINT-010](../sprints/SPRINT-010-pr-gated-operating-model.md); #49 contracts and #50 bootstrap/full local gates verified; identity/intake/eligibility/release adoption pending |
| [Caldova gallery extension](2026-11-13-caldova-gallery-extension-plan.md) | `@urruegg` accountable; inline plan/readiness approval at `8be6aa8` after written spec `4ef63d1` | [#41](https://github.com/urruegg/frontier-envisioning/issues/41), [SPRINT-008](../sprints/SPRINT-008-caldova-gallery-extension.md); ten real captures and full local gate verified; PR/CI separate |
| [Agent FinOps baseline](2026-11-12-agent-finops-baseline-plan.md) | `@urruegg` accountable; actual subagent-driven plan/readiness approval at `efb3468` | [#35](https://github.com/urruegg/frontier-envisioning/issues/35), [decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), D1 #38 / D2 #37 / D3 #39 and [SPRINT-007](../sprints/SPRINT-007-agent-finops-baseline.md); implementation in progress, delivery not yet verified |
| [Version 1.9.2](2026-11-12-version-1.9.2-plan.md) | `@urruegg` accountable; mechanical preparation | [#33](https://github.com/urruegg/frontier-envisioning/issues/33), [SPRINT-006](../sprints/SPRINT-006-version-1.9.2.md); local gates/rebuild proof pass, live PR/CI separate |
| [Internal user documentation](2026-11-12-internal-user-documentation-plan.md) | `@urruegg` accountable; execution directed in conversation | [#31](https://github.com/urruegg/frontier-envisioning/issues/31), [SPRINT-005](../sprints/SPRINT-005-internal-user-documentation.md); local gates pass, PR/CI and human review separate |
| [SPRINT-004 implementation](2026-11-11-handover-1.9-preview-finops-plan.md) | `@urruegg` accountable; parent plus bounded workers under approved written plan | [#25](https://github.com/urruegg/frontier-envisioning/issues/25), [receipt](../intake/handover-1.9.0.md), [SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md); D0–D5 local technical delivery complete, human-merged [PR #29](https://github.com/urruegg/frontier-envisioning/pull/29), 11 November; release/manual acceptance separate |
| [Selective 1.7 intake](2026-11-10-handover-1.7-intake-plan.md) | `@urruegg` accountable; parent coordinates bounded builder/renderer/docs workers under approved plan | [#22](https://github.com/urruegg/frontier-envisioning/issues/22), human-merged [#23](https://github.com/urruegg/frontier-envisioning/pull/23), [receipt](../intake/handover-1.7.0.md), [SPRINT-003](../sprints/SPRINT-003-handover-1.7-intake.md); local technical integration completed in human-merged [PR #24](https://github.com/urruegg/frontier-envisioning/pull/24), 11 November, main `907c3ca`; release/manual acceptance separate |
| [Anonymised distribution](2026-11-10-anonymised-distribution-plan.md) | `@urruegg` accountable; inline AI-assisted maintenance | [#20](https://github.com/urruegg/frontier-envisioning/issues/20), [SPRINT-002](../sprints/SPRINT-002-anonymised-distribution.md); no external clearance inferred |
| [Plural documentation layout](2026-11-10-documentation-layout-plan.md) | `@urruegg` accountable; scoped AI-assisted cleanup | [#18](https://github.com/urruegg/frontier-envisioning/issues/18); maintainer-directed naming/removal amendment, evidence in [SPRINT-001](../sprints/SPRINT-001-docs-governance-and-accessibility.md) |
| [Master implementation/delegation plan](2026-11-09-docs-governance-implementation.md) | Parent coordinator; `@urruegg` accountable | [#6](https://github.com/urruegg/frontier-envisioning/issues/6); integration through human-merged [#15](https://github.com/urruegg/frontier-envisioning/pull/15); protected human work remains separate |
| [Documentation foundation](2026-11-09-documentation-foundation-plan.md) | Bounded docs/builder workers | [#10](https://github.com/urruegg/frontier-envisioning/issues/10), human-merged [#12](https://github.com/urruegg/frontier-envisioning/pull/12); compatibility-index contract superseded by #18 |
| [Governance prose](2026-11-09-agent-governance-plan.md) | Bounded governance worker | [#9](https://github.com/urruegg/frontier-envisioning/issues/9), [#13](https://github.com/urruegg/frontier-envisioning/pull/13), then main via #15; policies remain Proposed |
| [Accessibility](2026-11-09-accessibility-plan.md) | Renderer worker; bounded catalogue correction | [#7](https://github.com/urruegg/frontier-envisioning/issues/7), main via #15; [A6 verification](../intake/2026-11-10-accessibility-verification.md#a6-linked-catalogue-ci-failure-corrected) |
| [Human governance handoff](2026-11-09-human-governance-plan.md) | `@urruegg`; person only | [#8](https://github.com/urruegg/frontier-envisioning/issues/8); final sign-off recorded, ownership corrected through human-merged [#17](https://github.com/urruegg/frontier-envisioning/pull/17); protected routing remains open |

## Historical implementation plans

| Plan | Record |
|---|---|
| [Cowork M0 intake](2026-11-08-cowork-m0-implementation-plan.md) | Initial engineering intake; [design](../specs/2026-11-08-cowork-intake-design.md) |
| [Handover 1.6](2026-11-09-handover-1.6-plan.md) | 1.6 intake and reproduction; [design](../specs/2026-11-09-handover-1.6-design.md) |
| [Workflow legend](2026-11-09-workflow-legend-plan.md) | Sticky legend correction; [design](../specs/2026-11-09-workflow-legend-design.md) |

Use `YYYY-MM-DD-<topic>-plan.md` for numbered test-first tasks with exact files,
commands, expected results and dependencies. Keep specifications in the
[specification catalogue](../specs/README.md), not in this folder.

The original historical records retain their format and status. Only the six
named pre-governance specs/plans are exempt from new metadata; their local links
and catalogue coverage still apply. Current plans require the six-field header.
Original approval evidence belongs to the linked records and sprint; it does not
activate policies, authorise protected actions or promise a delivery date.
