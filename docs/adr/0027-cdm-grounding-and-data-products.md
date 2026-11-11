# ADR-0027: Ground the process ontology in the Microsoft Common Data Model, on a medallion semantic layer with data products

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-11 |
| Author | Received ADR author not recorded; Copilot AI-assisted selective adaptation |
| Status | Proposed; integration evidence is not decision or release approval |
| Scope | Proposed standard mappings, semantic layers and governed data products; not a FinOps ADR |
| References | [Catalogue](README.md), [ADR-0026](0026-process-ontology-fabric-iq.md), [PRD intake](../prd.md#191-development-intake), [Design intake](../solution-design.md#191-development-intake), [SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md), [Receipt](../intake/handover-1.9.0.md) |

## Context

The process ontology keeps business names but needs an agreed canonical shape
and accountable data owners. The received proposal uses Microsoft Common Data
Model, Dataverse and finance and operations concepts, medallion layers and
governed products. These are design proposals, not proof that every Dynamics 365
table already matches, that Link to Fabric is available for every source or
that a product has been published. This ADR concerns CDM/data products, not FinOps.

## Decision

- Propose a standard entity per business concept where appropriate. Preserve
  `cdm`, `dataverse`, `operations` and `custom`, match intent (`exact`, `extends`,
  `related`, `custom`), table/key/property mapping, source IDs and checked flags.
  Keep the business name; standard names become synonyms/descriptions in Turtle.
  Verify actual table/column semantics with the data owner before use.
- Propose bronze source ingestion, conformed silver business objects and gold
  products/semantic models owning measures. Use suitable table bindings for
  agent-facing entities while the recorded semantic-model limitation applies;
  verify the current limitation in the target tenant.
- Propose journey/shared Fabric domains and corresponding Purview governance
  domains with accountable owners. Local models create no domains or permissions.
- Record purpose, intended uses, access process and quality status per product,
  with commitment, sensitivity, lineage, endorsement and glossary/critical
  elements where needed. Missing fields are publication gaps. AI-grounding
  approval does not grant agent-action approval; actions need additional review.
  Documents remain knowledge products rather than analytical data products.
- Generate design/register downloads locally; retain Python/browser Turtle
  byte parity without claiming native Fabric import certification.

## Consequences and integration qualifications

A common vocabulary can reduce cross-system ambiguity, but mapping work remains
for Dynamics 365 as well as SAP and other systems. The canonical model is a
data-owner decision, not an automatic conversion.

The catalogue has **eleven unverified F&O entries**. The integrated Caldova D1
model has **six mappings to verify** and an **Employee binding gap**. These
are different scopes, not conflicting verification totals. Integrated evidence
also reports 18 data products and one knowledge product, 19 unique products;
that is a local model inventory, not published service commitments.

Source IDs S18–S44 and the recorded `checked: 2026-11-11` date remain in
`plugin/skills/frontier-process/templates/fabric-iq-canon.json`. Key pointers:
[Common Data Model, S18](https://learn.microsoft.com/en-us/common-data-model/),
[Medallion architecture, S33](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture),
[Operational standards, S35](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/data/operational-standards-unified-data-platform)
and [Purview data products, S38](https://learn.microsoft.com/en-us/purview/unified-catalog-data-products).
Their current availability, publication/deprecation claims and tenant behaviour
were not independently checked by this intake. Use the
[process method](../../plugin/skills/frontier-process/references/ontology-method.md)
and manual import/data-agent verification before relying on them.

## Alternatives considered

Keeping each source model in silver leaves vocabulary inconsistent. Renaming
business objects to standard table names loses workshop language. Documentation-
only mapping omits provenance from exports. Binding agent-facing entities to
gold semantic models ignores the recorded Preview limitation. The received
preference for unified-data-platform guidance over older Cloud-Scale Analytics
is retained as rationale, not a newly verified deprecation claim.
