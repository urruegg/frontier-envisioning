# Caldova architecture and workshop gallery

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted intake |
| Status | Five additional captures approved in conversation; written spec/readiness pending |
| Scope | Existing core Blueprint architecture and workshop views; no plugin feature change |
| References | [Catalogue](README.md), [Issue #41](https://github.com/urruegg/frontier-envisioning/issues/41), [Design](../specs/2026-11-13-caldova-gallery-extension-design.md), [Gallery](../demo/README.md), [Original documentation plan](../plans/2026-11-12-internal-user-documentation-plan.md) |

## Outcome and request

Internal readers can inspect the existing architecture and workshop capabilities
in the Caldova Blueprint gallery before installing the plugin.
The maintainer requested Landing zone, Layers and integrations, Discovery,
Risks/assumptions/open decisions and Evidence on 13 November 2026.

The maintainer selected **`approve-ten-captures`** after the proposed design:
retain the original five images and add five genuine captures, captions and
navigation instructions for the existing offline HTML. The links-only
alternative was not selected. This is design-scope evidence, not written-plan
approval or a protected label-field change.

## Boundaries

Continue the existing generator and manifest workflow. Keep the sample
core-only, synthetic, offline and private; no FinOps operations, real engagement
data, renderer change, deployment or new product capability is needed.
Architecture tab state requires an explicit UI selection, not an invented URL.

PR #40 was independently confirmed human-merged at `9115ccc8`; its approval
does not approve new work or release the plugin. Follow-up #41 has the real
issue, accountable human owner `@urruegg` and testable acceptance in the design.
The existing isolated worktree now uses `docs/41-caldova-gallery` from that
merged base. Primary main was not modified.

No plugin files or version carriers are in scope. Protected session-start
routing #8 and release-cache #30 remain human-owned. Planning records, the
full ready work package and final verification will distinguish actual
decisions and results from proposed execution.
