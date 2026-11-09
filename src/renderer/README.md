# Blueprint renderer

Sources of the Frontier Company Blueprint HTML: `skeleton.html` (page shell with the `/*__CSS__*/` and `/*__JS__*/` slots and the JSON data island), `template.css` and `template.js` (14 views). `python tools/dev.py template` assembles them into `plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html`, which `build_blueprint.py` fills with a blueprint's data. Rules: `.github/instructions/renderer.instructions.md`.
