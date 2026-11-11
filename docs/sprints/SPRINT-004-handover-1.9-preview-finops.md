# SPRINT-004: 1.9 intake and optional Preview FinOps

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-11 |
| Author | Copilot SDK in VS Code; AI-assisted sprint planning |
| Status | Design and written plan approved; implementation starting, acceptance not yet verified |
| Scope | Selective process/ontology intake and seven GA skills plus acknowledged optional Preview FinOps |
| References | [Catalogue](README.md), [Parent #25](https://github.com/urruegg/frontier-envisioning/issues/25), [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md), [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md), [Plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) |

## Outcome and work items

Keep the received process improvements while making FinOps genuinely optional
and Preview, with actual awareness before operations/figures and no hidden
dependency of the GA core. Product maturity is separate from provider Preview,
mapping confidence, release, deployment and external clearance.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#25](https://github.com/urruegg/frontier-envisioning/issues/25) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D0-D5](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) | `@urruegg`; parent coordinator | Actual written-plan approval | Planning only | Actual design quote below; no new product verification |
| [#28 process](https://github.com/urruegg/frontier-envisioning/issues/28) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D1](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d1-process-models-and-deterministic-artifacts) | `@urruegg`; bounded builder | D0 and plan approval | Proposed | Received source only; not executed |
| [#26 FinOps](https://github.com/urruegg/frontier-envisioning/issues/26) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D2](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d2-operational-finops-preview-gating) | `@urruegg`; bounded builder | D1; single wrapper writer | Proposed | No runtime gate claimed |
| [#27 renderer](https://github.com/urruegg/frontier-envisioning/issues/27) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D3](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d3-ontology-and-preview-aware-ui) | `@urruegg`; bounded renderer | D1-D2 and built fixtures | Proposed | No new view/maturity implementation |

## Approval and readiness

At `2026-11-11T10:29:30.009+01:00` the maintainer specified the optional Preview
FinOps/non-GA grounding and model boundary, and GA status for the other skills.
After the proposal, at `2026-11-11T11:02:02.033+01:00`:

> design is approved and you can proceed

Actual approval is recorded on #25 and in the linked idea. The earlier unavailable
form did not grant approval; this later instruction approves the design direction.
The new written plan did not exist then and still requires separate approval.

- [x] Real parent and child issues, owner, sample data and affected paths defined.
- [x] Source version 1.9.0 / 279-file fingerprint identified and unchanged.
- [x] Bundled-but-gated design direction and product-maturity boundaries approved.
- [x] Per-invocation/scenario acknowledgement and default/Preview modes explicit
  in the plan for review; no cached/global consent.
- [x] After the written plan was presented, the maintainer explicitly stated
  "okay the plan is approved please implement it sub agent driven now".
  This is recorded on #25; the earlier unavailable form is not the approval.
- [ ] Human label state checked separately if applied; no agent mutation.

## Evidence and constraints

Current main: `907c3ca5d1ce94ca479ec7c9a3887187574cc0f4`, 1.7.1.
Received path/hash inventory:
`904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9`.
The original comparison has 214 unchanged, 48 changed and seventeen new files
against the 1.7 receipt. The wrapper guide remains historical 1.7 context.

The preceding intake analysis checked static syntax and limited redacted hygiene,
not incoming runtime correctness. Current 1.7.1 baseline gates pass; those results
are not evidence of implemented 1.9.1 or a working Preview gate.

No incoming execution, source/version/maturity change, tenant import, actual
Cowork install or new distribution artifact is claimed at this planning stage.
Keep the repository private; protected #8 routing, approvals/labels, licences/
releases/workflows, merge/tag/deploy and external/IP clearance remain human work.
