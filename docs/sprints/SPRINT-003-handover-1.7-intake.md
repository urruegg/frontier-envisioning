# SPRINT-003: Refined Cowork handover intake

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted planning and evidence maintenance |
| Status | Selective design approved; written plan proposed; implementation not started |
| Scope | Governed 1.7.1 feature intake with subagent checkpoints and build/distribution acceptance |
| References | [Catalogue](README.md), [Issue #22](https://github.com/urruegg/frontier-envisioning/issues/22), [Idea](../ideas/2026-11-10-handover-1.7-intake.md), [Spec](../specs/2026-11-10-handover-1.7-intake-design.md), [Plan](../plans/2026-11-10-handover-1.7-intake-plan.md) |

## Goal and work item

Integrate the four-part/seventeen-view 1.7 feature set into unreleased 1.7.1
without losing current accessibility, privacy, provenance and governance.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#22](https://github.com/urruegg/frontier-envisioning/issues/22) | [Idea](../ideas/2026-11-10-handover-1.7-intake.md) | [Spec](../specs/2026-11-10-handover-1.7-intake-design.md) | [P0-P5 plan](../plans/2026-11-10-handover-1.7-intake-plan.md) | `@urruegg` accountable; parent coordinates bounded builder/renderer/docs workers | Actual written-plan approval before delegation; original raster/receipt and protected controls preserved | Planning only; no implementation worker started | Actual design approval below; verification evidence is for unchanged baseline only |

## Readiness and real approval evidence

- [x] Real issue #22 and linked idea/spec/plan/sprint exist.
- [x] Outcome, source fingerprint, affected surfaces and I17 acceptance defined.
- [x] Customer-neutral Caldova sample and original 1.6.0 inventory available.
- [x] The recommended selective design was approved at
  `2026-11-10T23:41:47.373+01:00`, with the exact quote recorded in the
  [idea](../ideas/2026-11-10-handover-1.7-intake.md#actual-approval-evidence) and #22.
- [x] Development version 1.7.1 is separate from received 1.7.0 artifact evidence.
- [ ] The maintainer has reviewed and approved this newly written plan.
- [ ] Human readiness/label state verified separately if applied; no agent mutation.

Do not treat this sprint, a file status or the unavailable earlier form as approval.
The request for subagent-driven execution is recorded; workers remain behind the
written-plan approval gate.

## Sequencing and acceptance

P0 receipt/bump/isolation precedes P1 models, then P2 deterministic demo.
P3 renderer uses that demo. P4 docs/backlog follows model decisions and final UI
wording. Parent schedules one writer per shared file. P5 runs complete L1/L2,
real ZIP/privacy/checksum/install verification and final review.

The full plan records exact allowlists, commands, negative tests and stop rules.
No deadline or effort commitment is inferred. No actual 1.7.1 build or test pass
is claimed until execution supplies evidence.

## Preserved baseline

Main `a840f5864b764740114d26ba7e7e972da8277505` was clean before planning.
The incoming 262-file canonical hash is
`1d9063faa40222d5aacb2e1d3172ef6b953057831090ede8d6eaf4bb20ad7f48`
and was reverified unchanged before these documents were written.

The prior analysis ran strict L1 on the unchanged 1.6.1 baseline:
172 tests, 385 subtests, 41 DOM tests; one expected unreleased-manifest skip,
`ALL GATES PASSED`. Incoming 1.7.0 received test/release claims are not
independently executed results.

The repository stays private. The result remains an internal development
candidate. Protected session-start routing under #8, formal approvals/merge,
releases/tags, deployment and external/IP clearance remain human work.

## Planning checkpoint

The eight-file planning change passed
`python tools/dev.py check --strict`: `ALL GATES PASSED`, 172 tests,
385 subtests and 41 DOM tests, with the expected unreleased-1.6.1 manifest skip.
`python tools/dev.py docs --strict` reports zero errors. The plan was self-reviewed
for P0-P5 ownership/dependencies, fourteen acceptance criteria, links and explicit
build/browser/distribution/install checks.

The written-plan approval form returned **user unavailable**. This is not an
approval or refusal. No implementation subagent was started and no feature source
or version was changed. Save/push the planning branch for the maintainer to review;
resume P0 only after actual written-plan approval. Current validation proves the
preserved 1.6.1 baseline plus planning documents, not an integrated 1.7.1 product.
