# Sprint catalogue

| Field | Value |
|---|---|
| Version | 1.16 |
| Date | 2026-11-25 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Maintained catalogue; approval belongs to the linked records, not this guide |
| Scope | Linked work, dependencies, blockers and validation evidence |
| References | [Docs](../README.md), [Idea catalogue](../ideas/README.md), [Spec catalogue](../specs/README.md), [Plan catalogue](../plans/README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/6) |

| Sprint | Goal | State |
|---|---|---|
| [SPRINT-013](SPRINT-013-agent-factory-handover.md) | Add the optional Agent Factory full starter-repository handover skill for 1.11.0 | [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [idea](../ideas/2026-11-25-agent-factory-handover.md), [written spec](../specs/2026-11-25-agent-factory-handover-design.md), [staged plan/W0](../plans/2026-11-25-agent-factory-handover-plan.md); `@urruegg` accountable. Actual written spec `7f650c4` approved; W0 approval/host+receiver proof pending before exact downstream plans. Factory only; systems/D365 deferred. Not ready; no production implementation. |
| [SPRINT-012](SPRINT-012-release-evidence-simplification.md) | Remove manual release-evidence retention without removing automated verification | [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [idea](../ideas/2026-11-24-release-evidence-simplification.md), [approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [real plan](../plans/2026-11-25-release-evidence-simplification-plan.md); `@urruegg` accountable; spec `67dc9a5` and subsequent actual plan/execution `22f512f` approved. Bounded #68/#69/#70 implementation; protected adoption separate. |
| [SPRINT-011](SPRINT-011-process-grounding-and-optional-systems.md) | Correct current process grounding before optional systems foundation and Dynamics 365 | [#58](https://github.com/urruegg/frontier-envisioning/issues/58), [#59](https://github.com/urruegg/frontier-envisioning/issues/59), [idea](../ideas/2026-11-17-optional-systems-extensions.md), [correction spec](../specs/2026-11-17-process-governance-sap-grounding-design.md), [plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md); `@urruegg` accountable, original plan/readiness at `35ad763` and separate [#66](https://github.com/urruegg/frontier-envisioning/issues/66) amendment approved; implementation/reviews, local L2 and exact-package proof complete; final head/gate/server evidence in [PR #65](https://github.com/urruegg/frontier-envisioning/pull/65); human #52/#8 remain |
| [SPRINT-010](SPRINT-010-pr-gated-operating-model.md) | Make genuine human PR approval the routine engineering/release gate | [#48](https://github.com/urruegg/frontier-envisioning/issues/48), [idea](../ideas/2026-11-14-pr-gated-operating-model.md), [specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [plan](../plans/2026-11-14-pr-gated-operating-model-plan.md), [ADR-0030](../adr/0030-pr-gated-engineering-automation.md); owner `@urruegg`; spec `8de16ca`, subagent plan/readiness `e8ea6bd`, #49 contracts and #50 bootstrap/full local gates verified; live adoption pending |
| [SPRINT-008](SPRINT-008-caldova-gallery-extension.md) | Extend the Caldova gallery with architecture and workshop captures | [#41](https://github.com/urruegg/frontier-envisioning/issues/41), [idea](../ideas/2026-11-13-caldova-gallery-extension.md), [design](../specs/2026-11-13-caldova-gallery-extension-design.md), [plan](../plans/2026-11-13-caldova-gallery-extension-plan.md); owner `@urruegg`; inline plan/readiness at `8be6aa8`; ten captures and full local gate verified; PR/CI and human sign-off separate |
| [SPRINT-007](SPRINT-007-agent-finops-baseline.md) | Versioned offline Agent FinOps baseline before build handover | [#35](https://github.com/urruegg/frontier-envisioning/issues/35), [decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36); spec approved at `2e3c0e7`, plan/readiness at `efb3468`; owner `@urruegg`; local strict L1/L2, exact-ZIP execution and independent two-build identity verified; PR/CI, human sign-off and publication remain separate |
| [SPRINT-006](SPRINT-006-version-1.9.2.md) | Verified 1.9.2 build from the current merged product | [#33](https://github.com/urruegg/frontier-envisioning/issues/33); local verification complete, PR/CI and publication separate |
| [SPRINT-005](SPRINT-005-internal-user-documentation.md) | Internal user guide, Caldova HTML/gallery and starter prompt | [#31](https://github.com/urruegg/frontier-envisioning/issues/31); local implementation/gates verified; live PR/CI and human review separate |
| [SPRINT-004](SPRINT-004-handover-1.9-preview-finops.md) | Selective 1.9 process intake and optional acknowledged Preview FinOps | [#25](https://github.com/urruegg/frontier-envisioning/issues/25), children #28/#26/#27; D0–D5 local technical delivery complete, human-merged [PR #29](https://github.com/urruegg/frontier-envisioning/pull/29), 11 November; release/manual acceptance separate |
| [SPRINT-003](SPRINT-003-handover-1.7-intake.md) | Selective 1.7.1 feature intake, build and internal distribution | [#22](https://github.com/urruegg/frontier-envisioning/issues/22); local technical integration completed in human-merged [PR #24](https://github.com/urruegg/frontier-envisioning/pull/24), 11 November, main `907c3ca`; historical seven-skill evidence retained, current package has eight; release/manual acceptance separate |
| [SPRINT-002](SPRINT-002-anonymised-distribution.md) | Anonymised current references and validated distribution artifacts | [#20](https://github.com/urruegg/frontier-envisioning/issues/20); local strict gates, eleven-entry bundle and seven-skill offline install verification pass; internal candidate, review/clearance separate |
| [SPRINT-001](SPRINT-001-docs-governance-and-accessibility.md) | Documentation foundations, governance, accessibility and linked plural-layout cleanup | #15 human-merged with L1/L2 evidence and final sign-off; #17 human-merged ownership correction. #18 cleanup tracked; policies Proposed, protected routing still open |

Sprint state records delivery, not design approval, permissions or an invented
schedule. Each ready item has a real issue and governing idea/spec/plan links.

SPRINT-007 began as an early draft row. Its full work-item record now links
the real implementation plan, written after explicit written-spec approval.
The later plan/readiness approval at `efb3468` is a separate actual decision.
The sprint now records actual source-qualified local engineering and handoff
proof, not inferred labels, human acceptance, publication or deployment.
