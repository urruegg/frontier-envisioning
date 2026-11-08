# Changelog

Releases of the Frontier Envisioning plugin. Engineering changes to the repository are recorded in the pull requests.

## 1.4.0 — 2026-11-08

- **Blueprint follows the Innovation Hub journey.** Part 1 Vision: Overview, Org model, Blueprint, Journeys, Attendees. Part 2 Design: Agents, Agent identity, Target architecture, Use cases, IT readiness, FinOps. Workshop: Discovery, Roadmap, Evidence (14 views).
- **Agent Factory journey.** A canon journey with DevSecOps: lifecycle from hypothesis to validated, designed, ready for build, build, release and operate; an agent board computed from eight handover checks (Definition of Ready); seven build steps with the GitHub Copilot harness, Superpowers and the CAT agent skills to reuse; evaluation pyramid L0 to L5; controls, roles, phases and resources. Six factory agents get identities (repository agents).
- **Attendees page.** Who took part, their role and organisation, what they contributed, linked to journeys and use cases.
- **Target architecture in four tabs.** Landing zone (CAF design areas, WAF and Responsible AI lenses, one agent landing zone per journey with DEV, TEST and PROD, data classes, MVP markers, identity icons), Layers and integrations, Flows, and Decisions: architecture decision records with seven Innovation Hub canon ADRs and a live workshop verdict.
- **Use cases in the Hub template.** A detail page per use case (General with the problem statement and its provenance, Value with business value, Feasibility), deep links `#/usecases/<id>`.
- **IT readiness page.** Preparation items P-01 to P-30, readiness checks R-01 to R-15, builder workstation W-01 to W-11, questions for IT, decisions D-01 to D-08, environments and timeline, with live status exported with the notes.
- **Microsoft product icons** across the parts (only the icons used are embedded; `--no-product-icons` leaves them out; see THIRD-PARTY-NOTICES.md).
- Scripts: `canon.py` adds the canon without overwriting (and skips a canon ADR whose title exists); `build_blueprint.py --canon` upgrades a 1.3 blueprint; `merge_feedback.py` applies `ready:` and `adr:` verdicts; `scaffold_design_docs.py` adds the landing zone and the Agent Factory to the solution design, the canon ADRs and `it-readiness.md`; `seed_identity.py` seeds factory agents as repository agents.
- Caldova demo: five journeys (Agent Factory included), 29 agents, 8 attendees, 9 decisions, IT readiness in progress. Self-test: 29 checks.

## 1.3.0 — 2026-11-04

- **New skill frontier-value-case.** Business value in CHF per use case: value tree (efficiency, quality, revenue, strategic; cash, capacity, risk), assumption register with owners, ranges, evidence and questions; budget and economic views, NPV, ROI, payback, break-even, sensitivity, ranges; seed, calculation, blueprint apply and workshop merge scripts.
- **New skill frontier-finops.** Agent cost model in CHF: Copilot Credits by event with licence coverage, licences, Azure, people and build; unit economics; purchase options (pay-as-you-go, capacity packs, Copilot Credit P3, Agent P3); credit-cost scenarios; guardrails; tagging keys from the agent identity; versioned rates file with sources and a 90-day verify rule.
- **Blueprint.** A dedicated FinOps page; business value in the use cases (value tree, assumptions) and the matrix (bubble size by value, dashed while a hypothesis); the assumption register with live confirm, adjust (agreed value) or reject, exported with the workshop notes; value and cost on the roadmap MVP cards.
- `build_with_identity.py --value --finops` calculates both on copies and renders everything in one build; `merge_feedback.py` keeps assumption verdicts; the scripts reproduce the method's worked example.
- Self-test: 23 checks.

## 1.2.0 — 2026-10-30

- **Agent identity page in the blueprint.** A new page below Agents shows the naming rule, journey colours, DEV and TEST bands, the agent family, the MVP identity sheet, all names per environment with a length check, the decisions to confirm, the Microsoft guidance applied and a workshop validation box.
- **Agents use their identity everywhere.** Display names and icons in the agent list and canvas (with an identity panel), role cards, journeys, org model, use cases, roadmap MVP cards and the blueprint view; the working name stays visible.
- **Blueprint and identity kit in one build.** `build_with_identity.py` (frontier-blueprint) seeds the identity proposal (from the customer's Office theme when given), builds and validates the kit, writes the identity into the blueprint and renders the HTML. The Caldova demo builds both.
- `apply_identity.py` also writes icons per environment, the outline icon, technical names and the page data; `build_blueprint.py` screens them; `merge_feedback.py` keeps identity feedback as `identity_feedback`.
- Self-test: 18 checks.

## 1.1.0 — 2026-10-30

- New skill **frontier-agent-identity**: the agent identity kit, generalised from an Innovation Hub HR engagement. From the blueprint and the customer's brand it creates
  - the naming convention `<PO> <Domain> [Scope] [DEV|TEST]` with clean production names (30 characters) and environment-neutral technical names (schema, solution, variables, connection references, flows, folders);
  - one colour per journey from the customer's own palette, contrast-checked (4.5:1), with DEV and TEST bands;
  - icons per agent and environment in the Microsoft 365 sizes (colour 192 and 32, outline 32, SVG sources), identity cards, agent family overview, MVP identity sheet, colour schema and an HTML catalogue;
  - generated docs, `validate_identity.py`, `stamp_identity.py` (names and icons into an unpacked solution before packing), unit tests, Azure Pipelines and GitHub Actions templates, and GitHub Copilot instructions.
- Icons are drawn by a standard-library renderer (no browser or image library), so customers can rebuild them on any build agent.
- Glyph library: 37 Fluent UI System Icons (MIT) and 24 Frontier glyphs; importer for more Fluent glyphs.
- `read_office_theme.py` reads a customer's theme colours and fonts from an Office file; `seed_identity.py` proposes names, kinds, glyphs and colours with a review report; `make_kit.py` builds, validates, tests and zips the kit; `apply_identity.py` writes the identity into the blueprint.
- Blueprint template: role cards, journey views and the agent canvas show each agent's icon and display names when an identity is present.
- Orchestrator: step 6b (identity) with gate E; `engagement.json` records the identity version.
- Caldova demo: "Build the identity kit demo for Caldova" (fictitious brand, 27 agents).

## 1.0.1 — 2026-10-22

- The sample company is now **Caldova Industrial AG** (fictitious, the same company as the HR Frontier design sample): demo blueprint and example context pack renamed.
- One package for everyone: `frontier-envisioning-plugin-1.0.1.zip` installs from a Cowork chat ("Install the Frontier PlugIn") and is also the Microsoft 365 app package for the organisation catalogue.
- `README.md` setup guide at the package root, with exact steps for Copilot Cowork.
- `install/prepare_install.py` and `install/plugin-install.json`: the package is checked file by file before anything is installed; new, update and reinstall are detected.
- Demo on request: "Build the Frontier blueprint demo for Caldova".
- Skill metadata carries the version; the self-test covers the install (13 checks).
- MIT License: `MIT.md` in the repository and the install package; `license: MIT` in every skill; SPDX headers in every script and in the blueprint renderer; `plugin.json` licence set to MIT.

## 1.0.0 — 2026-10-22

First release.

- Four skills: `frontier-envisioning` (end-to-end method), `frontier-context-discovery` (Work IQ and transcripts to a cited context pack), `frontier-blueprint` (generic Frontier Company Blueprint HTML, feedback merge, customer version), `frontier-solution-design` (PRD, solution design, ADRs).
- Generic blueprint template generalised from the procurement four-journeys mockup: ten views, HAIRO org model with step-by-step reveal, role cards and nine-section role profiles, trigger canvas, seven declarations, use-case portfolio, live discovery notes with JSON export, evidence register with internal and customer visibility.
- Innovation Hub canon for the target architecture (layers 0 to 7 plus approval seams) grounded in Microsoft guidance as of October 2026.
- Caldova (fictitious) examples for the context pack and the blueprint; self-test and package builder.
