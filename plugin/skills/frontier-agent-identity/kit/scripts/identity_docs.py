#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Markdown and HTML documentation of the agent identity package, generated from the config."""
from __future__ import annotations

import base64
from pathlib import Path

import identity_lib as L

MS_CHECKED = "30 Oct 2026"
MS_SOURCES = [
    ("Design icons for agent acquisition and management (Microsoft 365 Copilot extensibility, updated 20 Nov 2025)",
     "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-icon-management",
     "192 × 192 full-bleed colour icon and a 32 × 32 icon; perfect square, no rounded corners, no border; flat colour background; "
     "4.5:1 contrast recommended; brand marks inside the 120 × 120 safe area; balance within the 96 × 96 centre; avoid words"),
    ("Configure agent details and instructions (Copilot Studio, GitHub Copilot harness, updated 21 Oct 2026)",
     "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-instructions",
     "agent name; icon as PNG of 100 KB or less; icon colour and accent colour"),
    ("Build agents in Agent Builder (Microsoft 365 Copilot)",
     "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-build-agents",
     "name up to 30 characters; description up to 1,000 characters; icon PNG 192 × 192"),
    ("Declarative agent manifest schema v1.5",
     "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json",
     "name up to 100 characters; description up to 1,000 characters"),
    ("Create and delete agents (Copilot Studio)",
     "https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot",
     "schema name set under Advanced settings when the agent is created; the solution's publisher sets the prefix"),
    ("Microsoft 365 app manifest schema (Teams)",
     "https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema",
     "short name 30 and full name 100 characters; short description 80 and full description 4,000; accentColor; "
     "colour icon 192 × 192; outline icon 32 × 32, white on transparent"),
    ("CopilotStudioSamples (unpacked agent samples)", "https://github.com/microsoft/CopilotStudioSamples",
     "bots/<schemaname>/bot.xml with <name> and <iconbase64> - verify once with your first export"),
    ("Fluent UI System Icons (MIT)", "https://github.com/microsoft/fluentui-system-icons", "glyph source for the Fluent glyphs"),
]


def _cust(cfg):
    return cfg["customer"]["short"]


def _rule(cfg) -> str:
    return "<PO> <Domain> [<Scope>] [" + " | ".join(L.env(cfg, e).get("postfix") or e for e in L.nonprod_envs(cfg)) + "]"


def _mvps(cfg):
    return sorted((a for a in cfg["agents"] if a.get("statusClass") == "mvp"), key=lambda a: (a.get("mvp") or "", a["id"]))


def _examples(cfg):
    m = _mvps(cfg)
    return m if m else cfg["agents"][:3]


def _status_label(palette, a):
    st = palette["statusStyles"].get(a.get("statusClass", "hypothesis")) or palette["statusStyles"]["hypothesis"]
    return a.get("mvp") if a.get("statusClass") == "mvp" and a.get("mvp") else st["label"]


def _header(cfg, title):
    return f"# {title}\n\nVersion {cfg['version']} · {cfg['date']} · {cfg.get('status', 'proposal')}.\n"


# ---------------------------------------------------------------- naming convention

def naming_md(cfg, palette) -> str:
    n = cfg["naming"]
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    envs = L.env_names(cfg)
    c = _cust(cfg)
    out = [_header(cfg, f"Naming convention for {c} agents") + "Machine-readable source: `config/agent-identity.json`.\n",
           "## 1. The rule\n", "```text",
           f"Display name  =  {_rule(cfg)}",
           f"                 PO     process-owner area: the {c} area that owns the business process",
           "                 Domain what the agent does, 1-3 words",
           "                 Scope  optional ISO country code, only when the process is country-specific (e.g. CH)",
           f"                 ENV    {' or '.join(nonprod)} - nothing in {prod}", "```\n"]
    ex = _examples(cfg)
    out.append("| " + " | ".join(["Agent", "Working name", "PO", "Domain · Scope"] + envs) + " |")
    out.append("|" + "---|" * (4 + len(envs)))
    for a in ex:
        d = a["derived"]
        label = a.get("mvp") or a["id"]
        dom = a["domain"] + (f" · {a['scope']}" if a.get("scope") else "")
        cells = [label, a.get("workingName") or a.get("blueprintName") or "", a["po"], dom]
        cells += [f"**{d['displayName'][e]}**" if e == prod else f"`{d['displayName'][e]}`" for e in envs]
        out.append("| " + " | ".join(cells) + " |")
    out.append(f"\nWhy this works for users: the first words say which {c} area stands behind the agent, the next words say "
               f"what it does, and only a test build carries an environment word. The {prod} name stays clean in Microsoft 365 "
               "Copilot, Teams and the agent store.\n")
    out.append(f"> **Assumption to confirm.** `<PO>` is read as the *process-owner area*: the area that owns the business process. "
               f"If {c} means something else - a fixed prefix or the product-owner team - change `naming.displayTemplate` or the "
               "`poAreas[].token` values in the config and run `python scripts/build_identity_assets.py`. Every name, icon card, "
               "catalogue entry and the stamping step follow automatically.\n")
    out += ["## 2. PO vocabulary\n",
            "Only these tokens are allowed (the validator rejects others). Short tokens keep names within the 30-character limit.\n",
            "| Token in the name | Code in technical names | Process owner | Journeys | Evidence |", "|---|---|---|---|---|"]
    for p in cfg["poAreas"]:
        ev = ", ".join(p.get("evidence") or []) or ("assumption" if p.get("assumed") else "-")
        owner = p.get("processOwner", "") + (" (assumed)" if p.get("assumed") else "")
        out.append(f"| {p['token']} | `{p['code']}` | {owner} | {', '.join(p.get('journeys') or [])} | {ev} |")
    out += ["\n## 3. Domain tokens\n",
            "- One to three words that say what the agent does: *Report*, *Guided Buying*, *Close Cockpit*.",
            "- No \"Agent\", \"Bot\" or \"Copilot\" (redundant in the agent store), no personal names, no environment words.",
            f"- Orchestrators end with *{n.get('orchestratorDomain', 'Lead')}* - the blueprint's lead agent of a journey.",
            "- `Scope` only when the process itself is country-specific; a name should survive a roll-out to more countries.",
            "- Keep the blueprint's working name in `workingName`; the display name is what users see.\n",
            "## 4. Length and characters\n",
            "| Item | Limit | Rule here | Source |", "|---|---|---|---|",
            f"| Agent display name (every surface) | 30 characters | {prod} name ≤ {L.max_base_length(cfg)} so the longest postfix still fits | Agent Builder name limit; Microsoft 365 app short name |",
            "| Allowed characters | - | letters, digits, spaces, hyphen, apostrophe; no `&`, `/`, `·` | proposal (XML and manifest safety) |",
            "| Microsoft 365 app short name | 30 characters | = display name | app manifest schema |",
            f"| Microsoft 365 app full name | 100 characters | \"{n['fullNamePrefix']}<{prod} name>\" plus \" (" + ")\" / \" (".join(nonprod) + ")\" | app manifest schema |",
            "| Short description | 80 characters | ≤ 72 in the config; non-production adds \"" + "\" / \"".join(L.env(cfg, e).get("shortPrefix", "") for e in nonprod) + "\" | app manifest schema |",
            "| Full description | 4,000 characters; 1,000 for declarative agents | non-production starts with a test-build banner | app manifest schema; declarative agent schema |",
            "| Icon | PNG, 100 KB or less | colour 192 × 192 and 32 × 32, outline 32 × 32 | Copilot Studio; Microsoft 365 icon guidance |\n",
            "## 5. Where the environment postfix applies - and where it never does\n",
            "| Artefact | " + " | ".join(envs) + " | Basis |", "|---|" + "---|" * len(envs) + "---|"]
    pf = {e: (L.env(cfg, e).get("postfix") or e) for e in envs}
    out.append("| Agent display name (Copilot Studio, Microsoft 365 Copilot, Teams) | " + " | ".join(
        "no postfix" if e == prod else f"`… {pf[e]}`" for e in envs) + " | stamped before packing (managed agents can't be renamed after import) |")
    out.append("| Microsoft 365 app short and full name | " + " | ".join(
        "no postfix" if e == prod else f"`… {pf[e]}` / `({e})`" for e in envs) + " | same as above |")
    out.append("| Short description | " + " | ".join(
        "plain" if e == prod else f"`{L.env(cfg, e).get('shortPrefix', '')}…`" for e in envs) + " | proposal: a test build is visible as one |")
    out.append("| Agent icon | " + " | ".join("clean" if e == prod else f"{e} band" for e in envs) + " | names **and icons** are stamped per environment |")
    out.append("| Schema name, solution, environment variables, connection references, flows, topics, repository folders | "
               + " | ".join("never" for _ in envs) + " | one package moves through every environment |")
    out.append("| Fabric data agents, repository agents | " + " | ".join("one name" for _ in envs)
               + " | Fabric deployment pipelines keep item names; repository agents have no environment |")
    out.append(f"| Infrastructure (runtime principals, Key Vault, Azure resources) | " + " | ".join("explicit environment token" for _ in envs)
               + f" | follow {c} IT's pattern |\n")
    out.append("Never put an environment into technical names: the same solution moves from development through test into "
               "production, so only what users see carries the environment.\n")
    pre = n["publisherPrefix"]
    out += ["## 6. Technical names (derived, environment-neutral)\n", "| Artefact | Pattern |", "|---|---|",
            f"| Publisher prefix | `{pre}` - {n.get('prefixDecision', 'to confirm')} |",
            f"| Agent schema name | `{pre}_<POCode><Domain>[<Scope>]`, set before the first save; the platform may append a suffix (record it in `overrides.schemaName`) |",
            f"| Solution | `{n['solutionPrefix']}<POCode><Domain>[<Scope>]`, display \"{n['solutionDisplayPrefix']}<{prod} name>\" |",
            f"| Environment variable | agent-specific `{pre}_<POCode><Name>[_<Scope>]`, shared `{pre}_<Name>` |",
            f"| Connection reference | `{pre}_<Connector><POCode>[<Scope>]` |",
            f"| Agent flow / workflow | `<{prod} name> - <Verb> <object>`; starts with a letter |",
            "| Topic | `<Verb> <object>` |",
            f"| Repository folder | kebab-case of the {prod} name: `agents/<slug>/` |",
            "| Microsoft Foundry agent | the slug, e.g. `service-diagnostics` |",
            f"| Fabric data agent | the {prod} name, in every workspace |",
            "| Declarative agent (app package) | `appPackage/<slug>`; one app package per environment with the stamped names |",
            "| GitHub Copilot custom agent | `.github/agents/<name>.agent.md` |\n"]
    rows = [a for a in ex if a["derived"]["schemaName"]]
    if rows:
        out += ["Examples:\n", "| Agent | Schema name | Solution | Environment variables | Connection references | Flows | Folder |", "|---|---|---|---|---|---|---|"]
        for a in rows:
            d = a["derived"]
            out.append(f"| {a.get('mvp') or a['id']} | `{d['schemaName']}` | `{d['solutionUniqueName']}` · \"{d['solutionDisplayName']}\" | "
                       f"`{d['envVarPrefix']}<Name>` | `{pre}_<Connector>{d['connectionContext']}` | \"{d['flowNamePrefix']}<Action>\" | `agents/{d['slug']}/` |")
        out.append("")
    if cfg.get("decisions"):
        out += ["## 7. Decisions to confirm\n", "| # | Decision | Proposed owner | When |", "|---|---|---|---|"]
        for dcs in cfg["decisions"]:
            out.append(f"| {dcs['id']} | {dcs['decision']} | {dcs.get('owner', '')} | {dcs.get('when', '')} |")
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------- colour schema

def colour_md(cfg, palette) -> str:
    c = _cust(cfg)
    out = [_header(cfg, "Colour schema per journey") + "Machine-readable source: `config/palette.json` and `brand/palette.css`.\n",
           "## 1. Sources\n"]
    for k, v in (palette.get("sources") or {}).items():
        out.append(f"- **{k}:** {v}")
    if palette.get("status"):
        out.append(f"- {palette['status']}")
    out += ["", "| Name used here | Hex | Source |", "|---|---|---|"]
    for nc in palette.get("named", []):
        out.append(f"| {nc['name']} | `{nc['hex']}` | {nc.get('source', '')} |")
    out += ["\n## 2. One colour per journey\n",
            "| Journey | Colour (source) | Icon background | Glyph | Contrast | Tints (UI backgrounds) | Text on white | Blueprint colour |",
            "|---|---|---|---|---|---|---|---|"]
    for jid, j in palette["journeys"].items():
        bp = j.get("blueprintColour")
        change = "unchanged" if bp and bp.upper() == j["background"].upper() else (f"was `{bp}`" if bp else "-")
        out.append(f"| {jid} · {j['name']} | {j['brandColour']} ({j.get('themeSlot', '-')}) | `{j['background']}` | `{j['glyph']}` | "
                   f"{j['contrast']}:1 | `{j['tint']}` / `{j['tintStrong']}` | `{j['textOnWhite']}` | {change} |")
    out.append("\nEach journey keeps one colour on every surface: icon background, Copilot Studio icon and accent colour, the "
               "Microsoft 365 app `accentColor`, identity cards and catalogue headers. Agents are told apart by their glyph, not by shades.\n")
    notes = [f"- {jid}: {j['note']}" for jid, j in palette["journeys"].items() if j.get("note")]
    if notes:
        out += ["Notes:\n"] + notes + [""]
    out.append("Contrast follows Microsoft's icon guidance (4.5:1 recommended for best accessibility). Where a brand colour misses "
               "4.5:1 with a white glyph, the package uses either a dark glyph from the palette or an accessible shade of the same "
               "colour - never a new colour.\n")
    out += ["## 3. Environment markers\n", "| Environment | Band | Label | Contrast | Detail |", "|---|---|---|---|---|"]
    for e in L.env_names(cfg):
        m = palette["environments"].get(e)
        if not m:
            out.append(f"| {e} | - | - | - | no marker |")
            continue
        out.append(f"| {e} | `{m['band']}` ({m.get('brandColour', '')}) | `{m['label']}` | {L.contrast(m['band'], m['label'])}:1 | "
                   f"white 4 px separator above the band |")
    ui = palette["ui"]
    out += ["\n## 4. Usage rules\n",
            "- **Icons:** full-bleed journey colour, glyph in the journey's glyph colour, nothing else (see `docs/icons-and-visuals.md`).",
            "- **Copilot Studio:** upload the colour icon; under *Colors* set the journey colour as icon colour or accent colour.",
            "- **Microsoft 365 app details:** `accentColor` = journey colour (in each agent's `identity.json`).",
            f"- **Cards, pages, Adaptive Cards:** body text `{ui['text']}`, backgrounds white or `{ui['background']}`, journey tint for chips and headers; "
            f"fonts {ui.get('headingFont', 'Arial')} (headings) and {ui.get('bodyFont', 'Arial')} (body) with Arial as the fallback.",
            "- **Never** introduce new colours for single agents; never lighten a journey colour or a band that sits just above 4.5:1.\n",
            f"Validate the mapping with {c}'s brand owner before production (decision list in `docs/naming-convention.md`).\n"]
    return "\n".join(out)


# ---------------------------------------------------------------- icons

def icons_md(cfg, palette, lib) -> str:
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    out = [_header(cfg, "Agent icons and visuals"), "## 1. Requirements we design against\n", "| Requirement | Source |", "|---|---|",
           "| Full-bleed colour icon 192 × 192 and a 32 × 32 icon; perfect square, no rounded corners and no border (Microsoft 365 adds both); "
           "flat colour background; contrast 4.5:1 recommended; balance within the 96 × 96 centre; avoid words | Microsoft Learn, Design icons for agent acquisition and management |",
           "| Agent icon is a PNG of 100 KB or less; icon colour and accent colour can be set | Microsoft Learn, Configure agent details and instructions (Copilot Studio) |",
           "| Microsoft 365 app: colour icon 192 × 192, outline icon 32 × 32 white on transparent | Microsoft 365 app manifest schema |",
           "| Environment-specific names **and icons** stamped before packing | this package (`scripts/stamp_identity.py`) |\n",
           "## 2. Design\n",
           "- Background: the journey colour, full bleed (`docs/color-schema.md`).",
           "- Glyph: one distinct glyph per agent, placed in the 96 × 96 centre - *filled* style on the colour icon, *regular* style on the outline icon. "
           "Glyphs come from Microsoft's **Fluent UI System Icons** (MIT) and from the **Frontier glyphs** drawn on the same 24-unit grid (MIT).",
           f"- {' and '.join(nonprod)}: a 36-pixel band at the bottom, outside the 96 × 96 balance area, with a 4-pixel white separator and the "
           "environment word. At 32 × 32 the word is not readable, but the band colour still shows the environment.",
           f"- {prod}: clean icon.",
           "- Icons are rendered by `scripts/raster.py` (Python standard library): the same pixels on every machine, no browser or image library needed.\n",
           "## 3. Files per agent (`agents/<slug>/identity/`)\n", "| File | Size | Use |", "|---|---|---|"]
    sfx = [L.env_suffix(cfg, e) for e in nonprod]
    out += [f"| `color-192.png`, " + ", ".join(f"`color-192{s}.png`" for s in sfx) + " | 192 × 192 | Copilot Studio agent icon; `iconbase64` in `bot.xml`; Microsoft 365 colour icon |",
            f"| `color-32.png`, " + ", ".join(f"`color-32{s}.png`" for s in sfx) + " | 32 × 32 | `color32x32` (optional) and small previews |",
            "| `outline-32.png` | 32 × 32, white on transparent | Microsoft 365 outline icon |",
            "| `icon.svg`, " + ", ".join(f"`icon{s}.svg`" for s in sfx) + ", `outline.svg` | vector | sources; the PNGs are rendered from the same geometry |",
            "| `identity.json` | - | names, descriptions, colours, files and Microsoft 365 details per environment |",
            "| `card.svg` (`card.png` when a converter is available) | 1200 × 630 | identity card for catalogue pages, SharePoint news, adoption mails |\n",
            "Agents without environments (Fabric data agents, repository agents) have only the clean icon.\n",
            "## 4. Where icons are set\n", "| Surface | How | Status |", "|---|---|---|",
            "| Copilot Studio (maker view) | Build tab → agent icon → upload; Colors | Microsoft Learn |",
            "| Unpacked solution | `bots/<schemaname>/bot.xml` → `<iconbase64>`; `stamp_identity.py` sets it per environment | element in Microsoft's published samples; verify with your first export |",
            "| Teams and Microsoft 365 Copilot | app details of the Teams / Microsoft 365 channel; stored separately from the maker icon | verify in DEV; the stamping step updates `teams.colorIcon` / `teams.outlineIcon` only when they already exist |",
            "| Declarative agent (app package) | `color.png` and `outline.png` of each environment's app package | app manifest schema |",
            "| Microsoft-managed agents (for example Employee Self-Service) | customisation layer, if the product allows it | verify in DEV |\n",
            "Teams and Microsoft 365 Copilot can cache agent icons for a while after publishing.\n",
            "## 5. Visuals in this package\n", "| File | Content |", "|---|---|",
            "| `visuals/agent-family.svg` (.png) | all agents by journey, with status and the MVP icons per environment |",
            "| `visuals/mvp-identity-sheet.svg` (.png) | MVP agents: icons per environment and size, names, technical names |",
            "| `visuals/colour-schema.svg` (.png) | brand palette, journey colours with contrast, environment markers |",
            "| `catalog.html` | the whole package on one page for people: open it in a browser |",
            "| `agents/<slug>/identity/card.svg` (.png) | one identity card per agent |\n",
            "## 6. Regenerate\n", "```bash",
            "python scripts/build_identity_assets.py      # names, icons (SVG + PNG), cards, visuals, docs, catalogue",
            "python scripts/validate_identity.py          # must report 0 errors",
            "python -m unittest discover -s scripts/tests -v", "```",
            "PNG copies of cards and visuals need an SVG converter (cairosvg, rsvg-convert, or Node.js with sharp); icons never do.\n",
            "To add an agent: add an entry to `config/agent-identity.json` (copy a similar one), pick a glyph from `scripts/glyphs/glyphs.json`, rebuild and validate. "
            "To add a Fluent glyph: download its 24 px filled and regular SVGs from the Fluent UI System Icons repository and run "
            "`python scripts/import_fluent_glyphs.py <name> <filled.svg> <regular.svg> --keywords \"word, word\"`.\n"]
    n_fluent = sum(1 for g in lib["glyphs"].values() if g["source"] == "fluent")
    out.append(f"Glyph library: {len(lib['glyphs'])} glyphs ({n_fluent} Fluent UI System Icons, {len(lib['glyphs']) - n_fluent} Frontier glyphs).\n")
    return "\n".join(out)


# ---------------------------------------------------------------- harness integration

def harness_md(cfg) -> str:
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    root = (cfg.get("repository") or {}).get("identityRoot", "identity")
    test_env = nonprod[-1] if nonprod else prod
    out = [_header(cfg, "Using the package in the repository and the release pipeline"),
           "## 1. Where the files go\n", "| Package path | Repository path |", "|---|---|",
           f"| `agents/<slug>/identity/*` | `{root}/agents/<slug>/identity/` (or next to each agent's harness files) |",
           f"| `config/*`, `scripts/*` | `{root}/config/`, `{root}/scripts/` |",
           "| `brand/*`, `visuals/*`, `docs/*`, `catalog.html` | `docs/identity/` |",
           "| `github/instructions/agent-identity.instructions.md` | `.github/instructions/` |",
           "| `pipelines/azure-pipelines/stamp-identity.yml` | `pipelines/templates/` |",
           "| `pipelines/github-actions/identity-validate.yml` | `.github/workflows/` |\n",
           "Keep `config`, `scripts`, `agents` and `brand` as siblings, or pass `--root` to the scripts.\n",
           "## 2. In the release pipeline\n", "| Stage | Identity step |", "|---|---|",
           f"| Export from development | after `pac solution unpack`: `stamp_identity.py --env {prod} --apply` turns development names and icons back into the canonical form before the pull request |",
           "| Pull request | `validate_identity.py` and `python -m unittest discover -s <scripts>/tests` (both blocking) |",
           f"| Test deployment | copy the unpacked tree; `stamp_identity.py --env {test_env} --apply --strict` → pack → import; then `stamp_identity.py --env {prod} --apply --strict` → pack the production artefact |",
           f"| Production | import the **identical** {prod}-stamped package; no rebuild |\n",
           "Agents imported as managed can't be renamed in the target environment, which is why stamping happens before packing.\n",
           "## 3. Maker checklist in development\n",
           "1. Preferred solution set before the first save.",
           "2. Schema name `<prefix>_<stem>` from `identity.json`, set under *Advanced settings* before the first save.",
           f"3. Display name `<{prod} name> {L.env(cfg, nonprod[0]).get('postfix', nonprod[0]) if nonprod else ''}`, icon `color-192{L.env_suffix(cfg, nonprod[0]) if nonprod else ''}.png`, description from `identity.json`.",
           "4. If the platform appended a suffix to the schema name, record it in `overrides.schemaName`.\n",
           "## 4. Other kinds of agents\n", "| Kind | Names and icons |", "|---|---|",
           "| Declarative agent (Microsoft 365 Copilot) | one app package per environment: `name` and `description` in the agent manifest (≤ 100 and ≤ 1,000 characters), short and full names in the app manifest, `color.png` and `outline.png` from `identity/` |",
           "| Microsoft Foundry agent | agent name = slug; when published to Microsoft 365 Copilot or Teams, use the display names and icons of the environment |",
           "| Fabric data agent | one item name in every workspace (deployment pipelines keep names); description from `identity.json` |",
           "| GitHub Copilot custom agent | `.github/agents/<name>.agent.md` front matter: the production name and the short description |",
           "| Microsoft-managed agent (for example Employee Self-Service) | verify in development whether the customisation layer can set the name and icon; otherwise rely on the description banner |\n",
           "## 5. What still needs a check in development\n", "| # | Check | Expected result |", "|---|---|---|",
           "| V-1 | `bot.xml` of the first agent export | `<name>` and `<iconbase64>` present (as in Microsoft's samples) |",
           "| V-2 | Teams / Microsoft 365 icon fields after publishing | `applicationmanifestinformation` with `teams.colorIcon` / `teams.outlineIcon`, or icons set in the channel |",
           "| V-3 | Suffix appended to schema names | recorded in `overrides.schemaName` |",
           f"| V-4 | Post-import name check | names in {test_env} equal `displayName.{test_env}` |\n"]
    return "\n".join(out)


# ---------------------------------------------------------------- evidence

def evidence_md(cfg) -> str:
    out = ["# Evidence used in this package\n"]
    if cfg.get("evidence"):
        out += ["| ID | Source | Date | Used for |", "|---|---|---|---|"]
        for e in cfg["evidence"]:
            out.append(f"| {e['id']} | {e.get('title', '')} | {e.get('date', '')} | {e.get('usedFor', '')} |")
        out.append("")
    out += [f"Microsoft documentation (checked {MS_CHECKED}):\n"]
    for title, url, used in MS_SOURCES:
        out.append(f"- {title} - {url} - {used}")
    out.append("\nAssumptions are marked as such in the config (`assumed: true`) and listed as decisions in `docs/naming-convention.md`.\n")
    return "\n".join(out)


# ---------------------------------------------------------------- catalogue (markdown)

def catalog_md(cfg, palette, by_journey) -> str:
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    total = sum(len(v) for v in by_journey.values())
    out = ["# Agent identity catalogue\n",
           f"Generated from `config/agent-identity.json` v{cfg['version']} ({cfg['date']}) by `scripts/build_identity_assets.py`. "
           "Do not edit by hand: change the tokens in the config and rebuild.\n",
           f"Display name = `{_rule(cfg)}`; {prod} has no postfix. Technical names never carry an environment.\n",
           f"**{total} agents** in {len(by_journey)} journeys · **{len(_mvps(cfg))} MVP agents** · publisher prefix `{cfg['naming']['publisherPrefix']}`.\n"]
    for jid, items in by_journey.items():
        j = palette["journeys"][jid]
        out.append(f"\n## {jid} · {j['name']}\n")
        pos = ", ".join(sorted({a["po"] for a in items}))
        out.append(f"Colour **{j['brandColour']}** `{j['background']}` · glyph `{j['glyph']}` · contrast {j['contrast']}:1 · PO area(s): {pos}\n")
        out.append("| Icon | " + prod + " name | " + " | ".join(nonprod) + " | PO · Domain | Kind | Status | Technical | Folder |")
        out.append("|---|---|" + "---|" * len(nonprod) + "---|---|---|---|---|")
        for a in items:
            d = a["derived"]
            icon = f'<img src="../agents/{d["slug"]}/identity/color-192.png" width="40" alt="{L.esc(d["displayName"][prod])} icon">'
            envcells = [f"`{d['displayName'][e]}`" if L.is_scoped(a) else "same" for e in nonprod]
            tech = d["schemaName"] or (d["technical"] or {}).get("value") or "-"
            potok = f"{a['po']} · {a['domain']}" + (f" · {a['scope']}" if a.get("scope") else "")
            out.append(f"| {icon} | **{d['displayName'][prod]}** | " + " | ".join(envcells)
                       + f" | {potok} | {L.KINDS[a['kind']]['label']} | {_status_label(palette, a)} | `{tech}` | `agents/{d['slug']}/` |")
        for a in items:
            d = a["derived"]
            out.append(f"\n### {d['displayName'][prod]} ({a['id']})\n")
            out.append(f'<img src="../agents/{d["slug"]}/identity/card.svg" width="600" alt="Identity card for {L.esc(d["displayName"][prod])}">\n')
            out.append(f"- **Purpose (short):** {a['shortDescription']}")
            out.append(f"- **Full description:** {a['fullDescription']}")
            if a.get("audience"):
                out.append(f"- **Audience:** {a['audience']}")
            out.append(f"- **Process owner area:** {L.po_area(cfg, a['po']).get('processOwner', '')}")
            out.append(f"- **Owner (blueprint):** {a.get('owner') or 'to confirm'}")
            if a.get("workingName") or a.get("blueprintName"):
                out.append(f"- **Working name:** {a.get('workingName') or a.get('blueprintName')}")
            out.append(f"- **Channels:** {', '.join(a.get('channels') or []) or 'to confirm'}")
            out.append(f"- **Status:** {a.get('status', '')}")
            if d["schemaName"]:
                out.append(f"- **Technical:** schema `{d['schemaName']}` · solution `{d['solutionUniqueName']}` (\"{d['solutionDisplayName']}\") · "
                           f"variables `{d['envVarPrefix']}…` · connection references `{cfg['naming']['publisherPrefix']}_<Connector>{d['connectionContext']}` · "
                           f"flows \"{d['flowNamePrefix']}<Action>\"")
            elif d.get("technical"):
                out.append(f"- **Technical:** {d['technical']['label']} `{d['technical']['value']}`")
            out.append(f"- **Icon:** glyph `{a['glyph']}` on `{d['icon']['background']}` · files in `agents/{d['slug']}/identity/`")
            if a.get("notes"):
                out.append(f"- **Note:** {a['notes']}")
            out.append(f"- **Evidence:** {', '.join(a.get('evidence') or []) or 'blueprint hypothesis'}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------- README, changelog, notices, instructions

def readme_md(cfg, palette, by_journey, have_png) -> str:
    c = _cust(cfg)
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    envs = L.env_names(cfg)
    total = sum(len(v) for v in by_journey.values())
    ext = "png" if have_png else "svg"
    out = [f"# {c} agent identity package\n",
           f"Version {cfg['version']} · {cfg['date']} · {cfg.get('status', 'proposal')}\n",
           f"Naming convention, colour schema and icons for all **{total} agents** of the {c} Frontier blueprint "
           f"({len(by_journey)} journeys, MVPs included), ready to drop into {c}'s repository and release pipeline. Every name, "
           "colour and icon is generated from one config file and checked by a validator, so people, GitHub Copilot and the pipelines can't drift from it.\n",
           f"![Agent family](visuals/agent-family.{ext})\n",
           "## The rule in one line\n",
           f"**Display name = `{_rule(cfg)}`** - PO is the process-owner area, Domain is what the agent does, {prod} carries no postfix. "
           "Technical names (schema, solution, variables, connection references, flows, folders) never carry an environment.\n",
           "| Icon | Agent | Working name | " + " | ".join(envs) + " | Technical name |",
           "|---|---|---|" + "---|" * len(envs) + "---|"]
    for a in _examples(cfg):
        d = a["derived"]
        tech = d["schemaName"] or (d["technical"] or {}).get("value") or "-"
        out.append(f'| <img src="agents/{d["slug"]}/identity/color-192.png" width="40"> | {a.get("mvp") or a["id"]} | {a.get("workingName") or a.get("blueprintName") or ""} | '
                   + " | ".join(f"**{d['displayName'][e]}**" if e == prod else f"`{d['displayName'][e]}`" for e in envs) + f" | `{tech}` |")
    out += [f"\n## Colours: one per journey, from {c}'s own palette\n", "| Journey | Colour | Glyph | Contrast | PO area |", "|---|---|---|---|---|"]
    for jid, j in palette["journeys"].items():
        pos = ", ".join(sorted({a["po"] for a in by_journey.get(jid, [])}))
        out.append(f"| {jid} · {j['name']} | {j['brandColour']} `{j['background']}` | `{j['glyph']}` | {j['contrast']}:1 | {pos} |")
    bands = ", ".join(f"{e} icons carry a {palette['environments'][e].get('brandColour', palette['environments'][e]['band'])} band" for e in nonprod)
    out.append(f"\n{bands}; {prod} icons are clean. Details: `docs/color-schema.md`.\n")
    out += ["## What is inside\n", "```text",
            "README.md                          this file",
            "catalog.html                       the whole package on one page - open it in a browser",
            "docs/naming-convention.md          the rule, PO vocabulary, limits, where the postfix applies, technical names, decisions",
            "docs/color-schema.md               palette sources, journey colours, contrast, usage rules",
            "docs/icons-and-visuals.md          icon requirements, design, files and where to set them",
            "docs/harness-integration.md        where files go in the repository, pipeline stages, maker checklist",
            "docs/agent-identity-catalog.md     generated catalogue of all agents",
            "docs/evidence.md                   evidence and Microsoft documentation used",
            "config/agent-identity.json         SOURCE OF TRUTH: tokens per agent + derived names",
            "config/palette.json                brand palette, journey colours, environment markers",
            "brand/palette.css                  CSS variables for pages and cards",
            "agents/<slug>/identity/            per agent: identity.json, colour 192/32 per environment, outline 32, SVG sources, card",
            "visuals/                           agent family, MVP identity sheet, colour schema",
            "scripts/build_identity_assets.py   regenerates names, icons, cards, visuals, docs and catalogue (Python only)",
            "scripts/validate_identity.py       blocking checks for pull requests",
            "scripts/stamp_identity.py          stamps environment names and icons into an unpacked solution before packing",
            "scripts/tests/                     unit tests with a synthetic unpacked solution",
            "pipelines/                         Azure Pipelines step template and GitHub Actions workflow",
            "github/instructions/               GitHub Copilot instructions (copy to .github/instructions/)", "```\n",
            "## Quick start\n", "```bash",
            "python scripts/validate_identity.py                    # 0 errors expected",
            "python -m unittest discover -s scripts/tests -v        # naming and stamping tests",
            f"python scripts/stamp_identity.py --env {nonprod[-1] if nonprod else prod} --solution-dir <unpacked solution>   # dry run shows the changes", "```",
            "Change a name or colour: edit `config/agent-identity.json` or `config/palette.json`, then `python scripts/build_identity_assets.py` and validate again. "
            "Python 3.9 or later is all it needs.\n"]
    counts = {}
    for items in by_journey.values():
        for a in items:
            lab = _status_label(palette, a) if a.get("statusClass") != "mvp" else "MVP"
            counts[lab] = counts.get(lab, 0) + 1
    out += ["## Status\n", "- Agents: " + ", ".join(f"{v} {k}" for k, v in counts.items()) + ".",
            "- Verified against Microsoft documentation: name and description limits, icon rules, Microsoft 365 app manifest limits (`docs/evidence.md`).",
            "- To verify in development: `bot.xml` of the first export, Teams / Microsoft 365 icon fields, schema-name suffix (`docs/harness-integration.md` §5)."]
    if any(p.get("assumed") for p in cfg["poAreas"]):
        out.append("- Assumption: `<PO>` = process-owner area; tokens marked as assumed in `docs/naming-convention.md` §2.")
    if cfg.get("decisions"):
        out.append(f"- Decisions to confirm: {', '.join(d['id'] for d in cfg['decisions'])} (`docs/naming-convention.md` §7).")
    out += ["\nNo personal data, tenant identifiers or secrets are in this package; the test fixture is synthetic.\n",
            "## Licence and notices\n",
            "Scripts and Frontier glyphs: MIT, from the Frontier Envisioning plugin (Copyright (c) 2026 Urs Rüegg). "
            "Fluent glyphs: Fluent UI System Icons by Microsoft, MIT. "
            f"Names, colours, logo and descriptions are {c}'s. See `THIRD-PARTY-NOTICES.md`.\n"]
    return "\n".join(out)


def changelog_md(cfg) -> str:
    out = ["# Changelog\n"]
    for entry in cfg.get("changelog") or [{"version": cfg["version"], "date": cfg["date"], "items": ["First version."]}]:
        out.append(f"## {entry['version']} - {entry['date']}\n")
        out += [f"- {i}" for i in entry["items"]]
        out.append("")
    return "\n".join(out)


MIT_FLUENT = """MIT License

Copyright (c) 2020 Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


def notices_md(cfg, palette) -> str:
    c = _cust(cfg)
    out = ["# Third-party notices\n",
           "## Fluent UI System Icons\n",
           "The Fluent glyphs in `scripts/glyphs/glyphs.json` (source `fluent`) and the icons generated from them come from "
           "Fluent UI System Icons by Microsoft, https://github.com/microsoft/fluentui-system-icons, under the MIT License.\n",
           MIT_FLUENT, "",
           "## Frontier Envisioning plugin\n",
           "The scripts, the Frontier glyphs (source `frontier`) and the document templates come from the Frontier Envisioning "
           "plugin, MIT License, Copyright (c) 2026 Urs Rüegg. Every script carries an `SPDX-License-Identifier: MIT` header.\n"]
    lg = palette.get("logo") or {}
    if lg.get("file"):
        out += [f"## {c} logo\n", f"`{lg['file']}` shows {c}'s logo{(' (' + lg['source'] + ')') if lg.get('source') else ''}. "
                f"The logo is {c}'s trademark; use it according to {c}'s brand rules.\n"]
    return "\n".join(out)


def instructions_md(cfg) -> str:
    n = cfg["naming"]
    prod = L.prod_env(cfg)
    nonprod = L.nonprod_envs(cfg)
    return "\n".join([
        "---", 'applyTo: "**"', "---", f"# Agent identity rules for {_cust(cfg)} agents\n",
        "- The single source of truth for agent names, descriptions, colours and icons is `config/agent-identity.json` (plus `config/palette.json`). "
        f"Never invent or retype an agent name - read `derived.displayName.<ENV>` from the config or `agents/<slug>/identity/identity.json`.",
        f"- Display name pattern: `{_rule(cfg)}`; {prod} has no postfix; at most {n['maxDisplayLength']} characters ({prod} at most {L.max_base_length(cfg)}).",
        f"- Never put {', '.join(nonprod + [prod])} or any environment word into schema names, solution names, environment variables, connection references, flow or topic names, or folder names.",
        f"- Schema names start with the publisher prefix (`{n['publisherPrefix']}`) and are set before the first save.",
        "- New agent: add an entry to `config/agent-identity.json` (PO token from `poAreas`, Domain 1-3 words, glyph from `scripts/glyphs/glyphs.json`), run `python scripts/build_identity_assets.py`, "
        "then `python scripts/validate_identity.py`; commit the generated files. Never edit generated PNG, SVG, `identity.json` or the catalogue by hand.",
        "- Colours come only from `config/palette.json`; one colour per journey; icon contrast at least 4.5:1.",
        f"- After exporting from development, run `python scripts/stamp_identity.py --env {prod} --solution-dir <unpacked> --apply` before opening the pull request.",
        f"- Release pipelines stamp each environment's names and icons with `--apply --strict` before `pac solution pack`; {prod} imports the identical {prod}-stamped package.",
        "- Repository agents use the production name and short description in `.github/agents/<name>.agent.md`.", ""])


# ---------------------------------------------------------------- catalogue (HTML, for people)

def catalog_html(cfg, palette, by_journey, root: Path) -> str:
    c = _cust(cfg)
    ui = palette["ui"]
    prod = L.prod_env(cfg)
    envs = L.env_names(cfg)

    def uri(p: Path) -> str:
        return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii") if p.exists() else ""

    css = f"""
:root{{--text:{ui['text']};--muted:{ui['muted']};--line:{ui['line']};--bg:{ui['background']};--accent:{ui['accent']}}}
*{{box-sizing:border-box}}body{{margin:0;font-family:{ui.get('bodyFont', 'Arial')},'Liberation Sans',Arial,Helvetica,sans-serif;color:var(--text);background:#fff;line-height:1.45}}
header{{padding:40px 48px 24px;border-bottom:1px solid var(--line)}}h1{{font-size:34px;margin:0 0 6px}}h2{{font-size:24px;margin:0}}
.sub{{color:var(--muted);font-size:16px}}.rule{{display:inline-block;margin-top:14px;padding:10px 14px;background:var(--bg);border-radius:8px;font-family:Consolas,'Liberation Mono',monospace}}
main{{padding:24px 48px 48px}}.journey{{margin:28px 0 36px}}.jhead{{padding:14px 18px;border-radius:10px;display:flex;justify-content:space-between;align-items:baseline;gap:16px}}
.jhead small{{font-size:14px;opacity:.95}}table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted);font-weight:600;font-size:13px}}td img{{width:44px;height:44px;border-radius:6px;display:block}}.envs img{{width:30px;height:30px;display:inline-block;margin-right:4px;border-radius:4px}}
.name{{font-weight:700;font-size:15px}}.desc{{color:var(--muted)}}code{{font-family:Consolas,'Liberation Mono',monospace;font-size:12.5px;background:var(--bg);padding:1px 4px;border-radius:4px}}
.chip{{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}}
.palette{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}}.sw{{width:120px;height:64px;border-radius:8px;padding:8px;font-size:12px;border:1px solid var(--line)}}
footer{{padding:16px 48px 40px;color:var(--muted);font-size:13px}}@media print{{header,main,footer{{padding-left:0;padding-right:0}}.journey{{break-inside:avoid}}}}"""
    h = [f"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
         f"<title>{L.esc(c)} agent identity catalogue</title><style>{css}</style></head><body>",
         f"<header><h1>{L.esc(c)} agent identity catalogue</h1>",
         f"<div class=\"sub\">Version {L.esc(cfg['version'])} · {L.esc(cfg['date'])} · {L.esc(cfg.get('status', 'proposal'))} · "
         f"{sum(len(v) for v in by_journey.values())} agents in {len(by_journey)} journeys</div>",
         f"<div class=\"rule\">Display name = {L.esc(_rule(cfg))} &nbsp;·&nbsp; {L.esc(prod)} carries no postfix</div>",
         "<div class=\"palette\">"]
    for jid, j in palette["journeys"].items():
        h.append(f"<div class=\"sw\" style=\"background:{j['background']};color:{j['glyph']}\"><b>{L.esc(jid)}</b><br>{L.esc(j['background'])}<br>{j['contrast']}:1</div>")
    for e in L.nonprod_envs(cfg):
        m = palette["environments"][e]
        h.append(f"<div class=\"sw\" style=\"background:{m['band']};color:{m['label']}\"><b>{L.esc(e)} band</b><br>{L.esc(m['band'])}</div>")
    h.append("</div></header><main>")
    for jid, items in by_journey.items():
        j = palette["journeys"][jid]
        pos = ", ".join(sorted({a["po"] for a in items}))
        h.append(f"<section class=\"journey\"><div class=\"jhead\" style=\"background:{j['background']};color:{j['glyph']}\">"
                 f"<h2>{L.esc(jid)} · {L.esc(j['name'])}</h2><small>PO area: {L.esc(pos)} · {L.esc(j['brandColour'])} {L.esc(j['background'])}</small></div>")
        h.append("<table><thead><tr><th></th><th>Name and purpose</th><th>Names per environment</th><th>PO · Domain</th><th>Status</th><th>Technical</th></tr></thead><tbody>")
        for a in items:
            d = a["derived"]
            folder = root / "agents" / d["slug"] / "identity"
            st = palette["statusStyles"].get(a.get("statusClass", "hypothesis")) or palette["statusStyles"]["hypothesis"]
            lab = _status_label(palette, a)
            env_html = []
            for e in envs:
                if e != prod and not L.is_scoped(a):
                    continue
                env_html.append(f"<div><img src=\"{uri(folder / ('color-192' + L.env_suffix(cfg, e) + '.png'))}\" alt=\"{L.esc(e)} icon\"> "
                                f"<code>{L.esc(d['displayName'][e])}</code></div>")
            tech = []
            if d["schemaName"]:
                tech = [f"<code>{L.esc(d['schemaName'])}</code>", f"<code>{L.esc(d['solutionUniqueName'])}</code>"]
            elif d.get("technical"):
                tech = [f"{L.esc(d['technical']['label'])}: <code>{L.esc(d['technical']['value'])}</code>"]
            tech.append(f"<code>agents/{L.esc(d['slug'])}/</code>")
            h.append(f"<tr><td><img src=\"{uri(folder / 'color-192.png')}\" alt=\"{L.esc(d['displayName'][prod])} icon\"></td>"
                     f"<td><div class=\"name\">{L.esc(d['displayName'][prod])}</div><div class=\"desc\">{L.esc(a['shortDescription'])}</div>"
                     f"<div class=\"desc\">{L.esc(L.KINDS[a['kind']]['label'])} · owner {L.esc(a.get('owner') or 'to confirm')}</div></td>"
                     f"<td class=\"envs\">{''.join(env_html)}</td><td>{L.esc(a['po'])} · {L.esc(a['domain'])}{(' · ' + L.esc(a['scope'])) if a.get('scope') else ''}</td>"
                     f"<td><span class=\"chip\" style=\"background:{st['bg']};color:{st['fg']}\">{L.esc(lab)}</span></td><td>{'<br>'.join(tech)}</td></tr>")
        h.append("</tbody></table></section>")
    h.append(f"</main><footer>Generated by scripts/build_identity_assets.py from config/agent-identity.json. Icons follow Microsoft's agent icon guidance "
             f"(192 × 192 full-bleed colour, 32 × 32, 4.5:1 contrast). Glyphs: Fluent UI System Icons (MIT) and Frontier glyphs (MIT). "
             f"Names, colours and descriptions are {L.esc(c)}'s.</footer></body></html>")
    return "".join(h)
