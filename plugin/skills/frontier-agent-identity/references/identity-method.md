# Agent identity method

How the kit names, colours and draws a customer's agents, and why. Generalised from an Innovation Hub HR engagement (October 2026) where the customer asked for one naming rule for 37 agents across development, test and production. Microsoft facts checked on 30 October 2026; sources at the end.

## 1. The naming rule

```text
Display name = <PO> <Domain> [<Scope>] [<ENV>]
  PO      process-owner area: the business area that owns the process (Recruiting, Procurement, Service)
  Domain  what the agent does, 1-3 words (Job Posting, Guided Buying, Report)
  Scope   optional ISO country code, only when the process itself is country-specific (CH)
  ENV     the non-production environment (DEV, TEST, UAT ...); nothing in production
```

Why it works: the first words tell users which area stands behind the agent, the next words what it does, and only a test build carries an environment word. Production names stay clean in Microsoft 365 Copilot, Teams and the agent store.

**`<PO>` is an assumption to confirm.** Customers often say "PO" without defining it: process owner, product owner or a fixed prefix. The kit assumes the process-owner area and lists it as decision N-1; if the customer means something else, change `naming.displayTemplate` or the PO tokens and rebuild.

### PO tokens
- One per process-owner area, short enough to leave room for the domain: "HR Ops" rather than "HR Operations".
- Seeded from the journey names; confirmed by the process owners (decision N-2). The validator rejects tokens that are not in `poAreas`.

### Domain tokens
- 1-3 words, a noun phrase of what the agent does. No "Agent", "Bot" or "Copilot", no personal names, no environment words.
- Lead agents (orchestrators) end with "Lead": "Service Lead", "Finance Close Lead".
- When a name is too long, prefer the words the business uses (the use-case name) over a mechanical cut. Record the reason in `notes`.

### Lengths and limits

| Item | Limit | Source |
|---|---|---|
| Agent name in Agent Builder | 30 characters | Microsoft Learn, Build agents in Agent Builder |
| Microsoft 365 app short name / full name | 30 / 100 characters | Microsoft 365 app manifest schema |
| Short description / full description | 80 / 4,000 characters | Microsoft 365 app manifest schema |
| Declarative agent name / description | 100 / 1,000 characters | declarative agent manifest schema v1.5 |
| Agent icon in Copilot Studio | PNG, 100 KB or less | Microsoft Learn, Configure agent details and instructions |

The kit keeps every display name within 30 characters, so it fits every surface; the production name is shorter by the longest postfix plus a space (25 with DEV/TEST, 22 with PREPROD). Short descriptions stay within 72 so the "DEV · " marker still fits 80.

## 2. Environments

| Artefact | Non-production | Production |
|---|---|---|
| Agent display name, app short and full name | "… DEV", "(DEV)" | clean |
| Short description | "DEV · …" | plain |
| Full description | starts with a test-build banner | plain |
| Icon | coloured band with the environment word | clean |
| Schema, solution, environment variables, connection references, flows, topics, folders | never an environment | never an environment |

The same solution moves from development to test to production, so only what users see carries the environment. Agents imported as managed can't be renamed in the target environment: names and icons are stamped into the unpacked solution before packing (`stamp_identity.py`). Exporting from development, stamping production first turns "… DEV" names back into the canonical form kept in Git. Fabric data agents and repository agents keep one name everywhere (Fabric deployment pipelines keep item names; repository agents have no environment).

Custom stages are fine: list them in order with production last (`--envs DEV,TEST,UAT,PROD`). Each non-production stage gets its own band colour.

## 3. Technical names (derived, environment-neutral)

| Artefact | Pattern |
|---|---|
| Publisher prefix | 2-8 lower-case letters or digits, starting with a letter, not "mscrm" (decision N-3) |
| Schema name | `<prefix>_<POCode><Domain>[<Scope>]`, set under Advanced settings before the first save; the solution's publisher sets the prefix |
| Solution | `<PREFIX><POCode><Domain>[<Scope>]`, display "<Customer> <production name>" |
| Environment variable | `<prefix>_<POCode><Name>[_<Scope>]` |
| Connection reference | `<prefix>_<Connector><POCode>[<Scope>]` |
| Agent flow | "<production name> - <Verb> <object>" |
| Repository folder | `agents/<slug>/` (kebab-case of the production name) |
| Foundry agent / Fabric data agent / declarative agent | slug / production name / `appPackage/<slug>` |

## 4. Colours

- **One colour per journey**, from the customer's palette (brand guide, Office theme, website). Agents are told apart by glyph, never by shades.
- **Contrast 4.5:1** between glyph and background (Microsoft's icon guidance recommends 4.5:1). If white fails, use the palette's darkest colour as the glyph; if that fails too, an accessible shade of the same colour. Never a new colour.
- **Tints** (12 % and 30 % of the colour on white) for chips, headers and table rows.
- **Environment bands:** the first non-production stage gets a warm brand colour (white label), the last a light brand colour (dark label); both at least 4.5:1. Neutral fallbacks are flagged.
- The seed maps each journey to the nearest brand colour of the blueprint's journey colour, so the blueprint and the kit stay recognisable. `apply_identity.py --colours` aligns the blueprint to the kit afterwards.

## 5. Icons

Microsoft's guidance for agent icons: a full-bleed colour icon of 192 × 192 and a 32 × 32 icon; a perfect square without rounded corners or border (Microsoft 365 adds both); a flat colour background; 4.5:1 contrast; brand marks inside the 120 × 120 safe area; visual balance within the 96 × 96 centre; no words. The Microsoft 365 app also needs an outline icon of 32 × 32, white on transparent.

The kit's design:
- Journey colour, full bleed; one glyph per agent in the 96 × 96 centre - filled style on colour icons, regular style on the outline icon.
- Glyphs: 37 from Microsoft's Fluent UI System Icons (MIT) and 24 Frontier glyphs drawn on the same grid for functions the Fluent subset lacks (cart, receipt, wrench, truck, factory, contract, banknote, globe and more). More Fluent glyphs can be imported from their SVG files.
- Non-production: a 36-pixel band at the bottom, outside the balance area, with a 4-pixel white separator and the environment word. At 32 × 32 the word can't be read, but the band colour still shows.
- Icons are rendered by a standard-library renderer, so every machine produces identical pixels; the unit tests check that the committed icons match the config.

## 6. Kinds of agents

| Kind | Environments | Technical names |
|---|---|---|
| copilot-studio | yes | schema, solution, variables, connection references, flows |
| ess (Microsoft-managed, customised) | yes, if the customisation layer allows renaming | as Copilot Studio; verify in development |
| declarative-agent | yes (one app package per environment) | app package folder; manifest name ≤ 100, description ≤ 1,000 |
| foundry-agent | yes | slug |
| fabric-data-agent | no | the production name in every workspace |
| repository-agent | no | `.github/agents/<name>.agent.md` |

The seed reads the kind from the blueprint's technology text; correct it in the config when the design changes.

## 7. Review checklist (with the customer)

1. PO tokens and their meaning (N-1, N-2).
2. Every shortened or truncated name has a natural domain; MVP names confirmed by the process owners (N-4).
3. Publisher prefix confirmed by the Power Platform team (N-3).
4. Journey colours confirmed against the brand guide (N-5).
5. Environment names and stages (N-6).
6. Glyph per agent: distinct within a journey, meaningful to users.
7. Validator 0 errors, unit tests passed; first export checked (`bot.xml`, Teams icon fields, schema-name suffix).

## Sources (checked 30 October 2026)

- Design icons for agent acquisition and management - https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-icon-management
- Configure agent details and instructions (Copilot Studio) - https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-instructions
- Build agents in Agent Builder - https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents
- Declarative agent manifest schema v1.5 - https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json
- Create and delete agents (Copilot Studio) - https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot
- Microsoft 365 app manifest schema - https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema
- CopilotStudioSamples (unpacked bot.xml) - https://github.com/microsoft/CopilotStudioSamples
- Fluent UI System Icons (MIT) - https://github.com/microsoft/fluentui-system-icons
