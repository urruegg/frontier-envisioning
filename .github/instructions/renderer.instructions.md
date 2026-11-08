---
applyTo: "src/renderer/**"
---
# Blueprint renderer (src/renderer)

- The blueprint is one self-contained HTML file: `skeleton.html` with the CSS and JS slots, `template.css`, `template.js`, and a JSON data island filled by `build_blueprint.py`. After every change run `python tools/dev.py template`; the generated template is committed and CI fails on drift.
- No external resources: no CDN, fonts, scripts, images or fetch calls. The page works offline in a workshop room and under a strict Content-Security-Policy (inline script allowed by hash only).
- No `eval`, `new Function`, inline event handler attributes (`onclick=`) or `javascript:` URLs; attach handlers with `addEventListener`. Never put the text `</script` in `template.js`.
- Escape every data value before it reaches `innerHTML`; use the existing escaping helpers.
- Views come from the view list with an availability rule, so blueprints without that data hide the view. Keep earlier blueprint versions rendering (the self-test builds a sparse seed and the 1.3 data).
- Accessibility: keyboard reachable controls, visible focus, `aria-*` on dialogs and tabs, sufficient contrast in light and dark schemes.
- Microsoft product icons appear only where the data uses them and stay unmodified (no crop, flip, rotate or distort).
- Add or extend DOM tests in `tests/dom/` (happy-dom) for new views and interactions, and the browser test when layout matters. Run `python tools/dev.py demo dom`.
