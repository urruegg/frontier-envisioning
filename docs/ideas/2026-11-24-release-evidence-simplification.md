# Release evidence without manual retention

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-24 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Flow approved; written design review and subsequent plan/readiness approval pending |
| Scope | Remove recurring manual release-evidence handling, retain automated verification and human publication |
| References | [Catalogue](README.md), [Issue #67](https://github.com/urruegg/frontier-envisioning/issues/67), [Design](../specs/2026-11-24-release-evidence-simplification-design.md), [Early sprint row](../sprints/README.md), [Retention #52](https://github.com/urruegg/frontier-envisioning/issues/52), [Guidance #9](https://github.com/urruegg/frontier-envisioning/issues/9) |

## Outcome

Keep the release journey simple: review and merge, then the maintainer runs
the release workflow. Automation handles exact-version evidence and integrity
checks. No repeated manual download, copied hash, manifest-retention commit or
follow-up PR is required by the proposed replacement.

This is developer/release tooling, not a plugin feature. Human publication,
existing quality gates and released-version integrity remain in scope.
Broader engineering automation under #48 is not activated.

## Actual human choices

The maintainer selected `remove-manual-ceremony`, then `release-assets-record`
and `offline-local-strict-ci`. This chooses published release assets as the
canonical evidence, offline-capable local checks and strict automated CI
verification. Publication-only verification and automated retention PRs were
presented but not selected.

The maintainer then selected `approve-flow` and requested
"no plesse proceed sub agent driven impplementation". This approves the
presented flow and selects the intended execution mode. It is not approval of
an unwritten specification/plan or permission to edit protected controls.
Additional complete-design confirmation was not obtained; the written
specification remains a review draft. A subsequent real plan needs its own
approval before delegated implementation.

Accountable owner: `@urruegg`. No issue assignment, milestone, `status:ready`
or `approved:*` label is inferred from those choices.

## Observed baseline

Main `b9e41e85bea84990f14cd17566042cb9e93ecb31` includes human-merged #65
and unreleased 1.10.1. The latest published version checked during intake is
1.10.0. The release workflow already generates/verifies checksums and compares
independently built packages. Duplicate manual repository retention causes the
additional recurring work.

The maintainer previously reported downloading and copying the exact 1.10.0
manifest. The historical rebuild/comparison step was paused; intake inspection
does not prove that the copied protected record was committed or merged.
Preserve any human-authored copy. Do not equate ticked #52 boxes with evidence.

## Boundaries and next gate

Preserve existing tags, assets, release records, provenance and raster pins.
No new plugin version or dependency is proposed. Changes to protected workflow,
guard, release-record or repository controls remain human-applied.
The [policy catalogue](../../.github/agent-policy/README.md) remains Proposed;
protected routing/native-controls work under #8 remains separate.

Review the written design, then write the test-first implementation plan and
create the fully linked sprint record. The early sprint catalogue row is
explicitly not ready; no placeholder plan file or invented approval is used.
