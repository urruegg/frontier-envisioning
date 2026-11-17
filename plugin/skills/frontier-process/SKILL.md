---
name: frontier-process
description: |
  Optional GA product wrapper for process ontology design: business objects, proposed CDM
  mappings, OneLake layers, data products and agent grounding. Writes local Turtle and design
  files plus the blueprint Ontology page; Fabric ontology/agent/operations remain Preview.
  Use for "build the process ontology for <customer>", "map the ontology to the Common Data
  Model", "define the data products" or "add the ontology to the blueprint".
  Do NOT use for Power BI data questions (powerbi or Fabric IQ plugin), blueprint HTML alone
  (frontier-blueprint), PRD/design documents (frontier-solution-design), or cost modelling
  (frontier-finops, optional Preview with confirmation first).
license: MIT
metadata:
  category: productivity
  icon: DataUsage
  version: "1.10.1"
  plugin: frontier-envisioning
  maturity: ga
  optional: true
  requires_preview_ack: false
---

# Frontier process ontology (Fabric IQ)

The optional data-design capability of the Frontier method. It proposes business
objects, Microsoft standard-entity mappings, medallion bindings, data products
and agent grounding from the blueprint. It prepares local files, not published
data products or tenant items. Everything is a hypothesis until data owners
confirm it. GA is the maintainer's wrapper designation, not result confidence,
provider GA, release/deployment or external/IP clearance.

Terms and source IDs are in [references/ontology-method.md](references/ontology-method.md).
The canon `templates/fabric-iq-canon.json` records a source check date of
11 November 2026, not a new independent availability check. Re-check dated Learn
sources and known issues before a workshop. Proposed standard mappings are in
`templates/cdm-map.json`; Dynamics 365/Dataverse origins do not verify every table.

Process work does not require FinOps. Continue without it when absent or declined,
stating any real cost/budget gap. For requested costs, first show the full notice
and obtain actual current-scenario confirmation via
[frontier-finops](../frontier-finops/SKILL.md); no cost operation or figure before
that gate. Do not reuse embedded legacy Preview costs as GA. Use clean core inputs
on decline, preserving original/provenance; missing requested FinOps is an error.

## Quick Start

```
User: "Build the process ontology for the Caldova blueprint"
1. Find the normalized blueprint (output, or OneDrive Documents/Cowork/frontier-envisioning/<slug>/)
2. python scripts/seed_ontology.py --blueprint blueprint.normalized.json --out working/frontier/<slug>/ontology.json
3. Refine the hypothesis (references/ontology-method.md): entity types, keys, relationships, sources, rules, metrics, data agents
4. python scripts/build_ontology.py --ontology .../ontology.json --blueprint blueprint.normalized.json --out-dir working/frontier/<slug>/ontology
5. Rebuild the blueprint with the Ontology page: build_with_identity.py ... --ontology .../ontology.json
6. Publish ontology.ttl, ontology.md, data-products.md, data-agents.md and the blueprint HTML; reply with the counts, gaps and decisions
```

## When to Use

- "Build the process ontology for Caldova" or "model Caldova's business objects in Fabric IQ"
- "Which data agents does the Service journey need, and what should they answer?"
- "How do SAP and Dynamics 365 get into OneLake for the agents?"
- "Map Caldova's ontology to the Common Data Model" or "which data products does the Service journey publish, and who owns them?"
- "Add the ontology to the blueprint" or "prepare the Fabric import"
- "Update the ontology with the workshop feedback" (the export carries `onto:<id>` verdicts)

## When NOT to Use

- Asking questions about a Power BI report or semantic model: use the powerbi skill or the Fabric IQ plugin in Cowork
- Building or updating the blueprint itself: use frontier-blueprint instead (this skill adds one page to it)
- PRD, solution design and ADRs: use frontier-solution-design instead
- Business value: frontier-value-case; requested costs: frontier-finops for its full Preview notice and confirmation first
- Agent names, colours and icons: use frontier-agent-identity instead
- Customer context from meetings, mail, chats and transcripts: use frontier-context-discovery instead
- Running the whole engagement: use frontier-envisioning instead (it calls this skill as an optional step)
- Creating items in a Fabric tenant: this skill prepares files; people import them in Fabric

## Workflow

### Step 1: Evidence
1. Start from the **normalized blueprint** of the engagement (journeys, stages, systems, KPIs, approval seams, agents, data agents and their data products, the digital feedback loop). Without a blueprint, run **frontier-blueprint** first.
2. When the customer has Power BI semantic models for a journey, read one with the Power BI tool `GetSemanticModelSchema` (after `DiscoverArtifacts`) and save its tables, columns, relationships and measures as TMSL JSON (`{"name", "tables":[{"name","columns":[{"name","dataType","isKey"}],"measures":[{"name","expression"}]}], "relationships":[{"fromTable","fromColumn","toTable","toColumn"}]}`). It becomes `--semantic-model model.bim --journey D3`: its measures become metrics the semantic model keeps owning. Never send customer data outside these tools.
3. Facts on systems of record, data owners and data quality come from the context pack and the transcripts (frontier-context-discovery); cite their evidence ids in `src`.

### Step 2: Seed
`python scripts/seed_ontology.py --blueprint blueprint.normalized.json --out ontology.json [--semantic-model model.bim --journey D3]`. The seed picks a journey pattern per journey (Lead-to-Order, Source-to-Pay, Request-to-Resolution, Record-to-Report, Hire-to-Retire, Plan-to-Produce), adds the shared core entity types, the concepts the feedback loop names for Fabric IQ, OneLake sources with a proposed path per system, bindings, metrics from the KPIs, the approval seam as a rule, one data agent per journey (with its data products mapped to entity types) and an operations agent where a journey has live signals. The `_todo` list names what to confirm.

### Step 3: Write the hypothesis
Follow [references/ontology-method.md](references/ontology-method.md):
1. Entity types in business language with a string or integer key; properties with supported types (string, integer, double, boolean, datetime); one type per property name across the ontology; time series only for values that change over time.
2. Relationship types as verbs (`places`, `resolved_by`) with cardinality; inheritance only where one concept really specialises another.
3. OneLake: mirroring for supported databases and SAP, shortcuts for Dataverse and open formats, eventstreams into an eventhouse for live events, pipelines for the rest. Documents, mail and web stay with Foundry IQ, Work IQ and Web IQ.
4. Rules in one sentence each; metrics named after the journey KPIs with the semantic model and DAX measure, or "to define".
5. Data agents: up to five sources each, the journey's agents as consumers, five realistic example questions; publish to Microsoft 365 Copilot only after the data protection review (OD-ONT-4).
6. Operations agents: natural-language rules and actions, approved by a named role in Teams.
7. Common Data Model: the seed takes each entity type's standard entity, table and columns from `templates/cdm-map.json`; keep the business name and confirm the mapping with the data owner. Entries marked "to verify" are checked in the table definition browser; with no standard entity, keep a custom extension (OD-ONT-5).
8. Semantic layer: propose silver tables `<namespace>_silver.<entity>` conformed to the agreed canonical model, live events in `<namespace>_events` and a gold semantic model per journey owning measures. Propose Fabric/Purview domains with the data owner; none is created here.
9. Data products: one per data agent product, with an accountable owner, business purpose, intended uses, access process and quality status; agent actions always need an additional review (R-ONT-7, OD-ONT-6).

### Step 4: Build and check
`python scripts/build_ontology.py --ontology ontology.json --blueprint blueprint.normalized.json --out-dir <folder>`. Fix every error (names, keys, types, unknown ends, more than five sources). Read the warnings: unbound entity types, unknown agents or journeys, standard entities or columns that don't fit, entity types bound to a semantic model that a data agent uses (known issue R-ONT-2). It writes `ontology.ttl`, `ontology.md`, `data-products.md`, `data-agents.md` and `ontology.normalized.json`.

Use `--strict` when warnings must block handoff. Invalid models or strict warnings
fail before publishable writes; do not overwrite good artifacts or suppress
mapping gaps. Customer projections must exclude internal-derived descriptions,
bindings, instructions, products, rules, metrics and operations proposals, not
just source IDs.

### Step 5: Blueprint page and publish
1. Rebuild the blueprint with `--ontology ontology.json` (frontier-blueprint's `build_with_identity.py`): the Ontology page appears in Part 2 Design, the Fabric prerequisites in IT readiness and the ontology risks in the register.
2. `CopyArtifact(surface="output", ...)` for the HTML, `ontology.ttl`, `ontology.md`, `data-products.md` and `data-agents.md`; confirm `"ok": true` for each.

### Step 6: After the workshop
`python scripts/merge_ontology_feedback.py --ontology ontology.json --feedback <customer>-workshop-feedback.json --out ontology.v0.2.json`, then build again. Validated, adjusted and rejected verdicts and notes land on the entity types, relationship types, data products, data agents and operations agents; `onto:model` validated marks the whole model.

## Output format (reply)

- File names: the blueprint HTML, `ontology.ttl`, `ontology.md`, `data-products.md`, `data-agents.md`.
- One table: per journey the entity types, the OneLake sources and their path, the data agent and its consumers.
- Grounding: how many entity types rest on a standard entity, which are custom, which mappings to verify; data products ready to publish and their gaps.
- Gaps: entity types without binding, data products still to model, metrics without a measure.
- The decisions to take (OD-ONT-1 to OD-ONT-6) and the preview caveats that matter for this customer.
- Manual next step: verify native import into an empty Fabric ontology (Preview)
  item, then keys/bindings/rules/metrics and data-agent behaviour in the tenant.
  Local exports and byte-parity tests do not prove that import or availability.

## Guardrails

- Never invent customer systems, tables, owners or numbers; unknowns stay "[To complete]" or "to confirm".
- Use Microsoft's names for Fabric IQ items and say which are in preview; never promise features beyond the cited Learn pages.
- Agents read with the user's permissions; data agents are read-only; every action of an operations agent is approved by a person.
- Personal data: model people only in the roles the process needs; never rank or evaluate employees, and keep candidate data minimal.
- Keep Microsoft-internal evidence out of customer versions (the blueprint's customer build removes it).
- Always confirm before sharing outside Microsoft: show the customer version first.

## Failure handling

- If the normalized blueprint is missing: run frontier-blueprint first; never seed an ontology from memory.
- If a system of record, key, table or owner is not found in the evidence: keep it "to confirm" with the data owner as the open question; never fabricate a table or a column.
- If the Power BI tool is unavailable or the semantic model cannot be read: seed from the blueprint only and keep the metrics "to define".
- If a journey matches no pattern: the generic pattern applies; ask the process owner for the five to eight business objects before the workshop.
- `build_ontology.py` reports errors: fix the named field and build again; never hand-edit `ontology.ttl`.
- A property name with two types: rename one of them (Fabric reuses a property name only with the same type).
- The data agent needs more than five sources: split it by sub-process or rely on the ontology as the single context source.
- The Fabric import skips elements: compare the import log with `ontology.md`; OWL restrictions are not imported.
- If an entity type has no standard entity in `templates/cdm-map.json`: keep it a custom extension in its namespace and name the closest standard entity in its note; never invent a table name.
- If a mapping is marked "to verify" or a column is not found in the table definition: keep it "to verify" in the data product gaps and ask the data owner; never present it as confirmed.

## Files

- `scripts/ontology_lib.py`: checks, process map, Turtle, design document, data agent kit
- `scripts/seed_ontology.py`: blueprint (and an optional semantic model) to the ontology hypothesis
- `scripts/build_ontology.py`: check and write ontology.ttl, ontology.md, data-agents.md, the normalized JSON
- `scripts/apply_ontology.py`: the Ontology page data in the blueprint (used by build_with_identity.py)
- `scripts/merge_ontology_feedback.py`: workshop verdicts into the ontology
- `templates/ontology-patterns.json`: journey patterns, core entity types, KPI and system hints
- `templates/fabric-iq-canon.json`: Fabric IQ stack, paths, data architecture (medallion, domains, semantic models), data product standard, build steps, readiness, risks, decisions, Microsoft sources
- `templates/cdm-map.json`: the Microsoft standard entity, table, key and columns per pattern entity type
- `references/ontology-method.md`: how to model, ground in the Common Data Model, layer, publish data products, bind and ground agents
- `examples/caldova-ontology.json`: fictitious Caldova; integrated D1 evidence
  reports 27 entities, 33 relationships, 126 properties, nine sources, four data
  agents and four semantic models; 18 data products plus one knowledge product
  (19 unique products). Six integrated mappings remain to verify and Employee
  has a binding gap. These differ from the catalogue's eleven unverified F&O
  entries; neither scope is tenant verification.
