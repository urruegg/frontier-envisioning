# SPRINT-008: Caldova architecture and workshop gallery

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Written spec approved; plan/readiness confirmation pending |
| Scope | Five additional real core-gallery captures and navigation guidance |
| References | [Catalogue](README.md), [Issue #41](https://github.com/urruegg/frontier-envisioning/issues/41), [Idea](../ideas/2026-11-13-caldova-gallery-extension.md), [Design](../specs/2026-11-13-caldova-gallery-extension-design.md), [Plan](../plans/2026-11-13-caldova-gallery-extension-plan.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#41](https://github.com/urruegg/frontier-envisioning/issues/41) | [Outcome](../ideas/2026-11-13-caldova-gallery-extension.md) | [G41-01 to G41-05](../specs/2026-11-13-caldova-gallery-extension-design.md#5-acceptance-and-verification) | [Tasks 1-4](../plans/2026-11-13-caldova-gallery-extension-plan.md) | `@urruegg` accountable | Written plan/readiness confirmation | Plan/readiness pending; no implementation started | Written spec approved at `4ef63d1`; actual capture/full gate/PR proof not yet produced |

## Actual decisions and readiness

- The maintainer requested the five named views and selected
  **`approve-ten-captures`**: retain the existing five and add real captures,
  captions and offline HTML navigation.
- The maintainer separately selected **`approve-written-gallery-spec`** for
  the written design at `4ef63d110a72dc9a301496317e2e5ef1311becee`.
- This plan was written after that answer. Its approval/readiness remains
  pending. Labels, assignment/milestone fields and formal GitHub approval are
  not inferred from conversation choices.

The problem, five acceptance criteria, affected tooling/docs and synthetic
sample are identified. Product version remains the unreleased 1.10.0 candidate;
no plugin file change or bump is planned. The human owner is `@urruegg`;
the historical PRD milestone table is not a new server-field assignment.
The only blocking decision is plan/readiness/execution confirmation.

## Isolation and verification boundary

The existing isolated worktree is reused on `docs/41-caldova-gallery` at
human-merged main `9115ccc8` (#40). The primary main checkout is untouched.
Planning documentation passed strict docs at `4ef63d1`; that is not
implementation, capture or quality-gate proof.

No runtime or generated assets have changed. Record actual RED/GREEN,
capture/tab-state, ten-image provenance, full gate, review and draft PR
evidence here only after execution. No public visibility, deployment, release,
financial consent or protected-label authority is granted.
Protected session-start routing #8 and release-cache #30 remain human-owned.
