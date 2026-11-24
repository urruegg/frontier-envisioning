# Process ontology method (Fabric IQ)

*Method maintenance: Copilot AI-assisted, 24 November 2026; original authorship not recorded.*

Use the [process skill](../SKILL.md) when process/data design is requested.
It turns the blueprint into local ontology and design proposals, not tenant
items or published data products. Examples below use only the fictitious
Caldova Industrial AG. The wrapper's GA designation does not make Fabric
ontology, agent integrations or operations agents GA, verify mappings or
approve a release, deployment or external sharing.

## 1. Sources and limits

Source IDs S1–S44 refer to `../templates/fabric-iq-canon.json`; standard-entity
proposals are in `../templates/cdm-map.json`. The canon records
`checked: 2026-11-11`. That date and S1–S44 remain historical evidence, not an
independent current availability or tenant check. The additive G59 records below
were checked read-only by the parent on **17 November 2026**; this maintenance
does not claim a new 24 November fetch. Re-check dated
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
- S38: [Data products in Unified Catalog](https://learn.microsoft.com/en-us/purview/unified-catalog-data-products) — retained historical context, not new setup guidance

These are source pointers, not claims that their current publication,
availability or import behaviour has been verified here.

Current governance/SAP evidence uses separate IDs, never retargeted S IDs:

| Canon ID | Microsoft source | Source updated |
|---|---|---|
| G59-P1 | [Learn about Microsoft Purview Unified Catalog](https://learn.microsoft.com/en-us/purview/unified-catalog) | 12 November 2026 |
| G59-P2 | [A next step in the evolution of the Microsoft Data Governance strategy](https://techcommunity.microsoft.com/blog/microsoft-security-blog/a-next-step-in-the-evolution-of-the-microsoft-data-governance-strategy/4572227) | 12 November 2026 |
| G59-P3 | [Microsoft Fabric Mirrored Databases From SAP](https://learn.microsoft.com/en-us/fabric/mirroring/sap) | 27 June 2026 |
| G59-P5 | [OneLake catalog overview](https://learn.microsoft.com/en-us/fabric/governance/onelake-catalog-overview) | 29 September 2026 |
| G59-P6 | [Domains](https://learn.microsoft.com/en-us/fabric/governance/domains) | 29 September 2026 |
| G59-P7 | [SAP Datasphere mirroring tutorial](https://learn.microsoft.com/en-us/fabric/mirroring/sap-datasphere-tutorial) | 5 June 2026 |

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

For confirmed design routes, bind agent-facing entity types to suitable tables,
not semantic-model bindings while the recorded S6/S17 limitation applies
(R-ONT-2); re-check it in the tenant.
Keep semantic models as measure owners. Conditional sources have no new default
item/table binding; an entity's `source` is provenance, not proof of binding.
Mail/meetings remain Work IQ; documents/policies remain Foundry IQ knowledge;
web sources remain Web IQ. Do not copy master data into an agent-owned store.

### 3.1 Current governance, not a historical setup recipe

For new proposals, use source-qualified **OneLake catalog** guidance for
discovery/governance and **Fabric domains** to group associated workspaces/items
(G59-P1/P2/P5/P6). Derived rows retain `fabric_domain`/`governance_domain` keys,
with `Fabric domain (shared business objects)` or `Fabric domain (journey)`
grouping labels. The field name does not mandate Purview governance creation.
Domain assignment does **not** change visibility or access, grant permission or
enforce a security boundary. Keep workspace/item permissions, OneLake security,
Purview security/compliance, sensitivity labels and DLP as separate controls.

Unified Catalog and classic Purview **data governance**, not all Purview, are
retiring: the dated sources state no new accounts and maintenance through
12 November 2027. Preserve existing-estate migration context. Ask the governance
owner and account team about feature, contractual and regulated transition
gaps; neither the sources nor the plugin establish full parity or approve
migration. Saved domain labels, architecture, build steps, readiness and risks
remain recorded evidence alongside current guidance, not fresh instructions
to create retiring structures.

### 3.2 Conditional SAP routes

The documented candidate for supported source families is **SAP Datasphere →
ADLS Gen2 → Fabric/OneLake** (G59-P3/P7). Datasphere replication flows take an
initial snapshot and changes to staging; Fabric merges them into OneLake Delta
tables with a **read-only replicated SQL surface**. This is not direct mirroring
from an arbitrary SAP system.

Fresh SAP sources use `path: "unresolved"`, `item: null`, `status: "later"`.
Their source-local `route_assessment` has a derived `state`, a
`candidate_path` (`"mirroring"` or `null`), `prerequisites`, `commercial_note`
and `src`. The candidate is source-qualified guidance, not a selection;
Ariba and unrecognised family hints receive no mirroring candidate. These are
name-based hints, not confirmation of support. No automatic ready pipeline
fallback is supplied.

The checklist contains exactly these five records:

| Prerequisite key | Estate confirmation needed |
|---|---|
| `supported_source` | Actual SAP source-family support for the proposed route |
| `fabric_capacity` | Existing suitable Fabric capacity |
| `datasphere_environment` | Suitable SAP Datasphere environment |
| `premium_outbound_integration` | Premium Outbound Integration entitlement |
| `adls_gen2_permissions` | ADLS Gen2 staging and required permissions |

Each record has `status` (`unknown`, `confirmed` or `unsupported`), text `note`
and a `src` list. Keep the SAP-side commercial dependency **unpriced / to
confirm**. Naming it is not pricing, licence approval or a FinOps invocation.

To assert selection, obtain real owner-authored estate evidence for all five,
with non-empty notes/references resolving in the supplied Blueprint `evidence`
register, a named accountable source `owner` and an explicitly authored supported
`path` with its matching `item`. The local resolver recognises estate records
by `type: "estate"` or an `ESTATE-` ID, excluding public/documentation records
and Microsoft Learn/Tech Community URLs. Those markers do not authenticate the
author or prove the estate. Public documentation, a system name, a placeholder
owner or an imported `state` flag cannot confirm prerequisites.

Normalisation derives `conditional` or `owner_confirmed`; the latter means only
an owner-asserted design selection, never tenant verification, licence readiness,
provider GA, deployment or publication authority. Even all five confirmed
prerequisites do **not** select an unresolved path. Rebuild with the actual
Blueprint estate context; without it, confirmation remains conditional.
Consider alternatives only with applicable sources and owner evidence, not an
invented route catalogue or assumed availability.

For unresolved sources, the new default binding is
`{"layer":"silver","item":null,"table":null,"origin":"default"}`.
Saved route/item/status/table choices are retained as **recorded proposals**,
not counted in current `stats.bound`, graph/panel bound claims or mounted-table
claims while conditional. Dependent data products retain a named
`source route <id>: conditional` publication gap even if other fields are filled.
Independent supported eventhouse/secondary bindings remain unchanged.

## 4. Data and knowledge products

For each product record accountable owner, business purpose, intended uses,
access process and quality status, plus sensitivity, lineage, endorsement,
glossary/critical elements and service commitment where needed (S35; S38 retained
as historical evidence). Use current OneLake catalog/Fabric-domain guidance
above, not S38 as a new Unified Catalog setup recipe.
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
   An ordinary conditional draft succeeds with warnings. Add `--strict` when
   warnings must block handoff: exit 1, `files: {}`, no new output directory
   and no overwrite of good outputs. Malformed assessments and reserved G59
   citation collisions fail even ordinarily, before projection/output effects.
   Fix errors; never edit generated Turtle to hide a gap.
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

Normalisation works on a detached proposal, not the original file. Keep saved
paths/items/scheduling statuses, tables, authored domain rows, IDs, citation
snapshots, feedback and verdicts as recorded evidence. Missing legacy SAP
assessments receive the unknown checklist, not inherited confirmation.
`current_guidance` supplies separate `governance`/`sap` entries, each `{text, src}`,
in JSON, HTML and all three Markdown variants/downloads. New G59 citations are
appended to `sources_doc`; an occupied ID with different fact content is an
error, never permission to rewrite old evidence.

`current_readiness["F-06"]` contains `status` and `gaps`. Any conditional source
keeps it `open`, with source-ID-specific gaps, while the saved F-06 status/notes
and workshop verdict remain unchanged. The Blueprint uses that effective open
assessment for the process F-06 readiness aggregate, not a saved “done” verdict.
Do not present conditional routes/products as ready or mounted. Current guidance
also qualifies saved risk mitigations; it does not erase their historical text.
Grouping, privacy, feedback targets and Turtle/import contracts are unchanged.
Public guidance cannot declassify restricted prerequisite notes or ancestry.

Process does not require FinOps. For requested costs, follow the full
[FinOps notice and actual current-scenario confirmation](../../frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure)
before any cost operation/recommendation/figure. On decline, preserve old
Preview originals/provenance and use clean core/ordinary non-FinOps inputs;
state the budget gap, not zero costs or passed readiness.
