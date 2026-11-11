# Design rules for Frontier solution designs

The rules every PRD and solution design produced with this plugin keeps. They generalise the Innovation Hub's design-repository practice (for example the HR Frontier sample), so the second use case costs materially less than the first.

## 1. Platform commitments

1. **Systems of record stay authoritative.** No agent-side copy of master data. The process store (for example Dataverse) records what ran, what it touched, what happened and what a person must still do, never the master-data values. Test: if the system of record were restored from backup, would this column now be wrong? Then it does not belong in the process store.
2. **The workflow owns the process; the agent owns the judgement.** Trigger, step sequence, audit writes, approvals and escalation run as deterministic workflow steps; the agent is called where reasoning is needed and returns values with confidence, or a refusal.
3. **Every write path declares an envelope, enforced server-side.** Which targets, which fields, under which conditions, with which refusals; rejected regardless of what the agent asks for.
4. **The agent never holds the write connection.** A governed access layer (a workflow called as a tool, an MCP server or a custom connector) owns the connection through a connection reference bound to a service identity.
5. **People decide.** Anything with a consequence for a person, a customer commitment, money or a published figure stops at an approval seam with state.

## 2. Three independent enforcement layers

| Layer | Enforces | Defeated by |
|---|---|---|
| Agent instructions and skills | The intended behaviour | Prompt injection in outside content |
| Access layer (declared actions) | Read-before-write, allow-list, idempotency | A defect in the access layer |
| System-of-record permissions (integration user) | What the credential can touch at all | Only a security change in the system |

Design the system permissions first, then the access layer, then the agent.

## 3. The seven declarations

Write envelope, refusal set, escalation path, grounding sources, data classification, people-decision surface, measurement. A use case that cannot answer all seven is not ready.

## 4. Identity and environments

- One Microsoft Entra Agent ID per agent and environment; separate service identities for workflows and access layers; no long-lived secrets where workload identity federation works.
- DEV (synthetic data), TEST (approved test data), PROD; managed solutions promoted by a pipeline; environment variables and connection references for everything environment-specific.
- One DLP data group holding the full connector inventory, applied before the first artefact is built; outbound connectors blocked unless reviewed.

## 5. Observability and cost

Run records, field-level outcomes, exception queue, evaluation test sets in CI/CD, consumption alerts (an exhausted capacity must never block a date-bound process silently), Purview audit for data-protection events.

Design is independent of FinOps. Missing budget evidence stays open with its
real owner, not zero or an automatic readiness pass. Only for requested Preview
costs, follow the [full notice and actual scenario confirmation](../../frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure)
before operations/recommendations/figures. Preserve the warning, non-GA
grounding/model limitations, assumptions and scenario/model/rate/source
provenance in cost-derived requirements, ROI/NPV, comparisons and exports.
Legacy/imported costs remain Preview; a technical flag, old JSON or workshop
status is not budget approval. Independently verify prices and terms.

## 6. Identifiers and naming

| Prefix | Meaning |
|---|---|
| FR-0001 | Functional requirement (platform 0001 to 0099, use cases from 0100) |
| NFR-0001 | Non-functional requirement |
| AC-001 | Acceptance criterion |
| D-01 | Open business decision |
| TD-01 | Open technical decision |
| ADR-0001 | Architecture decision record |
| UC-0001 | Use case |

Numbers are allocated once and never reused, including after supersession. A use-case PRD may add requirements; it may never weaken the platform's. An approved ADR outranks narrative text.

## 7. Repository structure (when the user wants a design repository)

```
README.md                 product at a glance, MVP, the three decisions to settle first
AGENTS.md                 the rules every agent must satisfy (commitments, declarations, refusals)
docs/prd.md               platform requirements (FR, NFR, roles, gates)
docs/solution-design.md   architecture, integration, security, ALM, observability
docs/journey-and-raci.md  journeys, RACI, sequencing, the seven declarations per use case
docs/adr/                 ADR-0001 … why, and what was rejected
docs/ideas/               one record per use-case idea and its lifecycle
<domain>/docs/use-cases/  use-case PRDs for graduated use cases
data/                     field lists and mappings; never real personal data
```

## 8. ADR template

```
# ADR-000n: <title>
- Status: proposed | accepted | superseded by ADR-000m
- Date: YYYY-MM-DD
## Context        what forces the decision (cite evidence ids)
## Decision       what we do
## Rationale      why, with the Microsoft guidance it follows
## Alternatives   what we rejected, and why
## Consequences   what becomes easier, harder, or must be monitored
```
