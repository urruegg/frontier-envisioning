---
name: frontier-blueprint
description: |
  Builds or updates the Frontier Company Blueprint HTML in 17 views: Vision (Microsoft IQ
  feedback loop, HAIRO org model, journeys, use cases, PRD), Design (agents with workflow
  and identity, landing zone, ADRs, IT readiness), Build (Roadmap, Agent Factory Plan,
  FinOps) and Workshops (evidenced attendees, Discovery, Risks, Evidence).
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
  version: "1.9.1"
  plugin: frontier-envisioning
  maturity: ga
  optional: false
  requires_preview_ack: false
---

# Frontier Company Blueprint

Produces a single, self-contained HTML file a solution engineer can present and work in during the envisioning workshop. It follows the Innovation Hub method: the customer's business context (from **frontier-context-discovery**) becomes a hypothesis of how the company, or one function, could run human-led and agent-operated, grounded in Microsoft's Frontier guidance. The workshop validates it live; the exported feedback is merged into the next version.

The HTML follows the Innovation Hub journey in seventeen views:

| Part | Views |
|---|---|
| **1 Vision** | Overview (Frontier phase ladder and **digital feedback loop** through Microsoft IQ) · Org model (HAIRO) · Blueprint · Journeys, including **Agent Factory** (DevSecOps, handover checks, build steps, evaluations) · Use cases (problem/provenance, value, feasibility and matrix) · **PRD** (MVP requirements, Markdown download, scope verdict) |
| **2 Design** | Agents (trigger canvas, Copilot Studio-style workflow, seven declarations, role profile) · Agent identity · Target architecture (**Landing zone**, Layers and integrations, Flows, **Decisions/ADRs**) · **IT readiness** |
| **3 Build** | Roadmap and MVP candidates · **Plan** (factory journey lanes, stages, phases, WIP limits, CSV handover) · FinOps |
| **4 Workshops** | **Attendees** (sessions and evidenced contributions) · Discovery questions and live notes · **Risks** (register, heat map, ratings) · Evidence register |

Agent identity icons mark agents everywhere; Microsoft product icons mark products, design areas and factory tools (only the icons used are embedded).

Part labels and descriptions can be overridden with `parts`. This is unreleased
1.7.1, selectively adapted from received 1.7.0; version metadata is not release
or distribution approval.

## Quick Start

```
User: "Build the Frontier blueprint for Caldova"
1. Find customer-context.json (input/, output, OneDrive via ReadFileContent)
2. python scripts/seed_blueprint.py --context customer-context.json --out working/frontier/caldova/blueprint.json
3. Write the hypothesis: stages, personas, lead + specialist agents, approval seam, scores, MVP canvases
4. python scripts/build_with_identity.py --data .../blueprint.json --out-dir working/frontier/caldova [--theme <customer deck>.pptx] [--value value.json --finops finops.json] --save-normalized ...
   -> Caldova Frontier Company Blueprint.html (with the Agent identity page) + identity/Caldova - agent identity package v1.0.zip (proposal)
5. CopyArtifact the HTML, the kit zip and catalog.html to output; reply with journeys, agents, MVP candidates and the proposed names
```

**Agent identity (built by default).** `build_with_identity.py` creates the agent identity kit together with the HTML, using the scripts of **frontier-agent-identity** installed next to this skill: it seeds a proposal from the blueprint (names, journey colours, glyphs; the customer's Office theme when one is given), builds and validates the kit, writes the identity into every agent and renders the blueprint with the **Agent identity** page below Agents. Every agent view then uses the display name and icon; the working name stays visible. Names stay a proposal until the customer approves them in the identity review (frontier-agent-identity, Gate E).

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
- Business value, ROI and the assumptions behind them: use **frontier-value-case**; agent costs, credits and guardrails: use **frontier-finops**
- A generic slide or one-pager: use the pptx or document skills
- A plain HTML page without the blueprint method: use the html skill

## Workflow

### Demo (no customer needed)
When the user asks for the demo or the sample ("Build the Frontier blueprint demo for Caldova"), run `python scripts/build_with_identity.py --data examples/caldova-blueprint.json --identity-config ../frontier-agent-identity/examples/caldova-agent-identity.json --palette ../frontier-agent-identity/examples/caldova-palette.json --value ../frontier-value-case/examples/caldova-value.json --finops ../frontier-finops/examples/caldova-finops.json --out-dir working/demo --html "Caldova Frontier Company Blueprint (demo).html"` and publish the HTML, `identity/Caldova - agent identity package v1.0.zip` and the kit's `catalog.html` as `Caldova - agent identity catalogue.html`. Caldova Industrial AG is fictitious; say so in the reply.

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
1. `python scripts/build_with_identity.py --data working/frontier/<slug>/blueprint.json --out-dir working/frontier/<slug> --html "<Customer> Frontier Company Blueprint.html" --save-normalized working/frontier/<slug>/blueprint.normalized.json --report working/frontier/<slug>/build-report.json` plus `--theme <file>` when a customer-authored deck or template is available (find one with the `SearchM365` tool and download it with `ReadFileContent`, or ask the user to attach it) and `--prefix <publisher prefix>` when known. It writes the identity kit to `identity/` (proposal, `seed-report.md`) and the HTML with the Agent identity page. After the identity review, pass the reviewed `--identity-config` and `--palette` instead; `--no-identity` builds the blueprint without the kit. With `--value` and `--finops` (from frontier-value-case and frontier-finops) it also calculates both on copies: business value in the use cases and the matrix, and the FinOps page.
   A blueprint from release 1.3 or earlier gets the canon with `--canon`; `--no-product-icons` leaves the Microsoft product icons out.
2. Fix every ERROR. Read the WARN lines: unknown agents in stages, uncited evidence ids, MVP agents missing declarations, an unofficial "… IQ" name or unknown area in the feedback loop, an unknown workflow node or trigger type or an unknown agent in a workflow. Rebuild until clean or every remaining warning is deliberate.
3. Validate the HTML with the html skill's validator when available (`validate.py` must report success).
4. Customer version (only when asked, or before anything leaves Microsoft): add `--audience customer`. Risk visibility is resolved against original sources before scrubbing; internal-only content, `internal_notes` and cached derived PRD fields are removed, then final risks/PRD derive from scrubbed sources. Attendee contributions follow source visibility. A removed source ID alone is not sanitisation. The build refuses if any `meta.internal_terms` string remains. Name it `<Customer> Frontier Company Blueprint (customer).html` and review embedded data and downloads as well as visible text.

### Step 4: Publish
1. `CopyArtifact(surface="output", source="working/frontier/<slug>/<file>.html", destination="<file>.html")`; confirm `"ok": true`. Publish the identity kit zip and its `catalog.html` (as `<Customer> - agent identity catalogue.html`) the same way, and the normalized JSON: it is the canonical blueprint for the next version.
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
- If the identity kit fails (the summary's `notes` say why): the blueprint is still built without identity; report the reason, fix it with **frontier-agent-identity** and build again.
- If no customer theme is available: the journey colours come from the blueprint and are flagged; say so and ask for a customer-authored deck or template.

## Files

- `templates/frontier-blueprint-template.html` — the renderer (data placeholder `"__BLUEPRINT_DATA__"`)
- `templates/blueprint-defaults.json` — Innovation Hub canon: digital feedback loop (Microsoft IQ, the four areas, mapping rules, Microsoft sources), governance, security, knowledge, build & run, foundation, target-architecture layers, horizons, discovery bank, Agent Factory, landing zone, canon ADRs, IT readiness
- `templates/product-icons.json` — Microsoft product icons with their notice and the text rules that map product names to icons
- `scripts/canon.py` — adds the canon blocks to a blueprint without overwriting what it has, and completes the feedback loop from the journeys
- `scripts/seed_blueprint.py` — context pack to blueprint seed
- `scripts/build_blueprint.py` — validate, normalise, customer version, render
- `scripts/build_with_identity.py` — blueprint and agent identity kit in one step (default build); with `--value` and `--finops` also the business value and the FinOps page
- `scripts/workflow.py` — the agent workflows: Copilot Studio node and trigger types, derivation from the canvas plan, checks (used by the build)
- `scripts/prd_model.py` — canonical PRD derivation, identical to the solution-design copy
- `scripts/risks.py` — risk derivation, ratings and retained source/ID bindings
- `scripts/merge_feedback.py` — merge the workshop feedback export (identity feedback kept as `identity_feedback`)
- `references/authoring-guide.md` — how to write the hypothesis, scoring rubric, journey pattern library
- `references/blueprint-schema.md` — every field of the blueprint JSON
- `examples/caldova-blueprint.json` — complete fictitious example and demo (Caldova Industrial AG: four business journeys plus the Agent Factory, 29 agents, 8 attendees)
