# SPRINT-001: Documentation, governance and accessibility

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Human design, plans and readiness approved; D1-D5 in draft PR #12, G1-G3 in draft PR #13 (policies Proposed); A1-A4 implemented, A5 docs handed off, A4/A5 acceptance blocked; human #8 pending; sprint incomplete |
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
| [#9](https://github.com/urruegg/frontier-envisioning/issues/9) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Governance](../plan/2026-11-09-agent-governance-plan.md) | `@urruegg` accountable; parent coordinates governance worker | Stacked on #10 draft PR #12 | G1-G3 delivered, not merged; policies Proposed; human activation pending | [Draft PR #13](https://github.com/urruegg/frontier-envisioning/pull/13), HEAD `fb0c182`, targets `feat/10-documentation-foundation` |
| [#7](https://github.com/urruegg/frontier-envisioning/issues/7) | [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md) | [Accessibility](../plan/2026-11-09-accessibility-plan.md) | `@urruegg` accountable; parent coordinates renderer and bounded A5 docs work | Human plan/readiness evidence recorded; stacked on governance #13; shared-doc writers finished | A1-A4 implemented, A5 docs handed off; catalogue AA blocks A4/A5 acceptance; final parent verification/manual checks pending | Renderer HEAD `4969c13`; [new handoff](../intake/2026-11-10-accessibility-verification.md); prior browser 41 passed, 2 failed; no accessibility PR yet |
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
- [x] Parent established isolated worktrees; G2 started clean at `d07bd7e`,
      stacked on draft PR #12. Plugin/version was unchanged in G2.
      Accessibility now uses unreleased 1.6.1 and is stacked on governance #13.
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

The next checkpoint is parent review/final accessibility verification and a
human scope decision for the excluded identity generator. Catalogue AA text
contrast (Later wave 4.40:1; Finance header 4.33:1, both schemes) leaves full
L2 red. This is not only the original best-practice empty-header finding.
No new scope approval, gate waiver or catalogue assertion skip is recorded.
A4/A5 acceptance and human #8 protected routing/access/ownership plus manual
Narrator/zoom/real high-contrast/voice checks remain open.
The initial A5 document-contract integration failure was resolved in `2703703`
without backdating or weakening historical protections. Final strict L1 passes;
full L2 still fails only on the two excluded-catalogue AA cases.

## Current implementation evidence

- D1-D5 implemented and spec/code-reviewed in
  [draft PR #12](https://github.com/urruegg/frontier-envisioning/pull/12),
  open and not merged, targeting main from `feat/10-documentation-foundation`.
  The PR records strict L1 passing: 136 tests, one expected unreleased-version
  skip, 239 subtests, 34 plugin checks and 15 DOM tests; docs strict: zero errors.
  These are foundation results, not accessibility acceptance or sprint completion.
- Foundation PR #12 remains an open draft at `93465cb`; governance
  [PR #13](https://github.com/urruegg/frontier-envisioning/pull/13) remains an
  open draft at `fb0c182`, targeting `feat/10-documentation-foundation`.
  The parent reports cloud L1/L2/IaC passed for both, CodeQL neutral. Neither
  is merged. G1-G3 prose is delivered; policies remain Proposed and human
  activation is pending.
- G2 local validation on 2026-11-09: `python tools/dev.py docs --strict`
  passed with zero errors; unchanged guard/docs-contract pytest passed
  25 tests and 179 subtests; `lint --strict` passed with six pre-existing
  renderer warnings. Six in-memory routing/state acceptance checks were
  observed failing before the prose fixes and passing afterwards; no test or
  hook source was edited. `python tools/dev.py check --strict` ended with
  **ALL GATES PASSED**: 136 tests, one expected unreleased-version skip,
  239 subtests, 34 plugin checks and 15 DOM tests. This was the G2 checkpoint,
  before subsequent G3/PR #13 delivery; it is not sprint completion or policy
  activation. Local L2 was not rerun for prose-only G2.
- Protected session-start still names legacy product/intake paths; human #8
  must update it. Guard test success proves retained restrictions, not migrated
  routing or server settings. No protected files or labels were changed by G2.
- Accessibility A1 `1a10453`; A2 `5478918`/`4b8d653`; A3 `463dc99`;
  A4 `0857eda`/`4969c13` implement the bounded renderer changes. The retained
  browser report has 41 passed and 2 failed tests, both catalogue AA cases;
  the prior DOM run passed 41 tests. These are retained renderer results,
  not a fresh A5 L2 run. Distinct axe-state counts are not inferred from
  report totals that include retries.
- A5 product/engineering/authoring documentation and this tracking are handed
  off with [fresh-check evidence](../intake/2026-11-10-accessibility-verification.md).
  Strict docs passed with 0 errors; strict lint passed with 0 errors and
  6 existing warnings; package/install inventory regenerated. The single
  full strict L1 attempt stopped at document-contract tests: 6 failed,
  135 passed, 1 skipped, 234 subtests passed. A standalone DOM run then
  passed all 41 tests. No source/test/fixture changes or backdating were made.
  That was the initial A5 checkpoint, not the final verification result.
- Parent correction `2703703` retains the historical fixture/hashes and
  mutation guards while permitting real revision dates and the approved
  current accessibility additions. Final `check --strict`:
  **ALL GATES PASSED**, 145 tests, one expected unreleased-version skip,
  311 subtests, 34 plugin checks and 41 DOM tests.
- Final `site e2e --strict`: **42 passed, 2 failed**, both standalone
  catalogue AA schemes. Axe summaries contain 140 executions and 136 distinct
  labelled states; 134 have no applicable WCAG violations, with incomplete/
  best-practice findings retained. This is not manual acceptance or full
  conformance. See the [final handoff](../intake/2026-11-10-accessibility-verification.md#final-parent-verification-2026-11-10).

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
