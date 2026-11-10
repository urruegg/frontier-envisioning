# Plural documentation layout implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Maintainer-directed scoped cleanup; validation and delivery tracked in the sprint |
| Scope | Test-first checker/bundle migration and reference repair, preserving manual moves and historical evidence |
| References | [Catalogue](README.md), [Issue #18](https://github.com/urruegg/frontier-envisioning/issues/18), [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md#plural-layout-amendment-2026-11-10), [Spec](../specs/2026-11-10-documentation-layout-design.md), [Sprint](../sprints/SPRINT-001-docs-governance-and-accessibility.md) |

**Goal:** One plural documentation layout and two direct product authorities.

**Architecture:** Keep the existing stdlib Markdown parser and task runner.
Map logical work kinds to plural paths, name historical exemptions precisely,
and remove the obsolete bundle dependency rather than adding a redirect.

**Tech Stack:** Markdown, Python 3.11+, unittest/pytest, existing packaging tools.

**Owner:** `@urruegg` accountable; scoped AI-assisted implementation in the primary
checkout's cleanup branch. No delegation or protected action is required.

## 1. Preserve and reproduce

- Compare the maintainer's moved files with their Git originals; preserve them.
- Create #18 and a non-main branch without resetting or stashing the moves.
- Add `tests/unit/test_docs_layout.py` for plural folders, active-plan metadata,
  historical link checks, logical kinds and retired paths. Update the exact
  complete-bundle test in `tests/unit/test_release_tools.py`.
- Run both test files before production edits. Expected red: singular-directory,
  metadata-waiver, kind-resolution and obsolete-bundle assertions fail.

## 2. Migrate the consumers and documentation

Depends on step 1.

- Update only the routing/exemption parts of `tools/check_docs.py`; preserve its
  Markdown parsing, explicit diagnostics and gate integration.
- Remove the combined index from `tools/build_release.py` and START inventory.
  Update contract/validation fixtures without weakening historical hash guards.
- Consolidate `docs/plans/README.md`, catalogue moved historical designs in specs,
  and repair current local references and product-section destinations.
- Remove the combined index and residual singular directories. Keep historical
  commit URLs, immutable inventories and the product's historical file table.
- Update packaged README and changelog, then regenerate with
  `python tools/dev.py package`; do not hand-edit the install inventory.
- Record the exact protected session-start route proposal under #8, not in code.

## 3. Verify and hand off

Depends on step 2.

- Run the layout, docs-validation, docs-contract and release-tools unit tests
  together; all must pass, including original section and mutation guards.
- Run `python tools/dev.py docs --strict`, plus a bounded offline local-link
  audit of non-vendored Markdown surfaces outside the checker metadata scope.
- Run `python tools/dev.py check --strict`; require `ALL GATES PASSED`.
- Run `python tools/dev.py bundle`; inspect the finished archive for both exact
  product authorities, checksums and no retired index.
- Record exact results and the remaining protected-hook handoff in SPRINT-001.
  Publish only the scoped cleanup branch/draft PR through normal hooks.
  A person reviews and merges; no release or deployment is implied.
