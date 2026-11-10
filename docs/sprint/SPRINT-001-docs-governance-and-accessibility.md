# SPRINT-001: Documentation, governance and accessibility

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Human design, plans and readiness approved; D1-D5 in draft PR #12, G1 Proposed, G2 running; A not started; human #8 pending; sprint incomplete |
| Scope | The bounded work package for the eight approved requirements; not a delivery-date commitment |
| References | [Sprint catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Plan](../plan/2026-11-09-docs-governance-implementation.md), [Product requirements](../prd.md), [Solution design](../solution-design.md) |

Current delivery states and approval evidence are recorded below. Historical
planning validation is explicitly separated from implementation evidence.
Neither document status nor local link validation proves approval or access.

## Goal and boundaries

Establish maintainable product documents and linked engineering records,
clarify agent boundaries, and remove measured renderer accessibility barriers.
Do not migrate source host, rewrite history, relax output/raster guards, change
protected controls by agent, or claim assistive-technology acceptance from scans.

## Work items

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#10](https://github.com/urruegg/frontier-envisioning/issues/10) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Documentation](../plan/2026-11-09-documentation-foundation-plan.md) | `@urruegg` accountable; parent coordinates docs/builder workers | Human plan/readiness evidence recorded | D1-D5 implemented and spec/code-reviewed; not merged | [Draft PR #12](https://github.com/urruegg/frontier-envisioning/pull/12), targets main |
| [#9](https://github.com/urruegg/frontier-envisioning/issues/9) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Governance](../plan/2026-11-09-agent-governance-plan.md) | `@urruegg` accountable; parent coordinates governance worker | Stacked on #10 draft PR #12 | G1 implemented (policies Proposed); G2 running; G3 pending | G1 `d07bd7e`; local `docs/9-agent-governance`, no governance PR yet |
| [#7](https://github.com/urruegg/frontier-envisioning/issues/7) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Accessibility](../plan/2026-11-09-accessibility-plan.md) | `@urruegg` accountable; parent coordinates renderer worker | Human plan/readiness evidence recorded; #10 before final product-doc update | A1-A5 not started | [Measured baseline](../intake/2026-11-09-accessibility-audit.json); no implementation evidence |
| [#8](https://github.com/urruegg/frontier-envisioning/issues/8) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Human handoff](../plan/2026-11-09-human-governance-plan.md) | `@urruegg`; human execution only | #10/#9 before routing activation; #7 before manual accessibility acceptance | Human action pending | No settings, invitation or protected edit performed |

## Readiness

- [x] User problem/outcome and all eight acceptance groups recorded.
- [x] Design approved in the user conversation on 9 November 2026.
- [x] Real parent/child issues created and linked; no invented tracker IDs.
- [x] Customer-neutral samples and measured baseline evidence available.
- [x] User separately approved implementation plans on 2026-11-09; PR #11
      human-merged at 12:46:18Z, main `b0b4776`.
- [x] User explicitly approved readiness/design after the earlier blocker;
      the parent recorded the exact decision on #6.
- [x] Parent established isolated worktrees; G2 starts clean at `d07bd7e`,
      stacked on draft PR #12. Plugin/version is unchanged in G2.
- [ ] Human label-field synchronisation remains under #8; no agent applied
      protected labels and no field change is claimed.

Exact human quotes are preserved in the
[idea's approval provenance](../idea/2026-11-09-docs-governance-and-accessibility.md#approval-provenance).
The [plan-approval/preflight comment](https://github.com/urruegg/frontier-envisioning/issues/6#issuecomment-6740481819)
recorded the earlier label blocker; the subsequent
[readiness comment](https://github.com/urruegg/frontier-envisioning/issues/6#issuecomment-6742446199)
records the explicit instruction to proceed, not label mutation. No effort
commitment, Proposed-policy acceptance, permission or release is inferred.

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

The next checkpoint is G2 validation and parent review, then bounded G3/A work.
Human #8 protected routing/access/ownership and manual acceptance remain open.
Identity-catalogue best-practice headers need separate guarded product-output
approval; manual screen-reader/zoom/high-contrast acceptance is not complete.

## Current implementation evidence

- D1-D5 implemented and spec/code-reviewed in
  [draft PR #12](https://github.com/urruegg/frontier-envisioning/pull/12),
  open and not merged, targeting main from `feat/10-documentation-foundation`.
  The PR records strict L1 passing: 136 tests, one expected unreleased-version
  skip, 239 subtests, 34 plugin checks and 15 DOM tests; docs strict: zero errors.
  These are foundation results, not G2, cloud acceptance or sprint completion.
- G1 committed at `d07bd7e`; policy files remain Proposed with human acceptance
  pending. G2 is bounded instruction/routing work on this stacked branch.
- G2 local validation on 2026-11-09: `python tools/dev.py docs --strict`
  passed with zero errors; unchanged guard/docs-contract pytest passed
  25 tests and 179 subtests; `lint --strict` passed with six pre-existing
  renderer warnings. Six in-memory routing/state acceptance checks were
  observed failing before the prose fixes and passing afterwards; no test or
  hook source was edited. `python tools/dev.py check --strict` ended with
  **ALL GATES PASSED**: 136 tests, one expected unreleased-version skip,
  239 subtests, 34 plugin checks and 15 DOM tests. G2 parent review and
  subsequent G3 remain pending; this is not sprint completion or policy
  activation. Local L2 was not rerun for prose-only G2.
- Protected session-start still names legacy product/intake paths; human #8
  must update it. Guard test success proves retained restrictions, not migrated
  routing or server settings. No protected files or labels were changed by G2.

## Historical planning evidence (before PR #11 merge)

- [Header baseline: 134 tracked Markdown files](../intake/2026-11-09-markdown-header-audit.csv).
- [Accessibility baseline: 38 Edge scans](../intake/2026-11-09-accessibility-audit.json).
- Planning-only self-review: twelve new Markdown records, 81 local references,
  eleven Python examples, fourteen JavaScript examples and fifteen PowerShell
  examples checked. The architecture return-tail example was parsed in its
  declared function context. Syntax/reference validation does not establish
  future feature integration or acceptance.
- Eight pure checker-example tests also passed in memory; no checker source
  file was created or integrated at that stage. This validated the plan
  examples, not the later D1-D5 implementation or delivery acceptance.
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
  implementation changes in that historical planning branch.
- Planning PR/cloud evidence is separate from the future implementation PRs.
  Passing those existing gates did not mark the work items complete.
