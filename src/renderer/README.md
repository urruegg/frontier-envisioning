# Blueprint renderer

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Renderer source guide; document revision, not product version |
| References | [Documentation](../../docs/README.md), [Renderer instructions](../../.github/instructions/renderer.instructions.md), [Testing strategy](../../docs/engineering/testing-strategy.md) |

Sources of the Frontier Company Blueprint HTML: `skeleton.html` (page shell with the `/*__CSS__*/` and `/*__JS__*/` slots and the JSON data island), `template.css` and `template.js` (14 views). `python tools/dev.py template` assembles them into `plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html`, which `build_blueprint.py` fills with a blueprint's data. Rules: `.github/instructions/renderer.instructions.md`.
