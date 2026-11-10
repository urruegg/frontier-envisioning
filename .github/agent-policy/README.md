# Agent policy catalogue

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot; AI-assisted drafting |
| Status | Proposed; human acceptance pending |
| Scope | Catalogue and authority boundaries for proposed Frontier engineering agent policy |
| References | [AGENTS](../../AGENTS.md), [Issue #9](https://github.com/urruegg/frontier-envisioning/issues/9), [Idea](../../docs/ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../../docs/specs/2026-11-09-docs-governance-and-accessibility-design.md), [G1 plan](../../docs/plans/2026-11-09-agent-governance-plan.md), [Master plan](../../docs/plans/2026-11-09-docs-governance-implementation.md), [Sprint](../../docs/sprints/SPRINT-001-docs-governance-and-accessibility.md), [Workflow](AGENT_WORKFLOW.md) |

## Authority and purpose

[AGENTS](../../AGENTS.md) is the working-agreement entry point. This catalogue
separates stable policy responsibilities from reusable skills and role-specific
agent definitions. These proposed documents neither grant permissions nor
replace active controls.

| Layer | Responsibility | Source |
|---|---|---|
| Policy | Stable authority, workflow and human boundaries; proposed here until accepted | This catalogue |
| Reusable skills | Repeatable engineering procedures and validation | [Project skills](../skills) |
| Agent personas | Bounded roles, tool limits and handoffs | [Agent definitions](../agents) |

| Policy | Responsibility |
|---|---|
| [AGENT_WORKFLOW](AGENT_WORKFLOW.md) | Linked intake, approval, execution and evidence |
| [NON_DELEGABLE_WORK](NON_DELEGABLE_WORK.md) | Human boundaries and stop/escalation response |
| [KPI_BASELINE](KPI_BASELINE.md) | Aggregate delivery evidence, not employee scoring |
| [BREAK_GLASS](BREAK_GLASS.md) | Human incident procedure; no agent bypass rights |

Policy activation requires recorded human acceptance. Existing stricter
requirements remain binding during the transition. Instructions and personas
do not replace permissions, hooks, GitHub rulesets or human approvals.
