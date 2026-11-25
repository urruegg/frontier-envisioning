---
name: frontier-agent-identity
description: |
  Creates the brand identity kit for a customer's agents from the Frontier Company Blueprint:
  naming convention with environment postfixes (<PO> <Domain> [Scope] [DEV|TEST]), one colour
  per journey from the customer's brand (4.5:1 contrast), icons with DEV and TEST bands, cards,
  catalogue, and validate and stamp scripts with pipeline templates. Reviews and finalises the
  proposal that every blueprint build creates. Use when asked to "create the agent identity kit
  for <customer>", "name the agents", "agent naming convention", "icons and colours for the
  agents", "DEV and TEST agent names" or "build the identity kit demo for Caldova". Do NOT use
  for a logo, illustration or picture (image generation); use frontier-blueprint for the
  blueprint itself and frontier-solution-design for PRD and design documents.
license: MIT
metadata:
  category: productivity
  icon: PaintBrush
  version: "1.11.0"
  plugin: frontier-envisioning
  maturity: ga
  optional: false
  requires_preview_ack: false
---

# Agent identity kit

Gives every agent in a customer's Frontier blueprint a name, colour and icon that people recognise and pipelines can't get wrong. One config file is the source of truth; scripts derive every display name per environment, every technical name, every icon and every document from it, and a validator blocks drift in pull requests.

What the customer receives (one zip, ready for their repository):
- **Naming convention:** `<PO> <Domain> [Scope] [DEV|TEST]`, production without a postfix, 30 characters; environment-neutral technical names (schema, solution, variables, connection references, flows, folders).
- **Colour schema:** one colour per journey from the customer's own palette, contrast-checked; DEV and TEST bands.
- **Icons per agent:** colour 192 × 192 and 32 × 32 per environment, outline 32 × 32, SVG sources; identity card 1200 × 630.
- **Visuals and catalogue:** agent family, MVP identity sheet, colour schema, `catalog.html`, generated docs.
- **Automation:** `validate_identity.py`, `stamp_identity.py` (names and icons into an unpacked solution before packing), unit tests, Azure Pipelines and GitHub Actions templates, GitHub Copilot instructions.

## Quick Start

```
User: "Create the agent identity kit for Caldova"
1. Find blueprint.json in the engagement folder (validated version preferred)
2. Brand: python scripts/read_office_theme.py <customer deck>.pptx --out brand.json  (+ website colours, sources)
3. python scripts/seed_identity.py --blueprint blueprint.json --brand brand.json --prefix <prefix> --out-dir working/identity/<slug>/config
4. Review seed-report.md with the user: PO tokens, shortened names, MVP names, colours, prefix
5. python scripts/make_kit.py --config .../agent-identity.json --palette .../palette.json --out working/identity/<slug>/<slug>-agent-identity --zip "<Customer> - agent identity package v1.0"
6. python ../frontier-blueprint/scripts/build_with_identity.py --data blueprint.json --identity-config .../agent-identity.json --palette .../palette.json --out-dir working/frontier/<slug>
   (kit and blueprint together: identity in every agent, Agent identity page below Agents)
7. CopyArtifact the zip and catalog.html to output; reply with the names table and open decisions
```

Demo: "Build the identity kit demo for Caldova" runs step 5 with `examples/caldova-agent-identity.json` and `examples/caldova-palette.json` (fictitious brand).

Every blueprint build already runs steps 3, 5 and 6 as a proposal (frontier-blueprint's `build_with_identity.py`). When the engagement folder has `identity/config/seed-report.md`, start at Step 4 with it.

Agent identity remains in Design in the four-part blueprint; the Build >
Plan cards reuse its icons and names. Vision > PRD/scaffold requirements keep
canonical IDs when selecting a subset. Plan readiness or a displayed identity
status does not approve names, provision Entra identities or authorise deployment.

This GA product wrapper works without FinOps. GA is the maintainer's designation,
not result confidence, provider GA or release/distribution approval. Identity
does not need cost modelling. For requested costs, first show the full notice
and obtain actual current-scenario confirmation through
[frontier-finops](../frontier-finops/SKILL.md). On decline or absent unrequested
FinOps, continue identity and state the gap; a requested missing module is an
error. Preserve legacy Preview originals/provenance and use clean core inputs,
not cached Preview-derived value, on the declined path.

## When to Use

- The blueprint's agents are about to be built and need names, icons and colours for DEV, TEST and PROD.
- A customer asks for an agent naming convention, an agent icon set or a colour schema for their agents.
- An existing kit needs new agents, renamed agents, another environment (for example UAT) or the customer's real brand.

## When NOT to Use

- What the agents cost: load frontier-finops for its Preview notice and confirmation first.
- What the agents are worth: use frontier-value-case instead.
- A logo, illustration, poster or picture: use image generation instead.
- Building or updating the blueprint itself: use frontier-blueprint instead (this skill only adds identity to it).
- PRDs, solution design and ADRs: use frontier-solution-design instead.
- Gathering customer context or analysing transcripts: use frontier-context-discovery instead.
- Running the whole engagement end to end: use frontier-envisioning instead.
- Creating the agents in Copilot Studio or deploying them: the customer's build team uses the kit.

## Workflow

### Step 1: Locate the blueprint and the engagement
Read `engagement.json` and the blueprint from the engagement folder (OneDrive `Documents/Cowork/frontier-envisioning/<slug>/`, then `input/`). Prefer the validated blueprint; a hypothesis blueprint works, and its status is shown on every card. Never mix customers.

### Step 2: Collect the brand - evidence first
Follow [references/brand-discovery.md](references/brand-discovery.md). In order of trust: the customer's brand portal or guide, a customer-authored Office file (theme colours and fonts), the customer's website, the blueprint colours. Find candidates with the `SearchM365` tool (decks or templates the customer sent) and read a brand guide with `ReadFileContent`; for the theme itself, ask the user to attach the customer's deck or template and run `read_office_theme.py` on it. Record every source with an evidence id in `brand.json`. Never invent brand colours; without a brand source the seed uses the blueprint colours and flags it. Use the customer's logo only when their brand rules allow it.

### Step 3: Seed the identity
Run `seed_identity.py`. It proposes PO tokens from the journeys, a 1-3 word domain per agent (shortened to fit, and flagged), the kind of each agent from its technology (Copilot Studio, declarative, Foundry, Fabric data agent, repository agent), a glyph per agent, MVP and status labels from the blueprint, descriptions within the limits, journey colours mapped to the nearest brand colour with 4.5:1 contrast, and DEV/TEST bands. Ask for the publisher prefix if it is not in the evidence; the seed proposes one from the customer name and lists it as decision N-3.

### Step 4: Review with the user
Show a table: journey, blueprint name, proposed display name, kind, glyph, status. Resolve every "shortened" note with a natural 1-3 word domain, confirm the PO tokens and the MVP names, and check the colours. Edit `agent-identity.json` (tokens only: `po`, `domain`, `scope`, `glyph`, `workingName`, `notes`) - never the `derived` block. Decisions N-1 to N-6 stay open with owners until the customer confirms them. Details: [references/identity-method.md](references/identity-method.md). Workshop feedback from the blueprint's Agent identity page arrives in the merged blueprint as `identity_feedback`; resolve it here.

### Step 5: Build, validate and package
Run `make_kit.py` with `--zip`. It copies the kit, builds names, icons, cards, visuals, docs and the catalogue, validates and runs the unit tests. Gate: validator 0 errors and tests passed - otherwise fix the config and run it again. Warnings (a glyph used twice in a journey) are reported to the user. Icons need nothing but Python; PNG copies of cards and visuals use an SVG converter when one exists. Layout and options: [references/kit-reference.md](references/kit-reference.md).

### Step 6: Rebuild the blueprint with the identity
Run `../frontier-blueprint/scripts/build_with_identity.py --data <blueprint.json> --identity-config <reviewed agent-identity.json> --palette <palette.json> --out-dir <engagement folder>`: it builds the kit and the blueprint together. Every agent then carries its display names, icons per environment and technical names, the journey colours follow the palette, and the blueprint has the **Agent identity** page below Agents (naming rule, journey colours, environment bands, agent family, MVP identity sheet, all names, decisions, Microsoft guidance, workshop validation). `apply_identity.py --colours` alone writes the same data into a blueprint JSON.

### Step 7: Save and hand over
Publish the zip and `catalog.html` to output with `CopyArtifact`; save the kit folder to the engagement folder (`identity/`) and add it to `engagement.json` (`identity_version`). The customer's team copies the package into their repository (`docs/harness-integration.md` in the kit).

## Output format (reply)

- The zip by file name, and what is in it in one line.
- A table of the MVP agents: display name per environment and technical name.
- Journey colours with contrast; validator and test result.
- Open decisions (N-1 to N-6) with owners, and anything flagged (shortened names, fallback colours, no brand source).

## Guardrails

- Identity can supply allocation keys to an acknowledged Preview FinOps model;
  this kit does not tag deployed resources or validate a budget.

- Never invent brand colours, logos or fonts: every colour has a source and an evidence id, or it is marked as a blueprint colour.
- Always keep icon contrast at or above 4.5:1; use the brand's dark colour or an accessible shade of the same colour, never a new colour.
- Never put an environment word into technical names; only display names, descriptions and icons carry it.
- Never edit generated files (`derived`, PNG, SVG, docs, catalogue) by hand; change the config and rebuild.
- Never present names as final: they are proposals until the process owners confirm them.
- Always show the proposed names, kinds and colours to the user before building the kit, and ask about every shortened name.
- Do not use real customer data in test fixtures; the stamping tests build a synthetic solution.
- Always keep Microsoft-internal notes out of the kit: it is a customer deliverable.
- Preserve original copyright and Microsoft product-icon terms. An internally
  prepared kit or customer-scrubbed blueprint is not external/IP sharing approval.

## Failure handling

- If the seed or the build reports an unknown PO token, journey or glyph: fix the config entry it names and run it again.
- If the validator fails: each line names the check (N1-N6, D1, C1-C2, F1-F3) and the agent; shorten the domain, fix the colour or rebuild.
- If no SVG converter is available for cards and visuals: the kit keeps SVG copies; say so (icons are always PNG).
- If no brand source can be found: continue with the blueprint colours only after telling the user, and keep decision N-5 open.
- If the blueprint is missing or belongs to another customer: stop and ask which engagement to use.
- If a disk write fails in the sandbox: run the step again; `make_kit.py` rebuilds the folder from scratch.

## Files

- `scripts/read_office_theme.py` - theme colours and fonts from .pptx/.potx/.docx/.dotx/.xlsx/.thmx into `brand.json`
- `scripts/seed_identity.py` - blueprint (+ brand) to `agent-identity.json`, `palette.json` and `seed-report.md`
- `scripts/make_kit.py` - kit folder and zip: build, validate, test
- `scripts/apply_identity.py` - identity into the blueprint JSON: names, icons per environment, technical names and the Agent identity page data
- `kit/` - the customer package template: scripts (build, validate, stamp, renderer, docs, visuals, tests), glyph library, pipelines, schema
- `examples/caldova-brand.json`, `examples/caldova-agent-identity.json`, `examples/caldova-palette.json` - fictitious demo
- `references/identity-method.md`, `references/brand-discovery.md`, `references/kit-reference.md`
