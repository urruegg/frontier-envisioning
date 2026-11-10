# SPRINT-001: Documentation, governance and accessibility

| Field | Value |
|---|---|
| Version | 0.8 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | #15 integrated with passing local/cloud checks; final acceptance recorded; ownership corrected through human-merged #17; #18 locally verified, review/merge separate; protected routing remains open |
| Scope | The bounded work package for the eight approved requirements; not a delivery-date commitment |
| References | [Sprint catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md), [Plan](../plans/2026-11-09-docs-governance-implementation.md), [Product requirements](../prd.md), [Solution design](../solution-design.md) |

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
| [#10](https://github.com/urruegg/frontier-envisioning/issues/10) | [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md) | [Documentation](../plans/2026-11-09-documentation-foundation-plan.md) | `@urruegg` accountable; parent coordinates docs/builder workers | Human plans/readiness evidence recorded | D1-D5 implemented, reviewed and human-merged to main | [PR #12](https://github.com/urruegg/frontier-envisioning/pull/12), main merge `4a7d62f` |
| [#9](https://github.com/urruegg/frontier-envisioning/issues/9) | [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md) | [Governance](../plans/2026-11-09-agent-governance-plan.md) | `@urruegg` accountable; parent coordinates governance worker | Human-controlled policy/routing publication remains separate | Integrated into main through #15; policy files remain Proposed, not proof of controls | [PR #13](https://github.com/urruegg/frontier-envisioning/pull/13), then [#15](https://github.com/urruegg/frontier-envisioning/pull/15), main `5d68b71` |
| [#7](https://github.com/urruegg/frontier-envisioning/issues/7) | [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md) | [Accessibility](../plans/2026-11-09-accessibility-plan.md) | `@urruegg` accountable; parent coordinates renderer and targeted catalogue correction | Scenario-level manual evidence is distinct from sign-off | Integrated on main; local/cloud L1/L2/IaC pass, all 44 browser tests; final human sign-off recorded | [PR #15](https://github.com/urruegg/frontier-envisioning/pull/15); [A6 verification](../intake/2026-11-10-accessibility-verification.md#a6-linked-catalogue-ci-failure-corrected) |
| [#8](https://github.com/urruegg/frontier-envisioning/issues/8) | [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md) | [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md) | [Human handoff](../plans/2026-11-09-human-governance-plan.md) | `@urruegg`; human execution only | Sole-account ownership/routing execution and actual control evidence | Final sign-off recorded; enterprise invitation superseded; protected H1/H2 still human-only | [Human acceptance](https://github.com/urruegg/frontier-envisioning/issues/8#issuecomment-6768225688); CODEOWNERS/hooks/settings not changed by the agent |
| [#18](https://github.com/urruegg/frontier-envisioning/issues/18) | [Idea amendment](../ideas/2026-11-09-docs-governance-and-accessibility.md#plural-layout-amendment-2026-11-10) | [Layout spec](../specs/2026-11-10-documentation-layout-design.md) | [Layout plan](../plans/2026-11-10-documentation-layout-plan.md) | `@urruegg` accountable; scoped AI-assisted cleanup | Maintainer's manual moves and explicit plural/index-removal decision | Local targeted/full gates, link audit and complete bundle pass; review/merge and cloud results separate | Red/green evidence below; [#18](https://github.com/urruegg/frontier-envisioning/issues/18) carries the PR/cloud handoff; protected hook handoff remains #8 |

## Plural-layout cleanup (#18)

The maintainer's manual moves are retained on `chore/18-plural-documentation-layout`.
Before production changes, the new layout and exact bundle tests produced
7 expected failures, 9 passes and 11 passing subtests. The failures demonstrated
singular physical routing, the blanket historical-plan exemption, missing
plural-kind resolution and the obsolete index in the complete bundle.
Verification after implementation:

- The four targeted layout/docs-validation/docs-contract/release-tools test files
  pass: 76 tests and 310 subtests.
- `python tools/dev.py docs --strict`: no metadata, catalogue, local-link or
  traceability errors. A separate offline audit uses the same link parser across
  all 130 owned, non-vendored Markdown surfaces: zero local-link errors.
- `python tools/dev.py check --strict`: `ALL GATES PASSED`; 162 tests,
  373 subtests, 41 DOM tests. The one skip is the existing release-reproduction
  comparison for unreleased 1.6.1, not a bypass of an existing release.
- `python tools/dev.py package` regenerates the install inventory from the
  packaged README. `python tools/dev.py bundle` passes; the finished complete ZIP
  has 13 entries, both product documents match current source bytes, its START
  inventory omits the retired index, and all four distribution ZIP checksums
  match `SHA256SUMS.txt`.
- Protected controls, immutable release/intake inventory records and the
  original raster/product-section fixtures remain unchanged. No renderer code
  changes; L2 is not rerun locally for this documentation/tooling cleanup.

These are local results, not a claim of cloud CI, approval or main integration.
The [tracking issue](https://github.com/urruegg/frontier-envisioning/issues/18)
links the proposed PR and subsequent cloud evidence.

Current protected-context exception: `.github/hooks/scripts/session_start.py`
still places both specs and plans in `docs/plans/`. Human #8 must direct new
records to `docs/ideas/`, `docs/specs/`, `docs/plans/` and `docs/sprints/`,
preserving all quality and human-only boundaries. The hook is not edited here.
Historical inventories/receipts, commit-qualified source URLs and the original
1.6.0 file table are provenance, not current routing consumers.

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
[idea's approval provenance](../ideas/2026-11-09-docs-governance-and-accessibility.md#approval-provenance).
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

PR #15 is human-merged to main `5d68b71`; fresh local and actual post-merge
cloud CI passed L1/L2/IaC. The user supplied final governance/manual-accessibility
sign-off, then clarified the sole public-cloud account: use `@urruegg` only.
No enterprise-account invitation or second reviewer is required.

The remaining #8 execution evidence is for human-applied CODEOWNERS and
protected intake routing, plus verification of actual controls. Final sign-off
does not manufacture scenario-level Narrator/zoom/high-contrast/voice records.
The enterprise-account proposal and previous pending-approval statements below
are historical checkpoints, superseded by this decision. The sprint is not
declared fully complete while protected operations remain unapplied.

## Sole-maintainer refinement and final sign-off (2026-11-10)

The user's account clarification directly amends DG-06 and H1-H3 under the
existing #8 ideas/specs/plan package. All-path intended ownership is `@urruegg`;
the enterprise-only account is not a collaborator or independent reviewer.
The maintainer records sign-off against the exact PR head and passing checks,
then merges when actual server rules permit. GitHub formal self-approval is
not available; agent review is advisory. No agent changes review settings,
waives gates, applies protected labels or performs protected edits.

The [human plan](../plans/2026-11-09-human-governance-plan.md#h1-sole-public-cloud-ownership-person-only)
contains the minimal human-applied `* @urruegg` target; the
[operating model](../engineering/github-setup.md#4-sole-maintainer-review-and-merge)
explains the GitHub author-review limitation and exact sign-off workflow.
This documentation refinement changes no repository control or product output.

The earlier A5 contract failure and catalogue failures below are preserved
checkpoints, not the current gate result.

## A6 current automated verification

Generator corrections `423ec42`/`53015ba` resolve the original two catalogue
failures: accessible rendered status text and full-opacity subtitles.
Only two version-scoped current input hashes change; 205 generated inputs,
223 original PNGs, README and final-release ZIP authority remain checked.
Independent review found no generator/guard defect; commit the matching parent
reference/inventory together before publishing.

Local strict L1 passes: 156 tests, 375 subtests, one expected unreleased skip,
34 plugin checks and 41 DOM tests. Local strict L2 passes all 44 tests.
The [dated report](../intake/2026-11-10-accessibility-verification.md#a6-linked-catalogue-ci-failure-corrected)
records red/green evidence, deterministic hashes and remaining manual limits.

## Human merge and integration checkpoint (2026-11-10)

The user stated that all three PRs are approved and execution may proceed.
Authenticated PR records and fetched Git ancestry confirm #12 merged to main,
#13 merged to the foundation branch, and #14 merged to the governance branch.
The approved accessibility head is contained in `240f557`, but not in current
main `4a7d62f`. Human merges into feature branches do not propagate to main.

A separate draft integration branch, `chore/6-integrate-approved-stack`,
starts from the exact human-merged stack. Preparing that PR does not merge it,
waive L2 or extend permission to the excluded identity generator. The separate
catalogue scope question remained unanswered when the user-input facility was
unavailable; no expansion is inferred from PR approval.

The checkpoint evidence below predates these merges and is retained as history.
At that checkpoint the catalogue decision was still missing. The later
explicit CI-fix request authorises A6; human #8 actions remain outstanding.

Fresh verification of the exact human-merged tree `240f557`:
`python tools/dev.py check --strict` ended with **ALL GATES PASSED**;
`python tools/dev.py site e2e --strict` reported **42 passed, 2 failed**,
the same light/dark catalogue AA cases. No failing assertion was suppressed.
The three tracking-document updates add no production or guardrail change.

## Implementation checkpoints before human merges

- D1-D5 implemented and specs/code-reviewed in
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
