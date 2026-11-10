# Identity kit reference

## 1. Package layout (what the customer receives)

```text
README.md, CHANGELOG.md, THIRD-PARTY-NOTICES.md, catalog.html
config/agent-identity.json        source of truth: tokens per agent + derived names
config/palette.json               brand palette, journey colours, environment markers, status styles
config/agent-identity.schema.json JSON schema of the config
brand/palette.css (+ logo.png)    CSS variables
agents/<slug>/identity/           identity.json, color-192*.png, color-32*.png, outline-32.png, icon*.svg, outline.svg, card.svg/.png
visuals/                          agent-family, mvp-identity-sheet, colour-schema (.svg, .png)
docs/                             naming-convention, color-schema, icons-and-visuals, harness-integration, agent-identity-catalog, evidence
scripts/                          build_identity_assets.py, validate_identity.py, stamp_identity.py, import_fluent_glyphs.py,
                                  identity_lib.py, identity_visuals.py, identity_docs.py, raster.py, glyphs/glyphs.json, tests/
pipelines/                        azure-pipelines/stamp-identity.yml, github-actions/identity-validate.yml
github/instructions/              agent-identity.instructions.md for GitHub Copilot
```

## 2. `agent-identity.json` (frontier-agent-identity/1.0)

| Field | Meaning |
|---|---|
| `customer.name`, `customer.short` | legal name and short name used in full names, cards and docs |
| `naming.displayTemplate` | default `{po} {domain} {scope} {env}` |
| `naming.maxDisplayLength` | 30; `maxBaseLength` is derived from the longest postfix |
| `naming.publisherPrefix`, `allowedPrefixes`, `prefixDecision` | Power Platform publisher prefix and its decision status |
| `naming.solutionPrefix`, `solutionDisplayPrefix`, `fullNamePrefix` | solution unique-name prefix, solution display prefix, app full-name prefix |
| `naming.stripLeadingFromStem` | optional, avoids doubled words in solution names (for example `["HR"]`) |
| `environments[]` | ordered; `name`, `postfix`, `shortPrefix`, `fullBanner`; production has `"production": true` |
| `poAreas[]` | `token` (in names), `code` (in technical names), `processOwner`, `journeys`, `evidence`, `assumed` |
| `agents[]` | `id`, `journey`, `role` (orchestrator, specialist, data), `po`, `domain`, `scope`, `kind`, `glyph`, `status`, `statusClass`, `mvp`, `shortDescription` (≤ 72), `fullDescription`, `audience`, `owner`, `channels`, `workingName`, `blueprintName`, `evidence`, `notes`, `overrides` (`schemaName`, `solutionUniqueName`, `slug`) |
| `agents[].derived` | generated - never edit |
| `decisions[]`, `evidence[]`, `changelog[]` | rendered into the docs |

## 3. `palette.json` (frontier-agent-palette/1.0)

`named[]` (brand colours with sources), `journeys{}` (`background`, `glyph`, `contrast`, `tint`, `tintStrong`, `textOnWhite`, `brandColour`, `themeSlot`, `note`), `environments{}` (`band`, `label`, `separator`, `brandColour`), `ui{}` (`text`, `muted`, `background`, `line`, `accent`, `dark`, `headingFont`, `bodyFont`), `statusStyles{}` (chip colours per status class), `sourceShort`, `status`, `wordmark`, `logo`.

The HTML catalogue renders status text with an accessible shade against the
status background, targeting 4.6:1 to keep a margin above the 4.5:1 normal-text
minimum. Journey-header subtitles retain the full foreground opacity; an icon
colour pair's contrast must not be reduced by a translucent text style.
These display corrections do not change the source palette, icon artwork,
names or identity cards. Browser contrast checks cover the actual HTML output.

## 4. Commands

| Step | Command |
|---|---|
| Brand from an Office file | `python scripts/read_office_theme.py <file> --out brand.json --customer "<name>" --short <short> --evidence-id E12` |
| Seed | `python scripts/seed_identity.py --blueprint blueprint.json --brand brand.json --prefix <p> --envs DEV,TEST,PROD --po "D1=Sales" --out-dir <dir>` |
| Kit | `python scripts/make_kit.py --config <dir>/agent-identity.json --palette <dir>/palette.json --out <kit> [--logo logo.png] [--identity-root identity] --zip "<Customer> - agent identity package v1.0"` |
| Blueprint | `python scripts/apply_identity.py --blueprint blueprint.json --kit <kit> --out blueprint.json --colours` |
| Inside the kit | `python scripts/build_identity_assets.py`, `python scripts/validate_identity.py`, `python -m unittest discover -s scripts/tests -v`, `python scripts/stamp_identity.py --env TEST --solution-dir <unpacked> [--apply --strict]` |

`make_kit.py` exits 1 when the validator reports errors or a unit test fails; the zip is written only when both pass.

## 5. Validator checks

N1 names fit 30 characters, allowed characters, non-production postfix · N2 production name leaves room for the longest postfix · N3 no environment words in technical names (and none in production names) · N4 unique names, slugs, schema and solution names · N5 publisher prefix rules, schema-name pattern · N6 known PO token, journey, glyph and kind; derived names up to date · D1 description limits (72/80, 4,000, 1,000 for declarative agents) · C1 icon contrast ≥ 4.5:1 · C2 band label contrast ≥ 4.5:1 · F1 icon files and sizes, PNG ≤ 100 KB · F2 transparent outline, opaque colour icons · F3 identity.json up to date · W1 glyph twice in a journey (warning) · W2 PO area not linked to the journey (warning).

## 6. Customising

- **Another environment:** add it to `environments` before production; add its band to `palette.environments`; rebuild.
- **Renamed agent:** change `po`/`domain`/`scope`, rebuild; the old folder is removed and the stamping step maps by schema name (record a platform suffix in `overrides.schemaName`).
- **New glyph:** pick one from `scripts/glyphs/glyphs.json`, or import a Fluent glyph with `import_fluent_glyphs.py <name> <filled.svg> <regular.svg> --keywords "…"`.
- **Logo:** `make_kit.py --logo <png> --logo-aspect <width/height>` - only with the customer's permission.
