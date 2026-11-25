# SPRINT-013: Agent Factory handover

| Field | Value |
|---|---|
| Version | 0.7 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Full plan/readiness `5dbfc8a` approved; #74/#75/#76 locally verified and reviewed; #77 projection/export CLI in progress; final integration/gates pending, Cowork deferred |
| Scope | Planned 1.11.0 optional Agent Factory handover only; systems/D365 deferred |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [Idea](../ideas/2026-11-25-agent-factory-handover.md), [Design](../specs/2026-11-25-agent-factory-handover-design.md), [Staged plan](../plans/2026-11-25-agent-factory-handover-plan.md), [Actual written approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078), [#58 deferral](https://github.com/urruegg/frontier-envisioning/issues/58#issuecomment-7161780922) |

## Outcome and work item

Add **Envisioning Agent Factory**, registered as optional Preview
`frontier-agent-factory` inside the existing plugin. Prepare a full starter
repository ZIP from the exact selected template and relevant reviewed
envisioning files, with explicit gaps and real transfer/review evidence.
No business runtime, remote repository, tenant provisioning or deployment.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#72](https://github.com/urruegg/frontier-envisioning/issues/72) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-01-AF-16](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Approved combined production plan](../plans/2026-11-25-agent-factory-offline-implementation-plan.md) | `@urruegg` accountable | Reviewed bounded #74-#79 slices and final actual candidate gates | Full plan approved; execution in progress, not complete | [Actual full-plan receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7167852054); earlier spec/W0/host receipts below |
| [#73](https://github.com/urruegg/frontier-envisioning/issues/73) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [Host/receiver boundary](../specs/2026-11-25-agent-factory-handover-design.md#4-template-discovery-acquisition-and-compatibility) | [W0 Tasks 1-4](../plans/2026-11-25-agent-factory-handover-plan.md#3-w0-task-1-baseline-and-exact-source) | `@urruegg` accountable and assigned; bounded receiver builder | Actual W0/host-amendment approval; pinned reference and isolated dependencies | Actual source/receiver exit verified: 30 pass, one privilege skip, four validators exit 0; Cowork deferred/not performed | Ordered parent specification then correctness review; attribution correction applied; no protected ready/approval label inferred |
| [#74](https://github.com/urruegg/frontier-envisioning/issues/74) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-16](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Task 1](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#3-task-1--baseline-then-bump-then-finite-raster-profile) | `@urruegg` accountable and assigned; bounded builder | Actual full plan/readiness `5dbfc8a` | Local `c51c6e9` version/raster slice verified; not final Factory candidate | [Bounded review/evidence](https://github.com/urruegg/frontier-envisioning/issues/74#issuecomment-7169371390) |
| [#75](https://github.com/urruegg/frontier-envisioning/issues/75) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-02-AF-08/10](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Tasks 2-4](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#4-task-2--w1-strict-data-safe-local-reads-and-fixed-schema-subset) | `@urruegg` accountable and assigned; bounded builder | Reviewed #74 | Local `bf54731` cleared both ordered reviews; 37 focused tests passed | [W1 handoff/evidence](https://github.com/urruegg/frontier-envisioning/issues/75#issuecomment-7170756785); no whole-exporter/final-gate claim |
| [#76](https://github.com/urruegg/frontier-envisioning/issues/76) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-04/10/11](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Tasks 5-6](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#7-task-5--w2-extract-the-proven-raw-zip-mechanism-without-release-drift) | `@urruegg` accountable and assigned; bounded builder | Reviewed #75 | Local `d1c0b3f` cleared both ordered reviews; archive/release focused proof below | [W2 handoff/evidence](https://github.com/urruegg/frontier-envisioning/issues/76#issuecomment-7171760018); no full Factory candidate claim |
| [#77](https://github.com/urruegg/frontier-envisioning/issues/77) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-05-AF-11/14/15](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Tasks 7-10](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#9-task-7--w3-passive-authored-byte-projection-and-explicit-selection) | `@urruegg` accountable and assigned; fresh bounded builder | Reviewed #75/#76 | Projection, privacy/financial boundaries and CLI implementation in progress | No completed exporter or final-gate proof yet |
| [#79](https://github.com/urruegg/frontier-envisioning/issues/79) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-01/12/13/16](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Tasks 11-13](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#13-task-11--w4-ninth-skill-maturity-installer-and-registration) | `@urruegg` accountable and assigned | Reviewed #77; disjoint prose #78 before final gates | Pending; not delegated | No ninth-skill/package/receiver candidate result yet |
| [#78](https://github.com/urruegg/frontier-envisioning/issues/78) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-01-AF-16 documentation](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Task 14](../plans/2026-11-25-agent-factory-offline-implementation-plan.md#16-task-14--w4-productengineering-prose-not-historical-rewriting) | `@urruegg` accountable and assigned; eligible docs route | Reviewed #77; coordinates disjoint #79 code | Pending; not delegated | No fictional product/release verification |

Create real bounded child issues only when their actual execution plans are
approved, before delegation. Do not treat W0 evidence as approval for unwritten
W1-W4 plans. No assignee, milestone or protected label has been inferred.

## Actual human decisions

Conversational sections were approved with no changes: factory boundary,
artefact contract and validation. The human selected full-starter-repository,
review-starter-with-explicit-gaps, GitHub Cloud first, latest stable template
discovery with explicit immutable unreleased bootstrap only after a healthy
no-release lookup, and subagent-driven implementation.

The actual written specification was then presented at
`7f650c48bdce5c94f4f1745119e1ea87dd0b0f24` and separately approved:
`written_spec=approve-written-factory-spec`, `changes=no changes`.
The committed specification's automatically recorded SHA256 is
`7655d0340508e5f203aaeb7f9e1c11eff0f22efff58e0a3d6390099aa3eeb7d0`.
This is approval evidence for that document, not a recurring user hash step,
formal GitHub self-approval, plan approval, tenant permission or publication.

The independent systems/D365 programme #58 moves to a later unspecified
release. Its old 1.11 target is historical; this sprint does not absorb its
scope or invent a new deadline.

The staged plan and full sprint at `c8cc5bb` were subsequently presented and
actually approved with `approve-w0-and-start-receiver-verification`,
`no changes`. A real bounded child #73 was then created and assigned before
dispatching a fresh developer receiver worker. The actual Cowork-evidence
request received **"we din't have it at all"**, not a host pass. The written
host-gate amendment at `f4b2609` was then separately presented and actually
approved: `approve-offline-preview-defer-cowork-validation`,
`no change please proceed`. The [actual receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613)
approves offline Preview development with actual source/receiver proof;
Cowork remains not performed and cannot be advertised as validated.

## Staged execution and blockers

| Work package | Exit / acceptance | Current state |
|---|---|---|
| W0: verification spike | Genuine available-host source/reference acquisition and actual pinned receiver checks; actual Cowork explicitly deferred under approved amendment | Verified source/reference and receiver evidence, 30 tests passed/one skip and four validators exit 0; no simulated host pass |
| W1: local source/intake contract | Strict offline receipt/profile, ID/scope/role/evidence/review/history handling; real RED/GREEN and actual approved exact plan | #75 locally verified at `bf54731`; both ordered reviews clear, 37 focused tests passed |
| W2: archive | Bounded raw ZIP validation, safe paths/modes/inventory, threshold and good-output-preservation tests, shared-helper reuse without release regression | #76 locally verified at `d1c0b3f`, both ordered reviews clear |
| W3: projection/export | Approved authored bytes, scope/privacy/FinOps boundaries, deterministic full ZIP, separate truthful statuses | Approved plan and reviewed W1/W2; #77 implementation in progress |
| W4: integration/acceptance | Ninth optional Preview skill, current metadata/docs/installer/self-test, independent package/receiver proof and exact-head gates; unavailable Cowork explicitly not performed | Blocked by reviewed W3 and actual production-plan approval |

The [combined production plan](../plans/2026-11-25-agent-factory-offline-implementation-plan.md)
at `5dbfc8a` actually received `approve-complete-plan-and-implement`, with
no revision requested. Its [real approval receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7167852054)
governs the W1-W4 tasks with bounded fresh workers and ordered technical review,
not repeated human check-ins between already-approved tasks.
No new producer RED/GREEN or implementation result is implied by that plan.

Actual Cowork exact-template archive retrieval is **not demonstrated** by this
VS Code session. The approved amendment permits offline work, not networking
inside the plugin or a claim that the absent host is supported.
W0's actual fixture tests validate only the reference receiver. They do
not validate a producer that has not been built.

The receiver's 64 MiB cumulative validation budget counts baseline bytes
and, with `--source-root`, original bytes too. Later threshold tests must
exercise that actual traversal, not treat it as 64 MiB independently for each.
Engineering gaps can remain in valid needs-clarification intake; missing
mandatory structural/evidence fields cannot be filled with fictional values.

## Actual planning evidence

The design-only package at `7f650c4` changed five Markdown records/catalogues.
`python tools\dev.py docs --strict` passed with zero errors and its own
`ALL GATES PASSED` summary; `git --no-pager diff --check` passed.
Inline placeholder/consistency/scope review passed, and the planning branch
was clean and pushed before written-spec review.

During plan preparation, read-only API byte inspection confirmed reference
`0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`:

- `docs/intake/intake.schema.json`: 8,381 bytes, SHA256
  `04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f`.
- `tools/intake.py`: 15,736 bytes, SHA256
  `4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370`.
- Actual receiver code confirms strict schema plus role/transfer/review/path/
  digest checks, and the shared source/baseline byte budget.
- Live #72 is open with no assignee/milestone and no protected approval/ready
  labels. That observation does not revoke the actual written-spec approval.
- Actual local inventory found Python 3.14/3.11 and Node `v26.13.1`.
  The available Python 3.14 meets the declared receiver minimum, not proof
  its dependencies/tests pass. Node 26 is not the Node 24 LTS profile;
  no full receiver toolchain readiness is claimed.

No upstream code, new producer test, template acquisition in Cowork, full
gate, customer ZIP, plugin bump or product change was performed by planning.
Future evidence must be appended with real commands, outcomes and source IDs.

## Actual W0 execution and ordered evidence review

The bounded worker successfully queried the complete release/tag lists:
both empty at its 25 November observation. It acquired an exact clean
reference checkout at `0bb2b1b`, verified all 149 ordinary source blobs /
726,850 bytes and both schema/validator fingerprints above. This does not
select a customer bootstrap, authenticate an archive signature or prove
continued latest-release absence.

The initial Python 3.14 command failed before intake tests ran because an
unrelated user-site `tools` package shadowed the pinned namespace. Process-only
user-site isolation resolved that collision and exposed a real missing
`jsonschema` dependency. The first official-PyPI restore failed TLS. The
second/final attempt used normal existing package-manager configuration and
restored the pinned `jsonschema==4.25.1` into the task's isolated receiver
environment. No shared environment, pin, certificate, proxy, authentication
or TLS-verification setting was changed; no feed/account details are retained.

Actual final receiver context:

```powershell
$factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
$python = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env\Scripts\python.exe'
$fixtures = Join-Path $factory 'tests\fixtures\intake'
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
$env:PYTHONNOUSERSITE = '1'
Set-Location -LiteralPath $factory
```

| Actual command after that context | Result |
|---|---|
| `& $python -m unittest discover -s tests -p test_intake.py -v` | Exit 0: 31 tests, 30 passed, one skipped, zero failures/errors; `test_symlink_is_not_followed` skipped for Windows privilege error 1314 |
| `& $python -m tools.intake validate (Join-Path $fixtures 'accepted.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: baseline and source bytes; recorded human approval not authenticated |
| `& $python -m tools.intake validate (Join-Path $fixtures 'needs-clarification.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: baseline and source bytes; recorded human approval not authenticated |
| `& $python -m tools.intake validate (Join-Path $fixtures 'rejected.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: valid synthetic rejected disposition, no provided artefact bytes; not accepted scope or transfer permission |
| `& $python -m tools.intake validate (Join-Path $fixtures 'accepted.json') --root (Join-Path $fixtures 'workspace')` | Exit 0: baseline bytes and recorded evidence only; originals explicitly not checked |

These are real reference-receiver results, not tests of a future producer.
All fixture identities and approvals remain synthetic. Node 24/full receiving
toolchain certification and actual Cowork checks remain not performed.

The parent reviewed specification compliance first, then correctness of the
bounded evidence. A narrow attribution issue was corrected: the normal-source
recovery instruction came from the controller, not an additional human
approval or a newly supplied feed identity. The actual human W0 and host
amendment receipts remain separate. No further receiver defect was inferred.

Required new producer coverage remains explicit: restricted material,
approved transfer with absent approval, junction/reparse safety, unexecuted
symlink rejection, generic/equal-digest transformation errors, non-finite JSON
and exact-at/one-byte-over limits including the shared source/baseline budget.
Do not treat the reference's absent tests as passing coverage.

The source checkout and restored receiver environment are task-owned and
retained for directly dependent implementation planning and actual produced-
package acceptance; no background helpers remain. No current/upstream
repository source was edited by the receiver worker. Existing historical
failures stay in the session evidence report rather than being rewritten as
passes. No plugin bump, new exporter, customer ZIP or protected action occurred.

## Combined production plan: written, not implemented

The [actual W1-W4 plan](../plans/2026-11-25-agent-factory-offline-implementation-plan.md)
has been written and corrected after direct review. It now includes minimal
complete-release metadata, unknown-stable failure cases, selection from the
customer-safe tree, strict input prevalidation, legacy financial detection and
byte-preserved accepted history with portable path/collision checks.
One actual approval of that complete written plan can govern all its tasks;
technical review is not an extra human approval loop between approved tasks.

Actual planning validation passed: `python tools\dev.py docs --strict`
reported zero errors and its own `ALL GATES PASSED`; whitespace passed.
All 33 Python, three JSON and nine PowerShell code blocks passed syntax
parsing **without execution**. These checks do not claim new producer
RED/GREEN, package compatibility, a product full gate or Cowork support.
The actual full-plan/readiness approval subsequently received is recorded
above. It is not a product test result or human-only permission.

## Task 1: actual baseline and named 1.11.0 profile

The existing isolated worktree moved from approved planning `5dbfc8a` to
`feat/72-agent-factory`; no second worktree or primary-checkout change.
All six real bounded #74-#79 issues were created and assigned before their
workers, using the existing non-protected labels only. No protected
ready/approval label, milestone or formal GitHub approval is inferred.
The parent/work-package links are real body/plan cross-references; no native
GitHub sub-issue relationship is asserted.

Before any plugin edit, the unchanged **1.10.1** baseline at `5dbfc8a` ran
focused evidence/raster tests (51 run, 50 passed, one Windows privilege skip),
package/demo (205 non-raster inputs, 223 pinned PNGs; tracked sources unchanged),
and `python tools\verify_release.py --online`. That authoritative exact-version
lookup returned **development**, no exact published release/conflicting tag;
it was not a comparison of published 1.10.1 or current output with 1.10.0.

The same fresh process-local `$env:CI='true'; python tools\dev.py check --strict`
completed before bumping, ending **ALL GATES PASSED**: **924 passed,
eight skipped, 3,108 subtests**, self-test passed and **201/201 DOM tests**.
The known skips and pre-existing ESLint warnings remain in the actual evidence,
not rewritten as new-code successes. This is a local CI-context baseline, not
an actual server CI result for the final feature.

The first plugin change was sanctioned `python tools\dev.py bump 1.11.0`.
The new profile then observed real RED: 12 tests, 15 assertion failures,
zero errors, including named 1.11.0 replay being rejected. Minimal finite
support and its actually measured profile pin made the module GREEN:
12 passed; all 49 raster-family tests passed. Seven historical profile/base
records remained byte-identical. The source change adds only named 1.11.0,
not broad future-version support or relaxed release/archive authority.

Four extra exact-set assertion call sites required adding literal 1.11.0;
the [controller clarification](https://github.com/urruegg/frontier-envisioning/issues/74#issuecomment-7168719768)
records this coupled correction, not another human approval or a changed
product boundary. Candidate package/demo again passed 205/223 with the identity
ZIP rebuilt, not golden-copied; generated inventory came only from package.

Local commit `c51c6e92abdc8aa4625fe1e4413185d01e368b76` contains the 22 owned
version/profile/test/inventory paths. The parent completed specification review
then correctness review, and independently reran all 49 raster-family tests
(12.307 s, zero skips), strict repository rules (1.11.0, 668 files, zero errors)
and whitespace at that clean head. The [actual bounded evidence](https://github.com/urruegg/frontier-envisioning/issues/74#issuecomment-7169371390)
does not claim the new Factory skill is implemented, a final integrated full
gate passed, server CI passed or Cowork was tested.

## W1: actual strict source/intake contract and review corrections

The bounded #75 worker implemented only the ten owned common/contract,
reference/example and synthetic fixture/test files, initially at local
`af010b5`. The actual schema and validator-as-text fingerprints match the
pinned reference; exact MIT notices are retained in the packaged reference
and test fixture. No upstream code is executed or full source archive committed.
Real behavioural RED/GREEN covers strict JSON/types/dates, ordinary-file reads,
native junction refusal, exact byte limits, source receipts, all eight roles,
actual transfer/review/transform structure and immutable history.

Initial 28 passing tests were **not** treated as specification proof. Stage 1
found three real contract mismatches: an invented tag naming policy, malformed/
duplicate dependency-gap IDs passing prevalidation, and a flat-only artefact
restriction contrary to the pinned receiver. The same builder reproduced and
fixed all three at `f699b404`, preserving valid Git tags, exact pre-I/O IDs and
nested Windows-path artefacts. Stage 1 re-review returned **SPEC_COMPLIANT**.

Stage 2 then reproduced a blocking canonical FILE/descendant collision plus
timestamp-fraction precision and history-ID edge cases. They were fixed
test-first at `bf54731e2058dc456edbc69bc918160d6df4f8bc`:

- Canonical FILE ancestor/descendant conflicts reject in both orders before
  I/O, without rejecting distinct prefixes or explicit exact source reuse.
  Directory entries in future ZIP handling remain a separate concept.
- `timestamp_key(value)` compares UTC whole-second ordinals and full fractional
  digits without float/microsecond truncation; equivalent offsets/fractions
  tie correctly. `timestamp()` still returns an aware `datetime`.
- Every history entry receives exact identity validation before record lookup;
  valid raw accepted JSON and Windows path spellings stay unchanged.

The same quality reviewer verified those fixes and returned **QUALITY_CLEAR**:
37 tests passed, zero skips, with additional path/comparison probes.
The parent independently reran all 37 focused tests (11.677 s), owned Python
lint and whitespace checks at that clean head: passed. These ordered advisory
reviews are not formal GitHub approval or merge readiness.

The incomplete package was honestly reported as `GATE FAILED: package build`
and the full `check` aborted at the missing new skill procedure; registration
is deliberately W4. No placeholder, weakened checker or false full-gate
summary was introduced. The later known failures were not repeatedly rerun.
W2 only started after W1 cleared both reviews. Full exporter, installed-package,
actual produced-intake receiver and final candidate verification remain pending.

## W2: actual bounded archive and preserved release imports

The bounded #76 worker implemented seven owned shared-stream/archive/checker/
test paths at local `57690dc`. The pure helper copies are byte-identical and
the repository assertion is exercised with a complete test-owned fixture,
not a placeholder production skill or weakened check. The release consumer
only changes helper imports/wrapping; existing cache, network, JSON, source
and manifest policies and raw-validation algorithm remain unchanged.

Real RED/GREEN includes unsafe names/modes/links, local/central headers,
forged decoded sizes, CRC/EOF/trailing-stream validation, directory/file/case/
slash collisions, state/submodule refusal, exact wrapper handling, actual
UTC date boundaries and atomic write/flush/fsync/replace failures.
Measured positive and one-over cases use actual bytes/entries:
32 MiB compressed source, 64 MiB decoded source, 128 MiB final expanded content
and 4,096 members including directories/generated entries where applicable.
They do not substitute patched constants or declared ZIP sizes.

Early immutable-source smoke used only local read-only `git archive` and the
new parser: **149 files, 726,850 bytes**, all source modes, required schema/
validator fingerprints, licences and locks preserved. No source member was
executed. That is foundation parsing proof, not a full producer/receiver or
Cowork result.

Stage 1 returned **SPEC_COMPLIANT**. Stage 2 then found a genuine direct
file-path import regression that the existing test helper's `sys.path` setup
had masked. A fresh isolated-interpreter regression failed first; the minimal
explicit sibling-loader fix at `d1c0b3f` restored path/script/package imports
without a broad `ImportError` fallback, unrelated cached module or global
path mutation. The same reviewer reran four targeted tests plus fresh valid
STORE/DEFLATE and `EvidenceError` guard probes: **QUALITY_CLEAR**.

The parent independently reran the combined shared/archive/contract/release
suite at that clean head: **120 tests, 118 passed, two skipped** (88.835 s),
owned Python lint and whitespace passed. The two actual skips are Windows
symlink privilege 1314; native junction coverage passed. Existing 45
release-evidence tests remain in that combined result. No symlink-creation
pass or actual server CI result is inferred.

The package/check registration gap remains explicitly deferred to W4.
W3 only started after both W2 reviews cleared; full CLI/privacy/financial,
exact installed package, actual generated-intake receiver and final
authoritative candidate gates remain pending. No new human approval,
protected action, release or Cowork support claim was introduced.

## Human boundaries

Keep published 1.10.x records immutable; a 1.11.0 bump is for the approved
product change, not a way around failed reproduction. Only Caldova synthetic
samples belong in repository tests. Customer/internal transfer needs genuine
clearance regardless of public repository visibility.

Merges, releases/tags, protected labels/settings/workflows and tenant operations
remain human-only. Protected session-start routing under #8 remains an
outstanding human dependency, not silently migrated by this sprint.
