# Blueprint renderer

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Renderer source guide; document revision, not product version |
| References | [Documentation](../../docs/README.md), [Renderer instructions](../../.github/instructions/renderer.instructions.md), [Testing strategy](../../docs/engineering/testing-strategy.md) |

Sources of the Frontier Company Blueprint HTML: `skeleton.html` (page shell with the `/*__CSS__*/` and `/*__JS__*/` slots and the JSON data island), `template.css` and `template.js` (17 views across Vision, Design, Build and Workshops). `python tools/dev.py template` assembles them into `plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html`, which `build_blueprint.py` fills with a blueprint's data. Rules: `.github/instructions/renderer.instructions.md`.

The optional `parts` labels/descriptions override navigation copy without changing route IDs. PRD requirements use the embedded shared Python model's IDs; the Markdown download does not renumber them. Plan derives stages from the existing Agent Factory checks and supports journey/MVP filtering. Its CSV is a handover format requiring destination field mapping, not a native Azure Boards or GitHub Projects import. WIP limits are advisory, not approval.

Risk ratings, status and notes use `risk:<id>` feedback validations; MVP scope uses `prd:scope`. They share the existing localStorage namespace and Discovery JSON/text exports. Optional PRD/risk fields hide unavailable pages; Plan falls back to default phases/checks without a board configuration. Keep the current modal, keyboard, contrast and locally scrollable layout safeguards when extending these views.

Run `python tools/dev.py template package demo dom` and `python tools/dev.py site e2e`. Feature regressions and actual Markdown/CSV/feedback download tests live in `tests/dom/handover-17.test.mjs` and `tests/e2e/handover-17.spec.mjs`. Browser tests attach light/dark screenshots at 1440px and 320px.
