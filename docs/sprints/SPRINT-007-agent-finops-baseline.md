# SPRINT-007: Agent FinOps baseline before build handover

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Backend and optional build integration reviewed; explicit test fixture and user guidance in progress; final gates pending |
| Scope | Offline baseline-first 1.10.0 internal candidate, not live FinOps operations |
| References | [Catalogue](README.md), [Parent #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [Idea](../ideas/2026-11-12-agent-finops-baseline.md), [Design](../specs/2026-11-12-agent-finops-baseline-design.md), [Plan](../plans/2026-11-12-agent-finops-baseline-plan.md), [ADR-0028](../adr/0028-versioned-agent-finops-baselines.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#35](https://github.com/urruegg/frontier-envisioning/issues/35) | [Outcome/input](../ideas/2026-11-12-agent-finops-baseline.md) | [Baseline design](../specs/2026-11-12-agent-finops-baseline-design.md) | [Tasks 0-8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; accountable | Actual D35-09 plan/readiness approval recorded | Approved for bounded implementation; no label change inferred | Spec approval `2e3c0e7`; plan approval `efb3468`; no delivery/PR proof yet |
| [#38](https://github.com/urruegg/frontier-envisioning/issues/38) | [Baseline-first](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01 to AFB-10](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D1, Tasks 1-3](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D1, estimated M | Actual plan approval and reviewed Task 0 | Engine/records/export checkpoint reviewed at `b623228a` | Integrated wrapper/UI and final installed/distribution proof pending |
| [#37](https://github.com/urruegg/frontier-envisioning/issues/37) | [Canvas/handover](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-01/06/09/11](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D2, Tasks 4/6](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D2, estimated M | Reviewed D1; fixture preparation before UI | Task 4 reviewed at `11e11f18`; explicit fixture preparation running | Renderer and browser proof not yet delivered |
| [#39](https://github.com/urruegg/frontier-envisioning/issues/39) | [Verified candidate](../ideas/2026-11-12-agent-finops-baseline.md) | [AFB-10/11/12](../specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance) | [D3, Tasks 0/5/7/8](../plans/2026-11-12-agent-finops-baseline-plan.md) | `@urruegg`; D3, estimated M | Preparation first; final proof after D1/D2 | Task 0 reviewed; remaining D3 work pending | Scoped evidence below, not full 1.10.0 quality/distribution proof |

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
The explicit fixture, self-test and UI work follow this checkpoint.

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
