---
id: INT-13
title: "Split the renderer into modules (no bundler)"
milestone: "Later"
labels: [type:chore, area:renderer, priority:P3, size:L]
---
## Context

`src/renderer/template.js` is one file of about 180 KB. Modules make reviews and agent edits safer.

## Acceptance criteria

- [ ] `src/renderer/js/*.js` concatenated in a declared order by `tools/assemble_template.py`
- [ ] The first refactor PR is a pure move: the generated template stays byte-identical
- [ ] DOM and browser tests unchanged and green
