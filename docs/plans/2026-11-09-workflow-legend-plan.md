# Workflow Legend Overlap Implementation Plan

> **For agentic workers:** Use executing-plans inline; test the actual pointer
> and layout behavior before changing implementation.

**Goal:** Correct #4 in an unreleased 1.6.1 patch.

**Architecture:** A bounded upper grid owns the sticky agent list and summary;
the full-width workflow remains below it. Existing source/generation and
historical-identity guard patterns are retained.

**Tech stack:** Existing Python stdlib tooling, node:test/happy-dom and Playwright.

## 1. Branch and failing layout tests

- [x] Create `fix/4-workflow-legend-overlap` from merged `origin/main`.
- [x] Add a DOM assertion in `tests/dom/blueprint.test.mjs` that navigation
      belongs to `.agtop`, and the workflow is outside that containing block.
- [x] Add Chromium regression cases in `tests/e2e/blueprint.spec.mjs`:
      1440px scrolled pointer hits/clicks and 1024px keyboard navigation.
- [x] Run the targeted tests against 1.6.0 and observe the missing boundary and
      intercepted-hit failures.

```powershell
node --test --test-name-pattern="bounded summary" tests\dom\blueprint.test.mjs
python tools\dev.py site
npx playwright test --grep "legend remains"
```

## 2. Patch version and bounded grid

- [x] Bump before source edits:

```powershell
python tools\dev.py bump 1.6.1 --date 2026-11-09
```

- [x] Reuse grid rules in `src/renderer/template.css` for `.agwrap,.agtop`.
      Include `.agtop` in the responsive one-column selector.
      Give `.agwrap > .agtop` full-column span and `min-width:0`.
- [x] In `renderAgents`, wrap only `list` and `main`:

```javascript
h("div",{class:"agwrap"},
  h("div",{class:"agtop"}, list, main), flow, rest)
```

- [x] Regenerate and rerun targeted layout tests.

```powershell
python tools\dev.py template package
```

## 3. Explicit guarded preview identity

- [x] In `tests/unit/test_demo_raster.py`, first test missing 1.6.1 preview
      support and conflicting-record rejection.
- [x] Add `PREVIEW_VERSIONS = {"1.6.1"}` without changing the received release set.
- [x] When the current record is absent only for that preview, verify against
      the existing 1.6.0 identity record. When present, verify the current record.
      Return the reference version in build evidence.
- [x] In `tools/build_demo.py`, select the union of explicitly supported
      received and preview versions. Retain all input/asset guards.

```powershell
python -m pytest tests\unit\test_demo_raster.py -q
```

## 4. Verification and handoff

- [x] Run strict L1 and complete Chromium acceptance, including scrolling,
      pointer hits, keyboard, agent switching and screenshots.
- [x] Update 1.6.1 CHANGELOG, relevant renderer documentation, PRD and README.
- [x] Verify all historical release records, guardrails and fixture assets
      are unchanged. No release manifest is created for the preview.
- [ ] Commit with #4 in the body and the required co-author trailer.
- [ ] Push the patch branch and open a draft PR using the repository template.
- [ ] Verify cloud checks; leave merge, approvals, releases and deployment
      to people.

```powershell
python tools\dev.py check --strict
python tools\dev.py site e2e --strict
git push --set-upstream origin fix/4-workflow-legend-overlap
```

## Local verification evidence — 9 November 2026

- Red: the new DOM boundary assertion and desktop overlap assertion failed
  against 1.6.0. Responsive behaviour already passed. Preview-policy tests
  failed before explicit support was added.
- `python tools/dev.py check --strict`: **ALL GATES PASSED**; 84 unit/pipeline
  tests passed, one unreleased-version reproduction test skipped, all 34 plugin
  checks and 15 DOM tests passed. No 1.6.1 release manifest exists.
- `python tools/dev.py site e2e --strict`: **ALL GATES PASSED**; all nine Chromium
  tests passed, including 1440px and 1024px geometric non-intersection, actual
  pointer hits, clicks, keyboard activation and agent switching.
- Both corrected workflow screenshots were visually inspected; the legend is
  unobstructed at each width.
- The preview build reports `reference_version: "1.6.0"`, `preview: true`,
  223 restored PNGs and 36 restored visuals. No live conversion is claimed.
- Historical records, fixture manifest/assets and protected guardrails have no
  changes against `origin/main`. The only fixture change is its explanatory
  README. `git diff --check` reported no whitespace errors.
- Direct review of the layout, regressions and finite preview guards found no
  blocking issues. Cloud checks and human review remain separate handoff steps.
