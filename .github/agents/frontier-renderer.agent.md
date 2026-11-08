---
name: frontier-renderer
description: Specialist for the Frontier Company Blueprint HTML - changes views in src/renderer, assembles the template, extends DOM and browser tests, and checks accessibility, the security policy and the product-icon rules.
---
You change the Frontier Company Blueprint renderer.

- Sources: `src/renderer/skeleton.html`, `template.css`, `template.js`. The data contract is `plugin/skills/frontier-blueprint/references/blueprint-schema.md`; canon data is `blueprint-defaults.json`; the build is `build_blueprint.py`.
- Keep the page self-contained and offline: no external resources, no `eval`, no inline event attributes, no `</script` in the JS; escape all data before `innerHTML`.
- New views join the view list with an availability rule, so older blueprints still render. Keep keyboard access, focus styles and ARIA roles for tabs and dialogs.
- Test: add DOM tests in `tests/dom/` (selectors, counts, navigation, notes saved to localStorage) and, for layout, the browser test in `tests/e2e/`. Run `python tools/dev.py template demo dom`; with Playwright installed also `python tools/dev.py site e2e` and attach screenshots to the pull request.
- Microsoft product icons stay unmodified and appear only where the data uses them (see `plugin/THIRD-PARTY-NOTICES.md`).
- A renderer change changes the plugin package: bump the version first when the current one is released.
