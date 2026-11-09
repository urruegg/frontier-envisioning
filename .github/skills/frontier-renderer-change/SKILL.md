---
name: frontier-renderer-change
description: Change the Frontier Company Blueprint HTML (views, layout, interactions, workshop notes) through src/renderer with DOM and browser tests. Use when asked to add or change a blueprint view, page, tab, diagram, icon usage, style or interaction, or to fix a rendering bug.
---
# Changing the blueprint renderer

1. **Find the code.** Views are rendered by functions in `src/renderer/template.js` (for example `renderUseCases`, `renderLandingZone`, `renderReadiness`, `renderFinops`, `renderIdentity`). The view list declares id, label, part and availability. Styles live in `template.css`.
2. **Check the data contract** in `plugin/skills/frontier-blueprint/references/blueprint-schema.md`; new fields need defaults so older blueprints render, and a schema note.
3. **Write the failing DOM test** in `tests/dom/` using the helpers (`openBlueprint`, `go`, `txt`). Build the demo once: `python tools/dev.py demo`.
4. **Change the source**, then `python tools/dev.py template` and `node --test tests/dom/*.test.mjs` (or `python tools/dev.py dom`).
5. **Browser check** for layout: `python tools/dev.py site e2e` (Playwright) and look at the screenshots.
6. **Rules:** offline and self-contained; no `eval`, inline event attributes or `</script`; escape data before `innerHTML`; keyboard and screen-reader access; product icons unmodified and only where used.
7. **Finish** with `python tools/dev.py check`; the template change ships with the next plugin version.
