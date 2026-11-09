# SPRINT-001: Documentation, governance and accessibility

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code |
| Status | Proposed sprint; design approved, plan approval and implementation pending |
| Scope | The bounded work package for the eight approved requirements; not a delivery-date commitment |
| References | [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Plan](../plan/2026-11-09-docs-governance-implementation.md), [Current PRD/design](../prd-and-solution-design.md) |

## Goal and boundaries

Establish maintainable product documents and linked engineering records,
clarify agent boundaries, and remove measured renderer accessibility barriers.
Do not migrate source host, rewrite history, relax output/raster guards, change
protected controls by agent, or claim assistive-technology acceptance from scans.

## Work items

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#10](https://github.com/urruegg/frontier-envisioning/issues/10) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Documentation](../plan/2026-11-09-documentation-foundation-plan.md) | Parent coordinates registered docs/builder workers | Plan approval, real readiness | Proposed; not implemented | Implementation PR not created |
| [#9](https://github.com/urruegg/frontier-envisioning/issues/9) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Governance](../plan/2026-11-09-agent-governance-plan.md) | Parent coordinates governance worker | #10 authoritative documents/checker | Proposed; not implemented | Implementation PR not created |
| [#7](https://github.com/urruegg/frontier-envisioning/issues/7) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Accessibility](../plan/2026-11-09-accessibility-plan.md) | Parent coordinates renderer worker | Plan approval; #10 before final product-doc update | Proposed; not implemented | [Measured baseline](../intake/2026-11-09-accessibility-audit.json) |
| [#8](https://github.com/urruegg/frontier-envisioning/issues/8) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Human handoff](../plan/2026-11-09-human-governance-plan.md) | `@urruegg`; human execution only | #10/#9 before routing activation; #7 before manual accessibility acceptance | Human action pending | No settings, invitation or protected edit performed |

## Readiness

- [x] User problem/outcome and all eight acceptance groups recorded.
- [x] Design approved in the user conversation on 9 November 2026.
- [x] Real parent/child issues created and linked; no invented tracker IDs.
- [x] Customer-neutral samples and measured baseline evidence available.
- [ ] User separately approves implementation plans.
- [ ] A person applies required readiness/approval labels or records the
      permitted approval evidence; agents do not apply protected labels.
- [ ] Parent confirms current main/worktrees, dependencies and version status.

The approval message is recorded in the [spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md).
No implementation start date, effort commitment or approval of policies,
permissions or release has been inferred from that message.

## Capacity and sequencing

Schedule one writer per shared surface. Documentation/checker tasks precede
governance routing; renderer source tasks are isolated and may overlap only
with disjoint prose work. Parent owns version/dependency/generation and final
integration checkpoints. Human controls and acceptance remain separate.

Capacity is not committed. The plan specifies small steps and review checkpoints
rather than promising an unmeasured calendar deadline.

## Definition of done

- Each child meets its exact acceptance and records real red/green or document
  validation evidence, scoped commits and PR links.
- Required local/cloud gates pass; generated artifacts are regenerated; no
  archived release, historical evidence or protected guardrail is rewritten.
- Documentation references/catalogues and eligible headers are coherent.
- Applicable accessibility automation, focus/keyboard/reflow checks pass, and
  best-practice/incomplete/manual findings are reported explicitly.
- People complete ownership/access/routing and manual acceptance actions.
- People review and merge; release and deployment remain separate decisions.

## Open blockers and next checkpoint

The next checkpoint is **user plan approval**, followed by human readiness and
bounded delegated implementation. No implementation subagent has been launched.
Identity-catalogue best-practice headers need separate guarded product-output
approval; manual screen-reader/zoom/high-contrast acceptance is not complete.

## Evidence

- [Header baseline: 134 tracked Markdown files](../intake/2026-11-09-markdown-header-audit.csv).
- [Accessibility baseline: 38 Edge scans](../intake/2026-11-09-accessibility-audit.json).
- Planning-only self-review: twelve new Markdown records, 81 local references,
  eleven Python examples, fourteen JavaScript examples and fifteen PowerShell
  examples checked. The architecture return-tail example was parsed in its
  declared function context. Syntax/reference validation does not establish
  future feature integration or acceptance.
- Eight pure checker-example tests also passed in memory; no checker source
  file was created or integrated. This validates the plan examples, not the
  future repository wiring or delivery acceptance.
- `python tools/dev.py check --strict`: **ALL GATES PASSED**; 84 existing
  unit/pipeline tests passed, one unreleased-version reproduction test skipped,
  all 34 plugin checks and 15 DOM tests passed. Six existing ESLint warnings
  remain; no renderer/source change was made to address unrelated warnings.
- Imported JSON is byte-identical, SHA-256
  `c9a397267557753a7fcf97d992a702d8437d916a26d85a1c4f82108eaf44c6d2`.
  CSV cells/content are unchanged; repository text rules normalise CRLF to LF.
  Original CSV SHA-256:
  `b9af7038a64178597b4586205896c74f66af24698e3dcaa49a4bf8467941542a`;
  committed LF CSV SHA-256:
  `72adb6bcbf958acb6defa7f502e24268e18495e5e556f3b041bd413a77d79e51`.
- The package hash remains
  `e5ca20493787df84311c68ffd2ed8f94ec76cdc9610d42861fe694c557bb365b`.
  Product, source, dependency, test, instruction and protected paths have no
  implementation changes in this planning branch.
- Planning PR/cloud evidence is separate from the future implementation PRs.
  Passing existing gates does not mark the proposed work items complete.
