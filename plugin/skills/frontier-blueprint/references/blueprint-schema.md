# Blueprint JSON reference (frontier-blueprint/1.0)

*Copilot AI-assisted procedure maintenance, 24 November 2026; original authorship retained.*

Every field is optional unless marked required. Missing fields render as "To be confirmed". Unknown fields are kept but not shown. `src` is always a list of evidence ids.
Financial inputs and generated reports follow the stricter contracts below;
optional Blueprint fields never supply default prices, quantities or approval.

## parts (four-part journey; optional views)

Vision: Overview, Org model, Blueprint, Journeys, Use cases, PRD.
Design: Agents, Agent identity, Target architecture, IT readiness, optional Ontology.
Build: Roadmap, Plan, optional Preview FinOps. Workshops: Attendees, Discovery, Risks, Evidence.
Views whose optional data is absent may be hidden; existing routes remain usable.
`parts` overrides labels and one-line purposes:
`{"vision": {"label": "Part 1 · Vision", "desc": "…"}, "design": {"label": "Part 2 · Design", "desc": "…"}, "build": {"label": "Part 3 · Build", "desc": "…"}, "workshops": {"label": "Part 4 · Workshops", "desc": "…"}}`.

## meta (required: customer)

| Field | Meaning |
|---|---|
| id | Stable blueprint id (default: customer slug + "-frontier"); the workshop feedback is tied to it |
| customer, short | Legal and short name |
| eyebrow, headline, subtitle | Header texts |
| engagement, prepared_by, presenter | Cover texts |
| workshop_date, location | Shown in the banner |
| status | hypothesis (default) or validated |
| status_note | Replaces the default banner sentence |
| audience | internal or customer (set by the build) |
| internal_terms | Strings that must not appear in a customer version (build refuses) |
| version, date | Version label; feedback merges bump it |
| accent | #RRGGBB accent colour |
| logo_data_uri | PNG/JPEG/GIF/WebP base64 data URI provided by the customer |
| domain_label, domain_label_plural | "Journey"/"journeys" by default; "Pillar"/"pillars" etc. |
| center_label | Centre label of the org model (default "Human-led") |
| summary, footnote | Overview lead text, footer |

## mission, frontier, outcomes

- `mission`: `{label, statement, attribution, prompt, src}`
- `frontier`: `{current_phase 1-3, target_phase 1-3, automation_current 1-3, automation_target 1-3, note, src}`; phases follow the Work Trend Index (human with assistant, human-agent teams, human-led agent-operated); automation levels follow Microsoft's traditional, digital, agentic process automation.
- `outcomes`: `[{name, desc, src}]`, `measured_by`: text
- `human_led`: `{Direction, Accountability, Judgement, Relationships}`; `approval_seam`: text

## feedback_loop (Part 1 > Overview: digital feedback loop)

Microsoft's digital feedback loop for the customer, drawn as an animated diagram on the Overview: four areas around Microsoft IQ. Each area sends **signals** to Microsoft IQ, receives a proposed **action** that a person approves, and returns a measured **outcome**, which becomes the next signal. `canon.py` adds it (seed, `build_blueprint.py --canon`) with every business journey mapped to one area; each build completes empty lists of a linked area from its journeys (systems, agents, KPIs, MVP use cases) and never overwrites.

| Field | Meaning |
|---|---|
| heading, intro, note | Section heading, lead text and a note under the panel |
| center | `{name: "Microsoft IQ", tagline}` |
| iq | `[{id: work/fabric/foundry/web, name, desc, products[]}]`: the four Microsoft IQ layers (Work IQ, Fabric IQ, Foundry IQ, Web IQ); `products` adds the Microsoft product icons |
| approval | Text of the approval band in the centre ("Human approval before every action") |
| trust | `[{name, logo}]`: Microsoft Entra, Microsoft Purview, Microsoft Agent 365 |
| flow | Five legend labels (signal, Microsoft IQ, proposed action, human approval, measured outcome) |
| ring | `{label, caption}` of the outer loop |
| animation_note | Replaces the default sentence that explains the animation |
| quadrants | `[{pillar, journeys[], title, signal, action, outcome, summary, signal_type, signals[], actions[], outcomes[], use_cases[], question, status, src[], workshop_notes[]}]` |
| sources | `[{title, url}]` Microsoft sources (https only) |
| status, src, derived | Hypothesis status, evidence, `true` when the canon derived it |

- `pillar` (one area each; the official names of the four areas): `engage_customers` (Engage customers, customer signal), `optimize_operations` (Optimize operations, operational data), `empower_employees` (Empower employees, employee signal), `transform_products` (Transform products, product telemetry). A missing area is drawn as "To be discovered".
- `signal`, `action`, `outcome`: the short lines on the diagram card (default: the first item of the list).
- `signals[]`: `{text, iq[] (work, fabric, foundry, web), type, src[]}`: what is observed and through which Microsoft IQ layer.
- `actions[]`: `{text, agents[] (agent ids or names), approval, src[]}`: what agents propose and who approves.
- `outcomes[]`: `{text, kpi (a KPI name of a linked journey: baseline and target are shown), journey, assumptions[] (value-case assumption ids, shown with their workshop status), src[]}`.
- Only official Microsoft names: Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ, Web IQ. The build warns about any other "… IQ" name, an unknown layer or area, or an unknown journey.
- Workshop verdicts arrive as `loop:<pillar>` (status and notes of the area).

## leaders (centre of the org model)

`[{id: "L1", role, short, initials (max 3 letters), name (optional), direction, decides, accountable_for: ["D1"]}]` (1 to 7)

## domains (required: at least one)

| Field | Meaning |
|---|---|
| id, name, short_name, color | D1 …, display name, label on the arc, #RRGGBB |
| leader | Leader id who is agent boss for the lead agent |
| journey_name, journey_tagline, vision, ai_contribution, business_impact | Journey header |
| stages | `[{name, happens, pain, ai, agent (agent name), src}]` |
| personas | `[{role, kind: Internal/External/Approver, goal, pain, help, decides, src}]` |
| orchestrator | Lead agent (agent fields below plus mission, memory, planning, goals) |
| agents | Specialist agents |
| data_agent | `{name, products: []}` |
| systems | List of system names |
| channels | `{people: [], triggered: []}` |
| outcomes, measured_by, human_led, approval_seam | Journey-level overrides |
| kpis | `[{kpi, definition, baseline, target, src}]` |
| horizon_plan | `{H1, H2, H3}` texts |
| discovery | `{"Business & process": [{id, q, why, status: open/partial/answered, answer, src}], …}` |
| use_cases | `[{id, name, horizon, wave, value 1-5, feasibility 1-5, mvp, status, agents: [names], problem, idea, kpis, dependencies, risks, src}]` |

## agent (lead and specialist)

| Field | Meaning |
|---|---|
| id | D1-A01 … (lead: D1-LEAD) |
| name, alias, short | Display name; optional persona name; ring label |
| capability | One sentence |
| autonomy, autonomy_level | Text and/or 1-3 (Assist / Act with approval / Act within guardrails) |
| horizon | H1, H2, H3 |
| lifecycle | Planned, Prototype, Pilot, Active, Upskilling, Retired |
| status | hypothesis, validated, adjusted, rejected, open |
| mvp | true or a label ("MVP candidate A") |
| owner | Agent boss (role) |
| trigger, outcome, channels, technology, pattern | Role card fields |
| canvas | `{trigger[], instructions, plan[], outcome, data_sources[], connectors[], approval[], autonomy, skills[], pattern, build, workflow}`; `workflow` see below |
| declarations | `{write_envelope, refusal_set, escalation_path, grounding_sources, data_classification, people_decisions, measurement}` |
| profile | Nine sections: `starting_point, contribution, impact, mission, trigger, input, output, tasks[], reports_to, works_with[], hands_off_to, autonomous, approval, escalation, knowledge[], rules[], not_allowed[], systems[], channels[], tone, language, kpis[]` |
| workshop_notes | Added by merge_feedback.py |
| internal | true removes the item from customer versions |

### canvas.workflow (Agents > Workflow, plugin 1.6)

The agent's plan as a **Copilot Studio workflow** (the workflow designer, powered by the GitHub Copilot harness): one trigger, typed steps (the designer's nodes), branches that rejoin or end, and the desired outcome. Drawn full width under the trigger canvas, dark like the maker canvas. Without an authored workflow, `workflow.py` derives one from `canvas.trigger`, `canvas.plan`, `canvas.approval`, `canvas.connectors` and `canvas.outcome` on every build (`"derived": true`, shown as "Derived from the plan"); author it to take control.

| Field | Meaning |
|---|---|
| name, status | Workflow name; `draft` (default) or `published` |
| trigger | `{type, label, detail, system}`; `type`: `manual` (Manual), `recurrence` (Recurrence), `connector` (Connector event), `http` (When an HTTP request is received), `agent` (When an agent calls the workflow). Unknown types warn; a missing type is read from the label |
| steps | `[{type, label, detail, agent, system, approver, defaults[], branches[], steps[], note}]` in order |
| outcome | The desired outcome (default: `canvas.outcome`) |
| src, derived | Evidence; `true` when derived from the plan (re-derived on each build) |

- Step `type`: `agent` (calls an agent; `agent` names it by id), `classify` (routes to categories), `extract` (returns defined fields and tables from documents), `copilot` (Microsoft 365 Copilot, Researcher, Analyst or Cowork), `human_review` (approval or request for information; `approver` names who decides), `connector` (an action in a connected system; `system` names it, its icon is shown), `function` (code), `variable`, `if_else` (condition), `loop` and `scope` (containers with `steps[]`), `respond` (Respond to the agent, for workflows an agent calls) and `note` (an annotation). Aliases such as `If/Else`, `Human review`, `approval`, `for each` are accepted.
- AI steps (Agent, Classify, Extract, Copilot) are marked "results can vary"; Connector, Function, Variable, If/Else, Loop, Scope and Respond are deterministic; Human review is a person.
- `defaults[]`: the paths that continue on the main path (If/Else: `["Yes","No"]`-style; Classify: the categories; Human review: `["Approved"]`-style).
- `branches[]`: `{label, steps[], then: continue|end, end}`; a branch with `then: "end"` (or an `end` label) stops at an end node named by `end`; otherwise it rejoins the next step. Only If/Else, Classify and Human review branch.
- `note`: a sticky note above the step. Ids `n1, n2, …` are added by the build.
- The build warns about unknown node or trigger types, unknown agents, branches on a non-branching node, nested containers (drawn flat) and an empty workflow.

## Shared blocks

`governance.items[]`, `intelligence_resources {title, subtitle, lifecycle[], agent_file[], runs_on[]}`, `security[]`, `knowledge[] (scope: internal/external/principle)`, `build_run[]`, `foundation[]`, `horizons[] {h, label, meaning}`.

## architecture

`{title, intro, src, principles[{name, desc}], layers[{name, purpose, blocks[{name, desc, status, tag, kind: agent/workflow/control/system}]}], flows[{name, note, steps[{actor: human/workflow/agent/system, text}]}], patterns[{pattern, where, why}], decisions[…], open_decisions[{id, question, owner}], landing_zone{…}, sources[]}`

**decisions (ADRs)**: `[{id, title, status: proposed/agreed/adjusted/rejected, context, decision, rationale, alternatives, consequences, areas[] (landing-zone area letters), canon: true for Innovation Hub canon ADR-F01…, workshop_notes, src}]`. Shown under Target architecture > Decisions with a workshop verdict (`adr:<id>`; validated becomes agreed).

**landing_zone** (added by the canon; Target architecture > Landing zone):

| Field | Meaning |
|---|---|
| title, intro, caption | Texts above the diagram |
| principles | `{waf|caf|rai: {short, name, items[[key, name, meaning]]}}`; the lens buttons highlight the areas whose `applies` has the key |
| classes | `[[id, label, colour, rule]]` data classes (public, internal, confidential, restricted) |
| stages | `{now, next, later}` labels for the environment stage pills |
| areas | `{A, B, C, D1-D4, E, G, H, I, J, R, X, P, D, F: {letter, title, label (short diagram title), sub, logos[] (product icon keys), bullets[], applies{key: text}}}` |
| lz | One agent landing zone per business journey: `[{id: F1…, domain: D1…, stages {DEV, TEST, PROD: now/next/later}, classes[], mvp: false or a label}]` |
| common, sources | Shared rules; https links |

## attendees (Part 4 > Attendees)

`{title, intro, date, place, note, src[], people[{name, role, org (the customer's short name or "Microsoft"), where (on site, remote), team, focus[], contributions[], quote, sessions[], src[]}]}`.
Focus values link journey names/short names/IDs and use-case names/IDs.
A contribution is `{text, src[], at}`: statement, evidence IDs and transcript
time (`"01:42:10"`). Plain sentences remain accepted, falling back to the
person's `src`. `sessions` lists session evidence IDs (defaults to `src`).
The build flags missing evidence and counts `contributions_with_evidence`.
The seed uses named stakeholders and transcript facts with
`facts[].evidence[].speaker`; names require agreement, otherwise use roles.

## prd (Part 1 > PRD)

The build's `scripts/prd_model.py` and the identical solution-design copy derive
the page, Markdown download and `design/prd.md` from one canonical model.

- Authored, retained fields: `title`, `status` (hypothesis, draft, agreed,
  adjusted, rejected), `owner`, `version`, `problem`, `goals[]`, `non_goals[]`,
  `out_of_scope[]`, `exit_test`, `release_plan[[phase, scope, exit criterion]]`,
  `notes`, `src[]`, `workshop_notes[]`, `internal`.
- Derived fields include `basis`, `mvp_agents[]`, `vision`, `commitments`,
  `maturity`, `scope[]`, `use_cases[]`, `problems[]`, `personas[]`, `platform[]`,
  `agents[{agent, requirements[{id, kind, text, priority, verify}], declarations}]`,
  `nfr[]`, `acceptance[]`, `kpis[]`, `roles`, `dependencies[]`, `risks[]`,
  `decisions[]`, `definition_of_ready[]`, `release_plan_default`.
- Requirement IDs use the complete blueprint's canonical agent order before
  selection; `--mvp` subsets retain surviving IDs, not a new local sequence.
  These customer-MVP IDs are not plugin-product requirement IDs.
- Workshop verdict: `prd:scope` (validated maps to agreed). Owner/status and
  Definition of Ready text are metadata, not execution approval.

## risks (Part 4 > Risks)

`{title, intro, src[], source_ids{}, items[{id, title, description, category,
likelihood, impact, owner, mitigation, status, journeys[], use_cases[], agents[],
src[], content_src[], source_key, canon, origin, derived, workshop_notes[],
resolution}]}`.

Categories: value, adoption, data, security, rai (Responsible AI), technology,
cost, delivery, people. Status: open, mitigating, accepted, closed. Likelihood
and impact must be finite integers 1-5, excluding booleans; score is their
product, high from 15 and medium from 8. Invalid authored values warn (strict
mode fails); invalid feedback reports without silently changing ratings.

`risks.py` derives use-case `risk_points` (sentences or
`{text, likelihood, impact, owner, mitigation, category}`), blocked readiness
items and canon `risk_canon`, retaining authored/workshop risks. Unknown
categories, statuses and links warn. Initial IDs use `R-01`… for authored,
`R-<use case>-<n>` for use-case points, `R-<item id>` for readiness and `R-C01`…
for canon. Normalised `source_ids` binds source keys to IDs and retains retired
IDs. Each bound record carries `source_key`; source edits/reordering reserve
old identities instead of applying old verdicts to new content.

Keep that normalised history with feedback. Discarding source bindings and
retired-ID history cannot guarantee old ID-only feedback identity.
`risk:<id>` carries status, likelihood, impact and note; a rated risk becomes
workshop-owned (`derived: false`). Rejected closes it as `resolution: "not a risk"`.
Unknown IDs are reported. `content_src` preserves the content's evidence
independently of a later workshop verdict; a verdict does not declassify it.

## factory (Agent Factory journey and DevSecOps)

The canon adds one domain with `kind: "factory"` (id `D<n>`, lead and five specialists, short name "Factory") and this block:

| Field | Meaning |
|---|---|
| lifecycle | `[{id, name, what, gate, icons[]}]`: hypothesis, validated, designed, ready for build, build, release, operate |
| handover | Definition of Ready: `[[check id, meaning]]` (validated, canvas, declarations, identity, value, cost, readiness, owner) |
| steps | `[{id, name, loop: plan/build/verify/release/operate, what, agent, tools[[icon key, text]], gate, evidence, superpowers, cat[], customer}]` |
| pyramid | Evaluation levels `[[L0…L5, name, what, when, threshold]]` |
| controls, roles, phases | Branch protection and approvals; `[{id: agent id, decides}]`; `[[phase, when, what]]` |
| superpowers_note, resources, sources | Notes and https links |

An agent's factory stage is computed in the HTML from `lifecycle` text and the eight handover checks; nothing to store.
For agents actually in build-handover scope, the `cost` criterion requires the
[strict per-agent baseline check](../../frontier-finops/references/guardrails.md#strict-financial-build-handover),
not legacy F1/F2 or an approved status. Keep it within the existing handover
checks; other checks and the declared build/release/operate
stages remain unchanged. Core draft workshops can continue with named
financial gaps; do not infer financial readiness or start cost work from a gap.

`board` (Part 3 > Plan): `{title, intro, phases[{id, name, stages[], what}],
wip{stage id: limit}}`. Default phases: Idea (hypothesis, validated), Design
(designed, ready), Build (build), Deploy and operate (release, operate).
The board shows journey lanes, stage columns, identity/MVP cards, autonomy,
owner, handover-check share and next step, with journey/MVP filters.
CSV columns: ID, Title, Work Item Type, State, Area Path, Tags, Description,
Acceptance Criteria, Owner. Quoting and formula-prefix handling protect the
download; destination mapping is still required. CSV is handover, not live
integration or native import certification. WIP/readiness is not permission.

## it_readiness (Part 2 > IT readiness)

`{title, intro, workshop{title, outcomes[], who[], agenda[[time, topic]]}, control_plane{options[{id, name, logos[], fits, strengths, watch}], criteria[]}, groups[{id, title, logos[], items[{id: P-01…, item, why, owner, stage: workshop/prototype/build/production, status}]}], checks[{id: R-01…, kind, check, test, evidence, status}], workstation[{id: W-01…, check, expected, status}], questions[{id: Q-01…, group, question, who, status, answer}], decisions[{id: D-01…, decision, options, recommendation, owner, status}], environments[{name, purpose, type, region, status}], timeline[[when, what]]}`. Status: open, in progress, done, blocked; questions answered; decisions agreed. Workshop updates arrive as `ready:<id>`.

## Use-case template fields (Hub business-envisioning template)

Besides the scoring fields, a use case may carry: `problem` (string, or `[[provenance, text]]` with provenance workshop, board, transcript, customer, microsoft, hypothesis), `today`, `pain`, `idea`, `idea_points[]`, `objective`, `key_results[]`, `strategy`, `value_score` and `value_text`, `figures[{amount, label, source}]`, `personas`, `appeal`, `stakeholder_role`, `stakeholder_org`, `tech_fit`, `tech_points[]`, `change_resistance`, `timeframe`, `timeframe_note`, `risk_score`, `risk_points[]`, `safeguards[]`. Top-level `uc_scales` labels the scores: `{value_low, value_high, risk_low, risk_high, timeframe{1…5: text}}`. The detail page opens at `#/usecases/<id>`.

## logos (product icons, written by the build)

`logos {key: {name, uri, uri_white}}`, `logo_rules [[regex, key]]`, `logos_note`: embedded by `build_blueprint.py` from `templates/product-icons.json`, only for the keys and names the blueprint uses; `--no-product-icons` leaves them out. Never edit by hand.

## Roadmap and evidence

- `mvp_options`: `[{option, use_case, domain, why, needs, src}]`
- `next_steps`: `[{step, owner, when, status}]`
- `evidence`: `[{id, type, title, date, source, participants, visibility: internal/customer, summary, quote}]`

## Customer-output boundary

Resolve risk content visibility against original sources before scrubbing,
including promoted legacy workshop risks. Remove internal-only content and
`internal_notes`, scrub provenance, discard cached derived PRD fields and derive
final risks/PRD from permitted sources. Attendee contributions follow evidence
visibility too. Removing an internal source ID alone is not sanitisation:
check embedded JSON and downloadable Markdown, not only the rendered page.
Customer export is not external/IP clearance; private/internal distribution
and icon/copyright terms in the plugin guide still apply.

For successor `agent_finops`, project against current consumed Blueprint
root/domain/agent parents and transitive source dependencies before JSON/HTML
or identity ZIP products. Rates, FX, outcomes and review evidence carry
restrictions too. Unknown sharing/ancestry fails closed; unresolved references
and ambiguous source collisions refuse before outputs. Valid combined ontology/
baseline sources resolve on a detached, namespace-aware copy without changing
originals or imposing that opt-in strict graph on ordinary GA process work.
Cached views cannot weaken current restrictions or customer scopes.

## identity (agent identity kit)
Written by frontier-agent-identity (`apply_identity.py`, or `build_with_identity.py` in this skill); never by hand. Without it the Agent identity page is hidden.

Top level `identity`: `kit`, `version`, `date`, `status` (for example "proposal for <Customer> approval"), `customer`, `rule` (`<PO> <Domain> [<Scope>] [DEV | TEST]`), `max_length` (30), `prefix`, `prefix_note`, `solution_prefix`, `environments[]` (`name`, `postfix`, `production`, `band`, `label`, `band_name`, `label_contrast`, `banner`), `journeys[]` (`id`, `name`, `po`, `colour`, `glyph`, `colour_name`, `contrast`), `po_areas[]` (`token`, `owner`, `journeys`, `assumed`), `decisions[]` (`id`, `decision`, `owner`, `when`), `rules[]` (Microsoft guidance: `title`, `url` (https only), `text`), `brand` (`source`, `status`), `validation` (`errors`, `warnings`), `package` (zip file name).
Identity branding is not Entra identity provisioning.

Per agent (lead, specialist, `data_agent`) `identity`: `display_name`, `names` {ENV: name}, `icon` (production) and `icons` {ENV: icon} as base64 SVG/PNG data URIs, `outline`, `tokens` (`po`, `domain`, `scope`), `kind`, `schema`, `solution`, `repo`, `colour`, `contrast`, `glyph`, `status`, `status_class`, `short_description`, `description`, `slug`, `kit`. Invalid icons and colours are dropped with a warning.

`identity_feedback[]`: workshop feedback from the Agent identity page, added by `merge_feedback.py` (`date`, `topic`, `status`, `note`, `src`).

## ontology (optional process proposal)

Written by frontier-process `apply_ontology.py` or requested through
`build_with_identity.py --data blueprint.json --ontology ontology.json --out-dir working/core`.
The process skill owns the model and local normalized/Turtle/design/product/
data-agent outputs; see its [method](../../frontier-process/references/ontology-method.md).
The Ontology page is optional in Design. Preserve dated canon, checked/to-verify
mappings, source visibility and workshop `onto:<id>` verdicts. Native Fabric
import and tenant agents remain manual Preview checks, not consequences of
local file generation. This path does not require FinOps.

### Additive process grounding (unreleased 1.10.1)

The contracts stay `frontier-blueprint/1.0`, `frontier-ontology/1.0` and
`frontier-fabric-iq-canon/1.0`. This is a bounded SAP/governance correction, not
a global route framework. The process canon retains `checked: 2026-11-11` and
S1–S44; appended G59-P1/P2/P3/P5/P6/P7 records carry `checked: 2026-11-17`.
See the [dated sources and method](../../frontier-process/references/ontology-method.md#1-sources-and-limits);
no new source fetch or catalogue-wide re-verification is implied.

| Location within `ontology` | Actual shape and meaning |
|---|---|
| `sources[].path`, `item`, `status` | Fresh SAP sources use `"unresolved"`, `null`, `"later"`. Unresolved means no selected route/item, not a binding source. Saved selections/scheduling statuses remain recorded evidence. |
| `sources[].route_assessment` | Source-local object with derived `state`, derived `candidate_path`, `prerequisites`, text `commercial_note` and `src` list. Existing `content_src`/visibility ancestry still applies. |
| `route_assessment.state` | Derived `"conditional"` or `"owner_confirmed"`, never trusted from an imported flag. Owner-confirmed means an offline owner-asserted design selection only. |
| `route_assessment.candidate_path` | `"mirroring"` or `null`, derived from source-family hints. An option, not selected support; Ariba/unrecognised family hints have no mirroring candidate. |
| `route_assessment.prerequisites` | Exactly `supported_source`, `fabric_capacity`, `datasphere_environment`, `premium_outbound_integration`, `adls_gen2_permissions`. Each record requires `status` (`"unknown"`, `"confirmed"` or `"unsupported"`), text `note` and `src` list. |
| `entity_types[].binding` | New unresolved defaults: `{"layer":"silver","item":null,"table":null,"origin":"default"}`. Saved tables remain recorded proposals, not effective binding proof. |
| `current_guidance` | Derived `governance` and `sap` entries, each `{text, src}`. Current sourced clarification alongside, not replacement of, saved architecture/build/readiness/risk text. |
| `current_readiness` | Derived `{"F-06":{"status":"open","gaps":["source route <id>: conditional"]}}` while any source route is conditional. Without such gaps, uses recorded F-06 status (default `"open"`) and `gaps: []`. |
| `sources_doc` | Retains saved evidence snapshots; appends missing G59 records without reusing S IDs. Different fact content occupying a reserved G59 ID is an error. |

Confirm all five prerequisites with real owner-authored estate evidence,
non-empty notes and references resolving in the supplied Blueprint `evidence`
register, plus a named source `owner` and an explicitly selected supported
`path` with its matching `item`. The resolver recognises `type: "estate"` or
`ESTATE-` IDs, excluding public/documentation records and Microsoft Learn/
Tech Community URLs. These structural markers do not authenticate the evidence.
Public sources, name matches, missing Blueprint context and placeholder owners
do not establish confirmation. Complete prerequisites never auto-select
`path: "unresolved"` or supply a ready pipeline fallback.

The documented candidate is **SAP Datasphere → ADLS Gen2 → Fabric/OneLake**:
snapshot and changes, OneLake Delta tables and a read-only replicated SQL
surface. Existing Fabric capacity, Datasphere environment, source support,
Premium Outbound Integration entitlement and staging permissions remain estate
checks. Keep the commercial dependency **unpriced / to confirm**; this neither
invokes FinOps nor grants licensing/financial approval.

Current governance uses OneLake catalog and Fabric-domain grouping, not new
retiring Unified Catalog/classic governance creation. Domain assignment does
not affect visibility/access or enforce security. Preserve actual permissions,
OneLake security, Purview security/compliance, sensitivity labels and DLP.
Existing-estate feature/contractual/regulatory migration gaps need the governance
owner/account team; no full parity or retirement of all Purview is claimed.
Derived `fabric_domain`/`governance_domain` keys remain, with grouping labels;
saved authored domain rows/labels remain recorded.

Preserve paths/items/statuses/tables/domains, IDs, citations, feedback and
verdicts as **recorded evidence**. Conditional sources do not count in
`stats.bound`, graph/panel bound claims, mounted-table claims or dependent
publication readiness. Products retain `source route <id>: conditional` gaps.
The saved F-06 verdict stays unchanged; effective process F-06 stays open in
the Blueprint readiness aggregate. Independent supported eventhouse/secondary
bindings, grouping, feedback and Turtle/import contracts are unchanged.
Current guidance appears in HTML and all three Markdown variants/downloads.

Ordinary conditional drafts succeed with warnings. `build_ontology.py --strict`
fails on warnings with `files: {}`, before a new output directory or overwrite.
Malformed assessments and reserved citation collisions fail even without
strict mode, before projection/output effects. Public guidance cannot launder
restricted notes, bindings or feedback into customer output.

## agent_finops (optional versioned Preview derivative)

Generated from explicitly supplied authoritative
`frontier-finops-baseline/1.0` models or `frontier-finops-snapshot/1.0` frozen
snapshots, with matching `frontier-finops-owner-review/1.0` records where
reviewed. Follow the [FinOps versioned Quick Start](../../frontier-finops/SKILL.md#quick-start--requested-versioned-baseline);
new cost work requires the full notice and actual current-scenario confirmation.
Every top-level invocation or changed scope/model/rates/grounding renews that
awareness. The CLI flag is a technical assertion for one wrapper chain only.
Core/default builds do not need or automatically invoke FinOps.

### Authoritative build inputs

Both `build_with_identity.py` and standalone `build_blueprint.py` accept:

| Flag | Contract |
|---|---|
| `--agent-finops <baseline-or-snapshot.json>` | Repeat for separate agents' active authoritative models/snapshots, never reports |
| `--agent-finops-review <recorded-review.json>` | Repeat for externally asserted reviews of explicitly supplied frozen targets; omit for unreviewed drafts |
| `--as-of YYYY-MM-DD` | Explicit financial evaluation date |
| `--audience internal` or `--audience customer` | Intended projection audience |
| `--customer-scope <matching-scope>` | Matching authored/inherited scope for customer-specific output, not authorisation |
| `--acknowledge-finops-preview` | Current technical acknowledgement after actual confirmation, not approval |

The wrapper combines these sources with ordinary `--value`, requested
`--ontology` and default identity. It uses `--out-dir` and optional `--html`,
`--save-normalized` and `--report`. Standalone rendering consumes embedded
ontology/value/identity from `--data`, uses `--out` for HTML and accepts
`--save-normalized`/`--report`; it has no wrapper `--value`/`--ontology` flags.
See the [Blueprint procedure](../SKILL.md#requested-versioned-baseline--authoritative-sources)
for exact examples and output paths.

Rebuild/revalidation requires the actual current models/snapshots, matching
recorded reviews, date, audience/scope and fresh acknowledgement. A valid cached
view is replaceable derivative data, not sufficient authority; malformed
caches cannot be blessed by supplying sources. Conflicting active revisions,
unmatched reviews or mixed legacy `finops`/successor sources refuse rather
than selecting a silent winner. Preserve originals; migration is explicit and
creates a draft, with no inherited approval, acknowledgement or implied FX.

### Generated view and projected records

Never hand-author financial fields or embed full private baselines here.
The exact generated envelope is:

```text
agent_finops: {
  schema: "frontier-agent-finops-view/1.0",
  notice, maturity: "Preview", as_of, audience,
  records: [projected report DTO, ...],
  financial_permission: false, limitations
}
```

Each record is an **already projected**
`frontier-agent-finops-report/1.0` report. The authoritative field definitions
and complete shape are in the [baseline projection contract](../../frontier-finops/references/agent-finops-baseline.md#audience-projection-and-exact-derivative-dto).
Its permitted profile/baseline context, scenario inputs/results, formulas,
evidence, gaps and dated handover context are derivatives, not a re-importable
model or owner-review record. Keep `agent_finops` separate from ordinary
`value_case` and legacy `finops`/`finops_preview`. An unconsumed new baseline
does not make independent ordinary value Preview; legacy-derived value stays
Preview with its provenance. Do not automatically feed successor amounts into
legacy CHF NPV/ROI.

Use projected decimal-string amounts, status/reason and already calculated
monthly/annual/unit metrics as supplied. No JavaScript recosting or numeric
coercion of financial decimals. Missing required arithmetic inputs remain
unavailable; known usable stale/unverified prices may yield labelled
provisional drafts with verified/provisional contributions, never readiness.
Withheld money has `amount: null`, `status: withheld` and a reason; restricted
identities, evidence, headers and hashes must not be reconstructed. Public rows
are not a complete total. Never substitute zero or old legacy costs, or rebuild
raw sources client-side. Customer JSON/Markdown and Blueprint records use the
same projected report contract; internal reports may retain private context.
Classification and matching customer scope are not clearance or access control.

Figures and financial exports require separate transient, document-local viewer
acknowledgement; reload resets it, with no localStorage consent. Keep the notice
visible and gate linked assumptions/derived costs as well as flat/nested
figures. Ordinary independent value remains available.

### Financial handover and workshop feedback

At build handover, every agent in scope needs a complete validated profile and
meaningful twelve-month low/expected/high scenarios/denominators, every in-scope
driver priced with current applicable evidenced rates/FX, the frozen exact
baseline ID/version/material hash, matching external finance-owner or evidenced
delegation review, and current lineage/audience/scope validation. There is no
conditional unpriced exception; provisional or synthetic data cannot establish
real financial readiness.

Local workshop notes/proposals create new draft inputs; they neither mutate
frozen data nor approve a baseline. Material changes need a new version and
exact-target review. Raw status and legacy F1/F2 are not financial approval.
Structural validity, pricing, external review and dated readiness are separate.
Review records are externally asserted, not authenticated financial, build or
deployment permission; local snapshots/hashes are not tamper-proof archives.
The offline baseline slice adds no dedicated FinOps Agent factory, operating
loop, live billing/provider imports, cloud deployment or identity provisioning.

## value_case and finops (business value and FinOps)

The `finops` and `finops_preview` shapes below describe the explicit legacy
`frontier-finops/1.0` cost path, not successor defaults or its financial gate.
Written by frontier-value-case (`apply_value.py`) and optional frontier-finops
(`apply_finops.py`), never by hand. Ordinary value-only wrapper use is
`build_with_identity.py --data blueprint.json --value value.json --out-dir working/core`.
Only after the [full FinOps notice and actual scenario confirmation](../../frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure),
the cost form adds `--finops finops.json --acknowledge-finops-preview`.
Each new invocation/scope/model/rates/grounding needs renewed acknowledgement;
technical metadata is not independent human approval. Without value data the
use cases retain their scores; without FinOps data its page is hidden.
Omitting a flag does not cleanse previously embedded Preview fields. On decline,
preserve old originals and use clean core/ordinary non-FinOps inputs, not cached
Preview value. Do not remove provenance or relabel legacy/imported FinOps GA.

`finops_preview` carries technical caller/current-invocation metadata, the
notice and scenario/model/rate/source fingerprints. Cache/model/rates mismatch
requires fresh calculation before apply. The browser independently gates flat/
nested results and linked assumptions, including derived ROI/NPV/unit costs
and PRD summaries. Viewer acknowledgement is document-local, resets on reload,
never localStorage consent, and leaves the warning visible. Ordinary own value
remains; private components/rankings/outcomes are withheld, not zero. Never
recover `internal_notes`. Viewer acknowledgement is not access control.
Preview limitations/provenance follow downloads, replies and design exports.

`use_cases[].business_value` (the numeric `value` stays the 1-5 score for the matrix): `status` (hypothesis, partly validated, validated), `confidence`, `open_assumptions`, `range_year` (`low`, `base`, `high`; `weak`, `strong` corners), `economic_year`, `budget_year`, `capacity_year`, `risk_year`, `cost_year`, `build`, `npv`, `npv_budget`, `roi`, `payback_months`, `break_even` (`assumption`, `value` or `always_positive`, `statement`, `unit`), `levers[]` (`name`, `driver`, `category`, `formula`, `annual`, `booked`, `rejected`, `note`, `assumptions`), `assumptions[]` (ids).

`value_case`: `status`, `version`, `date`, `currency`, `horizon_years`, `discount_rate`, `realisation_default`, `totals`, `scenarios`, `assumptions[]` (`id`, `statement`, `unit`, `low`, `base`, `high`, `source_type`, `confidence`, `src`, `owner`, `question`, `status`, `note`, `use_cases`, `rank`, `swing_npv`), `questions[]` (top ids), `inputs_needed[]`, `discipline[]`, `sources[]` (https links only).

`finops`: `status`, `currency`, `rates_version`, `rates_checked`, `rates_age_days`, `verify`, `fx`, `purchase`, `coverage_note`, `agents[]` (`id`, `name`, `harness`, `audience`, `coverage`, `sessions`, `billable_share`, `credits_month`, `lines` {credits, licences, azure, people}, `total_month`, `build`, `unit`, `events[]`), `totals`, `purchase_options[]`, `credit_scenarios[]`, `guardrails[]`, `lessons[]`, `tags[]`, `assumptions[]`, `rates[]`, `sources[]`, `note`.

`assumption_feedback[]`: workshop verdicts on assumptions (`ass:<id>`) and the FinOps model, added by `merge_feedback.py` (`date`, `id`, `kind`, `status`, `value`, `note`, `src`); `merge_value_feedback.py` applies them.
