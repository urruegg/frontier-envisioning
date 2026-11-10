# Non-delegable work

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot; AI-assisted drafting |
| Status | Proposed; human acceptance pending |
| Scope | Existing human-only actions, protected surfaces and the required agent stop/handoff |
| References | [AGENTS](../../AGENTS.md), [Issue #9](https://github.com/urruegg/frontier-envisioning/issues/9), [Idea](../../docs/ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../../docs/specs/2026-11-09-docs-governance-and-accessibility-design.md), [G1 plan](../../docs/plans/2026-11-09-agent-governance-plan.md), [Master plan](../../docs/plans/2026-11-09-docs-governance-implementation.md), [Sprint](../../docs/sprints/SPRINT-001-docs-governance-and-accessibility.md), [Policy catalogue](README.md), [Workflow](AGENT_WORKFLOW.md), [Human incident procedure](BREAK_GLASS.md) |

## Human-only boundaries

Agents must not:

- Give design, plan, readiness, PR or release approvals; merge PRs; create
  releases or tags; force-push or push to `main`.
- Change repository settings, rulesets, secrets, variables or permissions;
  invite collaborators; set protected labels such as `status:ready` or
  `approved:*`.
- Run deployments or workflows manually; make `azd`/`az` changes
  (`az bicep build` remains the existing allowed validation exception).
- Bypass commit hooks or edit protected governance files.

Protected files include hooks/guardrails, CODEOWNERS, licences, immutable release
records, release/deployment workflows, the neutrality denylist and vendored
third-party skills. The authoritative existing
[AGENTS restrictions and protected-file table](../../AGENTS.md) remain in force;
this list does not narrow them.

Generated files change only through approved source/build commands, never
manual edits. Customer-data classification, external distribution and release
acceptance are not delegated merely because an agent can access a tool.
This does not add a ban on approved offline data stripping within an authorised
task or grant authority to reclassify or distribute the data.

## Required response

Stop the prohibited action. Identify the boundary and accountable human.
Prepare only a safe, scoped decision/change artefact. Record the real human
decision and its evidence without inventing it. Do not resume automatically.

Approval of a design or plan is not approval to cross these boundaries.
No emergency or convenience exception grants an agent bypass rights.
The [human incident procedure](BREAK_GLASS.md) permits an agent to prepare a
safe handoff only, not to perform the procedure.
