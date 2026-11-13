# SPRINT-008: Caldova architecture and workshop gallery

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Plan/readiness approved; ten actual captures verified; full gate and PR pending |
| Scope | Five additional real core-gallery captures and navigation guidance |
| References | [Catalogue](README.md), [Issue #41](https://github.com/urruegg/frontier-envisioning/issues/41), [Idea](../ideas/2026-11-13-caldova-gallery-extension.md), [Design](../specs/2026-11-13-caldova-gallery-extension-design.md), [Plan](../plans/2026-11-13-caldova-gallery-extension-plan.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#41](https://github.com/urruegg/frontier-envisioning/issues/41) | [Outcome](../ideas/2026-11-13-caldova-gallery-extension.md) | [G41-01 to G41-05](../specs/2026-11-13-caldova-gallery-extension-design.md#5-acceptance-and-verification) | [Tasks 1-4](../plans/2026-11-13-caldova-gallery-extension-plan.md) | `@urruegg` accountable | Actual plan/readiness approval at `8be6aa8` | Inline implementation and real captures verified; full gate pending | RED/GREEN and capture proof below; no PR/full-gate result yet |

## Actual decisions and readiness

- The maintainer requested the five named views and selected
  **`approve-ten-captures`**: retain the existing five and add real captures,
  captions and offline HTML navigation.
- The maintainer separately selected **`approve-written-gallery-spec`** for
  the written design at `4ef63d110a72dc9a301496317e2e5ef1311becee`.
- This plan was written after that answer. The separate
  **`approve-inline-gallery`** response approved the plan/readiness at
  `8be6aa815ca54878bd6d7e95f454c9b2e3364d80` and selected inline execution.
  Labels, assignment/milestone fields and formal GitHub approval are not inferred.

The problem, five acceptance criteria, affected tooling/docs and synthetic
sample are identified. Product version remains the unreleased 1.10.0 candidate;
no plugin file change or bump is planned. The human owner is `@urruegg`;
the historical PRD milestone table is not a new server-field assignment.
No blocking design/readiness decision remains.

## Isolation and verification boundary

The existing isolated worktree is reused on `docs/41-caldova-gallery` at
human-merged main `9115ccc8` (#40). The primary main checkout is untouched.
Planning documentation passed strict docs at `4ef63d1`; that is not
implementation, capture or quality-gate proof.

No runtime or plugin files changed. No public visibility, deployment, release,
financial consent or protected-label authority is granted.
Protected session-start routing #8 and release-cache #30 remain human-owned.

## Test-first and actual capture checkpoint

- Baseline: all 15 existing gallery tests passed before edits.
- RED: the extended 16-test file produced seven expected assertion failures
  (including architecture subtests): five missing captures, missing tab-state
  records, accepted unexpected tab metadata and missing gallery links.
- GREEN: all 16 tests passed after the minimal capture/validator/doc updates.
  The state tests reject missing/swapped architecture tabs and unexpected tab
  state on other views, preserve all previous output bytes and reject a
  correspondingly corrupted saved manifest. Existing core-only, PNG, inventory
  and source-drift controls remain.
- `node --check tools/capture_docs.mjs` and scoped Ruff passed.
- `python tools/dev.py docs-demo` genuinely captured ten images from the
  current core offline HTML. All five new PNGs were visually inspected;
  Landing zone and Layers and integrations show different selected tabs.
  Discovery shows Service questions, Risks the heat map/details and Evidence
  the synthetic source register. No browser errors or HTTP requests were
  accepted by the capture runner.
- The manifest records `selected_tab: lz` and `selected_tab: layers` for the
  two architecture images and all actual PNG hashes/dimensions. The original
  five image bytes and core HTML remained unchanged.
- Fresh core comparison, strict docs (zero errors), 16 focused tests and
  whitespace passed after capture.

Navigation captions follow the existing HTML-link-plus-route-text convention:
the document checker validates real HTML anchors, not client-side `#/` routes.
No checker exemption or new renderer route was added to force deep links.
Architecture tab selection remains an explicit instruction.

Actual final full-gate and draft PR evidence will be added after execution;
the successful capture/unit checks alone are not whole-repository verification.
