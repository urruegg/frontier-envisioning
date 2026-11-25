# SPRINT-012: release evidence without manual retention

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Evidence/cache #68 implemented and both bounded reviews passed; gate integration #69 in progress |
| Scope | Issue #67 developer evidence/checker/guidance slices; protected workflow adoption remains separate |
| References | [Catalogue](README.md), [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [Idea](../ideas/2026-11-24-release-evidence-simplification.md), [Approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [Written plan](../plans/2026-11-25-release-evidence-simplification-plan.md), [Spec receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060), [#52](https://github.com/urruegg/frontier-envisioning/issues/52), [#8](https://github.com/urruegg/frontier-envisioning/issues/8) |

## Outcome and work item

Remove recurring manual downloads, copied hashes and retention PRs, without
removing automatic exact-version integrity/reproduction verification or the
human publication decision. Local checks remain offline-capable with an honest
not-performed outcome when no validated evidence is available.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#67](https://github.com/urruegg/frontier-envisioning/issues/67) | [Actual choices](../ideas/2026-11-24-release-evidence-simplification.md) | [RE-01–08](../specs/2026-11-24-release-evidence-simplification-design.md#6-testable-acceptance) | [Tasks 1–4](../plans/2026-11-25-release-evidence-simplification-plan.md) | `@urruegg` accountable | Reviewed child slices before stable integration; separate human protected adoption | Actual plan/execution direction recorded; implementation in progress | [Execution receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155657072); no publication/adoption result |
| [#68](https://github.com/urruegg/frontier-envisioning/issues/68) | [Evidence outcome](../ideas/2026-11-24-release-evidence-simplification.md) | [RE-02–06](../specs/2026-11-24-release-evidence-simplification-design.md#6-testable-acceptance) | [Task 1](../plans/2026-11-25-release-evidence-simplification-plan.md#task-1-validated-published-evidence-and-offline-cache) | `@urruegg` accountable and assigned; bounded builder | Approved plan at `22f512f` | Implemented; specification then correctness PASS | `33e6a76`; focused RED/GREEN and live exact-version proof below |
| [#69](https://github.com/urruegg/frontier-envisioning/issues/69) | [Automated checks](../ideas/2026-11-24-release-evidence-simplification.md) | [RE-01–06](../specs/2026-11-24-release-evidence-simplification-design.md#6-testable-acceptance) | [Task 2](../plans/2026-11-25-release-evidence-simplification-plan.md#task-2-gatecli-integration-and-existing-ci-read-access) | `@urruegg` accountable and assigned; bounded builder | Reviewed #68 contract | Test-first gate/CLI/CI integration in progress | No final full gate or protected adoption claimed |
| [#70](https://github.com/urruegg/frontier-envisioning/issues/70) | [No recurring ceremony](../ideas/2026-11-24-release-evidence-simplification.md) | [RE-01/07/08](../specs/2026-11-24-release-evidence-simplification-design.md#6-testable-acceptance) | [Task 3](../plans/2026-11-25-release-evidence-simplification-plan.md#task-3-active-guidance-and-bounded-human-adoption) | `@urruegg` accountable and assigned; bounded documentation | Reviewed #69 CLI/outcomes | Waiting for actual contract | No future validation/adoption result invented |

Do not invent child IDs before the plan is approved. At execution, allocate the
bounded evidence builder, gate consumer and documentation work in real linked
issues before delegating. Reviews are advisory; formal approval, adoption and
publication remain distinct.

## Actual decisions

The 24 November structured choices were `remove-manual-ceremony`,
`release-assets-record`, `offline-local-strict-ci`, `approve-flow` and a request
for subagent-driven implementation. The actual written spec was subsequently
approved on 25 November with **"spec is approved and you can implement"**,
referring to `67dc9a542d734ea7af91a2b40dda3ad823550375` and reviewed spec digest
`584b85e05780b1c276a637b48553191ebfd33c6ede0dc45ecf7c862f971d3926`.

The linked real plan was written afterwards and presented at `22f512f`.
The maintainer subsequently directed **"stop planning and start implementing"**,
with continued autonomous execution. The
[actual receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155657072)
records that distinct plan/execution decision. Real #68/#69/#70 children were
created and assigned afterwards, before delegation. No `status:ready`/
`approved:*` label, milestone, protected permission or publication is inferred.

## Baseline and actual planning validation

Planning uses the existing isolated worktree on
`docs/67-release-evidence-design`, based on merged main `b9e41e8`.
The original five-document planning package is `67dc9a5`.
On 25 November, before plan edits:

- `python -m unittest tests.unit.test_release_tools.LocalReleaseManifest tests.unit.test_release_tools.ManualReleaseWorkflow -q`
  passed **ten tests**.
- `python tools/dev.py docs --strict` passed with **zero errors / ALL GATES PASSED**.
- Read-only inspection confirmed the real 1.10.0 download/checksum/manifest
  formats. The release has four downloads, not four checksummed payload rows.
  Published source/tag identities and historical provenance remain unchanged.

These are real baseline/planning results, not future new-checker RED/GREEN,
CI networking, protected workflow adoption or release acceptance.

## Human adoption and handover

The normal CI workflow is editable within the plan's read-only token boundary.
The release workflow remains protected: a person supplies the equivalent
read-only token to its existing validation step after reviewing the software
and exact handover. No guard, workflow copy, repository setting, token-reading
diagnostic, agent dispatch, merge, tag or publication bypass is allowed.

Existing release records and any human-authored #52 copy remain untouched.
Only after the actual replacement is implemented, verified and adopted may
#52's old manual-retention process be recorded as superseded; no missing old
retention/merge is invented. Protected session-start routing/native controls
under #8 remain a separate human dependency.

## Evidence/cache implementation and ordered review

The bounded #68 implementation is committed through
`33e6a766918a809fe1b18a8ba5548c258ec9f0be`. The initial scaffold test run
observed missing-behaviour failures; the first complete module then passed.
The controller independently ran 36 tests under `CI=true`: all passed except
one Windows filesystem-symlink privilege skip. ZIP symlink rejection ran.

Specification review reproduced a raw LZMA decompression exception escaping
the `EvidenceError` boundary. A focused test failed before the narrow fix at
`0af58a3` and passed afterwards. Correctness review then reproduced forged ZIP
header sizes defeating the standard ZIP reader's truncating integrity check.
Eight strengthened tests observed seven failures before the fix; an EOF
regression additionally failed in three subcases.

At `33e6a76`, raw STORED/DEFLATED output has bounded size/CRC/EOF/complete-stream
validation before cache acceptance. Other compression methods are rejected.
Both actual published ZIPs were measured as DEFLATED, so this preserves the
observed release format rather than adding a general archive framework.
The builder's final module run executed 45 tests: 44 passed and the same one
Windows filesystem-symlink case was skipped. Ruff and whitespace passed.

The reviewer reran the original forged-size probe and eight directly coupled
regressions: rejection/no-cache and all eight tests passed. Both ordered stages
are clear, with no remaining high-confidence findings in that bounded scope.
Advisory review is not human approval or protected-workflow adoption.

The controller also ran the new resolver against actual published 1.10.0,
bound to source `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`. Its downloaded
evidence validated, and all four normally rebuilt historical artefacts
matched. Offline cache reuse matched the same source; after ZIP hardening,
the real plugin/SBOM streams and four-artefact comparison still passed.
Current 1.10.1 lookup independently returned confirmed development with no
exact release/conflicting tag. These are actual read-only checks, not a new
publication, retained-manifest commit or final consumer/full-CI result.

## Gate integration checkpoint

The bounded #69 implementation is `b8cba42a18e705fa6721f621a12044e47219878e`.
It changes only the six named consumer/test/normal-CI files, not the protected
release workflow or plugin.

The builder observed RED for missing explicit manifests, consumer outcome/error
cases, gate/workflow wiring and empty manifests before making them pass.
The controller independently ran the combined evidence/release/task-runner/
documentation-runner selector under `CI=true`: **93 tests run: 90 passed, three
known skips** (the Windows symlink privilege case and two legacy workflow
contracts), in 95.872 seconds.

The controller also executed the real task-runner entry point twice:

- Local offline `python tools/dev.py verify-release` reported `not-performed`
  and ended with **LOCAL CHECKS COMPLETED; published-release verification
  NOT PERFORMED**, not an unqualified full pass.
- With `CI=true`, the same command performed the actual remote lookup and
  reported confirmed `development` for 1.10.1, ending **ALL GATES PASSED**.
  That is an authoritative absent-release/tag outcome, not reproduction of
  1.10.0 or a published release.

These are focused integration results. Ordered #69 reviews, final full gates,
actual CI and protected human adoption remain separate at this checkpoint.
