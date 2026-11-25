# SPRINT-012: release evidence without manual retention

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Written specification approved; concrete plan/readiness approval pending |
| Scope | Issue #67 developer evidence/checker/guidance slices; protected workflow adoption remains separate |
| References | [Catalogue](README.md), [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [Idea](../ideas/2026-11-24-release-evidence-simplification.md), [Approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [Written plan](../plans/2026-11-25-release-evidence-simplification-plan.md), [Spec receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060), [#52](https://github.com/urruegg/frontier-envisioning/issues/52), [#8](https://github.com/urruegg/frontier-envisioning/issues/8) |

## Outcome and work item

Remove recurring manual downloads, copied hashes and retention PRs, without
removing automatic exact-version integrity/reproduction verification or the
human publication decision. Local checks remain offline-capable with an honest
not-performed outcome when no validated evidence is available.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#67](https://github.com/urruegg/frontier-envisioning/issues/67) | [Actual choices](../ideas/2026-11-24-release-evidence-simplification.md) | [RE-01–08](../specs/2026-11-24-release-evidence-simplification-design.md#6-testable-acceptance) | [Tasks 1–4](../plans/2026-11-25-release-evidence-simplification-plan.md) | `@urruegg` accountable; no inferred assignment | Actual approval of the concrete plan; reviewed code slices before prose/integration; human protected-workflow adoption | Written spec approved; plan/readiness pending, not ready for delegation | [Spec receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060); no implementation or publication result |

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

The linked real plan was written afterwards. Its own plan/readiness approval
is still pending. No `status:ready`/`approved:*` label, assignee, milestone,
protected-file permission or publication is inferred from either decision.

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
