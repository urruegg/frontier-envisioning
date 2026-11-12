# SPRINT-007: Agent FinOps baseline before build handover

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Human plan/readiness approved at efb3468; Task 0 in progress, delivery not yet verified |
| Scope | Offline baseline-first 1.10.0 internal candidate, not live FinOps operations |
| References | [Catalogue](README.md), [Parent #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [Idea](../ideas/2026-11-12-agent-finops-baseline.md), [Design](../specs/2026-11-12-agent-finops-baseline-design.md), [Plan](../plans/2026-11-12-agent-finops-baseline-plan.md), [ADR-0028](../adr/0028-versioned-agent-finops-baselines.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#35](https://github.com/urruegg/frontier-envisioning/issues/35) | [Outcome/input](../ideas/2026-11-12-agent-finops-baseline.md) | [Baseline design](../specs/2026-11-12-agent-finops-baseline-design.md) | [Tasks 0-8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; accountable | Actual D35-09 plan/readiness approval recorded | Approved for bounded implementation; no label change inferred | Spec approval `2e3c0e7`; plan approval `efb3468`; no delivery/PR proof yet |
| [#38](https://github.com/urruegg/frontier-envisioning/issues/38) | [Baseline-first](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01 to AFB-10](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D1, Tasks 1-3](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D1, estimated M | Plan approval; Task 0 version preparation | Draft; no code | Proposed bounded engine/records/projection/CLI work |
| [#37](https://github.com/urruegg/frontier-envisioning/issues/37) | [Canvas/handover](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01/06/09/11](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D2, Tasks 4/6](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D2, estimated M | D1 stable contract and review; fixture preparation before UI | Draft; no code | Existing wrapper/renderer integration, not a new app |
| [#39](https://github.com/urruegg/frontier-envisioning/issues/39) | [Verified candidate](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-10/11/12](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D3, Tasks 0/5/7/8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D3, estimated M | Preparation first; final proof after D1/D2 | Task 0 in progress; final verification pending | No full 1.10.0 gate, distribution or deployment evidence yet |

## Human evidence and gates

Actual structured answers D35-01 to D35-07 on #35/#36 approve the product
choices and four design sections. D35-08 is the actual
`approve-written-spec` response for
`2e3c0e79dc45c9ab06775def9f31cfb3bad7a8aa`.
The implementation plan was written only after that response.

The subsequent actual `approve-subagent-driven` response is D35-09:
**plan/readiness approved at `efb3468dbe597ea6112b6839c7019243ab44b885`**,
with subagent-driven execution selected. Design and plan approvals were
separate decisions. No ready/approved label, assignment, milestone-field
change or GitHub review is inferred. Proposed issue
classifications/sizes are not assertions about applied server metadata.
The historical PRD release table is not a live milestone assignment.

Use the existing private host and `@urruegg` as sole accountable human owner.
The user explicitly requires waiting at questions despite autopilot.
No live billing connector, deployed FinOps Agent, purchasing or authenticated
financial-approval service belongs to this sprint.

## Preparation evidence, not new-feature evidence

The native worktree was explicitly consented. Its clean 1.9.2 source passed
81 existing FinOps unit tests and the baseline documentation check.
The planning-only seven-file commit `2e3c0e7` passed
`python tools/dev.py docs --strict` with zero errors and `git diff --check`.
It was pushed without modifying runtime code or the product version.

These are planning/baseline results, not red/green implementation proof,
full 1.10.0 L1/L2, package execution or distribution acceptance.
The implementation will record exact checked heads, commands/results,
counts and archive hashes here after they exist.

Protected routing [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
and release-cache [#30](https://github.com/urruegg/frontier-envisioning/issues/30)
remain human-owned. No merge, tag/release, deployment or protected edit is
authorised by this sprint record.
