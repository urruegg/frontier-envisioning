# ADR-0026: Optional process ontology for Microsoft Fabric IQ, as its own skill, exported as OWL in Turtle

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-11 |
| Author | Received ADR author not recorded; Copilot AI-assisted selective adaptation |
| Status | Proposed; integration evidence is not decision or release approval |
| Scope | Optional process wrapper and local ontology exports in unreleased 1.9.1 |
| References | [Catalogue](README.md), [PRD intake](../prd.md#191-development-intake), [Design intake](../solution-design.md#191-development-intake), [Approved design](../specs/2026-11-11-handover-1.9-preview-finops-design.md), [SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md), [Receipt](../intake/handover-1.9.0.md) |

## Context

The blueprint names journeys, systems, KPIs and agents, but build teams also
need a shared vocabulary for business objects and their governed sources.
The received proposal uses Fabric IQ ontology (Preview) to connect those
objects to OneLake and agent grounding. Not every engagement needs it.
Fabric ontology/agent integrations and operations agents remain Preview;
source publication and tenant availability are not independently verified here.

## Decision

- Keep `frontier-process` a separate, optional GA **product wrapper** when
  requested. GA is the maintainer's designation, not mapping confidence,
  provider GA, release/deployment or external/IP clearance. It needs no FinOps.
- Seed a `frontier-ontology/1.0` proposal from journey patterns, blueprint
  evidence and optionally a TMSL semantic model. Preserve business names,
  source IDs, measure ownership, known issues and open owner/binding gaps.
- Validate names, keys, supported types, shared property types, relationships,
  single inheritance, source references, duplicate questions and at most five
  sources per data agent. Invalid models or strict warnings fail before
  publishable output, preserving previously good artifacts.
- Export local `ontology.normalized.json`, `ontology.ttl`, `ontology.md`,
  `data-agents.md` and `data-products.md`. OWL in Turtle is the proposed
  reviewable handover, not a certified Fabric item definition. Native import,
  keys, bindings, rules, metrics and tenant agent tests remain manual.
- Add the Ontology page only with requested ontology data. Keep readiness/risk
  proposals and `onto:<id>` feedback source-linked. Customer projection covers
  descriptions, bindings, instructions, products, rules, metrics and operations
  content, not merely source-ID removal.

## Consequences

The data layer can be designed without making it mandatory or provisioning
anything. Proposed data agents reuse journey identities; operations proposals
require live signals and a real human approval seam.

The [process method](../../plugin/skills/frontier-process/references/ontology-method.md)
links the received canon's dated S1–S44 source IDs, including
[Import and export ontologies (preview), S4](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-import-export).
Its recorded 11 November 2026 check date is not a new independent availability
check. Re-check known issues and import behaviour in the target tenant.
The local D1/D3 evidence in the sprint supports implementation, not import or
publication claims. Standard mappings and data-product rationale continue in
[ADR-0027](0027-cdm-grounding-and-data-products.md), also Proposed.

## Alternatives considered

Embedding all modelling in the blueprint skill would obscure optionality.
Generating Fabric REST item definitions would depend on tenant access and
changing Preview formats. A generic diagram lacks bindings, governance and
agent grounding. Modelling every source table confuses business vocabulary
with physical storage.
