# Accessibility implementation verification handoff

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-10 |
| Author | Copilot; AI-assisted A5 documentation and evidence maintenance |
| Status | Strict L1 passed after scoped contract correction; full L2 blocked by catalogue AA; human acceptance outstanding |
| Scope | New implementation evidence and handoff for #7; not the original audit, approval or a release record |
| References | [Issue #7](https://github.com/urruegg/frontier-envisioning/issues/7), [Approved spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [A5 plan](../plan/2026-11-09-accessibility-plan.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md), [Testing strategy](../engineering/testing-strategy.md), [Original audit](2026-11-09-accessibility-audit.json) |

## Boundary and provenance

Recorded on the actual machine date, 2026-11-10. This is a new handoff,
not a revision of the 38-scan design-stage audit or its original approval.
Design, plan and readiness approval on real
[#6](https://github.com/urruegg/frontier-envisioning/issues/6) remain recorded
in the [idea](../idea/2026-11-09-docs-governance-and-accessibility.md#approval-provenance).
They do not approve an expansion into the excluded identity generator.

This documentation work starts from `fix/7-blueprint-accessibility` at
`4969c139bb73e6c8973a6f1fbb7fc5ef7971f368`, stacked on governance.
Foundation [draft PR #12](https://github.com/urruegg/frontier-envisioning/pull/12)
is open at `93465cb`, targeting main. Governance
[draft PR #13](https://github.com/urruegg/frontier-envisioning/pull/13)
is open at `fb0c182`, targeting `feat/10-documentation-foundation`.
The parent reports cloud L1/L2/IaC passed for both, with CodeQL neutral.
Those are their checks, not accessibility-branch acceptance or a merge.
Policies remain Proposed; protected/manual #8 work remains pending.

## Implemented renderer work and retained evidence

| Task | Commit evidence | Delivery boundary |
|---|---|---|
| A1 | `1a10453` | Development-only axe and failing accessibility regressions |
| A2 | `5478918`, `4b8d653` | Modal focus containment/return and preservation of prior inert states |
| A3 | `463dc99` | Labelled roving tabs, pressed filters, SVG grouping; recovered interrupted work with DOM timing and default deep links preserved |
| A4 | `0857eda`, `4969c13` | Blueprint contrast, target sizing and reflow, including fully opaque operable filtered labels; catalogue AA acceptance remains blocked |
| A5 | This documentation handoff | Product/engineering guidance and factual tracking only; not full acceptance |

The retained Playwright HTML report in this worktree was inspected for its
aggregate: **43 tests, 41 expected/passed, 2 unexpected/failed, 0 flaky,
0 skipped**. This is the prior renderer run, not a fresh A5 browser execution.
Both failures are the light/dark site-and-catalogue AA tests. All fourteen
blueprint views, the site index, sampled brand variants and filtered SVG
states are reported clean for applicable rules.

The A4 worker reported 136 axe reports including retries. That is not a
verified distinct-state count; no unique-scan total is asserted here.
The parent will run final full L2 and reconcile exact counts. Full axe output
retains incomplete and best-practice findings; SVG/composited-colour review
is still necessary. The prior renderer DOM run passed 41 tests; fresh A5
validation is separated below.

## Blocking implementation finding and required decision

The catalogue has actual AA normal-text contrast failures in both schemes:
Later wave **4.40:1** and Finance header **4.33:1**, below 4.5:1.
The design-stage best-practice-only characterisation did not establish
catalogue conformance. Full L2 is red. Do not skip its assertion, waive its gate,
rewrite the hosted copy, or alter generator/profile/release hashes to pass.

The identity generator is outside this renderer plan. A scope-approval question
could not be answered because the user-input facility was unavailable.
No expanded scope is approved. A person must decide a separate versioned
identity-output phase and its guarded-output verification before remediation.
The [approved spec's dated finding](../spec/2026-11-09-docs-governance-and-accessibility-design.md#implementation-finding-2026-11-10)
records this without rewriting the original approval.

## Fresh A5 checks (2026-11-10)

| Command | Actual result |
|---|---|
| `python tools/dev.py package` | Exit 0; regenerated install inventory; 1.6.1 package SHA-256 `9b39a171f2a119ccdbecfa5bc74a225094d41e28bf999ea053afee9e4f479e2c` |
| `python tools/dev.py docs --strict` | Exit 0; 0 errors; external issue existence/approval not verified |
| `python tools/dev.py lint --strict` | Exit 0; repository rules 0 errors, ruff passed; ESLint 0 errors and 6 existing renderer warnings |
| `python tools/dev.py check --strict` with `CI=true` | Single full L1 attempt, exit 1 at unit tests: **6 failed, 135 passed, 1 skipped, 234 subtests passed** |
| `python tools/dev.py dom --strict` | Standalone exit 0 after L1 stopped: **41 tests passed, 0 failed, 3 suites, 0 skipped** |

Exact full-L1 summary:

```text
=== summary
ok                                                               0.0s  template drift (src/renderer -> blueprint template)
ok                                                               3.2s  lint
ok                                                               1.9s  documentation metadata, links and traceability
ok                                                              15.6s  customer-neutrality scan
FAILED: tests failed                                           106.9s  unit tests

GATE FAILED: tests failed
```

The root cause is `ProductDocumentSplit` in
`tests/unit/test_docs_contract.py`: two document metadata subtests pin
`2026-11-09`; one test hashes the original entire 1.6.1 patch note; three
section subtests hash A.8, B.5 and B.9. The requested real-date metadata,
NFR-0012 update and clearly separated development design/evidence trigger
those contracts. The historical 1.6.0 acceptance/release tables are unchanged.
No backdating, fixture/hash update, test edit, skip or waiver was made.
The docs-only worker did not change tests. The subsequent bounded correction
`2703703` now allows real ISO revision dates and the named approved current
accessibility additions while retaining original historical results, IDs,
anchors, provenance and inventory checks. The original fixture/hashes remain
unchanged; mutation regressions demonstrate those protections still fail when
historical content is altered.

The L1 attempt stopped before self-test, its package/demo/reproduction steps,
DOM and final archive scan. Only the standalone package and DOM results above
are claimed fresh. There is no `ALL GATES PASSED` result for full L1.
That description is the initial A5 attempt, not the final integration result.

## Final parent verification (2026-11-10)

After `2703703` and the focused narrow-header follow-up,
`python tools/dev.py check --strict` ended with
**ALL GATES PASSED**: **145 passed, 1 skipped, 311 subtests passed**;
all 34 plugin checks and 41 DOM tests passed. The skip is the expected
unreleased 1.6.1 reproduction check; no release manifest was fabricated.

`python tools/dev.py site e2e --strict` then completed with
**42 passed, 2 failed**. Both failures are the standalone identity-catalogue
AA cases, one per scheme; full L2 remains blocked, not waived. Every other
browser test passed, including all fourteen views, focus/tab regressions,
filtered operable nodes, 320px reflow and the existing workflow/legend checks.

Parsing actual scan-summary records from the final run gives **140 executions,
136 distinct labelled states, 134 states with no applicable WCAG violations**.
The two remaining states are the catalogue in light/dark; retries account for
four extra executions. Best-practice-only and incomplete findings remain
attached. These counts do not establish full WCAG conformance.

```text
=== summary (strict L1)
ok    0.0s  template drift (src/renderer -> blueprint template)
ok    3.3s  lint
ok    1.5s  documentation metadata, links and traceability
ok    9.0s  customer-neutrality scan
ok   62.9s  unit tests
ok   43.8s  plugin self-test
ok    0.3s  package
ok   24.8s  Caldova demo
ok    0.0s  release reproduction
ok   12.0s  DOM tests (happy-dom)
ok    7.2s  customer-neutrality scan
ALL GATES PASSED

=== summary (strict L2)
ok    0.1s  showcase site
FAILED: browser tests failed  220.6s  browser tests (Playwright)
GATE FAILED: browser tests failed
42 passed, 2 catalogue-only failures
```

Offline Edge screenshots were visually inspected for the filtered organisation,
evidence modal and 320px Overview. Review exposed a squeezed 115px title column;
a new failing browser assertion measured it, followed by a narrow-only grid
fix. The title now has 224px, branding moves below it, and all four targeted
header/reflow tests pass. No content is clipped or globally overflow-hidden.

Permanent review images (fictitious Caldova data only):

- [Filtered organisation, desktop](accessibility-review-2026-11-10/org-filtered-desktop.png).
- [Evidence modal, desktop](accessibility-review-2026-11-10/evidence-dialog.png).
- [Readable Overview at 320px](accessibility-review-2026-11-10/overview-320.png).

Final read-only spec/correctness review found no new blockers in the owned
blueprint implementation or scoped documentation-contract correction.
The known catalogue scope block and human acceptance still prevent a
merge-ready verdict. Generator, historical raster/profile, release records
and protected controls remain unchanged.

## Human and parent handoff

- Keep #6/#7 and A4/A5 acceptance open while catalogue AA remains unresolved.
- Strict L1 document-contract integration is resolved without backdating or
  weakening historical protection; the final L2 catalogue scope block remains.
- Parent publishes the draft and screenshots with the actual red L2 result;
  automation is not a manual assistive-technology inspection claim.
- Human [#8](https://github.com/urruegg/frontier-envisioning/issues/8) owns
  Narrator/screen-reader, 200–400% zoom, real Windows high-contrast and voice
  acceptance, plus protected ownership/access/routing actions.
- No source, test, generator, raster/profile, historical or protected edits
  are part of this A5 handoff. No WCAG certification, merge, release or
  deployment is claimed.
