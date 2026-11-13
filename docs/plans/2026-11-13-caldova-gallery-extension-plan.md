# Caldova Gallery Extension Implementation Plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Plan/readiness approved at 8be6aa8; inline execution under verification |
| Scope | Five additional core-gallery captures, state validation and reader guidance |
| References | [Catalogue](README.md), [Issue #41](https://github.com/urruegg/frontier-envisioning/issues/41), [Idea](../ideas/2026-11-13-caldova-gallery-extension.md), [Approved design](../specs/2026-11-13-caldova-gallery-extension-design.md), [SPRINT-008](../sprints/SPRINT-008-caldova-gallery-extension.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for inline execution, or superpowers:subagent-driven-development if separately selected. Execute the test-first steps below in order.

**Goal:** Add the requested architecture and workshop samples to the existing
Caldova gallery, retaining one offline HTML and ten genuine captures.

**Architecture:** Extend the two existing capture/view registries and their
manifest checks. Select architecture tabs through the current accessible UI;
capture actual state, without changing renderer routing or plugin behaviour.
The existing generator stages and validates assets before publishing.

**Tech stack:** Python standard library/unittest, existing Node/Playwright
Chromium capture tool and Markdown. Reuse installed dependencies.

## Authority and execution boundary

Owner: `@urruegg`. The maintainer selected `approve-ten-captures`, then
`approve-written-gallery-spec` for the written design at `4ef63d110a72dc9a301496317e2e5ef1311becee`.
This plan follows that separate written-spec decision. The subsequent actual
**`approve-inline-gallery`** response approved plan/readiness at
`8be6aa815ca54878bd6d7e95f454c9b2e3364d80` and selected inline execution.
No ready/approved labels are asserted.

Use the existing isolated worktree on `docs/41-caldova-gallery`, based on
human-merged main `9115ccc8`. Do not modify the primary main checkout or the
old FinOps branch. No plugin files, renderer, release/version carriers,
guardrails or historical sprint evidence are in scope.

## Task 1: Test the ten-image and architecture-state contract

**Files:** `tests/unit/test_docs_demo.py`.

- [ ] Run `python -m unittest tests.unit.test_docs_demo -v` on the unmodified
  implementation to establish the current baseline.
- [ ] Extend the existing expected image set and reader-gallery assertions
  from five to these ten names; keep the exact image-count assertion:

  ```python
  names = ("overview", "org-model", "agents", "agent-identity", "ontology",
           "landing-zone", "architecture-layers", "discovery", "risks", "evidence")
  self.assertEqual({p.name for p in (root / "docs/images/caldova").iterdir()},
                   {name + ".png" for name in names})
  ```

- [ ] Make the existing capture fixture emit the expected architecture state:

  ```python
  if name in {"landing-zone", "architecture-layers"}:
      row["selected_tab"] = "lz" if name == "landing-zone" else "layers"
  ```

- [ ] Add a focused publish/verify regression: remove or swap either
  architecture row's `selected_tab` in otherwise valid capture metadata.
  `publish` must raise `ValueError` and preserve every existing asset byte.
  Mutating the saved manifest the same way must make `verify` report an error.
  Retain the existing missing-image, incomplete-capture, unexpected-image,
  invalid-PNG, wrong-route and core-only tests; extend duplicate capture
  coverage only if the existing checks do not already prove rejection.
- [ ] Run `python -m unittest tests.unit.test_docs_demo -v` and record the
  expected RED: five-image output is insufficient and wrong tab metadata is
  currently accepted. Do not weaken assertions to make the old output pass.

## Task 2: Extend real capture and validation, without renderer changes

**Files:** `tools/capture_docs.mjs`, `tools/build_docs_demo.py`,
`tools/dev.py` (help text only).

- [ ] Append the five expected `(name, route)` pairs to Python `VIEWS`:

  ```python
  ("landing-zone", "#/architecture"), ("architecture-layers", "#/architecture"),
  ("discovery", "#/discovery"), ("risks", "#/risks"), ("evidence", "#/evidence")
  ```

- [ ] Keep a small architecture-state map in the validator and check each
  row's state after the existing exact ordered name/route/file check:

  ```python
  architecture_tabs = {"landing-zone": "lz", "architecture-layers": "layers"}
  if any(row.get("selected_tab") != architecture_tabs.get(row["name"]) for row in rows):
      raise ValueError("capture architecture tab state differs from the requested views")
  ```

  Keep the existing unique ordered inventory/dimension checks. Change active
  hard-coded five-image diagnostics/help text to ten or the current count.
  Do not change manifest schema identity or source/date canonicalisation.
- [ ] Extend the JS view list with the five names/routes and existing crumb
  labels. For architecture, explicitly click the exact accessible tab and
  verify the selected control/panel before capture:

  ```javascript
  await page.getByRole("tab", { name: tabLabel, exact: true }).click();
  await page.waitForFunction((id) =>
    document.getElementById(id)?.getAttribute("aria-selected") === "true", tabId);
  const active = await page.locator("#architecture-panel").getAttribute("aria-labelledby");
  if (active !== tabId) throw new Error("Architecture capture selected the wrong panel");
  row.selected_tab = active.replace("architecture-tab-", "");
  ```

  `tabLabel`/`tabId` are the requested `Landing zone`/`architecture-tab-lz` or
  `Layers and integrations`/`architecture-tab-layers` from the same view row.
  Read the actual selected state, not just the requested constant.
- [ ] Wait for substantive visible content before each new screenshot:
  landing-zone `.lzfig svg`, layers `.layers .layer`, Discovery `.qgroup .q`,
  Risks `.riskgrid`, Evidence `.evstats` and its table rows. Preserve fresh
  storage, viewport, font wait, top-of-page positioning, console/network
  errors and browser cleanup. Do not write workshop answers or ratings.
- [ ] Run the focused unittest file GREEN, then:

  ```powershell
  node --check tools\capture_docs.mjs
  ruff check tools\build_docs_demo.py tools\dev.py tests\unit\test_docs_demo.py
  ```

  Expected: all tests pass, valid JS and zero Ruff findings.

## Task 3: Reader guidance and genuine regeneration

**Files:** `docs/demo/README.md`, `README.md`, `docs/getting-started.md`,
`docs/README.md`; generated outputs only via the existing generator.

- [ ] Add Target architecture and Workshop sections to the gallery with
  exactly the five new images, useful alt text and short captions. Link the
  existing HTML routes. State that Layers and integrations needs a tab click.
  Explain proposed infrastructure/integrations, exported workshop notes and
  synthetic evidence; do not imply deployment or real engagement evidence.
- [ ] Update active five-image/count references in these reader documents
  and capture help text; preserve historical five-image claims unchanged.
  Update eligible metadata revisions and link #41.
- [ ] Run `python tools/dev.py docs-demo` with the existing Chromium cache.
  It builds the actual core and produces the HTML, ten real images and manifest.
  Never edit or copy generated output by hand.
- [ ] Inspect each of the five new PNGs. Confirm distinct selected architecture
  tabs and substantive requested content, readable viewport framing and no
  captured dialogs/errors. If content is wrong, fix the capture step and
  rerun; do not alter renderer layout to make a documentation image.
- [ ] Run:

  ```powershell
  python tools\build_docs_demo.py --check --demo build\demo
  python tools\dev.py docs --strict
  python -m unittest tests.unit.test_docs_demo -v
  ```

  Expected: ten actual hashes/states/dimensions verified against fresh core,
  zero document errors and all focused tests passing. Confirm `git diff`
  contains no plugin/runtime changes. Record actual image/source provenance.

## Task 4: Full gate, review and follow-up draft PR

- [ ] Run `python tools/dev.py check --strict`. It must finish with
  `ALL GATES PASSED`; record actual new test/subtest/self-test/DOM counts and
  expected skips, not copied #40 results. No parallel builders share outputs.
  A renderer behaviour change is not part of this plan; actual Playwright
  gallery generation is mandatory even without a new full L2 requirement.
- [ ] Review the bounded capture/validation diff and actual images against
  G41-01 to G41-05. Fix meaningful findings and rerun covering checks.
  Record actual proof in SPRINT-008, preserving historical records.
- [ ] Commit exact owned files with conventional messages, `Refs #41` and
  `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
  Push only `docs/41-caldova-gallery` and open a draft PR using the repository
  template, exact successful gate summary and genuine screenshots.
- [ ] Read actual CI results without inferring approval. Leave merge, labels,
  release, deployment, protected routing #8/#30 and human sign-off to people.

## Self-review and coverage

Tasks 1/2 cover G41-02/03; Task 3 covers G41-01/02/04; Task 4 covers G41-05.
No new plugin state, route, dependency, one-off HTML copy or configuration
framework is needed. Tests and captures use only the fictitious Caldova.
All implementation/check commands above are planned, not passing evidence.
