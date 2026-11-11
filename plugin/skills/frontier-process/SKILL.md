---
name: frontier-process
description: |
  Optional: builds the customer's process ontology for Microsoft Fabric IQ from the Frontier
  blueprint: entity types grounded in the Microsoft Common Data Model, relationships, rules and
  metrics on a medallion layer in OneLake, data products, one Fabric data agent per journey and
  operations agents for live signals. Writes ontology.ttl for the Fabric import, the design and
  data product documents, the data agent kit and the blueprint's Ontology page. Use when asked to
  "build the process ontology for <customer>", "model the business objects in Fabric IQ", "map
  the ontology to the Common Data Model", "define the data products" or "add the ontology to the
  blueprint".
  Do NOT use for questions on Power BI reports or data (use the powerbi skill or the Fabric IQ plugin),
  for the blueprint itself (use frontier-blueprint) or for the PRD and solution design
  (use frontier-solution-design).
license: MIT
metadata:
  category: productivity
  icon: DataUsage
  version: "1.9.1"
  plugin: frontier-envisioning
  maturity: ga
  optional: true
  requires_preview_ack: false
---

# Frontier process ontology (Fabric IQ)

The optional data capability of the Frontier method. The blueprint says how the company runs human-led and agent-operated; this skill names the business objects those journeys run on (customers, orders, assets, work orders, invoices ...) as an **ontology in Microsoft Fabric IQ**, grounds each one in a **Microsoft standard entity** (Common Data Model, Dataverse, finance and operations), binds it to a **medallion layer in OneLake** (silver conformed to the Common Data Model), publishes **data products** per the Cloud Adoption Framework standard, and grounds **Fabric data agents** (questions in business terms) and **operations agents** (live monitoring with approval in Teams) in that one vocabulary. Everything is a hypothesis until the data owners confirm it.

Terms used here are Microsoft's: ontology (preview), entity type, property, key, relationship type, business rule, metric, data binding, namespace, data agent, operations agent, ontology agent, OneLake, mirroring, shortcut, eventhouse; Common Data Model, standard entity, Link to Fabric, medallion (bronze, silver, gold), Direct Lake, Fabric domain, Purview governance domain, data product, endorsement. Sources and known issues are in `templates/fabric-iq-canon.json` (checked 11 November 2026; preview features change, re-check before a workshop); the standard entity per entity type is in `templates/cdm-map.json`.

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
- Business value and costs: use frontier-value-case for the value case; use frontier-finops for the costs
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
8. Semantic layer: silver tables `<namespace>_silver.<entity>` conformed to the Common Data Model (the ontology binds here), live events in `<namespace>_events`, a gold semantic model per journey in Direct Lake that owns the measures, one Fabric domain per journey (Purview: functional unit) and one for shared objects (Purview: data domain).
9. Data products: one per data agent product, with an accountable owner, business purpose, intended uses, access process and quality status; agent actions always need an additional review (R-ONT-7, OD-ONT-6).

### Step 4: Build and check
`python scripts/build_ontology.py --ontology ontology.json --blueprint blueprint.normalized.json --out-dir <folder>`. Fix every error (names, keys, types, unknown ends, more than five sources). Read the warnings: unbound entity types, unknown agents or journeys, standard entities or columns that don't fit, entity types bound to a semantic model that a data agent uses (known issue R-ONT-2). It writes `ontology.ttl`, `ontology.md`, `data-products.md`, `data-agents.md` and `ontology.normalized.json`.

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
- How to use it: import `ontology.ttl` into a new, empty ontology (preview) item; keys, bindings, rules and metrics are set in Fabric (the ontology agent proposes bindings, a person applies them).

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
- `examples/caldova-ontology.json`: the fictitious Caldova example (27 entity types, 24 on a standard entity, 18 data products, four data agents)
