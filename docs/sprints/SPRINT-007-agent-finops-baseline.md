# SPRINT-007: Agent FinOps baseline before build handover

| Field | Value |
|---|---|
| Version | 1.4 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Strict local L1/L2 passed; final archive and draft PR evidence pending |
| Scope | Offline baseline-first 1.10.0 internal candidate, not live FinOps operations |
| References | [Catalogue](README.md), [Parent #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [Idea](../ideas/2026-11-12-agent-finops-baseline.md), [Design](../specs/2026-11-12-agent-finops-baseline-design.md), [Plan](../plans/2026-11-12-agent-finops-baseline-plan.md), [ADR-0028](../adr/0028-versioned-agent-finops-baselines.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#35](https://github.com/urruegg/frontier-envisioning/issues/35) | [Outcome/input](../ideas/2026-11-12-agent-finops-baseline.md) | [Baseline design](../specs/2026-11-12-agent-finops-baseline-design.md) | [Tasks 0-8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; accountable | Actual D35-09 plan/readiness approval recorded | Approved for bounded implementation; no label change inferred | Spec approval `2e3c0e7`; plan approval `efb3468`; no delivery/PR proof yet |
| [#38](https://github.com/urruegg/frontier-envisioning/issues/38) | [Baseline-first](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01 to AFB-10](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D1, Tasks 1-3](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D1, estimated M | Actual plan approval and reviewed Task 0 | Engine/records reviewed at `b623228a`; driver coverage at `7dfdb79f` | Final integrated source/UI reviewed; full gates and final archive proof pending |
| [#37](https://github.com/urruegg/frontier-envisioning/issues/37) | [Canvas/handover](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01/06/09/11](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D2, Tasks 4/6](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D2, estimated M | Reviewed D1 and explicit fixture | Final recurring-only/coverage UI integration reviewed at `e2f5d9c1` | Scoped DOM/browser evidence below; full L2 pending |
| [#39](https://github.com/urruegg/frontier-envisioning/issues/39) | [Verified candidate](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-10/11/12](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D3, Tasks 0/5/7/8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D3, estimated M | Preparation first; final proof after D1/D2 | Source guidance and explicit fixture reviewed | Initial package/CLI evidence below, not full 1.10.0 quality/distribution proof |

## Human evidence and gates

Actual structured answers D35-01 to D35-07 on #35/#36 approve the product
choices and four design sections. D35-08 is the actual
`approve-written-spec` response for
`2e3c0e79dc45c9ab06775def9f31cfb3bad7a8aa`.
The implementation plan was written only after that response.

The subsequent actual `approve-subagent-driven` response is D35-09:
**plan/readiness approved at `efb3468dbe597ea6112b6839c7019243ab44b885`**,
with subagent-driven execution selected. Design and plan approvals were
separate decisions. No ready/approved label, assignment, milestone-field
change or GitHub review is inferred. Proposed issue
classifications/sizes are not assertions about applied server metadata.
The historical PRD release table is not a live milestone assignment.

Use the existing private host and `@urruegg` as sole accountable human owner.
The user explicitly requires waiting at questions despite autopilot.
No live billing connector, deployed FinOps Agent, purchasing or authenticated
financial-approval service belongs to this sprint.

Before Task 2, the actual `provisional-draft-figures` response is D35-10.
Known supplied stale/unverified rates may support explicitly provisional
draft totals/unit costs with source/date gaps and separated contributions.
Unknown values remain unknown; strict financial build handover is unchanged.
This targeted reporting decision was recorded before calculator code.

During combined ontology/baseline integration, the actual
`support-combined-source-resolution` response is D35-11. Separate source
registers are resolved on a detached, restriction-preserving view; ambiguity/
collisions reject during preflight before outputs. Valid combinations remain
supported, original inputs stay unchanged and unrelated source context does
not taint independent financial records.

## Preparation evidence, not new-feature evidence

The native worktree was explicitly consented. Its clean 1.9.2 source passed
81 existing FinOps unit tests and the baseline documentation check.
The planning-only seven-file commit `2e3c0e7` passed
`python tools/dev.py docs --strict` with zero errors and `git diff --check`.
It was pushed without modifying runtime code or the product version.

These are planning/baseline results, not red/green implementation proof,
full 1.10.0 L1/L2, package execution or distribution acceptance.
The implementation will record exact checked heads, commands/results,
counts and archive hashes here after they exist.

## Task 0: Version and identity-provenance checkpoint

The checked implementation is
`789c4b65fccf814b2d5f5f7ad71d4bbb215b74d3`, reviewed against the approved
plan head `efb3468`. It updates the standard version carriers to an
**unreleased internal 1.10.0 candidate**, with no engine/UI algorithm changes.
The installer metadata was regenerated. Active reader prose still needs the
planned Task 7 alignment; this is not a claim that the whole candidate is ready.

An actual SVG-only identity probe matched **205/205 paths and hashes** against
the approved 1.9.2/A6 mapping. The named LF 1.10.0 input record is pinned at
`53b5e9bf545501306db18e9f8aa6f0289aae8f56a8b12a3a1c8b240e9742846e`.
The preservation receipt in ignored build evidence covers **319 files,
223 original PNGs and three historical suffixes**, all unchanged.
No golden archive or arbitrary future-version allowance was substituted.

The combined raster/raster-17/raster-19/raster-192/raster-110/docs-demo selector
collects **46 tests** both before and after the change:

| Phase | Ordinary results | Subtests |
|---|---|---|
| RED against the prior raster implementation | 6 failed, 40 passed | 11 failed, 85 passed |
| GREEN | 46 passed | 96 passed |

Pytest combines ordinary and subtest failures in its RED summary, so
"17 failed, 40 passed" does not mean 57 collected tests. Technical spec review
independently verified **41 existing tests plus five new tests**, with no
hidden/removed regression cases, the actual probe, pins, preservation and
standard bump/installer output.

The subsequent bounded controller code-quality review found no meaningful
logic issue. Fresh controller checks passed: the new profile's five tests/
13 subtests, and all **81 legacy Preview/privacy/cache/value/wrapper tests**
after the bump. Strict docs and range whitespace checks also passed.
This is AI-assisted technical review, not independent human approval,
full L1/L2, final installed-package proof, distribution or deployment.

## Task 1: Contract checkpoint

The initial contract checkpoint was `03b49032`; spec fixes were committed
as `75333d14`, followed by the normalization correction at
`4454974a389100f28fe4d093af01c8a55df4ea14`. Scope is the pure contract module,
synthetic Caldova input, public concept-reference metadata, focused tests and
generator-produced installer. No calculator/records/projection/CLI/UI existed
at this checkpoint.

Spec review found and independently re-verified fixes for dependency-based
scenario uncertainty, empty-scope supplied references and incomplete
applicability entries. Code-quality review then found raw blank metadata being
compared after missing-value parsing. The bounded final correction was reviewed
directly: detached parsed comparison values, consistent None/blank/whitespace
gaps, retained genuine mismatch/unknown-enum errors and no input mutation.

The controller's final focused run passed **59 tests**, plus Ruff and whitespace.
The six normalization regression methods were reported RED with 17 failing
subtests before the fix; the earlier 13 spec-fix regressions were independently
replayed against pre-fix code. These are scoped technical checkpoints, not full
L1/L2, commercial pricing verification, authenticated financial approval or
final package/distribution acceptance.

## Task 4: Optional build integration checkpoint

The reviewed checkpoint is
`11e11f18b62810fe72720e50cc03cb2d6fec69bd`. Wrapper and standalone builds
consume repeatable authoritative baseline/review inputs with explicit date,
scope and fresh acknowledgement. Core, ordinary value and legacy-only paths
remain independent. Cached derivative views cannot supply financial authority.

D35-11 source resolution validates original raw and normalized typed graphs
before privacy selection. It preserves current consumed ancestry, Blueprint
parent restrictions and relevant derived products without importing unrelated
private context. The process helper extension is narrow and opt-in; valid
GA-only normalization remains unchanged.

The successor chain stages raw work privately and publishes customer-projected
counterparts. Identity-derived filenames, consumed input aliases and the full
resolved publication plan are checked before scripts/writes. Standalone
rendering and serialization finish before publication; all valid missing
parent directories are prepared before the first product file write.
Later filesystem failures are not presented as an atomicity guarantee.

Independent spec review passed with **394 focused tests** and a scan of
**776 files/ZIP members**. Quality review closed its identity escape,
reached-parent privacy and resource-alias findings. The final bounded
parent-preparation fix was reviewed directly; three selected standalone safety
tests passed, retaining invalid-path/alias/render controls. The worker's final
combined run passed **403 tests**. Strict L0 also passed at the earlier backend
checkpoint, with zero errors and six inherited ESLint warnings.

These are scoped source-qualified checks, not full L1/L2, actual final installed
handoff execution, rendered baseline capability or distribution clearance.
Task 5 below records the initial fixture and installed CLI checks. UI and final
quality/distribution proof remain pending.

## Task 2: Calculator checkpoint

The initial calculator was `d7de4b53`, followed by numerical/metadata corrections
at `bf7bf4db` and the bounded optional-FX-identity correction at
`984b3c408ebbe0765518b16277dc700816ae6c44`. The scope is the pure calculator,
baseline tests and generator-produced installer; no lifecycle, CLI or renderer
delivery is implied.

Independent spec review verified the exact-or-refuse intermediate Decimal
arithmetic, isolated context, nullable legacy ancestry, missing-versus-
incompatible applicability and D35-10 provisional figures. Unsupported
representations, including nonterminating intermediate line-price division,
raise explicit errors rather than silently returning incorrect cents.
Ordinary final unit ratios use exact quotient/remainder rounding.

The code-quality stage found a missing FX-identity draft case. Its bounded
correction was reviewed directly: optional identities are parsed and omitted
from `fx_refs`, while `/fx/<index>` dependencies, dated evidence, strict
handover gaps, input purity and private ancestry remain. Fresh controller
validation passed **109 baseline/calculator tests**; the worker's combined
run passed **190 tests**, including all 81 legacy Preview cases.
Rehashed fabricated results, stale receipts and cached acknowledgement do not
become valid calculation lineage.

These are scoped AI-assisted technical checks, not independent human approval,
verified commercial rates, financial authority or full L1/L2. The interim
full-check attempt exposed the separately corrected authority-ID guard; its
failure is not replaced by a success claim. Integrated full gates, browser,
final extracted-package execution and repeatable distribution remain pending.

The first real snapshot/CLI save-reload exercise exposed object-key iteration
changing diagnostic-array order. The producer correction at `6bef994e`
canonically orders only derived diagnostics, preserving authored and meaningful
arrays and strict forged-output rejection. Four focused permutation/roundtrip
regressions passed independently; the worker's combined run passed 194 tests.

## Task 3: Records, projection and CLI checkpoint

The reviewed checkpoint is
`b623228aba2122c7904b33d225294c4ce08e6c55`. It adds versioned snapshots,
externally evidenced review records, strict dated planning handover,
context-only explicit legacy migration, dependency-projected JSON/Markdown
and Blueprint report data, and the guarded CLI. It does not authenticate
financial authority or implement the wrapper, renderer or live operating loop.

The independent spec/privacy stage closed source-class/scope inheritance,
transitive reference closure, diagnostic-gap-path restrictions, digest/ID
aliases and mapping keys, schema-key collisions and synthetic-review cases.
The quality stage closed current-Blueprint apply ancestry, source cycles and
accepted nullable drafts. Shared DAG joins and unrelated public rows remain
usable; cyclic/restricted dependencies are withheld rather than zero-filled.
Synthetic records remain demonstrations, never financial permission.

The final bounded report correction was reviewed directly: merge the current
calculator's complete diagnostics with consumer-only cycle gaps, deduplicate
whole records and preserve canonical order/period/block context. Three focused
internal/customer API, Markdown and actual CLI coverage tests passed in the
controller loop. The worker's full focused run passed **292 tests**
(98 records/export plus 194 prior baseline/legacy tests), with all previous
privacy and synthetic controls retained. Installer metadata was regenerated
against the complete modules; all 93 source hashes were checked.

These are intermediate source-qualified checks. Final L1/L2, actual installed
handoff execution, screenshots and repeatable distribution are still pending;
no interim plugin ZIP is declared ready for distribution.

## Independent authority-document checkpoint

The PRD now has the approved candidate requirements **FR-0142 to FR-0153**
and **AC-045 to AC-056**, mapped to AFB-01 to AFB-12. The solution design adds
the intended offline boundaries/flow and explicitly pending B.9 verification.
These are approved requirements/design, not implementation or completed
calculator/integration/archive proof.

Parent checks passed `python tools/dev.py docs --strict` with zero errors,
new-definition uniqueness and actual historical byte preservation:

| Historical suffix from the 1.9.2 heading | Bytes | SHA-256 |
|---|---:|---|
| PRD | 65204 | `2db290c8000d4218da2cab2138ae92b65a0ac78cb910a4c1a63b2bdc105283a8` |
| Solution design | 63565 | `21b511ddab39de96e8f535f792d3874274d69e01102ff2251eb99adca456bf71` |
| CHANGELOG | 20500 | `227cd620b28b17b7e55c7393e5df8ac7d7b990895a47dfa3f85068559d4161bb` |

A subsequent unit check exposed the old identifier guard's finite allowlist,
which stopped at the approved 1.9.1 additions. The controller reproduced three
failures, then added a failing in-memory 1.10.0 boundary/identifier regression.
The guard now admits only the specifically approved 1.10.0 IDs when both
documents have exactly one named boundary. Future/unapproved IDs and missing/
duplicate boundaries still fail. The historical 1.9.1 simulation removes only
the later candidate block in memory, retaining its original unapproved-ID
checks; the migration fixture and historical content are unchanged.

All **25 documentation-contract/mutation tests** and targeted Ruff now pass.
This fixes a directly coupled documentation contract, not a bypass of historical
preservation. Full L1/L2 and final installed/distribution proof remain pending.

Protected routing [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
and release-cache [#30](https://github.com/urruegg/frontier-envisioning/issues/30)
remain human-owned. No merge, tag/release, deployment or protected edit is
authorised by this sprint record.

## Task 5: Explicit fixture and initial installed-package checkpoint

The initial tooling checkpoint is
`969dccca3c3d7dee423976b4ae1ad9850dabcac6`, independently reviewed against
the documentation-only successor `ca74dc7e`. The default core and legacy
profiles remain separate from the explicit baseline fixture. Its real data
island has one dated Preview record, `financial_permission: false` and blocked
synthetic handover. The local test site computes the page's actual CSP with
`connect-src 'none'`; this is not browser/UI verification.

The combined profile/site/runner tests went from **53 tests, 17 failures and
one error** to **55 passing tests**, including added reserved-output controls.
The actual self-test passed **68 checks**, retaining all 48 prior assertion
contracts. Its `ALL GATES PASSED` is the self-test step only, not full L1.
Independent fresh extraction passed **20 actual installed CLI checks**:
acknowledgement refusal without outputs, acknowledged synthetic lifecycle,
JSON/Markdown privacy, snapshot/receipt/review integrity, eight read-only
installer plans and core operation with the FinOps skill removed. Execution
used extracted scripts/examples/helpers, not working-tree imports.

The initial archive has **101 members**, all checked against source bytes and
the generated installer recipe. SHA-256:

- Plugin ZIP: `bed02d7ccf8d47382f6c23f71b5457fac49d68881e5f46223e0a57b62990368f`
- Installer: `257b8c0a2704fc2526fe6a7dd8f12ebf9bc525dd2c84e32e5f6469fbc46a9016`

Independent spec review passed. Subsequent quality review reproduced three
**Important blockers**, despite the 55 passing tests. They were fixed
test-first in `39ade06067842b755b5b29df17c13eeec89ffab3`:

1. Relative demo output was validated against caller CWD but interpreted by
   the child against the repository root, bypassing reserved-core protection.
   One caller-resolved absolute path now reaches every boundary. Independent
   real-wrapper probes confirm successful caller-relative output and refusal
   before touching reserved core.
2. Site cleanup could delete an explicitly supplied fixture nested inside
   the output directory after caching its HTML. Resolved equal/ancestry/alias
   overlaps now refuse before cleanup, preserving every consumed fixture.
3. Isolated Python `-E` ignored the UTF-8 environment setting, breaking
   decoded CLI output under a Unicode temporary path on Windows. Explicit
   `-X utf8` now enables child UTF-8 while retaining environment, user-site and
   bytecode isolation; no decoding error is suppressed.

The combined suite now passes **60 tests**, retaining the previous 55; all
**68 self-test checks** passed again. The exact initial ZIP passed **20 checks
under a Unicode temporary path**, including the original core-helper failure;
all 93 packaged skill files still match source bytes. The ZIP/installer hashes
above are unchanged. The controller independently passed the five new
regression methods; retained quality review passed 15 selected tests and
re-probed all three original failures without alias skips.

All three findings are closed, with no new high-confidence quality finding.
This clears Task 5 for Task 6, not human approval or overall merge readiness.
The initial archive/proof is not final distribution clearance; Task 8 repeats
execution against the exact final ZIP.

## Task 7: Source-guidance checkpoint

Source guidance was committed in `6228dd00` and `ca74dc7e`. FinOps,
orchestrator and Blueprint procedures each had a fresh consumer retrieval
probe before editing: the successor baseline/frozen-review workflow was not
documented. Sequential updates and repeated scenarios made that workflow
retrievable while retaining declined-core continuation, independent ordinary
value, current awareness and external-review limits. These are local procedure
tests, not live Cowork routing, actual financial consent or authenticated review.

The three descriptions measure **610 / 681 / 720 UTF-16 units**, each below
900; versions and negative routing remain intact. Parent review covered every
changed prose diff; strict documentation checks reported **zero errors**.
The reader journey and five-view gallery stay core-only. The baseline starter
first shows the full notice and waits for an actual response.

The historical suffix hashes above were rechecked unchanged after the
candidate-only changelog update. Generated HTML, five genuine captures and
manifest are still to be rebuilt after Task 6; the manifest owns their actual
version and hashes. No capture, full-gate or final-package result is inferred
from the updated guides.

## Core-only consumer-guard checkpoint

The controller reproduced a successor-data gap in the gallery and complete
bundle consumers. A core-tagged build report was insufficient proof that the
actual HTML contained no FinOps. Two gallery and five bundle subtests failed
before the fix, while the ordinary core/archive control passed.

Commit `1573c0c717a3dd4d2c57c3b02ae49644a98cc270` extends the existing
canonical core validator to `agent_finops` and reuses it on actual bundled
HTML before any overwrite. Successor report metadata also refuses. All
**17 focused consumer tests** passed, preserving previous outputs/checksums
and exact archive contents for valid core inputs. Actual full core HTML was
accepted; actual baseline HTML was rejected. Ruff, whitespace and strict
documentation checks passed; all three historical suffixes remained unchanged.

## Task 6: Renderer checkpoint

The accepted checkpoint is
`9a453857e7a55f9f016c3ce86d7f16cb580e6cf9`, following the initial
`151cdbb3` and spec corrections `a0bd2ef8`. It adds the separate projected
baseline view, transient acknowledgement, exact decimal text and gated
JSON/Markdown reports. The financial criterion remains within the existing
eight checks; other checks and declared build/release/operate stages remain.
Workshop proposals are new-draft inputs, not frozen-model edits or approval.
Independent ordinary value remains independent.

Spec review found and closed contradictory pricing/contribution statuses,
inconsistent projected owner/delegation/dates and omitted known-priced
subtotals. Subsequent quality review found and closed wrong-agent association,
missing frozen-version equality and contradictory consumed rate/source
evidence. The fixes preserve legitimate empty contribution groups, projected
customer hash omission, optional aliases and independent unused context.
They do not calculate prices, reconstruct hashes or authenticate external review.

Actual proof:

- The final cold template/demo/DOM/package run passed **161 DOM tests**:
  the prior 75 plus 86 new cases. Its `ALL GATES PASSED` covers those selected
  steps, not full L1.
- The focused Chromium run passed **17 tests**, including actual downloads,
  acknowledgement reset, private/unpriced states, known-priced subtotals,
  keyboard/reflow/accessibility and strict CSP. Recorded console errors and
  external requests: **zero**. Local test servers were stopped.
- Independent spec review passed 93 relevant DOM tests and actual projected
  Blob-download checks; the pre-fix renderer failed 27 of 29 new regressions,
  retaining two valid controls.
- Independent quality closure passed **122 relevant DOM tests** and
  **14 in-memory producer/consumer probes**, including all original failures.
  The controller separately passed the 29 spec-correction cases.
- Assembly and installer-recipe comparisons matched. ESLint reported zero
  errors and six inherited warnings; no adjacent tests were weakened.

Generated template SHA-256:
`1cd5d0596461730dc9599252e02477f093a7e370a80a89c87cfe72559ad02465`.
Genuine observed light/dark and association/subtotal captures and actual
downloads are retained under `build/evidence/task6/`. Positive readiness probes
use explicitly labelled test-only DTOs; the shipped producer example remains
synthetic and financially blocked.

## Ordinary combined-regression checkpoint

At `9a453857`, the unmodified command
`python -m unittest tests.unit.test_finops_baseline tests.unit.test_finops_baseline_io tests.unit.test_finops_preview -v`
passed **336 tests in 421.333 seconds**, exit zero and no skips. This is
targeted Python verification, not full L1/L2.

An earlier quiet run was interrupted before a result. A repeated-faulthandler
diagnostic then exited with a Windows native error while dumping a stack;
that diagnostic is not passing or failing production-test evidence.
An independent bounded investigation reproduced neither an ancestry defect
nor the native crash: the original two cases and 22 affected cases passed
normally, and measured ancestry work did not justify a source change.
No speculative optimisation, test reduction or exception suppression was made.
The complete ordinary 336-test run above subsequently passed in the same order.
The instrumentation failure's cause remains unestablished.

All source checkpoints are now reviewed. Full strict gates, final archive
reproduction/installed execution and the draft pull request remain pending;
scoped checks do not imply their completion.

## Generated core-documentation checkpoint

The standard `python tools/dev.py template package demo docs-demo` command
completed successfully after renderer and core-guard review. The template
remained 399,470 bytes. Full core regeneration verified all 205 named identity
inputs and restored the same 223 historical rasters; no future profile was
enabled. The current plugin ZIP hash at this checkpoint is
`af7bd2e10c8e34ed7f15800b60e31166c2ab9139dc2b1f31f31023a3289e94cf`;
this is not yet final distribution/repeatability proof.

The tracked core HTML and manifest now identify **1.10.0**, with 17 routes and
no FinOps. All five 1440 × 1000 light viewport captures were genuinely
recaptured and manually viewed: Overview, Org model, Agents, Agent identity
and Ontology. Their PNG bytes remained identical; the HTML and manifest changed.
The manifest records Chromium 156.0.8078.4 / Playwright 1.64.1, en-GB, UTC and
reduced motion. It owns the actual hashes and capture settings.

- Core HTML SHA-256: `44ad69aaddbd269debb468408a642daa38766e8e70661e79480576a9fb928e8b`
- Canonical HTML SHA-256: `1ecd07d7ebb398364ad76eb78b6bd6f1bf50a8138639c63437bca4ab84214d52`
- Source fingerprint: `422b646724247825e426e88afea0740408d40df9e89b7d1fdb8ba5cc21835c72`

`python tools/build_docs_demo.py --check --demo build/demo` verified the actual
fresh core, source fingerprint and five captures. Strict documentation checks
reported zero errors. These generated examples remain synthetic internal
workshop aids, not deployment, pricing verification or sharing clearance.

## Final integrated corrections and review

The fresh cross-component review of `02d3eaf` found two Important gaps that
the earlier scoped reviews had not caught: valid, reviewed recurring-only
producer reports were falsely blocked by the UI's one-time check; and approved
specification section 5.10's evidenced driver-coverage metric was missing.
Neither was accepted as a limitation.

Producer commits `5163ff0a` and `7dfdb79f` add
`driver_coverage` to results, dated handover and projected root/nested reports:
`priced_driver_count`, `in_scope_driver_count`, `status` and `reason`.
Only drivers whose applicable lines/periods have calculable quantities and
current applicable evidenced rates/FX count as priced. Unpriced drivers stay
in the denominator; provisional pricing is not complete evidence. Empty
scope is unavailable, not complete. Restricted consumed dependencies withhold
both counts; unrelated unused/private outcome context does not taint them.
Counts are not monetary exposure or proof that all real-world costs are known.

Actual producer proof includes nine initial failing tests with 29 assertion
failures, then nine passing tests and a 345-test normal regression pass.
Independent review then found a transitive consumed rate/FX source-gap case:
that correction had five expected failures before passing. All four consumed
stale/unverified parent variants now yield 2/3 incomplete, while unused-parent
controls remain 3/3 complete. Independent coverage closure passed 11 focused
tests and actual CLI/JSON/Markdown/receipt/privacy probes. The controller
separately passed 15 coverage tests. Monetary outputs/statuses and material
fingerprints remained unchanged. These ratios are test fixtures, not a quote.

Renderer commit `e2f5d9c1aa00056c8f50815ca3ce2c34dd03803a` respects reviewed
absence of one-time lines without inventing zero or weakening declared
unpriced/private costs. It displays the supplied coverage metric, gates it
with financial acknowledgement and preserves projected null counts.
Actual-producer recurring-only cases had two failures and three valid
controls before the fix; all five now pass. Seventeen initially failing
coverage-view cases now pass. The controller passed all 22 new cases.

The final cold DOM run passed **183 tests**, retaining the previous 161.
Focused real-CSP Chromium passed **18 tests**, including actual producer
flows, JSON/Markdown downloads, privacy, acknowledgement, keyboard,
accessibility and reflow; console errors/external requests remained zero.
Genuine component captures were inspected. Renderer template SHA-256:
`d43d0105ce3892538b31edeb7949fa8d79852689f709faa1bc3fd237082db006`.

The original final reviewer independently re-probed both findings at clean
`e2f5d9c1`: **12 audience cases passed**, with no remaining findings in that
bounded review. One-time-only scope did not establish a producer-ready/UI-blocked
mismatch. No source was changed by review and no authentication, real finance
approval or overall merge readiness is inferred.

The earlier generated-example hashes remain qualified to their checkpoint.
Full strict L1/L2, exact final-ZIP installed execution, two-build distribution
identity and the draft PR still follow.

Final standard regeneration after `e2f5d9c1` completed successfully:
`python tools/dev.py template package demo docs-demo`, followed by
`python tools/build_docs_demo.py --check --demo build/demo` and strict docs.
All 205 named identity inputs and 223 rasters were verified/restored again.
The template is 403,143 bytes; the current plugin ZIP SHA-256 is
`ca41bc60f0e7231476528dca6468f3f4222fe49ed1b403380ed3a41eac562b06`.
These remain generation checks, not full global/distribution acceptance.

The final core manifest records HTML SHA-256
`2e8d837642dd65659d20cb513884824d2ee0158c6a5cd0cbaa39880943d65bd2`,
canonical HTML
`df012181483342ebefac79ea0d0a5fe09e97695076e28def125eb9278b0c7d5a`,
and source fingerprint
`90252d29a5b675e0d7e6fddd9ec394e44ef1235896ba00b566a9d8ad78536ec4`.
The five genuine recaptures remain byte-identical to the five manually
inspected views. Core still has 17 routes and no FinOps.

## Full strict local gates

The final program/test source is `5262db5b8a42ef63fb4bdd4b0a3e3c12832fd0db`.
Both full commands ran sequentially and ended **ALL GATES PASSED**:

| Command | Actual result |
|---|---|
| `python tools/dev.py check --strict` | 711 tests passed, one expected unreleased-version skip, 2,355 subtests passed; 68 plugin self-tests and 183 DOM tests passed. Repository rules/Ruff/docs/neutrality passed; ESLint had zero errors and six inherited warnings. |
| `python tools/dev.py site e2e --strict` | 75 Chromium tests passed; the showcase step and full browser gate passed. |

The first L1 attempt found one directly dependent old test fixture: its bare
`b"demo"` HTML was now correctly rejected before the intended nested-package
privacy check. The controller reproduced the failure, supplied the existing
valid core fixture and preserved all privacy/error/no-overwrite assertions.
Commit `5262db5` changes only that test fixture. All 28 focused privacy and
core-consumer tests then passed before the full rerun. No production guard,
skip or exception policy was relaxed.

The successful L1 unit/pipeline run took 1,127.82 seconds; the full browser
suite reported 12.3 minutes, with 884.1 seconds for its preparation/execution
step. Raw command summaries are retained in
`build/evidence/finops-strict-l1-5262db5.log` and
`build/evidence/finops-strict-l2-5262db5.log`. Browser reports contain attached
actual screenshots and downloads; CI evidence remains separate.

After these program-source gates, PRD/solution-design changes record actual
automation evidence only. They do not change executable behaviour or claim
live Cowork routing/installation, authenticated finance authority, manual
assistive-technology acceptance, external/IP clearance, publication or deployment.
Archive-specific execution, repeat-build identity, hashes and the draft PR
are recorded only after the remaining checks.
