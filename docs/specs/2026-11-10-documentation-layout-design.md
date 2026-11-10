# Plural documentation layout

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; maintainer-directed, AI-assisted maintenance |
| Status | Scoped naming/removal decision explicitly directed by the maintainer; delivery evidence separate |
| Scope | Preserve manual moves, repair current references and remove obsolete document/index paths |
| References | [Catalogue](README.md), [Issue #18](https://github.com/urruegg/frontier-envisioning/issues/18), [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md#plural-layout-amendment-2026-11-10), [Plan](../plans/2026-11-10-documentation-layout-plan.md), [Sprint](../sprints/SPRINT-001-docs-governance-and-accessibility.md) |

## Decision and boundaries

The maintainer manually moved the records and explicitly requested plural
`docs/ideas/`, `docs/specs/`, `docs/plans/` and `docs/sprints/`, with historical
designs in specs and implementation plans in plans. Preserve those moves.
Consolidate the old plan catalogue into plans, remove the residual singular
directory, and remove the combined PRD/design compatibility index entirely.
Link directly to the [PRD](../prd.md) and [solution design](../solution-design.md).

This amends DG-02/DG-04 and the compatibility-index/bundle/blanket-legacy-folder
parts of D2-D4. It does not erase the original approved plan, migration receipt
or historical section hashes. Logical work kinds remain Issue, Idea, Spec and
Plan; only physical directory names change.

## Acceptance

1. All four canonical catalogues cover every direct Markdown child. No retired
   singular directory or combined index remains in the current repository.
2. Active local links, instructions, agents, skills, PR template and backlog
   sources resolve to the right plural location or separate product authority.
   Cross-folder links between the moved old designs/plans remain usable.
3. Current plans require metadata. The six pre-governance historical specs/plans
   retain their format through exact-path exemptions, not a whole-folder waiver;
   their links and catalogue coverage are still checked.
4. Sprint metadata and rows continue to prove local Issue/Idea/Spec/Plan shape,
   using singular logical kinds mapped to plural physical folders. Offline
   validation does not claim live issue existence, approval or permissions.
5. The complete bundle includes both authoritative product documents with exact
   bytes, inventory and checksums, and excludes the retired index even if a stale
   file exists at its old source path.
6. Original product IDs/sections, intake inventories, release manifests and raster
   fixtures remain unchanged. Commit-qualified historical URLs retain the paths
   valid in those snapshots. Historical mentions are not current consumers.
7. New regressions fail before the change, then targeted tests, strict docs and
   the full quality gate pass. Regenerate the install inventory for the packaged
   README change under the existing unreleased 1.6.1; do not hand-edit it.

## Human-only handoff

The protected session-start hook still directs both specs and plans to
`docs/plans/`. Under [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
a person must replace that route with the four plural locations while preserving
all existing quality, human-only and Superpowers context. No hook, CODEOWNERS,
settings, readiness/approval labels, release, merge or deployment is changed here.
