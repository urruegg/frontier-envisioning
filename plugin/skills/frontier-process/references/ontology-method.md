# Process ontology method (Fabric IQ)

Use the [process skill](../SKILL.md) when process/data design is requested.
It turns the blueprint into local ontology and design proposals, not tenant
items or published data products. Examples below use only the fictitious
Caldova Industrial AG. The wrapper's GA designation does not make Fabric
ontology, agent integrations or operations agents GA, verify mappings or
approve a release, deployment or external sharing.

## 1. Sources and limits

Source IDs S1–S44 refer to `../templates/fabric-iq-canon.json`; standard-entity
proposals are in `../templates/cdm-map.json`. The canon records
`checked: 2026-11-11`. That is received source metadata, not an independent
availability or tenant check by this documentation intake. Re-check dated
Microsoft Learn guidance, known issues and tenant eligibility before relying
on the proposal, and within the canon's 90-day review window.

Key references from that canon:

- S2: [What is ontology (preview)?](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview)
- S3: [Data binding in ontology (preview)](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data)
- S4: [Import and export ontologies (preview)](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-import-export)
- S6: [Create an operations agent grounded in an ontology (preview)](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-operations-agent)
- S14: [Add and configure data sources in a Fabric data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-add-datasources)
- S17: [Create a data agent grounded in an ontology (preview)](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-data-agent)
- S18: [Common Data Model](https://learn.microsoft.com/en-us/common-data-model/)
- S33: [Implement medallion lakehouse architecture in Fabric](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)
- S35: [Operational standards for a unified data platform](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/data/operational-standards-unified-data-platform)
- S38: [Data products in Unified Catalog](https://learn.microsoft.com/en-us/purview/unified-catalog-data-products)

These are source pointers, not claims that their current publication,
availability or import behaviour has been verified here.

## 2. Name the business objects

Use an ontology when journeys share business objects or need to reason across
systems. One team asking questions of a single table may need only a data agent.
Start from the seed's journey patterns; confirm names with the process owner.
For Caldova, Customer places Sales order and Asset has Work order are hypotheses.

| Element | Modelling rule |
|---|---|
| Entity type | One business concept, not one type per source table; keep business names and synonyms |
| Key | String or integer property identifying an instance; confirm master record and owner |
| Property | String, integer, double, boolean or datetime; one type per property name across the ontology |
| Time series | Changing values with a timestamp binding; confirm UTC handling |
| Relationship | Verb, known ends and cardinality; inheritance only for real specialisation, one parent |
| Rule | One sentence linked to the objects it constrains; identify the human approval seam |
| Metric | Journey KPI and owned measure, or an explicit “to define” gap |
| Namespace | Journey vocabulary plus shared core objects |

Ask what identifies each object, where its authoritative record lives, which
system changes it and who can confirm its quality. Never invent tables or owners.

## 3. Propose standard mappings and OneLake layers

CDM is a candidate common vocabulary, not proof that every Dynamics 365 table
already matches. Distinguish `cdm`, app-specific `dataverse`, finance and
operations `operations`, and `custom`. Keep `exact`, `extends`, `related` or
`custom` match intent, table/key/property proposals, source IDs and checked
status. Confirm logical names and columns against the actual system with its
data owner. SAP and other systems also need explicit mapping work.

The mapping catalogue has eleven unverified F&O entries. Integrated Caldova
D1 evidence has six mappings to verify and an Employee binding gap. Those are
different scopes; neither means all Dynamics 365 data has been verified.

| Layer | Proposal | Confirm before use |
|---|---|---|
| Bronze | Mirroring, shortcuts/Link to Fabric, eventstreams or pipelines, depending on supported source | Tenant/source support, permissions, freshness and data movement |
| Silver | Conformed business objects in `<namespace>_silver`; live events in `<namespace>_events` | Canonical model, keys, matching, lineage and quality |
| Gold | Curated products and journey semantic models owning measures | Consumers, measures, Direct Lake suitability and service commitment |

Bind agent-facing entity types to suitable tables, not semantic-model bindings
while the recorded S6/S17 limitation applies (R-ONT-2); re-check it in the tenant.
Keep semantic models as measure owners. Fabric domains per journey/shared core
and Purview governance domains are proposals, not automatically created items.
Mail/meetings remain Work IQ; documents/policies remain Foundry IQ knowledge;
web sources remain Web IQ. Do not copy master data into an agent-owned store.

## 4. Data and knowledge products

For each product record accountable owner, business purpose, intended uses,
access process and quality status, plus sensitivity, lineage, endorsement,
glossary/critical elements and service commitment where needed (S35, S38).
Missing fields are publication gaps, not approval. Approval for reporting or AI
grounding does not authorise agent actions; actions need additional review.
Documents are knowledge products, not automatically analytical data products.

Integrated Caldova evidence reports 18 data products plus one knowledge product,
19 unique products. Proposed owner roles and quality targets in examples are
not real service commitments or evidence of publication.

## 5. Ground agents and protect evidence

Propose one data agent per journey with realistic questions, intended consumers
and no more than five sources. Keep instructions/source descriptions and verify
example SQL/KQL/DAX in the tenant. Read-only answers respect user permissions;
publishing to Microsoft 365 Copilot requires a separate data-protection review
(S10). Operations-agent proposals need live signals and named human approval
for actions, not autonomous authority inferred from a model.

Customer projections must exclude internal-derived descriptions, bindings,
instructions, products, rules, metrics, operations proposals and promoted
workshop content. Removing source IDs alone is not sanitisation. Review embedded
data and all downloads; a customer projection is not external/IP clearance.

## 6. Build locally, then verify manually

1. Seed/refine with the [skill procedure](../SKILL.md); keep `ontology.json` as
   the working proposal and retain evidence IDs, checked flags and open gaps.
2. Build with `python scripts/build_ontology.py --ontology ontology.json --blueprint blueprint.normalized.json --out-dir working/ontology`.
   Add `--strict` when warnings must block handoff. Fix errors; strict warnings
   fail before publishable writes. Never edit generated Turtle to hide a gap.
3. Review `ontology.normalized.json`, `ontology.ttl`, `ontology.md`,
   `data-agents.md` and `data-products.md`; add `--ontology ontology.json` to the
   blueprint wrapper for the optional Ontology page.
4. Manual tenant work: re-check S4, import into a new empty ontology (Preview)
   item, inspect the import summary, and configure/verify keys, bindings, rules,
   metrics and permissions. OWL restrictions are not assumed imported.
5. Test native import, data-agent questions and operations approval in Fabric.
   Local deterministic output or Python/browser Turtle byte parity does not
   certify native import, product availability or tenant behaviour.
6. In the workshop, confirm keys, mappings, owners, products and questions.
   Export `onto:<id>` verdicts and merge with `merge_ontology_feedback.py`;
   revalidate and rebuild. Model validation is not publication approval.

Process does not require FinOps. For requested costs, follow the full
[FinOps notice and actual current-scenario confirmation](../../frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure)
before any cost operation/recommendation/figure. On decline, preserve old
Preview originals/provenance and use clean core/ordinary non-FinOps inputs;
state the budget gap, not zero costs or passed readiness.
