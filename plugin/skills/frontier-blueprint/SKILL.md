---
name: frontier-blueprint
description: |
  Builds or updates the Frontier Company Blueprint HTML: Vision, Design, Build and
  Workshops, with workflows, identity, PRD, Plan, risks and evidence. Ontology is optional;
  FinOps is optional Preview and needs explicit current-scenario awareness first.
  Use when asked to "build the Frontier blueprint for <customer>", "create the hybrid
  organisation mockup", "update the blueprint with the workshop feedback", "show the
  delivery Plan", "rate the workshop risks", "make the customer-ready version" or
  "show the Frontier blueprint demo". Do NOT use for gathering context (use
  frontier-context-discovery) or PRD and solution design documents (use
  frontier-solution-design); use frontier-agent-identity to review agent names.
license: MIT
metadata:
  category: productivity
  icon: Organization
  version: "1.10.0"
  plugin: frontier-envisioning
  maturity: ga
  optional: false
  requires_preview_ack: false
---

# Frontier Company Blueprint

*AI-assisted procedure maintenance, 13 November 2026; original authorship retained.*

Produces a single, self-contained HTML file a solution engineer can present and work in during the envisioning workshop. It follows the Innovation Hub method: the customer's business context (from **frontier-context-discovery**) becomes a hypothesis of how the company, or one function, could run human-led and agent-operated, grounded in Microsoft's Frontier guidance. The workshop validates it live; the exported feedback is merged into the next version.

The HTML follows the Innovation Hub journey; optional data determines the view set:

| Part | Views |
|---|---|
| **1 Vision** | Overview (Frontier phase ladder and **digital feedback loop** through Microsoft IQ) · Org model (HAIRO) · Blueprint · Journeys, including **Agent Factory** (DevSecOps, handover checks, build steps, evaluations) · Use cases (problem/provenance, value, feasibility and matrix) · **PRD** (MVP requirements, Markdown download, scope verdict) |
| **2 Design** | Agents (trigger canvas, Copilot Studio-style workflow, seven declarations, role profile) · Agent identity · Target architecture (**Landing zone**, Layers and integrations, Flows, **Decisions/ADRs**) · **IT readiness** · optional **Ontology** |
| **3 Build** | Roadmap and MVP candidates · **Plan** (factory journey lanes, stages, phases, WIP limits, CSV handover) · optional **FinOps (Preview)** |
| **4 Workshops** | **Attendees** (sessions and evidenced contributions) · Discovery questions and live notes · **Risks** (register, heat map, ratings) · Evidence register |

Agent identity icons mark agents everywhere; Microsoft product icons mark products, design areas and factory tools (only the icons used are embedded).

Part labels and descriptions can be overridden with `parts`. **1.10.0 is an
unreleased internal candidate.** Seven non-FinOps skills are GA product wrappers, not a guarantee of
result confidence, provider GA, release/deployment or external/IP clearance.
Fabric ontology/agent/operations features remain Preview with dated source and
mapping gaps; MOS3 `devPreview` remains a separate packaging protocol.

## Quick Start

```
User: "Build the Frontier blueprint for Caldova"
1. Find customer-context.json (input/, output, OneDrive via ReadFileContent)
2. python scripts/seed_blueprint.py --context customer-context.json --out working/frontier/caldova/blueprint.json
3. Write the hypothesis: stages, personas, lead + specialist agents, approval seam, scores, MVP canvases
4. python scripts/build_with_identity.py --data working/frontier/caldova/blueprint.json --out-dir working/frontier/caldova --save-normalized working/frontier/caldova/blueprint.normalized.json
   -> Caldova Frontier Company Blueprint.html (with the Agent identity page) + identity/Caldova - agent identity package v1.0.zip (proposal)
5. CopyArtifact the HTML, the kit zip and catalog.html to output; reply with journeys, agents, MVP candidates and the proposed names
```

**Agent identity (built by default).** `build_with_identity.py` creates the agent identity kit together with the HTML, using the scripts of **frontier-agent-identity** installed next to this skill: it seeds a proposal from the blueprint (names, journey colours, glyphs; the customer's Office theme when one is given), builds and validates the kit, writes the identity into every agent and renders the blueprint with the **Agent identity** page below Agents. Every agent view then uses the display name and icon; the working name stays visible. Names stay a proposal until the customer approves them in the identity review (frontier-agent-identity, Gate E).
This is branding, not Entra identity provisioning.

Add ordinary `--value value.json` without FinOps when requested. For process
work, use **frontier-process** and `--ontology ontology.json`. Neither requires
FinOps. For requested cost work, show the full notice and obtain actual
current-scenario confirmation from [frontier-finops](../frontier-finops/SKILL.md)
before any cost operation, recommendation or figure. Every top-level invocation
or changed scope/model/rates/grounding needs renewed acknowledgement; the wrapper
forwards `--acknowledge-finops-preview` within one action chain only. It is
technical acknowledgement, not human approval or financial permission.

### Requested versioned baseline — authoritative sources

For new work, follow the [FinOps versioned Quick Start](../frontier-finops/SKILL.md#quick-start--requested-versioned-baseline)
and [offline baseline contract](../frontier-finops/references/agent-finops-baseline.md)
for profiles, twelve-month low/expected/high scenarios, calculation, freeze and
exact-target external review. Do not duplicate that lifecycle in the Blueprint
or invent a handover CLI command.

After fresh confirmation, the existing wrapper accepts repeatable authoritative
baseline/snapshot and recorded-review inputs alongside ordinary value,
requested ontology and default identity:

```text
python scripts/build_with_identity.py --data blueprint.json --value value.json --ontology ontology.json --agent-finops baseline-A.json --agent-finops baseline-B.json --agent-finops-review recorded-review-A.json --agent-finops-review recorded-review-B.json --as-of YYYY-MM-DD --audience internal --out-dir working/frontier/<slug>/baseline-build --html "<Customer> Frontier Company Blueprint.html" --save-normalized working/frontier/<slug>/baseline-build/blueprint.normalized.json --report working/frontier/<slug>/baseline-build/build-report.json --acknowledge-finops-preview
```

These are placeholder paths for two different agents' authoritative baselines
or frozen snapshots and actual matching external review records, not invented
approvals. Replace the date and paths. Both `--agent-finops` and
`--agent-finops-review` repeat; omit review flags for unreviewed drafts, without
claiming approval. Omit unrequested `--value` or `--ontology`; identity remains
the default. Choose unused outputs outside the input locations.

For customer-specific output, use `--audience customer` and
`--customer-scope <matching-scope>` with new output paths. The current sources,
parent restrictions and scope must permit that projection; the flags are not
clearance or access control. The wrapper writes projected JSON/Markdown reports
under `agent-finops/report-001.json`, `report-001.md`, and subsequent indices.
Internal output also retains source/review copies; never share those as
customer reports.

Standalone rendering accepts the same authoritative source/review/date/scope
flags, but uses `--out` for HTML, not the wrapper's `--out-dir`/`--html`:

```text
python scripts/build_blueprint.py --data blueprint-with-ontology.json --agent-finops baseline-A.json --agent-finops-review recorded-review-A.json --as-of YYYY-MM-DD --audience internal --out working/frontier/<slug>/standalone/blueprint.html --save-normalized working/frontier/<slug>/standalone/blueprint.normalized.json --report working/frontier/<slug>/standalone/build-report.json --acknowledge-finops-preview
```

The standalone input may contain embedded ontology, ordinary value and identity;
it does not take the wrapper's `--value`/`--ontology` flags or create an identity
kit. Renew awareness for this invocation too. For a customer audience add the
matching scope where applicable.

Generated `agent_finops` is an **already projected derivative view**, not a
baseline or review. Rebuild/revalidation needs current authoritative sources,
matching reviews, date, scope and fresh acknowledgement; cached reports/DTOs
alone are insufficient. Do not hand-edit cost fields or embed full private
baselines. See the [view and authority contract](references/blueprint-schema.md#agent_finops-optional-versioned-preview-derivative).
Independent ordinary value does not become Preview merely because an
unconsumed new baseline is present; legacy-derived Preview retains provenance.

### Legacy costs — explicit separate path

For explicitly selected `frontier-finops/1.0` work, retain
`--finops finops.json --acknowledge-finops-preview` after fresh confirmation.
Do not auto-select legacy for a new baseline, mix legacy/successor cost sources
or choose a silent winner. [Explicit migration](../frontier-finops/SKILL.md#explicit-migration-never-automatic-conversion)
preserves originals/provenance and creates a draft with gaps, not inherited
approval, acknowledgement or implicit legacy FX.

### Decline or missing evidence

On decline or absent unrequested FinOps, continue core and state missing budget
evidence. Requested-but-missing FinOps is an explicit error. Old GA claims,
installed skills, JSON flags, notes and earlier runs are not consent. Keep old
embedded Preview originals unchanged; use clean core and ordinary non-FinOps
value inputs for the declined path. Omitting `--finops` does not cleanse old
fields. Do not invent `--no-finops`, strip provenance or reuse cached Preview
value as GA. Recalculate before apply after a cache/model/rates mismatch.
Draft workshops, ordinary value and identity can continue with named financial
gaps; neither missing costs nor a declined subflow grants financial/build
readiness. Do not start a cost operation merely because a handover gap exists.

## When to Use

- "Build the Frontier blueprint for Caldova" (after the context pack exists, or together with it)
- "Create the hybrid organisation mockup for Caldova procurement"
- "Update the blueprint with the workshop feedback" (a `*-workshop-feedback.json` exported from the HTML)
- "Make the customer-ready version" (strips Microsoft-internal evidence)
- "Show the agent identity in the blueprint" (the Agent identity page, built with the identity kit)

## When NOT to Use

- Gathering or refreshing the customer's context: use **frontier-context-discovery** first
- PRD, solution design, ADRs or a design repository: use **frontier-solution-design**
- Reviewing, rebranding or approving agent names, or stamping them into solutions: use **frontier-agent-identity**
- Business value/ROI: **frontier-value-case**; requested costs/guardrails: **frontier-finops** for its full Preview notice and confirmation first
- A generic slide or one-pager: use the pptx or document skills
- A plain HTML page without the blueprint method: use the html skill

## Workflow

### Demo (no customer needed)
For "Build the Frontier blueprint demo for Caldova", run
`python scripts/build_with_identity.py --data examples/caldova-blueprint.json --identity-config ../frontier-agent-identity/examples/caldova-agent-identity.json --palette ../frontier-agent-identity/examples/caldova-palette.json --value ../frontier-value-case/examples/caldova-value.json --ontology ../frontier-process/examples/caldova-ontology.json --out-dir working/demo --html "Caldova Frontier Company Blueprint (demo).html"`.
This curated demo requests process but not FinOps. If the optional process module
is absent, state that gap and omit `--ontology`; do not claim the Ontology output.
Publish the HTML, identity ZIP and catalogue after review. Caldova Industrial AG
is fictitious. A separately requested legacy Preview demo needs the full awareness gate
and adds `--finops ../frontier-finops/examples/caldova-finops.json --acknowledge-finops-preview`
with separate output, not the default demo.

### Step 1: Start from evidence
1. Look for the context pack: `input/`, the output folder, or OneDrive `Documents/Cowork/frontier-envisioning/<slug>/` (read it with the `ReadFileContent` tool, mode download). If it is missing, run **frontier-context-discovery** first (or, if the user insists on a quick draft, work from what they provide and mark everything as hypothesis).
2. Seed the blueprint: `python scripts/seed_blueprint.py --context customer-context.json --out working/frontier/<slug>/blueprint.json`. The seed copies evidence, journeys, KPIs, systems, stakeholder roles, ideas, actions and open questions, seeds the attendees from the named stakeholders, adds the Innovation Hub canon from `templates/blueprint-defaults.json` (the Agent Factory journey and its lifecycle, the landing zone, the canon ADRs `ADR-F01`…, the IT readiness checklist and the digital feedback loop with every journey mapped to one of its four areas; a canon decision whose title the blueprint already has is skipped), and lists every gap in `_todo`.

### Step 2: Write the hypothesis
Follow [references/authoring-guide.md](references/authoring-guide.md) and the field reference [references/blueprint-schema.md](references/blueprint-schema.md). For each journey:
1. Stages (4 to 6): what happens, the evidenced pain (cite `src`), what agents change, which agent owns the stage. Start from the journey pattern library in the guide, then adapt to the evidence.
2. Personas (3 to 5): goal, pain, how agents help, what they decide.
3. Lead agent (one per journey): mission, memory, planning, goals, agent boss.
4. Specialist agents (3 to 6): capability, autonomy (Assist / Act with approval / Act within guardrails), horizon (H1 to H3), trigger, outcome, technology. Workflow-first: a step that a rule can do is a workflow, not an agent.
5. The approval seam: what never leaves without a person.
6. Use cases scored for value and feasibility (1 to 5) with the rubric in the guide; 2 or 3 MVP candidates with why and needs.
7. For every MVP candidate agent: the full trigger canvas, the seven declarations and the role profile, and the workflow (`canvas.workflow`, guide §5a): trigger type, the designer nodes from trigger to outcome, a Human review before every write, branches that rejoin or end. Without it the build derives one from the plan and marks it "Derived from the plan".
8. Discovery questions: keep the seeded ones that matter; prefill `answer` with `src` where evidence exists.
9. For every MVP use case, the Hub use-case template: `problem` (a list of `[provenance, text]` pairs: workshop, board, transcript, customer, microsoft, hypothesis), `today`, `pain`, `idea`, `objective`, `key_results`, `figures` with their source, `tech_fit`, `risk_points`, `safeguards`, `dependencies` (see the schema).
10. Attendees: who took part and what each contributed (from the transcripts and notes); link contributions to journeys and use cases. Customer people by role unless they agreed to be named.
11. Landing zone and decisions: set per journey which of DEV, TEST and PROD exist now, next or later, and the data classes allowed; keep the canon ADRs, adapt their wording to the customer, add the customer's own ADRs.
12. IT readiness: owners and status from the IT conversation. Never assume the engineering control plane: keep GitHub, Azure DevOps and the hybrid open until the customer decides (decision D-01).
13. Digital feedback loop (Overview, guide §7b): check which journey belongs to which area (Engage customers, Optimize operations, Empower employees, Transform products); per area the customer's signals with their Microsoft IQ layer (Work IQ, Fabric IQ, Foundry IQ, Web IQ, from the systems, mails and transcripts found by discovery), the actions with their agents and the person who approves, the outcomes with the journey KPIs and the value-case assumption ids, and one workshop question. Use only official Microsoft names.
Also write the mission (cite the strategy facts), outcomes, leaders (accountable roles), and the architecture flows for the MVP. Delete `_todo` when done.

Write the authored PRD problem, goals, exclusions, exit test, release plan and
owner/status; let `prd_model.py` derive the requirements from the MVP scope.
The page and solution-design scaffold share identical model copies. Selected
subsets retain the full blueprint's canonical requirement IDs. Rate risk points
and blocked readiness items with finite integers 1-5, owner and mitigation;
retain canon/authored risks. Attendee contributions cite sources and transcript
times; missing evidence remains a flagged gap.

### Step 3: Build and check
1. `python scripts/build_with_identity.py --data working/frontier/<slug>/blueprint.json --out-dir working/frontier/<slug> --html "<Customer> Frontier Company Blueprint.html" --save-normalized working/frontier/<slug>/blueprint.normalized.json --report working/frontier/<slug>/build-report.json` plus `--theme <file>` when a customer-authored deck or template is available (find one with the `SearchM365` tool and download it with `ReadFileContent`, or ask the user to attach it) and `--prefix <publisher prefix>` when known. It writes the identity kit to `identity/` (proposal, `seed-report.md`) and the HTML with the Agent identity page. After the identity review, pass the reviewed `--identity-config` and `--palette` instead; `--no-identity` builds the blueprint without the kit. Ordinary `--value value.json` calculates/applies value on copies without FinOps. Optional process uses `--ontology ontology.json`. Requested successor costs use the authoritative-source flags above after awareness; explicitly selected legacy work retains `--finops finops.json --acknowledge-finops-preview` in that wrapper chain.
   For successor work, use a separate reserved output directory outside the
   input locations, as in the authoritative-source example above; do not append
   source flags while retaining this core command's input-containing output folder.
   A blueprint from release 1.3 or earlier gets the canon with `--canon`; `--no-product-icons` leaves the Microsoft product icons out.
2. Fix every ERROR. Read the WARN lines: unknown agents in stages, uncited evidence ids, MVP agents missing declarations, an unofficial "… IQ" name or unknown area in the feedback loop, an unknown workflow node or trigger type or an unknown agent in a workflow. Rebuild until clean or every remaining warning is deliberate.
3. Validate the HTML with the html skill's validator when available (`validate.py` must report success).
4. Customer version (only when asked, or before anything leaves Microsoft): add `--audience customer`. Risk visibility is resolved against original sources before scrubbing; internal-only content, `internal_notes` and cached derived PRD fields are removed, then final risks/PRD derive from scrubbed sources. Attendee contributions follow source visibility. A removed source ID alone is not sanitisation. The build refuses if any `meta.internal_terms` string remains. Name it `<Customer> Frontier Company Blueprint (customer).html` and review embedded data and downloads as well as visible text.
   For successor costs, revalidate current consumed parent/transitive sources,
   rates, FX, reviews and customer scopes before JSON, HTML or identity ZIP
   products. Reject unresolved references/ambiguous source collisions before
   output; unknown restrictions fail closed. Valid ontology/baseline combinations
   resolve on detached copies without changing original sources or tightening
   ordinary GA process handling globally.

#### Financial baseline check — build handover only

Building a draft HTML is not build handover. For every agent actually being
handed over for build, the financial criterion requires a complete validated
profile, meaningful twelve-month low/expected/high demand/dependency scenarios,
denominators and every in-scope cost driver priced with current applicable
evidenced rates/FX. Require the frozen exact baseline ID/version/material hash,
matching external finance-owner or evidenced-delegation review and current
lineage/audience/scope validation. Unpriced has no conditional exception;
provisional or synthetic evidence cannot establish real financial readiness.
See the [strict FinOps gate](../frontier-finops/references/guardrails.md#strict-financial-build-handover).

Legacy F1/F2, raw status and workshop verdicts are not financial approval.
Review is externally asserted, not authenticated financial, build or deployment
permission; local snapshots/hashes are not tamper-proof archives. Other
readiness checks and existing build/release/operate stages remain unchanged.
This offline slice adds no dedicated FinOps Agent factory, operating loop,
live billing/provider imports or cloud deployment.

### Step 4: Publish
1. `CopyArtifact(surface="output", source="working/frontier/<slug>/<file>.html", destination="<file>.html")`; confirm `"ok": true`. Publish the identity kit zip and its `catalog.html` (as `<Customer> - agent identity catalogue.html`) the same way, and the normalized JSON: it is the canonical blueprint for the next version.
   Its generated `agent_finops` records remain derivatives: retain authoritative
   baseline/snapshot and review files privately for the next financial rebuild.
2. Offer to save the engagement folder to OneDrive (`CopyArtifact(surface="user", source="working/frontier/<slug>", destination="frontier-envisioning/<slug>", recursive=true, overwrite=true)`).

### Step 5: After the workshop (feedback merge)
1. Find the exported `<customer>-workshop-feedback.json` (attached, or in Downloads uploaded by the user) and the normalized blueprint of the version shown in the workshop.
2. `python scripts/merge_feedback.py --blueprint blueprint.normalized.json --feedback <feedback.json> --out blueprint.v0.2.json --workshop-date <YYYY-MM-DD>`
3. Add what the workshop transcript adds (run **frontier-context-discovery** on it), then rebuild. IT readiness statuses (`ready:<id>`), ADR verdicts (`adr:<id>`; validated becomes agreed) and feedback-loop verdicts (`loop:<area>`) are applied directly. Feedback from the Agent identity page arrives as `identity_feedback`; resolve it with **frontier-agent-identity** before the names are approved. When the customer has confirmed the journeys and MVPs, set `meta.status` to `validated`.

4. Merge `prd:scope` and `risk:<id>` verdicts too. Rated derived risks become
   workshop-owned and survive rebuilds. Keep the normalised `risks.source_ids`,
   `source_key` and content provenance, including retired-ID history. Source
   edits/reordering must not silently inherit another risk's verdict; discarding
   this history cannot guarantee old ID-only feedback identity. Report unknown
   IDs or invalid ratings rather than treating them as successful updates.
5. Baseline-related workshop notes and proposals are inputs to a new draft,
   not edits to frozen data or external finance-owner approval. Changed material
   needs a new version, calculation/freeze and exact-target review through
   FinOps after renewed awareness. `meta.status: validated` does not pass
   financial handover. Rebuild with the current authoritative source flags,
   not only the cached view.

## Output format (reply)

- The file name of the HTML (and the customer version when built), one line on what it shows.
- The identity kit zip by file name: number of agents, validator and test result, and whether the names are a proposal; flag a missing brand source.
- A compact table: journeys, lead agent, number of specialists, MVP candidates.
- What is hypothesis versus evidenced (counts), and the top open questions for the workshop.
- The digital feedback loop: which journeys sit in which area, and the areas still to discover.
- The MVP workflows: trigger, number of AI, deterministic and human steps, and which are still derived from the plan.
- IT readiness: open preparation items with their owners, and the decisions still to take.
- PRD: scope/status and Markdown download; Plan: next steps and CSV handover;
  Risks: top scores, owners and unresolved evidence; Attendees: evidence gaps.
- Presenting tips: open the file in Edge or Chrome (OneDrive preview does not run it); arrow keys move between views; the Overview's feedback loop animates (pause button; it stays still when the device asks for reduced motion), select an area to see its signals, actions and outcomes; on an agent, the workflow starts as an overview (switch to the designer row, zoom, select a node for its properties, select a node type in Add to highlight it); the Org model reveals layers step by step; notes and validations are saved in the browser and exported from Discovery.

## Guardrails

- Fresh browser acknowledgement is independent of script acknowledgement and
  document-local, never localStorage consent. Reload resets it; the Preview
  warning persists. Gate flat/nested costs, linked assumptions and derived
  ROI/NPV/unit costs, comparisons and PRD summaries; keep ordinary own value.
  Private components/rankings/outcomes are withheld, not zero; never recover
  `internal_notes`. This is not encryption or access control. Carry limitations,
  assumptions and scenario/model/rate/source provenance into replies and exports.
  Missing budget evidence stays open with the real owner.
- Consume projected `agent_finops` decimal text, statuses, reasons and already
  calculated unit metrics. Never recost or coerce financial decimals in
  JavaScript, recover raw private dependencies, fall back to legacy costs or
  expose private headers/hashes. Withheld is not zero, and independent public
  rows are not a complete total.
- Never fabricate: hypotheses are labelled as hypotheses and only evidence-backed statements cite sources. Never invent customer numbers, quotes, systems or names.
- Never show Microsoft-internal evidence in a customer version; always build the customer version before sharing outside Microsoft.
- Always confirm before sharing: show the user the customer version and let them review before it is sent to anyone.
- Customer export is not external/IP approval. Keep the private source host and
  Microsoft-internal distribution boundary in the plugin guide.
- Plan CSV requires destination mapping, not live integration or native import
  certification. WIP/readiness, metadata and verdicts grant no build/deploy permission.
- Never let an agent decide about a person: hiring, pay, performance, promotion or exit stay human; mark such use cases with a named human decision-maker.
- Do not propose an agent where a rule works: deterministic steps are workflows.
- Product names and availability come from the reference architecture of the frontier-solution-design skill or Microsoft Learn; mark anything unverified as "to confirm".
- The HTML stays self-contained: no external scripts, fonts, images or links; customer logos only as PNG/JPEG data URIs the customer provided.
- Microsoft product icons come only from `templates/product-icons.json`: Microsoft trademarks, not covered by the MIT licence, used as Microsoft's icon terms allow (architecture diagrams, training, documentation) and never altered. Leave them out (`--no-product-icons`) when a customer version must carry no third-party marks.
- No competitor bashing; name the customer's existing systems neutrally.
- In the digital feedback loop use only official Microsoft names: Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ, Web IQ, and the four areas Engage customers, Optimize operations, Empower employees, Transform products; never invent an "… IQ".
- Never present proposed agent names as final: the Agent identity page shows the kit's status until the customer approves the names.
- Use only the customer's own brand material for the identity colours, and never reuse one customer's kit for another.

## Failure handling

- If `build_blueprint.py` reports an ERROR: fix the named field (duplicate id, missing customer, invalid logo) and rebuild; never hand-edit the HTML output.
- If many WARN lines name unknown stage agents: align stage `agent` names exactly with agent `name` values.
- If the customer build fails because of an internal term: rewrite the sentence or flag the item `"internal": true`.
- If the feedback file belongs to another blueprint id: stop and ask which blueprint version was shown.
- If the context pack is missing and the user wants a quick draft anyway: build from what they provide, mark every statement as hypothesis, and list the evidence still needed.
- On the core/legacy path, if the identity kit fails (the summary's `notes` say why): the blueprint is still built without identity; report the reason, fix it with **frontier-agent-identity** and build again.
- On the successor source chain, a requested component/source/review failure
  must not become a successful fallback build. Resolve the error and use new
  output paths; do not reuse cached reports or legacy costs as authority.
  Inspect any partial output after an I/O failure rather than assuming an
  atomic filesystem transaction.
- If no customer theme is available: the journey colours come from the blueprint and are flagged; say so and ask for a customer-authored deck or template.

## Files

- `templates/frontier-blueprint-template.html` — the renderer (data placeholder `"__BLUEPRINT_DATA__"`)
- `templates/blueprint-defaults.json` — Innovation Hub canon: digital feedback loop (Microsoft IQ, the four areas, mapping rules, Microsoft sources), governance, security, knowledge, build & run, foundation, target-architecture layers, horizons, discovery bank, Agent Factory, landing zone, canon ADRs, IT readiness
- `templates/product-icons.json` — Microsoft product icons with their notice and the text rules that map product names to icons
- `scripts/canon.py` — adds the canon blocks to a blueprint without overwriting what it has, and completes the feedback loop from the journeys
- `scripts/seed_blueprint.py` — context pack to blueprint seed
- `scripts/build_blueprint.py` — validate, normalise, customer version, render
- `scripts/build_with_identity.py` — core blueprint/identity, ordinary `--value`,
  optional `--ontology`; requested successor `--agent-finops`/
  `--agent-finops-review` with explicit date/scope, or separate legacy `--finops`;
  cost work requires current confirmation and `--acknowledge-finops-preview`
- `scripts/workflow.py` — the agent workflows: Copilot Studio node and trigger types, derivation from the canvas plan, checks (used by the build)
- `scripts/prd_model.py` — canonical PRD derivation, identical to the solution-design copy
- `scripts/risks.py` — risk derivation, ratings and retained source/ID bindings
- `scripts/merge_feedback.py` — merge the workshop feedback export (identity feedback kept as `identity_feedback`)
- `references/authoring-guide.md` — how to write the hypothesis, scoring rubric, journey pattern library
- `references/blueprint-schema.md` — every field of the blueprint JSON
- [Offline baseline contract](../frontier-finops/references/agent-finops-baseline.md) — authoritative models/reviews and projected `agent_finops` report DTOs
- `examples/caldova-blueprint.json` — complete fictitious example and demo (Caldova Industrial AG: four business journeys plus the Agent Factory, 29 agents, 8 attendees)
