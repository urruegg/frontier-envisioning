# Innovation Hub Frontier Solution Envisioning — Cowork plugin

## Product Requirements and Solution Design

| Field | Value |
|---|---|
| Product | Frontier Envisioning plugin for Microsoft Copilot Cowork (`frontier-envisioning`) |
| Document | PRD (Part A) and Solution Design (Part B) |
| Version | 1.6.0 — draft for review (plugin version 1.6.0) |
| Date | 8 November 2026 |
| Owner | Urs Rüegg, Sr Solution Engineer, Microsoft Innovation Hub Switzerland |
| Proposed reviewers | Innovation Hub leadership; Innovation Hub solution engineers; one account team piloting the plugin |
| License | MIT (`MIT.md`) · Copyright (c) 2026 Urs Rüegg · SPDX headers in every script; `license: MIT` in every skill |
| Basis | Procurement four-journeys blueprint mockup (solution-envisioning sample, October 2026); `urruegg/caldova-hr-frontier` (architecture-design sample, v1.5); Journai showcase: HAIRO model (hub.journai.ch) and "How we built our hybrid organisation" (architecture.journai.ch); Microsoft Frontier guidance (sources in B.14); an Innovation Hub HR agent identity package (October 2026, generalised and anonymised) for the agent identity kit; Innovation Hub HR and procurement workshop materials (November 2026: Agent Factory, landing zone, architecture decisions, IT preparation and readiness); an Innovation Hub showcase of the digital feedback loop with Microsoft IQ (November 2026, pattern only); Copilot Studio workflow designer and its Microsoft Learn documentation (November 2026: node and trigger types, the GitHub Copilot harness) |
| Deliverables | This document · README.md (setup guide) · generic Frontier Company Blueprint HTML template with the Caldova demo, the digital feedback loop on the Overview, the agent workflows, its Agent identity page, business value and FinOps page · install package `frontier-envisioning-plugin-1.6.0.zip` · repository starting point `frontier-envisioning-github-repo-1.6.0.zip` · Caldova agent identity package (demo) · Frontier visualisation and reuse evaluation (separate document) |

---

# Part A — Product Requirements

## A.1 Problem

Every Innovation Hub envisioning today is hand-built. The procurement sample is a bespoke HTML mockup of about 280 KB, more than half of it customer-specific data written by hand: four journeys, agents, discovery questions, workshop outcomes, PRD and next steps. The HR sample is a bespoke design repository with a PRD, a solution design, ADRs and a use-case portfolio. Both are excellent, and both started from a blank page.

Five things make that expensive and fragile:

1. **Context is scattered.** What the account team and the customer already said sits in meetings, transcripts, mail threads, Teams chats, account plans and decks. Collecting it is manual, and hypotheses lose the link to the evidence behind them.
2. **The method lives in people's heads.** The HAIRO organisation model, the agentic trigger canvas, the seven declarations, the Frontier phases and the target-architecture layers are applied differently from one engagement to the next.
3. **The workshop is captured outside the artefact.** Verdicts and answers end up in notes and have to be retyped into the next version.
4. **Envisioning and architecture design are disconnected.** The PRD and the solution design restart from scratch after the workshop.
5. **Agents get their identity by accident.** When the first agents are built, names, icons and colours are chosen per maker and per environment; "… DEV" ends up in solution names, test agents look like production agents, and nobody owns the convention.

## A.2 Vision

> Every Innovation Hub envisioning starts from the customer's own evidence and ends with a validated Frontier blueprint and a buildable design — in days, not weeks.

The plugin makes the Hub's method repeatable in Copilot Cowork: a solution engineer names the customer; Cowork gathers the context with Work IQ and the workshop transcripts, drafts the hypothesis hybrid organisation as an interactive blueprint, captures the workshop inside it, and produces the PRD and the solution design for the MVP agents, grounded in Microsoft's Frontier architecture guidance. When the agents are about to be built, every agent receives a brand identity - names per environment, colours from the customer's brand, icons in the Microsoft 365 sizes - generated from one config and checked in the customer's pipeline.

## A.3 Goals, non-goals and success measures

**Goals**

| # | Goal |
|---|---|
| G1 | Produce an evidenced, presentable Frontier Company Blueprint for any customer and scope (company or function) from one generic template |
| G2 | Make every customer statement traceable to its source, and keep Microsoft-internal material out of customer versions |
| G3 | Capture the workshop inside the blueprint and merge it into the next version without retyping |
| G4 | Carry the validated blueprint into a PRD, a solution design and ADRs that follow the Hub's design rules |
| G5 | Ground the target architecture in current Microsoft guidance, with dated availability |

**Non-goals (1.0)** — building agents in Copilot Studio; licensing or pricing calculations; updating CRM; sending anything to customers automatically; real-time co-editing of the blueprint by several people; languages other than English in the template; slide export.

**Success measures**

| Measure | Target | Baseline |
|---|---|---|
| Solution-engineer effort to a first blueprint after access to the evidence | ≤ 1 working day | To measure on the next two hand-built engagements |
| Customer statements in the blueprint that cite a source | ≥ 70 % of non-hypothesis items | Not tracked today |
| Workshops whose feedback is exported and merged | ≥ 90 % | Not tracked today |
| PRD and solution design draft available after the workshop | ≤ 5 working days | To measure |
| Internal evidence found in customer versions | 0 | — |
| Skill quality score (plugin validator) | ≥ 80 for every skill, no unresolved routing conflict | 96–100 at release (B.9) |

## A.4 Users

| Persona | Role in the engagement | What the plugin gives them |
|---|---|---|
| Innovation Hub solution engineer (primary) | Prepares, facilitates, designs | Context pack, blueprint, live capture, PRD and design |
| Account team (account executive, CSA, specialist) | Access, sponsor alignment, internal context | Evidence log; an internal blueprint that shows their context without leaking it |
| Customer sponsor | Confirms mission, priorities, MVPs | A customer-ready blueprint of their own organisation |
| Customer process owners | Validate journeys; become agent bosses | Journeys, role profiles, canvases to correct |
| Customer IT and security | Architecture, identity, data access | Target architecture, open decisions, ADRs |
| Hub lead | Quality and reuse across engagements | Consistent method, artefacts and canon |

## A.5 User journeys of the plugin

| Journey | When | Steps | Skill |
|---|---|---|---|
| J1 Prepare | Workshop minus 10 to minus 2 days | Frame scope → gather context → seed and write the hypothesis → build internal and customer versions → agenda and key questions | frontier-envisioning, frontier-context-discovery, frontier-blueprint |
| J2 Run the workshop | Workshop day | Present the views; validate agents and use cases; answer discovery questions; export the feedback | (the HTML, offline) |
| J3 Consolidate | Plus 1 day | Parse the workshop transcript → merge feedback → update the hypothesis → validated v1.0 → summary | frontier-context-discovery, frontier-blueprint |
| J4 Design | Plus 5 days | Scaffold PRD, solution design and ADRs → complete from evidence → verify availability | frontier-solution-design |
| J5 Continue | Any time | "What is next in the Caldova envisioning?" → phase detection from the engagement folder | frontier-envisioning |

## A.6 Scope

**In scope (1.0)**: four skills; the generic blueprint template; scripts for transcript parsing, context-pack validation, blueprint seed/build/merge and design scaffolding; the Innovation Hub canon (defaults and reference architecture); examples; self-test; MOS3 and personal packages.

**In scope (1.1.0)**: a fifth skill, `frontier-agent-identity`: naming rule, brand palette from the customer's Office theme, icon and card rendering without internet access, validation, stamping into Copilot Studio solutions, pipeline templates, the Caldova identity demo and agent identity in the blueprint.

**In scope (1.2.0)**: the Agent identity page in the blueprint (below Agents), identity names and icons wherever agents appear, and the blueprint and identity kit built in one step (`build_with_identity.py`), with workshop feedback on the identity kept for the review.

**In scope (1.3.0)**: two skills, `frontier-value-case` (value tree, assumption register, NPV, ROI, payback, break-even, sensitivity, workshop merge) and `frontier-finops` (cost per agent in CHF, purchase options, credit-cost scenarios, guardrails, rates file); the blueprint's FinOps page; business value in the use cases and the matrix with the assumptions to clarify in the workshop.

**In scope (1.4.0)**: the blueprint restructured along the Innovation Hub journey (Part 1 Vision, Part 2 Design, Workshop; 14 views); the Agent Factory as a canon journey with DevSecOps; the Attendees page; the landing zone (CAF, WAF, Responsible AI) and architecture decision records in the target architecture; use cases in the Hub business-envisioning template; the IT readiness page; Microsoft product icons; the matching scripts (canon, `--canon`, readiness and ADR merge, design scaffold, identity seed).

**In scope (1.5.0)**: Microsoft's digital feedback loop on the Overview: an animated diagram of the customer's four areas (Engage customers, Optimize operations, Empower employees, Transform products) around Microsoft IQ (Work IQ, Fabric IQ, Foundry IQ, Web IQ), with signals, actions with human approval and measured outcomes per area; its canon (official names and Microsoft sources), derivation from the journeys, build checks, workshop verdicts and discovery questions.

**In scope (1.6.0)**: each agent's workflow on the Agents view, drawn like the Copilot Studio workflow designer (powered by the GitHub Copilot harness): the trigger, the designer's nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent), branches and the desired outcome; derived from the canvas plan until authored (`canvas.workflow`); build checks; each MVP workflow in the solution design.

**Out of scope (1.0)**: see non-goals in A.3; anything requiring access to other people's mailboxes; any automatic sharing outside Microsoft.

## A.7 Functional requirements

Priority: **M** must, **S** should, **C** could. Verified by: **T** automated test (`tools/selftest.py`), **V** validator, **R** review, **D** demonstration.

### Discovery (frontier-context-discovery)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0001 | Find the customer's meetings in a computed window (default 90 days back to the workshop date) from the user's calendar | M | D |
| FR-0002 | Retrieve the transcript of each meeting through its join URL; treat 403/404 as final and record "no transcript" | M | D |
| FR-0003 | Parse transcripts (.vtt, text, .docx, saved JSON) into speaker turns with timestamps and envisioning signals (pain, metric, system, goal, decision, action, risk, idea, stakeholder) in English and German | M | T |
| FR-0004 | Search mail, Teams chats and files for the customer with Work IQ, and public sources on the web; read relevant documents | M | D |
| FR-0005 | Write a context pack in which every fact cites at least one registered source, with timestamp and short quote for transcripts | M | T |
| FR-0006 | Tag every source `internal` or `customer`; render an evidence log for either audience | M | T |
| FR-0007 | Report coverage gaps (journeys without pain or numbers, no systems, no stakeholders, no constraints, no transcript) | M | T |
| FR-0008 | Loop over many meetings or files in one tool script and return a compact table | S | R |

### Blueprint (frontier-blueprint)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0010 | Seed a blueprint from the context pack without inventing content; list every gap in `_todo` | M | T |
| FR-0011 | Render one self-contained HTML file from a JSON blueprint and a generic template | M | T, V |
| FR-0012 | Overview: mission, Frontier phase ladder (today and target), automation level, outcomes, journeys, reading legend | M | D |
| FR-0013 | Org model in the HAIRO style: human leaders in the centre, lead agents in the inner ring, specialist agents in the outer ring, journeys as arcs; step-by-step reveal; filter by journey; autonomy badges; MVP halo; planned positions dashed | M | D |
| FR-0014 | Role card and nine-section role profile for every agent, derived from data where the profile is not written | M | D |
| FR-0015 | Blueprint view per journey: outcomes, hybrid workforce (human-led and agent-operated), approval seam, governance → Intelligence Resources → security and trust, knowledge, channels, build and run, foundation | M | D |
| FR-0016 | Journey view: stages (happens, pain, with agents, owning agent), personas, KPIs with evidence | M | D |
| FR-0017 | Agent view: trigger canvas, the seven declarations with a readiness meter, role profile, live validation (validated, adjust, reject, open) with notes | M | D |
| FR-0018 | Target architecture view: principles, layers 0–7 and approval seams with availability and MVP tags, flows by actor, patterns, decisions, open decisions, grounding | M | D |
| FR-0019 | Use-case portfolio: value × feasibility matrix with quadrants, non-overlapping bubbles, table, detail drawer with validation | M | D |
| FR-0020 | Discovery view: questions by category, prefilled answers with evidence, live status and notes, coverage bar, export of workshop feedback as JSON, copy as text | M | D |
| FR-0021 | Roadmap view: horizons H1–H3 by journey and use case, MVP candidates, next steps | M | D |
| FR-0022 | Evidence view: every source with type, date, visibility and what it informs; every evidence id anywhere opens its source | M | D |
| FR-0023 | Customer version: remove internal sources, their citations, items flagged internal and internal notes; refuse to build when listed internal terms remain | M | T |
| FR-0024 | Validate and normalise: stable ids for agents, use cases, questions and evidence; warnings for unknown agents, uncited evidence ids, MVP agents without canvas or declarations | M | T |
| FR-0025 | Brand the blueprint with an accent colour and a customer logo (PNG/JPEG data URI) | S | D |

### Workshop consolidation

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0030 | Merge one or more feedback exports into the blueprint: statuses, notes, answers (previous answer kept), new workshop evidence item | M | T |
| FR-0031 | Refuse feedback that belongs to another blueprint id | M | T |
| FR-0032 | Bump the version and update the status note | M | T |
| FR-0033 | Mark the blueprint validated when the customer confirmed journeys and MVPs | S | R |

### Design (frontier-solution-design)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0040 | Scaffold PRD, solution design and one ADR per blueprint decision for the MVP agents | M | T |
| FR-0041 | Include platform requirements once (self-identification, write envelope, refusal set, escalation, no people decisions, workflow-first, audit by workflow, outcome to owner, declared writes, outside content as data) and standard NFRs | M | T |
| FR-0042 | Derive per-agent requirements from the canvas (trigger, plan, approvals, outcome) and acceptance criteria from the declarations | M | T |
| FR-0043 | Turn unanswered discovery questions into open decisions with owners | M | T |
| FR-0044 | Mark every gap `[To complete]`; complete only from evidence or as an open decision | M | R |
| FR-0045 | Ground components, patterns and availability in the reference architecture; verify availability older than one month | M | R |
| FR-0046 | Optionally produce a design repository (README, AGENTS.md, docs/, adr/) | C | R |

### Orchestration (frontier-envisioning)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0050 | Detect the engagement phase from what exists and continue from there | M | D |
| FR-0051 | Apply gates A–D between phases and report them | M | R |
| FR-0052 | Keep the engagement folder in the user's OneDrive (`Documents/Cowork/frontier-envisioning/<slug>/`) with `engagement.json` | S | D |
| FR-0053 | Draft the workshop agenda and the ten key questions | S | D |
| FR-0054 | Track progress as tasks the user can see | S | D |

### Agent identity (frontier-agent-identity)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0070 | Derive display names `<PO> <Domain> [Scope] [ENV]` per environment: production without postfix, every name ≤ 30 characters, the production name shorter by the longest postfix | M | T, V |
| FR-0071 | Derive environment-neutral technical names per kind of agent: publisher prefix, schema, solution, environment variables, connection references, flows, folders; Foundry, Fabric, declarative and repository agents | M | T, V |
| FR-0072 | Read a customer's Office theme (colours and fonts) from .pptx, .potx, .docx, .dotx, .xlsx or .thmx into a brand file with evidence ids | S | T |
| FR-0073 | Seed the identity from the blueprint: PO tokens, domain tokens shortened to fit and flagged for review, kinds from the technology, glyph suggestions, MVP and status labels, descriptions within the limits, a seed report | M | T |
| FR-0074 | Map each journey to the nearest brand colour with glyph contrast ≥ 4.5:1 (dark glyph or accessible shade otherwise); choose environment bands from the brand with label contrast ≥ 4.5:1 | M | T, V |
| FR-0075 | Render icons without a browser or image library: colour 192 × 192 and 32 × 32 per environment, outline 32 × 32, SVG sources; identical pixels on every machine | M | T |
| FR-0076 | Generate identity cards, the agent family, the MVP identity sheet, the colour schema (SVG; PNG when a converter exists) and an HTML catalogue | S | D |
| FR-0077 | Generate the kit's documents (naming convention, colour schema, icons, harness integration, catalogue, evidence), README, changelog, notices and GitHub Copilot instructions from the config | M | T |
| FR-0078 | Validate the kit (names, technical names, uniqueness, prefix, descriptions, contrast, files) and fail pull requests on errors | M | T |
| FR-0079 | Stamp names and icons per environment into an unpacked Copilot Studio solution before packing; dry run by default; strict mode for release pipelines | M | T |
| FR-0080 | Ship Azure Pipelines and GitHub Actions templates and unit tests that build a synthetic solution | S | T |
| FR-0081 | Write the identity into the blueprint; the blueprint shows icons and display names in the journey view, the agent canvas and the role card | S | T |
| FR-0082 | Build the Caldova identity kit demo on request | S | D |
| FR-0083 | Show an Agent identity page below Agents: naming rule, journey colours, environment bands, agent family, MVP identity sheet, all names per environment with a length check, decisions, Microsoft guidance and a workshop validation box | M | T |
| FR-0084 | Use the identity display name and icon wherever an agent appears (agent list and canvas with an identity panel, role card, journeys, org model, use cases, roadmap MVP cards, blueprint view); keep the working name visible | M | T |
| FR-0085 | Build the blueprint and the identity kit in one step: seed the identity proposal (customer Office theme when given), build and validate the kit, write the identity into the blueprint and render the HTML; if the kit fails, build the blueprint alone and say why | M | T |
| FR-0086 | Keep workshop feedback from the Agent identity page in the blueprint (`identity_feedback`) for the identity review | S | T |
| FR-0087 | Value tree per use case with drivers (efficiency, quality, revenue, strategic) and categories (cash, capacity, risk, revenue); each benefit counted once | M | T |
| FR-0088 | Assumption register: statement, unit, low, base, high, source type, confidence, evidence ids, owner, question, status; empty values listed as inputs to collect, never invented | M | T |
| FR-0089 | Calculate budget and economic views, risk separately, NPV, ROI, payback, break-even, sensitivity (top ten assumptions as workshop questions) and ranges | M | T |
| FR-0090 | Cost per agent and month in CHF: credits by event with licence coverage, licences, Azure, people, build; unit economics | M | T |
| FR-0091 | Compare pay-as-you-go, capacity packs, Copilot Credit P3 and Agent P3; credit-cost scenarios; guardrails with owners; tags from the agent identity | M | T |
| FR-0092 | Versioned rates file with source and date per rate; flag rates older than 90 days | M | T |
| FR-0093 | Blueprint: FinOps page; business value in the use cases and the matrix; live confirm, adjust or reject of assumptions with the agreed value, exported with the workshop notes | M | T |
| FR-0094 | Merge assumption verdicts into the value case and the FinOps model with a change log and a version bump | M | T |
| FR-0095 | Reproduce the method's worked example exactly (golden test) | M | T |

### Distribution and installation

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0060 | Install from a Cowork chat: the user attaches the package and says "Install the Frontier PlugIn"; Cowork checks the package and copies the seven skills into the user's skills folder after one approval | M | T, D |
| FR-0061 | Refuse a damaged or altered package: checksum per file, skill names, unexpected files | M | T |
| FR-0062 | Report per skill whether the install is new, an update or a reinstall, from the installed version | S | T |
| FR-0063 | One package serves both the chat install and the organisation catalogue (Microsoft 365 app package) | M | V |
| FR-0064 | Build the Caldova demo blueprint on request, without customer data | S | D |
| FR-0065 | A README setup guide in the package: steps for people and exact steps for Copilot Cowork | M | R |

### Innovation Hub journey (1.4.0)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0096 | The blueprint follows the Innovation Hub journey: Part 1 Vision (Overview, Org model, Blueprint, Journeys, Attendees), Part 2 Design (Agents, Agent identity, Target architecture, Use cases, IT readiness, FinOps), Workshop (Discovery, Roadmap, Evidence) | M | T, D |
| FR-0097 | Attendees page: people by organisation with role, place, focus and contributions; focus links open the journey or use case | M | D |
| FR-0098 | Agent Factory journey from the canon: lifecycle hypothesis → validated → designed → ready for build → build → release → operate; board computed from eight handover checks (Definition of Ready); build steps with tools, Superpowers and CAT skills; evaluation pyramid; controls, roles, phases, resources | M | T, D |
| FR-0099 | Landing zone tab: CAF design areas with product icons, WAF, CAF and Responsible AI lenses, one agent landing zone per journey with DEV, TEST and PROD stage, data classes, MVP marker and identity icons; a click opens the area's detail | M | D |
| FR-0100 | Decisions tab: ADR cards with canon flag, status filter and a live workshop verdict exported as `adr:<id>` and merged into the decision | M | T |
| FR-0101 | Use-case detail page in the Hub template (General with the problem statement and its provenance, Value, Feasibility), deep link `#/usecases/<id>` | M | D |
| FR-0102 | IT readiness page: preparation items, readiness checks, workstation, questions, decisions, environments, timeline; live status exported as `ready:<id>` and merged | M | T |
| FR-0103 | Microsoft product icons embedded only when used, with their notice; `--no-product-icons` leaves them out | M | T |
| FR-0104 | Canon added without overwriting (a canon ADR is skipped when its title exists); `build_blueprint.py --canon` upgrades an earlier blueprint | M | T |
| FR-0105 | The design scaffold adds the landing zone, the Agent Factory lifecycle, Definition of Ready and evaluation pyramid, the ADR origin and `it-readiness.md` | M | T |
| FR-0106 | The identity seed treats Agent Factory agents as repository agents with the process-owner token "Factory" | S | T |

### Digital feedback loop (1.5.0)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0107 | The Overview shows Microsoft's digital feedback loop as an animated diagram: the four areas (Engage customers, Optimize operations, Empower employees, Transform products) around Microsoft IQ with Work IQ, Fabric IQ, Foundry IQ and Web IQ; signals travel to Microsoft IQ, a proposed action waits at a human-approval gate, the measured outcome returns as the next signal | M | T, D |
| FR-0108 | Selecting an area shows its signals with their Microsoft IQ layer, its actions with the agents and who approves, its outcomes with the journey KPIs (baseline → target) and the value hypotheses, the linked journeys and use cases, a workshop question and a live verdict exported as `loop:<area>` and merged | M | T |
| FR-0109 | The canon derives the loop from the journeys (area by keyword, signals from the systems with their Microsoft IQ layer, actions from the agents and the approval seam, outcomes from the KPIs, MVP use cases); every build completes a linked area without overwriting | M | T |
| FR-0110 | Only official Microsoft names: the build warns about any other "… IQ" name, an unknown layer, area or journey; the canon carries the Microsoft sources | M | T |
| FR-0111 | The animation can be paused, stops when the device asks for reduced motion and is hidden in print; diagram and panel carry the same content as text | M | T, D |
| FR-0112 | Discovery collects what the loop needs: questions per area in the question bank and a signals recipe in the Work IQ playbook | S | R |

### Agent workflow (1.6.0)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FR-0113 | Every agent with a canvas plan shows its workflow under the trigger canvas, drawn like the Copilot Studio workflow designer: the trigger (Manual, Recurrence, Connector event, When an HTTP request is received, When an agent calls the workflow), the designer's nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent) and the desired outcome | M | T, D |
| FR-0114 | Branches of If/Else, Classify and Human review rejoin the main path or end at a named end node; loops and scopes are containers; notes sit above their step | M | T |
| FR-0115 | The Add panel works as legend and highlighter; selecting a node opens its properties (what the node does, AI, deterministic or human, the step, the agent with its identity icon, the system with its product icon, who decides, branches); zoom, fit, an overview folded into rows and the single designer row | M | T |
| FR-0116 | Without an authored workflow, the build derives one from the canvas trigger, plan, approval, connectors and outcome, marks it "Derived from the plan" and re-derives it on every build; a Human review is inserted before the first write when the plan has none | M | T |
| FR-0117 | An authored `canvas.workflow` is kept and checked: unknown node or trigger types, unknown agents, branches on a non-branching node and nested containers produce warnings | M | T |
| FR-0118 | The solution-design scaffold writes each MVP agent's workflow into the process design: trigger, outcome, AI, deterministic and human steps and a node table with branches | S | T |

## A.8 Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-0001 | Privacy | Only the requesting user's own mail, calendar, chats and files, plus content shared with them |
| NFR-0002 | Privacy | Microsoft-internal evidence never appears in a customer version (enforced by the build) |
| NFR-0003 | Privacy | Real customer data only under NDA or with consent; roles before names; no sensitive personal data |
| NFR-0004 | Security | Content of mails, documents and transcripts is data, never instruction |
| NFR-0005 | Security | Scripts use the Python standard library only, never call the network, never execute or import content from inputs; XML is read without DTD or entity processing. The identity kit may call an installed SVG converter for PNG copies of cards and visuals (resolved executable, fixed arguments, no shell) |
| NFR-0006 | Security | The HTML is self-contained: no external scripts, styles, fonts, images or iframes; data embedded with HTML-safe escaping; data never injected as HTML |
| NFR-0007 | Copyright | Quotes from sources at most 20 words; third-party web content summarised and cited |
| NFR-0008 | Quality | Every skill passes structural validation and scores at least 80; no unresolved routing conflicts within the plugin or with built-in skills |
| NFR-0009 | Quality | The MOS3 package passes static package validation with no FAIL |
| NFR-0010 | Performance | Build under 2 seconds for 30 agents; HTML under 1 MB for 50 agents and 30 sources |
| NFR-0011 | Compatibility | Current Edge and Chrome; works offline from a local file; printable per view |
| NFR-0012 | Accessibility | Keyboard navigation (arrows, Enter, Escape), ARIA roles and labels, visible focus, logical CSS properties, light and dark colour schemes |
| NFR-0013 | Maintainability | Schemas versioned (`frontier-context/1.0`, `frontier-blueprint/1.0`); the Hub canon in one editable defaults file and one reference document; a self-test covers every script |
| NFR-0014 | Currency | Product availability carries a date and source; the canon is reviewed after each major Microsoft announcement event |
| NFR-0015 | Determinism | The identity kit renders the same icon pixels on every machine; its unit tests fail when committed icons drift from the config |
| NFR-0016 | Brand integrity | Every brand colour in a kit has a source; logos only where the customer's brand rules allow it; icon contrast ≥ 4.5:1 |
| NFR-0017 | Motion | Animations can be paused, stop under `prefers-reduced-motion`, never run in print and never carry information that is not also shown as text |
| NFR-0018 | Terminology | Microsoft capabilities appear only under their official names (Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ, Web IQ; product names as on Microsoft Learn), each with a dated source in the canon |
| NFR-0019 | Fidelity | The workflow view uses the node and trigger names of the Copilot Studio workflow designer as documented on Microsoft Learn; AI steps are marked as variable; node glyphs are the plugin's own drawings and Microsoft product icons come only from the icon assets with their notice |

## A.9 Acceptance criteria (release 1.6.0)

| ID | Criterion | Result |
|---|---|---|
| AC-001 | `tools/selftest.py` passes all 34 checks | Passed |
| AC-002 | The Caldova example builds with no errors and renders all fourteen views without script errors | Passed (headless DOM test of every view, drawer and journey tab) |
| AC-003 | The template and a built blueprint pass the HTML validator with no errors or warnings | Passed |
| AC-004 | The customer build removes the two internal Caldova sources and every citation of them | Passed |
| AC-005 | Every skill validates and scores ≥ 80; the conflict scan reports no unresolved conflict | Passed (96–100; 21 internal pairs and 1 built-in pair resolved by delegation) |
| AC-006 | The security scan passes with no findings | Passed |
| AC-007 | The install package passes static Microsoft 365 package validation | Passed (one expected warning: builder metadata, see TD-04) |
| AC-008 | The install check passes on the released package and refuses an altered copy | Passed (build → extract → check → alter → check) |
| AC-009 | The Caldova identity kit builds for 33 agents with the validator at 0 errors and all kit unit tests passing | Passed |
| AC-010 | Icons from the built-in renderer match a reference SVG renderer | Passed (mean absolute difference below 0.02 of 255 per channel at 192 × 192) |
| AC-011 | A blueprint with identity renders every view without script errors and shows the icons in the journey, agent and role-card views | Passed (headless DOM test) |
| AC-012 | The Agent identity page renders for the Caldova demo, a seeded proposal, the customer version and a 1.1.0 blueprint without the page data; a blueprint without identity hides the page | Passed (headless DOM test) |
| AC-013 | One build produces the blueprint HTML and a validated identity kit, both seeded without a brand file and from the reviewed Caldova config | Passed (self-test and demo build) |
| AC-014 | The scripts reproduce the worked example of the value and FinOps method (credits, purchase options, scenarios, NPV, ROI, payback, break-even) | Passed (self-test) |
| AC-015 | The Caldova blueprint shows the FinOps page and business value in the use cases and the matrix; an assumption verdict is saved and exported | Passed (headless DOM test) |
| AC-016 | The Caldova demo shows the Attendees page, the Agent Factory (lifecycle, board, handover, steps, roles), the landing zone, the ADRs, a use-case detail page and the IT readiness page without script errors | Passed (headless DOM test) |
| AC-017 | The landing-zone diagram lays out the journeys without overlapping or clipped titles | Passed (diagram rendered to an image and reviewed; Caldova, four business journeys and the factory) |
| AC-018 | Workshop verdicts on readiness items and ADRs merge into the blueprint; unknown ids are reported, never invented | Passed (self-test) |
| AC-019 | A blueprint from release 1.3 built with `--canon` gains the factory journey, landing zone, canon ADRs and IT readiness | Passed (self-test) |
| AC-020 | The Overview of the Caldova demo shows the digital feedback loop: four areas, the four Microsoft IQ layers, sixteen animated movements, the panel follows the selected area, the animation pauses and a verdict is saved | Passed (headless DOM test) |
| AC-021 | A blueprint with an unofficial "… IQ" name, an unknown layer or an unknown area builds with a warning for each | Passed (unit test and self-test) |
| AC-022 | The Caldova demo shows the two MVP workflows: the trigger first and the outcome last, nodes in flow order for the keyboard, branch pills, the end node, notes, the agent identity icon; properties open with a click or Enter and close with Escape or the close button; Add highlights a node type; zoom and the designer row work; an agent without a plan says so | Passed (headless DOM test) |
| AC-023 | A missing workflow is derived from the plan (trigger type, node types, Classify categories, a Human review before the first write); unknown node types and agents warn; derived workflows follow a changed plan | Passed (unit tests and self-test) |
| AC-024 | The solution design lists each MVP workflow with its trigger, outcome, step counts and node table | Passed (unit test and self-test) |
| AC-025 | The workflow overview of the Caldova MVP agents fits the page width (at most 1,018 pixels at 100 %) without overlapping nodes, and the designer row keeps the branches on lanes below | Passed (diagrams rendered to images and reviewed) |

## A.10 Dependencies and assumptions

| Dependency | If missing |
|---|---|
| Copilot Cowork with Microsoft 365 tools: calendar, transcripts, Microsoft 365 search, Teams, OneDrive | Discovery falls back to attached files and public sources, flagged |
| Meeting transcription enabled for customer meetings, with participants informed | Discovery uses chats and notes; transcript-based evidence is missing |
| The user can share real data only under NDA | The blueprint stays a hypothesis on public and internal context |
| Python sandbox in Cowork for the scripts | The skills cannot build; nothing is published |
| A modern browser to present | The OneDrive web preview shows the file as text; open locally |
| The user's approval to write to their skills folder (`Documents/Cowork/skills`) | Nothing is installed; the five folders can also be copied there by hand |
| Customer brand sources (brand guide, customer-authored Office file, website) | The identity kit uses the blueprint colours and flags them (decision N-5) |
| An SVG converter (cairosvg, rsvg-convert or Node.js with sharp) | Identity cards and visuals stay SVG; icons are unaffected |

## A.11 Risks

| Risk | Mitigation |
|---|---|
| Naming confusion: "Frontier Company Blueprint" versus Microsoft's "Frontier Firm", "Frontier Suite", "Frontier program" and the services unit "Microsoft Frontier Company" | Naming note in the method; open decision D-01 |
| Product names and availability change (announcement events) | Dated availability, "verify" marker, canon review cadence (NFR-0014) |
| Internal context leaks into customer material | Visibility on every source; customer build gate; internal-term check |
| Transcripts used without the participants' knowledge | Use only meetings the user organised or attended; Teams transcription notice; NDA status in Frame |
| Over-automation: agents proposed where rules belong | Workflow-first test in the authoring guide; declarations; autonomy one level lower to start |
| Workshop notes lost (browser storage) | Export button on every view's validation; merge script; facilitator exports per block |
| Skill routing collides with built-in skills (meeting recap, HTML, documents) | Explicit exclusions and delegations; conflict scan in the release checklist |
| Agent names decided by the plugin instead of the process owners | Names are proposals; the seed flags every shortened name; decisions N-1 to N-6 with owners |
| Brand colours or logos used without the customer's consent | A source per colour; logos only with brand-rule permission; validation with the brand owner (N-5) |
| Microsoft limits for names, descriptions or icons change | Limits held in one place in the kit, dated sources in `docs/evidence.md`; the validator enforces them |

## A.12 Release plan

| Release | Content |
|---|---|
| 1.0 | Four skills, template, scripts, canon, examples, self-test, packages |
| 1.0.1 | Caldova demo data; one package for the chat install and the organisation catalogue; README setup guide; install check |
| 1.1.0 | Agent identity kit (frontier-agent-identity): naming convention, brand colours, Microsoft 365 icons, cards, catalogue, validate and stamp scripts, pipeline templates; identity shown in the blueprint |
| 1.2.0 | Agent identity page below Agents; identity names and icons wherever agents appear; blueprint and identity kit built in one step; identity feedback kept for the review |
| 1.3.0 | Business value (frontier-value-case) and FinOps (frontier-finops): value tree, assumption register, NPV and ROI in CHF, cost per agent, purchase options, guardrails; FinOps page; value in the use cases and the matrix with workshop verdicts |
| 1.4.0 | Innovation Hub journey structure: Part 1 Vision with the Agent Factory journey (DevSecOps, GitHub Copilot harness, CAT skills) and the Attendees page; Part 2 Design with the landing zone (CAF, WAF, Responsible AI), ADRs, use cases in the Hub template and the IT readiness page; Microsoft product icons; design scaffold and merge for readiness and ADRs |
| 1.5.0 | Digital feedback loop on the Overview: the customer's four areas around Microsoft IQ (Work IQ, Fabric IQ, Foundry IQ, Web IQ), animated signals, actions with human approval and measured outcomes; canon with official names and sources, derivation from the journeys, build checks, `loop:` verdicts, discovery questions |
| 1.6.0 (this release) | Agent workflow in the Copilot Studio workflow designer style: trigger, designer nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent), branches and the desired outcome per agent; derived from the canvas plan until authored; build checks; workflow tables in the solution design |
| 1.7 | Operate loop: plan versus actual from the Copilot Studio licensing reports, Microsoft 365 credit reports and Cost Management FOCUS exports; value and FinOps cockpit in Power BI; monthly digest. HubWorks integration (engagement contract, closeout pack, agenda blocks); German template labels; slide export of selected views through the pptx agent; Copilot Studio prototype pack (agent instructions and topics from the canvas, the workflow from `canvas.workflow`) |
| 1.8 | FOCUS 1.5 alignment (agent as principal, consumption currency); Agent 365 cost data; shared engagement folder on a Hub SharePoint site; feedback capture into a Microsoft List for multi-facilitator workshops |
| Later | A `frontier-diagrams` capability (editable architecture, landing-zone and factory diagrams from the blueprint and the agent definitions, official icon sets); see the visualisation and reuse evaluation |
| 2.0 | Work IQ APIs for richer context retrieval; Agent 365 registry export of validated agents; usage telemetry for the success measures |

## A.13 Open decisions

| ID | Decision | Owner |
|---|---|---|
| D-01 | Keep the name "Frontier Company Blueprint", or rename to "Frontier Firm Blueprint" to avoid confusion with Microsoft Frontier Company | Hub leadership |
| D-02 | Distribution: personal skills per engineer, or the organisation catalogue (MOS3) | Hub leadership, tenant admin |
| D-03 | Where engagement folders live: personal OneDrive or a Hub SharePoint site (sharing, retention) | Hub leadership |
| D-04 | Branding of customer versions: Microsoft only, or co-branded with the customer's logo and colour | Hub leadership |
| D-05 | Ownership and cadence of canon updates (defaults and reference architecture) | Hub solution engineering |
| D-06 | Defaults of the agent identity kit for Hub engagements: environment set, kinds, whether the Hub proposes the publisher prefix | Hub solution engineering |
| D-07 | Replace the product icons copied from presentation material with the official Microsoft icon sets; who maintains them | Hub solution engineering |
| D-08 | Whether the canon recommends one engineering control plane (GitHub or Azure DevOps) or keeps both open per customer | Hub solution engineering |

---

# Part B — Solution Design

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

- **Canon maintenance.** After each major Microsoft announcement event, the owner (D-05) reviews `frontier-reference-architecture.md` and `blueprint-defaults.json`, updates availability with dates and sources, bumps the minor version, runs the self-test and rebuilds the packages.
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

# Appendix — File inventory (1.6.0)

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
