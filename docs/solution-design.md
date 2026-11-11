# Frontier Envisioning — Solution Design

| Field | Value |
|---|---|
| Version | 1.2 |
| Date | 2026-11-11 |
| Author | Urs Rüegg (original product document); Copilot (AI-assisted split, accessibility maintenance and selective intake) |
| Status | Maintained design; no new product or release approval implied |
| Scope | Unreleased 1.7.1 intake design, preserved Part B/accessibility design, technical sources and historical 1.6.0 file inventory |
| References | [Product requirements](prd.md), [Product context](prd.md#product-context-and-provenance), [Docs](README.md), [D2 plan](plans/2026-11-09-documentation-foundation-plan.md), [Layout amendment](specs/2026-11-10-documentation-layout-design.md), [Intake plan](plans/2026-11-10-handover-1.7-intake-plan.md) |

**Unreleased 1.6.1 distribution hygiene (#20).** Both builders reuse the package
module's bounded, recursive byte/ZIP validator before writing inventory,
archive or checksum output. Member names, text and ZIP comments are inspected;
the complete bundle no longer includes the analysis-directory wildcard.
Valid entry bytes, ordering and fixed ZIP metadata are preserved. See the
[distribution spec](specs/2026-11-10-anonymised-distribution-design.md).

This document revision is independent of the plugin version. It is the
authoritative technical design; [prd.md](prd.md) owns the requirements,
release plan, product decisions and shared product/basis/licence/provenance
and owner context.

The split preserves historical results and claims, including the original
release verification tables and dated availability. They are not new test
results or approvals. The appendix retains the original 1.6.0 inventory
(including its former combined-document path); it is not a current file list.
The [unreleased 1.6.1 requirement](prd.md#161-patch-workflow-legend-accessibility)
remains separate from these historical claims.

## 1.7.1 development intake

**Received 1.7.0 features are selectively integrated as unreleased 1.7.1;
not a release.** The [current PRD intake](prd.md#171-development-intake),
[approved design](specs/2026-11-10-handover-1.7-intake-design.md) and
[written plan](plans/2026-11-10-handover-1.7-intake-plan.md) govern this delta.
[ADR-0025](adr/0025-four-part-journey-structure.md) records the received rationale
with Proposed status; the [sprint](sprints/SPRINT-003-handover-1.7-intake.md)
records execution evidence and remaining gates. Part B, its historical results
and the original inventory below are preserved, not replaced by the incoming
combined document.

### Four-part navigation and workshop outputs

| Part | Views |
|---|---|
| Vision | Overview, Org model, Blueprint, Journeys, Use cases, PRD |
| Design | Agents, Agent identity, Target architecture, IT readiness |
| Build | Roadmap, Plan, FinOps |
| Workshops | Attendees, Discovery, Risks, Evidence |

The seventeen-view rail and breadcrumb take optional labels/descriptions from
`parts`. Existing route IDs and older blueprints remain usable. The PRD view
downloads Markdown and records `prd:scope`; use-case risk links select the
register, while Roadmap and Agent Factory link to Plan. Notes stay in browser
storage until the feedback file is exported and merged.

### Canonical Python models and retained identity

`prd_model.py` is identical in frontier-blueprint and frontier-solution-design.
The HTML's embedded `prd` and scaffolded `design/prd.md` use the same derivation:
problem/provenance, scope, personas, functional/non-functional requirements,
acceptance, KPIs, business value, dependencies, risks, decisions, release plan
and Definition of Ready. Authored problem, goals, exclusions, exit test, release
plan, status and owner survive rebuilds. IDs are allocated from the full
blueprint's canonical agent order before subset selection; filtering must not
renumber the surviving requirements.

`risks.py` combines use-case risk points, blocked readiness items, canon and
authored/workshop risks. Finite integer likelihood/impact values from 1 to 5
produce score and level; booleans and invalid feedback are rejected/reported.
Normalised `risks.source_ids` retains current source bindings and retired IDs;
each bound risk carries `source_key`. Source changes reserve the old identity
rather than assigning its verdict to a different risk. Workshop-owned records
survive rebuilds with separate content provenance (`content_src`). Keep this
normalised history: discarding it cannot guarantee old ID-only feedback identity.

Attendee contributions carry text, source IDs and transcript timestamps, with
sessions and focus links. The seed uses evidenced transcript speakers; missing
evidence is flagged, never fabricated.

### Plan, privacy and preserved hardening

`factory.board` groups computed stages under Idea, Design, Build and Deploy.
The Plan view uses the existing eight handover checks, journey/MVP filters,
identity cards, owner/readiness/next-step values and WIP limits. Its CSV download
quotes delimiters, newlines and Unicode and handles spreadsheet formula prefixes.
It is handover data, not a live Azure Boards/GitHub Projects connector, a native
compatibility certification or permission to build/deploy.

For customer generation, resolve bound risk visibility **before** source
scrubbing, including promoted legacy workshop risks. Scrub internal-only objects
and content provenance, discard cached derived PRD fields, then derive final
risks and PRD from scrubbed sources. Embedded data and downloadable Markdown
must not retain internal-derived content merely after removing its source ID.
Attendee contributions follow the same evidence boundary.

Retain the A6 catalogue correction, modal/inert/focus lifecycle, roving tabs,
pressed filters, SVG controls, adaptive text contrast, bounded sticky layout,
targets and narrow reflow. Original brand/icon and release/raster bytes remain
historical evidence. The finite 1.7.1 raster-input profile is verified separately;
it does not replace original hashes or prove a release.

The repository remains private at `urruegg/frontier-envisioning`; development
distribution remains Microsoft internal. Keep the shared recursive pre-write
byte/ZIP guard, eleven-entry complete-bundle allowlist and analysis/intake
exclusions. Customer scrubbing, WIP/readiness and metadata are not external/IP
clearance. Final strict L1, integrated review, finished distribution/install-plan
acceptance and manual Cowork/assistive-technology checks remain separate;
no installation, publication or deployment is claimed here.

## Part B — Solution Design

## B.1 Architecture overview

```
Solution engineer ── natural language ──▶ Copilot Cowork (orchestrator)
                                             │ loads skills by intent
   ┌─────────────────┬─────────────────┬─────┴───────────┬─────────────────┬─────────────────┐
   ▼                 ▼                 ▼                 ▼                 ▼                 │
 frontier-         frontier-context- frontier-         frontier-solution-frontier-agent-   │
 envisioning       discovery         blueprint         design            identity          │
 (method, phases,  (Work IQ +        (seed, hypothesis,(PRD, solution    (names, colours,  │
  gates)            transcripts)      build, customer   design, ADRs)     icons, kit,       │
                                      version, merge)                     stamping)         │
   │                 │                 │                 │                 │                 │
   │      Microsoft 365 tools (Work IQ)        Python scripts (standard library, sandbox)    │
   │      calendar · transcripts · search · Teams · OneDrive · web                           │
   ▼                 ▼                 ▼                 ▼                 ▼                 │
  working/frontier/<slug>/  ──publish──▶ output (deliverables) ──keep──▶ OneDrive Documents/Cowork/frontier-envisioning/<slug>/
                                            │
                                            ▼
                       <Customer> Frontier Company Blueprint.html  (offline, any modern browser)
                       └─ workshop notes in browser storage ─ export ─▶ feedback.json ─▶ merge
                       <Customer> - agent identity package v1.0.zip  (customer repository and release pipeline)
```

The plugin follows the principle it recommends to customers: **the deterministic part is a script, the judgement is the model's.** Scripts validate, normalise, seed, render, merge and scaffold, the same way every time; Cowork reads the evidence, writes the hypothesis and completes the design.

## B.2 Components

### B.2.1 Skills

| Skill | Responsibility | Triggers (examples) | Delegates to |
|---|---|---|---|
| frontier-envisioning | Method, phase detection, gates, engagement folder, agenda | "prepare the Frontier envisioning for …", "what is next in the … envisioning" | the four skills below |
| frontier-context-discovery | Work IQ and transcript discovery; context pack; evidence log | "gather the customer context for …", "analyse the workshop transcript for …" | meeting-intel for plain recaps |
| frontier-blueprint | Seed, hypothesis authoring, build, customer version, feedback merge | "build the Frontier blueprint for …", "update the blueprint with the workshop feedback" | html skill for plain pages |
| frontier-solution-design | PRD, solution design, ADRs, design repository | "write the PRD for the … MVP", "design the target architecture for …" | docx agent for Word output |
| frontier-agent-identity | Brand discovery, identity seed, review, kit build, validation, stamping, identity in the blueprint | "create the agent identity kit for …", "agent naming convention", "build the identity kit demo for Caldova" | image generation for logos and pictures |
| frontier-value-case | Value tree, assumption register, calculation, blueprint apply, workshop merge | "build the value case for …", "ROI in CHF for the MVP agents", "update the value case with the workshop feedback" | sales skills for CRM deal business cases |
| frontier-finops | Usage model, cost lines, purchase options, scenarios, guardrails, rates | "what will the agents cost per month", "Copilot Credits for …", "pay-as-you-go, packs or P3?" | Azure Cost Management for non-agent spend |

Each SKILL.md carries trigger phrases, a "Do NOT use … use X" exclusion, a "When NOT to Use" section, a Quick Start, a numbered workflow naming the tools, an output format, guardrails and failure handling.

### B.2.2 Scripts

| Script | Input | Output |
|---|---|---|
| `parse_transcript.py` | .vtt, .txt/.md, .docx, saved JSON transcript | Turns (speaker, start, end, text), speaker stats, signals by category |
| `context_pack.py validate / render` | `customer-context.json` | Errors, warnings, coverage gaps, stats; evidence log markdown (internal or customer) |
| `seed_blueprint.py` | Context pack + `blueprint-defaults.json` | Blueprint seed with evidence, journeys, KPIs, systems, leaders, use cases, next steps, the Hub canon and `_todo` |
| `build_blueprint.py` | Blueprint JSON + template | Normalised JSON, HTML, build report; customer version with `--audience customer` |
| `canon.py` | Blueprint + `blueprint-defaults.json` | The Innovation Hub canon added without overwriting (Agent Factory, landing zone, canon ADRs, IT readiness, digital feedback loop) |
| `workflow.py` | Agents' canvases (used by the build) | Each agent's workflow: authored ones checked and given node ids, missing ones derived from the plan (`derived`) |
| `merge_feedback.py` | Normalised blueprint + feedback export(s) | Next blueprint version with statuses, notes, answers and workshop evidence |
| `scaffold_design_docs.py` | Normalised blueprint (+ MVP ids) | `prd.md`, `solution-design.md` (with each MVP workflow), `adr/ADR-000n-*.md`, `it-readiness.md` |
| `install/prepare_install.py` | The extracted package | Verification (checksums, names, unexpected files) and the install plan: skills, file counts, new/update/reinstall, the copy calls |
| `read_office_theme.py` | Customer-authored Office file | `brand.json`: theme colours, fonts, named colours with evidence ids |
| `seed_identity.py` | Blueprint (+ brand) | `agent-identity.json`, `palette.json`, `seed-report.md` |
| `make_kit.py` | Reviewed config and palette | The identity kit folder and zip; build, validation and unit-test results |
| `apply_identity.py` | Blueprint + kit | Blueprint JSON with `identity` per agent (names, icons per environment, outline, technical names) and the Agent identity page data; optionally the kit's journey colours |
| `build_with_identity.py` | Blueprint (+ customer theme, or the reviewed identity) | Blueprint HTML with the Agent identity page, the identity kit folder and zip, and a JSON summary |
| Kit: `build_identity_assets.py`, `validate_identity.py`, `stamp_identity.py`, `raster.py`, `import_fluent_glyphs.py` | Kit config | Names, icons, cards, visuals, docs, catalogue; validation report; stamped `bot.xml`; PNG rendering; glyph import |
| `seed_value.py`, `value_calc.py`, `apply_value.py`, `merge_value_feedback.py` | Blueprint, value.json, finops.json, feedback export | Value case seed; results (views, NPV, ROI, payback, break-even, sensitivity, ranges); business value in the blueprint; verdicts merged |
| `seed_finops.py`, `finops_calc.py`, `apply_finops.py` | Blueprint, value.json, finops.json, rates file | Cost model seed; cost lines, unit economics, purchase options, scenarios, guardrails, lessons; the FinOps page data |
| `tools/selftest.py` | Bundled examples | Pass/fail of 34 end-to-end checks, including the identity kit, the value and FinOps golden test, the one-step build and an install simulation |
| `tools/build_package.py` | Repository | Install package (chat install and organisation catalogue), source zip, `install/plugin-install.json`, checksums |

### B.2.3 Knowledge files

| File | Content |
|---|---|
| `method.md` | Phases, artefacts, gates, timeline, one-day agenda, roles, naming |
| `hairo-model.md` | HAIRO rings, role card, nine-section role profile, hybrid-organisation blueprint, mapping to Microsoft's Frontier Firm |
| `work-iq-playbook.md` | Search recipes, windows, transcript reading, visibility rules, deduplication, completeness checklist |
| `context-pack.md`, `question-bank.md` | Context schema; discovery questions by category, journey type and operating model |
| `authoring-guide.md`, `blueprint-schema.md` | How to write the hypothesis (autonomy, workflow-first, declarations, canvas, scoring, journey pattern library); every blueprint field |
| `frontier-reference-architecture.md`, `design-rules.md` | Microsoft Frontier layers, components, patterns, availability with sources; platform commitments, enforcement layers, identifiers, repository layout, ADR template |
| `identity-method.md`, `brand-discovery.md`, `kit-reference.md`, `glyphs.json` | Naming rule, environments, technical names, colours and icons with Microsoft sources; brand sources and the brand file; kit layout, config fields, commands, validator checks; 61 glyphs (37 Fluent UI System Icons, 24 Frontier glyphs) with keywords |
| `blueprint-defaults.json` | Hub canon used by the seed: governance, Intelligence Resources, security, knowledge, build and run, foundation, architecture layers, patterns, horizons, discovery bank |

## B.3 Data model

| Object | Schema | Key identifiers |
|---|---|---|
| Context pack | `frontier-context/1.0` | Sources E01…, facts F001…, journeys, stakeholders, systems, KPIs, constraints, ideas, decisions, actions, open questions |
| Blueprint | `frontier-blueprint/1.0` | Journeys D1…, leaders L1…, lead agents D1-LEAD, specialists D1-A01…, use cases UC01…, questions D1-Q01…, evidence E01… and workshop evidence W01…; workflow nodes n1… per agent |
| Workshop feedback | `frontier-blueprint-feedback` 1.0 | `validations["agent:D3-A05" or "uc:UC09"]`, `discovery["D3-Q02"]`, blueprint id and version |
| Design | Markdown | FR-0001…, NFR-0001…, AC-001…, D-01…, TD-01…, ADR-0001… |
| Engagement | `engagement.json` | Customer, slug, phase, workshop date, blueprint version, identity version, files, updated |
| Brand | `frontier-brand/1.0` | Theme slots, fonts, named colours with sources, optional journey colours, evidence E… |
| Agent identity | `frontier-agent-identity/1.0` | Agents keyed by blueprint id (D3-A05, D3-DATA); tokens `po`, `domain`, `scope`; `derived` names per environment; decisions N-1…, evidence |
| Palette | `frontier-agent-palette/1.0` | Journey colours with glyph, contrast and tints; environment bands; status styles; UI colours and fonts |
| Glyph library | `agent-glyphs/1.0` | Glyph name, source (fluent or frontier), keywords, filled and regular geometry |

Identifiers are allocated once and never reused. The blueprint id and version tie feedback to the version that was shown.

## B.4 Process flows

### B.4.1 Discovery

| # | Actor | Step |
|---|---|---|
| 1 | Cowork | Resolve customer, scope, workshop date; compute the window |
| 2 | Tools | Calendar view → meetings with the customer |
| 3 | Tools | Transcript list and transcript per meeting (403/404 final) |
| 4 | Script | `parse_transcript.py` per transcript → turns and signals |
| 5 | Tools | Microsoft 365 search: mail, chats, files; Teams messages; web |
| 6 | Cowork | Register sources with visibility; write facts with citations; fill journeys, stakeholders, systems, KPIs, constraints, ideas, open questions |
| 7 | Script | `context_pack.py validate` → fix errors; close or list gaps |
| 8 | Script | `context_pack.py render` → evidence log |
| 9 | Cowork | Publish; offer to keep the engagement folder |

### B.4.2 Blueprint build

| # | Actor | Step |
|---|---|---|
| 1 | Script | `seed_blueprint.py` → seed with canon and `_todo` |
| 2 | Cowork | Write the hypothesis per the authoring guide (stages, personas, lead and specialists, seam, scores, MVP canvases and declarations, mission, outcomes, flows, decisions) |
| 3 | Script | `build_blueprint.py` → canon completion, agent workflows (checked or derived from the plan), errors and warnings → fix → HTML and normalised JSON |
| 4 | Validator | HTML validator (self-contained, accessible markup) |
| 5 | Script | Customer version with `--audience customer` when anything leaves Microsoft |
| 6 | Cowork | Publish; reply with journeys, agents, MVP candidates, open questions |

### B.4.3 Workshop capture loop

| # | Actor | Step |
|---|---|---|
| 1 | Facilitator | Presents views; records verdicts on agents and use cases, answers and notes on questions (stored per blueprint id and version in the browser) |
| 2 | Facilitator | Exports `<customer>-workshop-feedback.json` at the end of each block |
| 3 | Script | `merge_feedback.py` → statuses, notes, answers, workshop evidence W0n, version 0.2 |
| 4 | Cowork | Adds transcript evidence; updates the hypothesis; rebuilds; sets `validated` when confirmed |

### B.4.4 Design

| # | Actor | Step |
|---|---|---|
| 1 | Script | `scaffold_design_docs.py` → PRD, solution design, ADRs with `[To complete]` markers |
| 2 | Cowork | Completes from evidence or open decisions; verifies availability; adds ADRs |
| 3 | Cowork | Publishes markdown; optionally Word documents through the docx agent or a design repository |

### B.4.5 Agent identity

| # | Actor | Step |
|---|---|---|
| 1 | Cowork | Collects brand sources; `read_office_theme.py` on a customer-authored file → `brand.json` with evidence ids |
| 2 | Script | `seed_identity.py` → config, palette and seed report (shortened names, colour adjustments, glyph choices flagged) |
| 3 | Cowork + user | Review: PO tokens, natural domains for shortened names, MVP names, colours, prefix; decisions N-1 to N-6 with owners |
| 4 | Script | `make_kit.py` → copy kit, build names, icons, cards, visuals, docs, catalogue → validate → unit tests → zip |
| 5 | Script | `build_with_identity.py` (frontier-blueprint) → identity in every agent and the Agent identity page; every blueprint build runs steps 2, 4 and 5 as a proposal |
| 6 | Customer | Copies the package into the repository; the pipeline validates on pull requests and stamps names and icons before packing |

## B.5 Blueprint HTML design

**Rendering.** One HTML file: inline CSS (about 63 KB), a vanilla JavaScript renderer (about 237 KB, no libraries) and the blueprint as a JSON island (`<script type="application/json" id="bp-data">`). The build escapes `<`, `>`, `&` and line separators in the JSON, so data can never close the script element; the renderer creates every element with DOM APIs and text nodes, never by injecting data as HTML. The raw template, opened without data, shows how to build it.

**Views and navigation (1.4.0).** Fourteen views in three parts along the Innovation Hub journey: Vision (Overview, Org model, Blueprint, Journeys with the Agent Factory, Attendees), Design (Agents, Agent identity, Target architecture with four tabs, Use cases with a detail page, IT readiness, FinOps), Workshop (Discovery, Roadmap, Evidence). Earlier releases: ten views in three parts (Vision, Design, Workshop) on a left rail; journey tabs on journey-specific views; deep links by hash (`#/agents/D3-A05`); arrow keys move between views; a pager at the end of each view; a drawer for role cards, role profiles, evidence and use cases (Escape closes, focus returns).

**Digital feedback loop (1.5.0).** The Overview draws the loop as one SVG (1200 × 700): the four areas as cards in the corners (Engage customers top left, Optimize operations top right, Empower employees bottom left, Transform products bottom right; colour of the first linked journey), Microsoft IQ as a circle in the centre with the four layers as chips, a human-approval band and the trust line (Microsoft Entra, Microsoft Purview, Microsoft Agent 365), and a dashed outer ring with direction marks for the loop. Each area has three curves to the centre: signal (card to Microsoft IQ), action (Microsoft IQ to card, with an approval gate at 30 % of its length) and outcome (dashed, card back to Microsoft IQ). The animation is SVG SMIL (`animateMotion` with key points), one 8-second cycle per area, offset by 2 seconds in clockwise order: two signal dots, an action packet that waits at the gate, an outcome dot; the centre pulses when a signal arrives. No script runs the animation, so the hosting policy needs no change; the pause button calls `pauseAnimations()`, reduced motion keeps the diagram still, print hides the particles. A click or Enter on a card selects the area: the chips of the layers it does not use dim, its curves thicken and the panel below lists its signals, actions and outcomes from the data.

**Agent workflow (1.6.0).** Under the trigger canvas, full width, the agent's workflow on a dark canvas with a dotted grid, like the Copilot Studio workflow designer: a bar (name, Draft, "Derived from the plan", AI, deterministic and human step counts), the Add panel with the eleven designer node types as legend and highlighter, the canvas and a floating properties panel. The layout runs the main path left to right from the trigger to the desired outcome (nodes 196 × 60, gap 40); If/Else, Classify and Human review nodes grow a pill per path, and their branches run on lanes below that rejoin the next step or end at an end node; loops and scopes are dashed containers around their steps; notes sit above their step. The overview folds the path into rows of at most 960 pixels with orthogonal wrap edges; the designer row keeps one line. Nodes are SVG groups with a role, a label and a tab stop in flow order (Enter opens, Escape closes); icons are the agent's identity icon, Microsoft product icons for Copilot Studio, Microsoft 365 Copilot and connector systems, otherwise the plugin's own glyphs. Print uses a light canvas without the panels.

**Org model layout.** The SVG (1000 × 1000) places human leaders in the centre (up to seven on a small circle), lead agents on an inner ring (radius 165) at the middle of their journey's arc, and specialists on an outer ring (radius 292). Journey arcs (radius 440) are sized by the number of specialists, with gaps between journeys and labels on text paths (flipped on the lower half so they stay readable). Labels run radially outward and wrap to two lines; lead labels sit on the inner side for top and bottom journeys and below the node otherwise, so they never cross the specialist ring. Dashed outlines mark planned positions, a halo marks MVP candidates, badges show the autonomy level, dimming shows the journey filter. The reveal control mirrors the HAIRO showcase: human-led → lead agents → agent teams.

**State.** Workshop notes and verdicts are stored in browser storage under `fbp:<blueprint id>:<version>`, so a new version starts clean and an old export cannot be applied to the wrong version. Export produces JSON for the merge script and plain text for minutes.

**Theming and accessibility.** CSS custom properties with light and dark schemes; accent and journey colours from data; logical properties for right-to-left support; ARIA roles and labels on interactive SVG nodes; visible focus; print rules that hide navigation.

**Unreleased 1.6.1 accessibility implementation (#7).** The drawer remains a
labelled `div` dialog, not a native `dialog`. Closed markup is `hidden`, `inert`
and `aria-hidden="true"`; an open drawer exposes `aria-modal="true"`, focuses
Close and contains Tab/Shift+Tab among visible, enabled, non-inert stops.
Opening snapshots each background element's existing inert state, then makes
the page, rail and skip link inert. Replacing drawer content preserves the
outer trigger and snapshot. Closing restores those exact prior states and
returns focus to that trigger, or the view if the trigger is unavailable.
The drawer becomes inert immediately; its delayed hide preserves normal
motion, is cancelled on rapid reopening and is immediate for reduced motion.

Journey, architecture and factory tabs have named tablists, roving tab stops
and labelled panels. Arrow/Home/End activation restores focus after rendering
without changing the intended route. Global view shortcuts retain input,
modifier and drawer guards; default agent deep links remain intact.
Org/ADR filters use `aria-pressed`, not tab selection. Interactive SVG roots
use labelled groups so their keyboard-operable children remain exposed.

Rendered text uses the higher-contrast black/white foreground on validated
opaque data-colour fills, or neutral ink on neutral panels. Brand values,
swatches, journey cues and Microsoft icon artwork are preserved. Filtered
Org/portfolio labels and filled backgrounds remain fully opaque; dimming is
restricted to decorative strokes, restored on keyboard focus. Checked target
families have at least 24 × 24 CSS pixel hit areas. Narrow rules wrap the banner
and min-content columns and stack affected grids at 320px; diagrams and tables
retain local scrolling. There is no global overflow-hiding workaround.

**Agent identity.** When agents carry an `identity` (from the identity kit), the journey view, the agents view and the role card show the agent's icon and its display names per environment. Icons must be base64 SVG or PNG data URIs (checked by the build and the renderer); anything else is ignored.

**Landing zone and factory (1.4.0).** The landing-zone diagram is computed for any number of journeys (width 1200): the tenant, identity, policy and front-door areas; the platform landing zone with four shared services; one agent landing zone per journey with its environments, data classes and agent icons, flanked by the sandbox and the Agent Factory; the systems of record, building blocks, vendor agents and retired agents. An agent's factory stage is computed in the browser from its lifecycle text and the eight handover checks, so nothing is stored twice. Product icons are looked up by key or by text rules and embedded only when used.

**Size.** The Caldova example (4 journeys, 23 agents, 16 use cases, 27 questions, 7 sources) renders to about 204 KB without identity; with the identity of 27 agents (icons per environment and the Agent identity page) about 360 KB. Release 1.6.0: the Caldova demo with its five journeys, 29 agents, identity, product icons, value case, FinOps page, feedback loop and two workflows renders to about 764 KB; the empty template is about 302 KB.

## B.6 Grounding in Microsoft's Frontier architecture

The target-architecture view and the solution design use the Hub canon, an Innovation Hub synthesis of Microsoft guidance (Microsoft does not publish this exact stack; the components are Microsoft's):

| # | Layer | Microsoft components |
|---|---|---|
| 0 | Journey & operating model | Work Trend Index guidance (agent boss, human-agent ratio, phases), collaboration patterns, Agents hub adoption patterns |
| 1 | Experience & channels | Microsoft 365 Copilot and Cowork, Teams, Outlook, Microsoft 365 Agents SDK |
| 2 | Orchestration & agents | Copilot Studio (multi-agent, A2A, workflows), Foundry Agent Service, Microsoft Agent Framework, Power Automate |
| 3 | Knowledge & context (IQ) | Work IQ, Fabric IQ and Fabric data agents, Foundry IQ on Azure AI Search, web grounding |
| 4 | Tools & actions | Power Platform connectors, MCP servers, Foundry toolboxes, A2A, governed access layers to systems of record |
| 5 | Models | Foundry model catalog and router, model choice in Copilot Studio |
| 6 | Identity, security & governance | Microsoft Entra Agent ID, Microsoft Agent 365, Microsoft Purview, Microsoft Defender, environments and DLP |
| 7 | Observability, evaluation & operations | Foundry Control Plane, Copilot Studio analytics and evaluations, Azure Monitor and Application Insights, Copilot Credits and cost alerts |
| + | Approval seams | Copilot Studio request-information step, Agent Framework tool approval, Teams approvals, Cowork checkpoints |

Design guidance carried into every blueprint and design: use the lowest complexity that works and go multi-agent only for security boundaries, separate owners or planned growth (Cloud Adoption Framework); choose the orchestration pattern per step (sequential, concurrent, group chat, handoff, magentic — Azure Architecture Center); build in a SaaS agent, Copilot Studio or Foundry by fit; one identity, owner and registry entry per agent; human oversight of high-impact actions stays with the customer.

The HAIRO frame maps onto these concepts: human-led centre ↔ agent boss and phase 3 of the Frontier Firm; Intelligence Resources ↔ IT and HR managing digital labour, with Agent 365 and Entra Agent ID as registry and identity; approval seam ↔ human-in-the-loop gates; knowledge scoped per agent ↔ Microsoft IQ with permission-aware grounding.

The autonomy levels used in blueprints (Assist, Act with approval, Act within guardrails) are a Hub synthesis anchored in the Cloud Adoption Framework's productivity, action and automation agent types and the Agents hub risk tiers; they are labelled as such.

Availability snapshot (22 October 2026, per sources): Microsoft 365 E7 and Agent 365 generally available since 1 May 2026; Entra Agent ID generally available; Copilot Cowork generally available since 16 June 2026; Copilot Studio multi-agent orchestration and A2A generally available since April 2026; Agent Framework 1.0; Microsoft IQ and the Work IQ APIs available since June 2026; Foundry IQ and Foundry Control Plane partly in preview; web grounding to verify. The full table and sources are in `frontier-reference-architecture.md`.

## B.7 Security and privacy design

| Concern | Design |
|---|---|
| Whose data | Only the user's own mailbox, calendar, chats and files, plus shared content; tools run as the user |
| Internal versus customer | Every source carries visibility; facts inherit it; the customer build removes internal sources, their citations, items flagged internal and internal notes, and refuses on listed internal terms |
| Outside content | Treated as data; the skills say so explicitly; the template renders data as text only |
| Scripts | Standard library only; no network, no evaluation of input; `.docx` and Office themes read with DTD and entity declarations refused and size limits; the identity kit calls an installed SVG converter only for PNG copies of cards and visuals (resolved executable, fixed arguments, no shell); security scan clean |
| Brand | Colours only from customer sources with evidence ids; logos only where the customer's brand rules allow it; fictitious brand in the demo |
| HTML | Self-contained; validator enforces no external references, no inline event handlers, no active data URIs; logos limited to raster data URIs |
| Storage | Session files under `working/`; deliverables in the output folder; engagement folder in the user's OneDrive on request; workshop notes in the presenter's browser until exported |
| People | Roles before names; no sensitive personal data; no performance judgements; no agent decides about a person |
| Consent and NDA | Frame phase records NDA status; transcripts only from meetings the user organised or attended |

## B.8 Packaging and distribution

| Package | Content | Use |
|---|---|---|
| `frontier-envisioning-plugin-1.1.0.zip` | `README.md` (setup guide), `MIT.md` (licence), `manifest.json` (devPreview schema, five `agentSkills` folders), `color.png` 192 × 192, `outline.png` 32 × 32, `install/plugin-install.json` (file list with checksums), `install/prepare_install.py`, `skills/<name>/…` | Everyone: attach in a Cowork chat and say "Install the Frontier PlugIn". Admins: upload to the organisation catalogue |
| `frontier-envisioning-1.1.0-source.zip` | `.claude-plugin/plugin.json`, `package/`, `install/`, `skills/`, `docs/`, `tools/`, README, MIT.md, changelog | Version control (for example a GitHub repository next to the HR sample) |

### B.8.1 Install from a Cowork chat

| # | Actor | Step |
|---|---|---|
| 1 | User | Attaches the zip in a new Cowork chat and says "Install the Frontier PlugIn" |
| 2 | Cowork | Extracts the zip to `working/frontier-plugin/` and reads `README.md` (section "For Copilot Cowork") |
| 3 | Script | `install/prepare_install.py` verifies every file against `install/plugin-install.json` and prints the plan; an altered or incomplete package stops here |
| 4 | Cowork | Copies each skill folder to the user's skills folder (`CopyArtifact`, surface user, recursive, overwrite); the user approves once |
| 5 | Cowork | Compares the copied counts with the plan, retries an incomplete copy, and reports the installed skills, version and three prompts to start with |
| 6 | OneDrive | Syncs `Documents/Cowork/skills/`; new chats load the seven skills |


Versioning follows semantic versioning; `manifest.json` and `plugin.json` must carry the same version (checked by the package builder). Builder metadata (`packageMetadata.json` with builder name, environment id, creator id and owners) is environment-specific and added by the publisher when the target catalogue requires it (TD-04).

## B.9 Quality and testing

| Check | Tool | Result at release |
|---|---|---|
| End-to-end scripts | `tools/selftest.py` | 34 of 34 passed |
| Value and FinOps method | Golden test against the worked example (81,780 credits, CHF 662.42 per month, NPV CHF 540,413, ROI 520%, payback 1.3 months, break-even 3.1%) | Reproduced exactly |
| Agent identity page | Headless DOM test: Caldova demo, seeded proposal, customer version, 1.1.0 data, blueprint without identity | Every view and journey tab renders; no script errors |
| Identity kit | Kit validator and unit tests on the Caldova kit (27 agents) | 0 errors, 0 warnings; all tests passed |
| Icon renderer | Pixel comparison with a reference SVG renderer | Mean absolute difference below 0.02 of 255 per channel |
| All views, drawers and tabs render without script errors | Headless DOM test on the Caldova example and on a sparse seed | Passed |
| Agent workflow | Unit tests of `workflow.py` (node and trigger types, rules, derivation, checks, build, scaffold); headless DOM test of the workflow view; diagrams rendered to images and reviewed | 10 unit tests and the DOM test passed; overview and designer row reviewed |
| Self-contained, valid HTML | HTML validator | No errors, no warnings |
| Skill structure | `validate_skill.py` | 7 of 7 passed |
| Skill quality | `score_skill.py` | frontier-agent-identity 100, frontier-value-case 100, frontier-finops 99, frontier-envisioning 98, frontier-blueprint 98, frontier-solution-design 96, frontier-context-discovery 96 |
| Routing conflicts | `conflict_scan.py` | 0 unresolved (21 internal pairs, 1 built-in pair resolved by delegation) |
| Bundled code and links | `validate_assets.py` | Passed |
| Security | `security_scan.py` (bandit and prose scan) | Passed, 0 findings |
| Tool descriptions | `validate_tool_descriptions.py` | Passed |
| Package | `validate_package.py` on the install package | Passed; one expected warning (builder metadata) |
| Install | Self-test simulation: build, extract, check, alter, check | Passed; the altered copy is refused |

### Development accessibility evidence (2026-11-10; not release results)

The following paragraphs retain the pre-correction A5 measurements. The
user subsequently authorised the targeted catalogue correction in A6;
the dated handoff separates its fresh results from this initial checkpoint.

Development-only axe-core 4.11.0 runs through Playwright under the real hosting
CSP; it is not embedded in the offline product. DOM and automated browser
regressions cover focus, tabs, filters, contrast, target sizes, reflow and
preserved workflow/legend behaviour. The retained browser run has 41 passed
and 2 failed tests; the failures are catalogue AA text contrast in both colour
schemes (Later wave 4.40:1; Finance header 4.33:1). The excluded identity
generator, hosted catalogue copy, historical profiles and hashes are unchanged.
Full L2 is blocking; no assertion is skipped or waived.

Best-practice and incomplete findings remain reported separately. SVG and
composited colours still need human assessment. Manual Narrator, zoom, real
Windows high-contrast and voice checks are pending under #8. A4/A5 acceptance
and full WCAG conformance are not claimed. Current evidence and the outstanding
scope decision are in the [verification handoff](intake/2026-11-10-accessibility-verification.md)
and [testing strategy](engineering/testing-strategy.md). The release table
above remains the historical 1.6.0 record.

Behavioural tests to run before organisation-wide release (isolated skill-validator runs):

| Prompt | Expected skill |
|---|---|
| "Prepare the Frontier envisioning for Caldova, workshop on 12 November" | frontier-envisioning |
| "Gather the customer context for Caldova procurement" | frontier-context-discovery |
| "Update the blueprint with the workshop feedback" (feedback attached) | frontier-blueprint |
| "Write the PRD and solution design for the Caldova MVP" | frontier-solution-design |
| "Create the agent identity kit for Caldova" | frontier-agent-identity |
| "Design a logo for our team" | none (image generation) |
| "Summarise yesterday's stand-up" | none (meeting-intel) |
| "Create an HTML one-pager for our team event" | none (create / html) |

## B.10 Operations

- **Canon maintenance.** After each major Microsoft announcement event, the owner ([D-05](prd.md#a13-open-decisions)) reviews `frontier-reference-architecture.md` and `blueprint-defaults.json`, updates availability with dates and sources, bumps the minor version, runs the self-test and rebuilds the packages.
- **Template changes.** Edit the template, rebuild the Caldova example, run the HTML validator and the self-test; schema changes bump `frontier-blueprint/x.y` and keep the renderer backward compatible.
- **Feedback.** Engineers report issues with the blueprint id and build report; recurring hypothesis patterns go into the journey pattern library.

## B.11 Reuse and extension

New journey types are added to the pattern library and the question bank; customer-specific branding is data (accent, logo, labels such as "Pillar" instead of "Journey"); new views are added to the renderer's view list with an availability rule so blueprints without that data hide the view.

## B.12 Architecture decisions

| ID | Decision | Rationale | Alternatives rejected |
|---|---|---|---|
| ADR-0001 | Four skills: one method orchestrator plus three phase skills | Precise routing, reuse of phases on their own, each skill scoreable and testable | One monolithic skill (poor routing, long instructions); one skill per view (fragmented) |
| ADR-0002 | The blueprint is a single self-contained HTML file with a JSON island | Presentable offline in any workshop room, mailable, no tenant dependencies, same pattern as the samples | Managed app or Power App (tenant dependency, licensing, slower to iterate); slides (no interactivity, no live capture) |
| ADR-0003 | Deterministic scripts for validation, build, merge and scaffolding; the model for judgement | Same input, same output where it matters; mirrors the workflow-first rule we recommend to customers | Model-only generation of HTML (inconsistent, unsafe escaping, untestable) |
| ADR-0004 | Evidence register with visibility and a customer build gate | Traceability for the customer; zero internal leakage by construction | Manual redaction before sharing |
| ADR-0005 | Hub canon of layers 0–7 plus approval seams, with dated availability | One vocabulary across engagements, grounded in Cloud Adoption Framework and Azure Architecture Center guidance | Product-by-product diagrams per engagement |
| ADR-0006 | HAIRO as the organisation frame, adapted to enterprises (journeys, functional agent names, optional aliases, autonomy and declarations) | Intuitive "human-led, agent-operated" picture executives understand; adds governance the enterprise needs | Classic capability maps (no human-agent relationship) |
| ADR-0007 | Workshop capture in the browser with JSON export and a merge script | Works offline and without accounts; versions stay explicit | Shared online store (needs tenant setup; planned for 1.8) |
| ADR-0008 | The agent identity is generated from one config, with the documents, and checked by a validator in the customer's pipeline | Names, icons and docs can't drift; the customer owns the source of truth | Hand-made icon sets and naming pages (drift, no enforcement) |
| ADR-0009 | Icons are drawn by a standard-library renderer; cards and visuals use an SVG converter only when one exists | Same pixels everywhere; customers rebuild on any build agent without a browser or image library | Headless browser rendering (heavy dependency, not available on every agent) |
| ADR-0010 | Glyphs from Fluent UI System Icons plus original Frontier glyphs, stored in the kit; no network at build time | Licence-clean (MIT), offline, consistent grid; more Fluent glyphs importable | Fetching icons at build time (network, availability); AI-generated icons (inconsistent, not reproducible) |
| ADR-0012 | Two new skills for value and FinOps on top of the blueprint's evidence and workshop loop (option O3 of the value and FinOps proposal) | Reuses evidence ids, the customer-version guard, workshop export and merge, identity keys; deterministic, testable calculations; rates refreshed independently | A standalone plugin (duplicates the loop); fields in the blueprint only (calculation mixed with rendering) |
| ADR-0013 | One assumption register for value and cost, ranges by root-sum-square, the purchase model a hypothesis until a usage baseline | The workshop clarifies the few numbers that matter; ranges stay credible; no unrefundable commitment on guesses | Corner scenarios only (implausible ranges); a recommended P3 tier from estimates |
| ADR-0014 | The Innovation Hub canon (Agent Factory, landing zone, canon ADRs, IT readiness) lives in `blueprint-defaults.json` and is added by `canon.py` without overwriting | One canon for every engagement, customer content always wins, earlier blueprints upgrade with `--canon` | Copying a customer fork of the template per engagement |
| ADR-0015 | Microsoft product icons are a separate, non-MIT asset embedded only when used, with a notice and an opt-out | Readability like the workshop decks while respecting Microsoft's icon terms | Embedding every icon; drawing look-alike icons |
| ADR-0016 | The factory stage of an agent is computed from its data and the handover checks, not stored | The board can never contradict the canvas, declarations, identity, value, cost and readiness data | A manually maintained stage field |
| ADR-0023 | The Overview's digital feedback loop is Microsoft's (four areas around Microsoft IQ), animated in SVG without script, with official Microsoft names enforced by the build (`docs/adr/0023-digital-feedback-loop.md`) | Explains the data-driven part in the customer's context; works under the showcase policy; every name can be looked up | A static diagram; a script-driven animation; the showcase's own layer names |
| ADR-0024 | Each agent's workflow is drawn like the Copilot Studio workflow designer from `canvas.workflow`, derived from the plan until authored, with the designer's node and trigger names (`docs/adr/0024-agent-workflow-view.md`) | Builders and customers see the deterministic workflow, the AI steps and the human decisions in the terms of the build; no drift from the plan | A list of plan steps; images per agent; Microsoft's designer icons; a flowchart library; generating Copilot Studio definitions now |
| ADR-0011 | Build the identity kit with every blueprint, as a proposal; approval stays a separate gate (E) | Agents carry their future names and icons from the first workshop, and the names are reviewed in context; one command | Kit only on request (identity arrives late; the blueprint shows working names) |

## B.13 Open technical decisions

| ID | Question | Owner |
|---|---|---|
| TD-01 | Move engagement folders and feedback to a Hub SharePoint site or Microsoft List for multi-facilitator workshops | Hub solution engineering |
| TD-02 | Use the Work IQ APIs directly for discovery once available in Cowork tool scripts | Hub solution engineering |
| TD-03 | Slide export of the Overview, Org model and Target architecture views through the pptx agent | Hub solution engineering |
| TD-04 | Builder metadata for the organisation catalogue (environment id, creator id, owners) | Tenant admin |
| TD-05 | Usage telemetry for the success measures without collecting customer content | Hub leadership |
| TD-06 | Stamping for declarative agents and Microsoft-managed agents (one app package per environment; ESS customisation layer) once verified in a customer development environment | Hub solution engineering |

## B.14 Sources

Innovation Hub samples: procurement four-journeys blueprint mockup (October 2026); `github.com/urruegg/caldova-hr-frontier` (README, docs/prd.md, docs/solution-design.md). Journai: hub.journai.ch (HAIRO model, role cards and role profiles), architecture.journai.ch (hybrid organisation blueprint).

Microsoft (accessed October 2026):
1. Work Trend Index 2025 — The year the Frontier Firm is born: https://www.microsoft.com/en-us/worklab/work-trend-index/2025-the-year-the-frontier-firm-is-born
2. Work Trend Index 2026: https://www.microsoft.com/en-us/worklab/work-trend-index/agents-human-agency-and-the-opportunity-for-every-organization
3. How Frontier Firms are rebuilding the operating model: https://blogs.microsoft.com/blog/2026/05/05/how-frontier-firms-are-rebuilding-the-operating-model-for-the-age-of-ai/
4. Cloud Adoption Framework — AI agents: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/
5. Single agent or multiple agents: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/single-agent-multiple-agents
6. Governance and security across the organisation: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/governance-security-across-organization
7. AI agent orchestration patterns: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
8. Microsoft Entra Agent ID: https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
9. Microsoft Agent 365 general availability: https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/
10. Microsoft IQ: https://learn.microsoft.com/en-us/microsoft-iq/
11. Copilot Studio workflows and request information: https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flows-request-for-information
12. Process automation levels: https://www.microsoft.com/en-us/microsoft-365-copilot/microsoft-copilot-studio/process-automation
13. Frontier program: https://www.microsoft.com/en-us/copilot/resources/frontier-program
14. Microsoft Frontier Company (services unit): https://blogs.microsoft.com/blog/2026/07/02/microsoft-frontier-company-ai-engineering-that-amplifies-and-protects-your-intelligence/

Agent identity (checked 30 October 2026): Design icons for agent acquisition and management (https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-icon-management); Configure agent details and instructions in Copilot Studio (https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-instructions); Build agents in Agent Builder (https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents); declarative agent manifest schema v1.5 (https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json); Create and delete agents in Copilot Studio (https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot); Microsoft 365 app manifest schema (https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema); Fluent UI System Icons (https://github.com/microsoft/fluentui-system-icons).

Innovation Hub journey (checked 8 November 2026): Microsoft Power Platform icons (https://learn.microsoft.com/en-us/power-platform/guidance/icons); Azure icons (https://learn.microsoft.com/en-us/azure/architecture/icons/); Microsoft Entra architecture icons (https://learn.microsoft.com/en-us/entra/architecture/architecture-icons); Microsoft Dynamics 365 icons (https://learn.microsoft.com/en-us/dynamics365/get-started/icons); CAT Agent Skills (https://microsoft.github.io/cat-agent-skills/); New Harness, New Rules? CAT's Got You (https://microsoft.github.io/mcscatblog/posts/new-orchestrator-resources/); Choose a harness (https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness); ALM for Copilot Studio (https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/alm); Well-Architected for Power Platform (https://learn.microsoft.com/en-us/power-platform/well-architected/).

The complete source list is in `skills/frontier-solution-design/references/frontier-reference-architecture.md`.

---

## Appendix — File inventory (1.6.0)

| Path | Purpose |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest (source form) |
| `package/manifest.json`, `color.png`, `outline.png`, `icon-512.png` | MOS3 manifest and icons |
| `skills/frontier-envisioning/` | SKILL.md; references: method, HAIRO model |
| `skills/frontier-context-discovery/` | SKILL.md; scripts: parse_transcript, context_pack; references: playbook, context pack, question bank; example context |
| `skills/frontier-blueprint/` | SKILL.md; template HTML (with the Agent identity page); defaults; scripts: seed, build, build_with_identity, merge; references: authoring guide, schema; Caldova example; 1.4.0: `scripts/canon.py`, `templates/product-icons.json`; 1.5.0: the digital feedback loop in the template, the defaults and `canon.py`; 1.6.0: `scripts/workflow.py` and the agent workflow in the template |
| `skills/frontier-solution-design/` | SKILL.md; script: scaffold_design_docs (with each MVP workflow since 1.6.0); references: reference architecture, design rules |
| `skills/frontier-agent-identity/` | SKILL.md; scripts: read_office_theme, seed_identity, make_kit, apply_identity; references: identity method, brand discovery, kit reference; `kit/` (customer package template: scripts, renderer, glyph library, tests, pipelines, schema); Caldova examples (brand, config, palette) |
| `skills/frontier-value-case/` | SKILL.md; scripts: seed_value, value_calc, apply_value, merge_value_feedback, fv_expr; reference: value method; Caldova and worked-example value cases |
| `skills/frontier-finops/` | SKILL.md; rates file (November 2026); scripts: seed_finops, finops_calc, apply_finops, fv_expr; references: FinOps for agents, guardrails; Caldova and worked-example cost models |
| `docs/prd-and-solution-design.md` | This document |
| `install/prepare_install.py`, `install/plugin-install.json` | Install check and release file list (generated by the package builder) |
| `tools/selftest.py`, `tools/build_package.py` | Self-test and package builder |
| `README.md` | Setup guide (install in Cowork), what to ask, package contents, organisation roll-out |
| `MIT.md` | MIT licence (also in the install package) |
| `THIRD-PARTY-NOTICES.md` | Microsoft product icons and other material not covered by MIT (also in the install package) |
| `CHANGELOG.md` | History |
