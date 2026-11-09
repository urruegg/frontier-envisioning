# Traceable documentation and accessible Frontier Envisioning

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code; user-requested work |
| Status | Idea accepted through design approval; implementation not approved |
| Scope | Repository documentation, engineering intake, agent governance and HTML accessibility |
| References | [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Plan](../plan/2026-11-09-docs-governance-implementation.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md) |

## Problem and outcome

Documentation and engineering guidance must remain current as the Cowork plugin
evolves. Requirements and architecture currently share one document. Intake
records lack a dedicated linked sprint catalogue. The HTML has measured
accessibility barriers despite existing functional tests.

The outcome is a constrained documentation agent, two authoritative product
documents, traceable idea/spec/plan/sprint/issue records, clear Frontier-specific
policy and an evidence-led accessibility improvement.

## Alternatives and decision

| Alternative | Assessment |
|---|---|
| Copy the reference repository | Rejected: wrong host authority, HR assumptions, excessive metrics and incompatible tooling |
| Split documents only | Insufficient: leaves governance, traceability and accessibility disconnected |
| Adapt in bounded workstreams | Accepted design: preserve contracts and add measurable checks with human governance seams |

Non-agent alternatives remain appropriate for mechanical validation and human
approvals. A documentation persona assists maintenance; deterministic checks
prove structure, and people retain decisions and permissions.

## Evidence, constraints and ownership

- [134-file header assessment](../intake/2026-11-09-markdown-header-audit.csv).
- [38-scan Microsoft Edge accessibility evidence](../intake/2026-11-09-accessibility-audit.json).
- The repository remains the approved private `urruegg/frontier-envisioning`
  source/issue/PR host. No Azure Repos/Azure Boards migration is included.
- Caldova Industrial AG is the fictitious sample. No customer data or secrets
  are introduced.
- Accountable maintainer: `@urruegg`. Human-owned collaboration and ownership
  changes are tracked in [#8](https://github.com/urruegg/frontier-envisioning/issues/8).
- Scope excludes releases, deployments, permissions, protected hook edits by
  agents, historical rewriting and blanket packaged-document header changes.

## Approval provenance

On 9 November 2026 the user wrote:

> Okay design is approved and you can write the plan to implement it sub agent delegated implementation after plan approval

This approves the design and planning. It does not approve the implementation
plan or authorise protected operations.
