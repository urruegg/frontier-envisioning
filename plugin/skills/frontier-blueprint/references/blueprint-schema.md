# Blueprint JSON reference (frontier-blueprint/1.0, plugin 1.4)

Every field is optional unless marked required. Missing fields render as "To be confirmed". Unknown fields are kept but not shown. `src` is always a list of evidence ids.

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
| canvas | `{trigger[], instructions, plan[], outcome, data_sources[], connectors[], approval[], autonomy, skills[], pattern, build}` |
| declarations | `{write_envelope, refusal_set, escalation_path, grounding_sources, data_classification, people_decisions, measurement}` |
| profile | Nine sections: `starting_point, contribution, impact, mission, trigger, input, output, tasks[], reports_to, works_with[], hands_off_to, autonomous, approval, escalation, knowledge[], rules[], not_allowed[], systems[], channels[], tone, language, kpis[]` |
| workshop_notes | Added by merge_feedback.py |
| internal | true removes the item from customer versions |

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

## attendees (Part 1 > Attendees)

`{title, date, place, note, people[{name, role, org (the customer's short name or "Microsoft"), where (on site, remote), team, focus[] (journey name, short name or id, or use-case name or id: each becomes a link), contributions[] (sentences), quote, src[]}]}`. Seeded from the named stakeholders of the context pack; name customer people only with their agreement, otherwise by role.

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

## identity (agent identity kit)
Written by frontier-agent-identity (`apply_identity.py`, or `build_with_identity.py` in this skill); never by hand. Without it the Agent identity page is hidden.

Top level `identity`: `kit`, `version`, `date`, `status` (for example "proposal for <Customer> approval"), `customer`, `rule` (`<PO> <Domain> [<Scope>] [DEV | TEST]`), `max_length` (30), `prefix`, `prefix_note`, `solution_prefix`, `environments[]` (`name`, `postfix`, `production`, `band`, `label`, `band_name`, `label_contrast`, `banner`), `journeys[]` (`id`, `name`, `po`, `colour`, `glyph`, `colour_name`, `contrast`), `po_areas[]` (`token`, `owner`, `journeys`, `assumed`), `decisions[]` (`id`, `decision`, `owner`, `when`), `rules[]` (Microsoft guidance: `title`, `url` (https only), `text`), `brand` (`source`, `status`), `validation` (`errors`, `warnings`), `package` (zip file name).

Per agent (lead, specialist, `data_agent`) `identity`: `display_name`, `names` {ENV: name}, `icon` (production) and `icons` {ENV: icon} as base64 SVG/PNG data URIs, `outline`, `tokens` (`po`, `domain`, `scope`), `kind`, `schema`, `solution`, `repo`, `colour`, `contrast`, `glyph`, `status`, `status_class`, `short_description`, `description`, `slug`, `kit`. Invalid icons and colours are dropped with a warning.

`identity_feedback[]`: workshop feedback from the Agent identity page, added by `merge_feedback.py` (`date`, `topic`, `status`, `note`, `src`).

## value_case and finops (business value and FinOps)
Written by frontier-value-case (`apply_value.py`) and frontier-finops (`apply_finops.py`), or by `build_with_identity.py --value --finops`; never by hand. Without them the use cases keep their scores only and the FinOps page is hidden.

`use_cases[].business_value` (the numeric `value` stays the 1-5 score for the matrix): `status` (hypothesis, partly validated, validated), `confidence`, `open_assumptions`, `range_year` (`low`, `base`, `high`; `weak`, `strong` corners), `economic_year`, `budget_year`, `capacity_year`, `risk_year`, `cost_year`, `build`, `npv`, `npv_budget`, `roi`, `payback_months`, `break_even` (`assumption`, `value` or `always_positive`, `statement`, `unit`), `levers[]` (`name`, `driver`, `category`, `formula`, `annual`, `booked`, `rejected`, `note`, `assumptions`), `assumptions[]` (ids).

`value_case`: `status`, `version`, `date`, `currency`, `horizon_years`, `discount_rate`, `realisation_default`, `totals`, `scenarios`, `assumptions[]` (`id`, `statement`, `unit`, `low`, `base`, `high`, `source_type`, `confidence`, `src`, `owner`, `question`, `status`, `note`, `use_cases`, `rank`, `swing_npv`), `questions[]` (top ids), `inputs_needed[]`, `discipline[]`, `sources[]` (https links only).

`finops`: `status`, `currency`, `rates_version`, `rates_checked`, `rates_age_days`, `verify`, `fx`, `purchase`, `coverage_note`, `agents[]` (`id`, `name`, `harness`, `audience`, `coverage`, `sessions`, `billable_share`, `credits_month`, `lines` {credits, licences, azure, people}, `total_month`, `build`, `unit`, `events[]`), `totals`, `purchase_options[]`, `credit_scenarios[]`, `guardrails[]`, `lessons[]`, `tags[]`, `assumptions[]`, `rates[]`, `sources[]`, `note`.

`assumption_feedback[]`: workshop verdicts on assumptions (`ass:<id>`) and the FinOps model, added by `merge_feedback.py` (`date`, `id`, `kind`, `status`, `value`, `note`, `src`); `merge_value_feedback.py` applies them.
