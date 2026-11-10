# Human incident handoff

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot; AI-assisted drafting |
| Status | Proposed; human acceptance pending |
| Scope | Human-only incident recording, narrow attended changes, restoration and validation |
| References | [AGENTS](../../AGENTS.md), [Issue #9](https://github.com/urruegg/frontier-envisioning/issues/9), [Idea](../../docs/ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../../docs/specs/2026-11-09-docs-governance-and-accessibility-design.md), [G1 plan](../../docs/plans/2026-11-09-agent-governance-plan.md), [Master plan](../../docs/plans/2026-11-09-docs-governance-implementation.md), [Sprint](../../docs/sprints/SPRINT-001-docs-governance-and-accessibility.md), [Policy catalogue](README.md), [Human boundaries](NON_DELEGABLE_WORK.md), [Workflow](AGENT_WORKFLOW.md) |

## Human incident procedure only

Use the normal protected PR path whenever available. This document grants no
agent right to approve, initiate, widen or execute bypass, direct `main` writes,
force pushes, permission changes or deployment.

An authorised person may assess an incident only through the organisation's
actual rules. Record the real incident/work item, reason, approver, exact
scope/refs/settings, start/end, commands, captured prior state, restoration
and validation evidence, and corrective PR.

The person captures current state, applies only the authorised narrow change
while attending it, restores protection immediately, runs required checks and
links the audit/corrective record. Stop for unclear scope, destructive risk,
failed validation or inability to restore protection.

Do not use emergency language for convenience, failed-test avoidance, unrelated
changes, concealment, unreviewed history, credentials or identity changes.
Do not copy nonexistent reference-repository workflows/rulesets or claim they
are active. Agents prepare a safe handoff only and never execute this procedure.
