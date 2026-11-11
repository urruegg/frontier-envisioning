# SPRINT-003: Refined Cowork handover intake

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-11 |
| Author | Copilot SDK in VS Code; AI-assisted planning and evidence maintenance |
| Status | Design and written plan human-approved; implementation in progress; final acceptance pending |
| Scope | Governed 1.7.1 feature intake with subagent checkpoints and build/distribution acceptance |
| References | [Catalogue](README.md), [Issue #22](https://github.com/urruegg/frontier-envisioning/issues/22), [Idea](../ideas/2026-11-10-handover-1.7-intake.md), [Spec](../specs/2026-11-10-handover-1.7-intake-design.md), [Plan](../plans/2026-11-10-handover-1.7-intake-plan.md), [Receipt](../intake/handover-1.7.0.md), [PRD intake](../prd.md#171-development-intake), [Design intake](../solution-design.md#171-development-intake) |

## Goal and work item

Integrate the four-part/seventeen-view 1.7 feature set into unreleased 1.7.1
without losing current accessibility, privacy, provenance and governance.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#22](https://github.com/urruegg/frontier-envisioning/issues/22) | [Idea](../ideas/2026-11-10-handover-1.7-intake.md) | [Spec](../specs/2026-11-10-handover-1.7-intake-design.md) | [P0-P5 plan](../plans/2026-11-10-handover-1.7-intake-plan.md) | `@urruegg` accountable; parent coordinates bounded builder/renderer/docs workers | Actual plan approval recorded; original raster/receipt and protected controls retained; P5 final gates/review/distribution pending | Implementation in progress; P1 review PASS; P3 completed with read-only review pending; P4 prose handoff | Human-merged [PR #23](https://github.com/urruegg/frontier-envisioning/pull/23), 11 November approval and [checkpoint receipt](../intake/handover-1.7.0.md) |

## Readiness and real approval evidence

- [x] Real issue #22 and linked idea/spec/plan/sprint exist.
- [x] Outcome, source fingerprint, affected surfaces and I17 acceptance defined.
- [x] Customer-neutral Caldova sample and original 1.6.0 inventory available.
- [x] The recommended selective design was approved at
  `2026-11-10T23:41:47.373+01:00`, with the exact quote recorded in the
  [idea](../ideas/2026-11-10-handover-1.7-intake.md#actual-approval-evidence) and #22.
- [x] Development version 1.7.1 is separate from received 1.7.0 artifact evidence.
- [x] The maintainer approved the written plan at **11 November 2026, 06:43 +01:00**:
  "pr is approved and you can proceed", after human-merged
  [PR #23](https://github.com/urruegg/frontier-envisioning/pull/23), main merge
  `fdaeec62416b91f5e4286f2849b8cbc27d65b02c`. See the
  [receipt](../intake/handover-1.7.0.md).
- [ ] Human readiness/label state verified separately if applied; no agent mutation.

Do not treat this sprint, a file status or the unavailable earlier form as approval.
The later actual human instruction above satisfies the written-plan gate; it
does not mutate labels or authorise protected actions.

## Sequencing and acceptance

P0 receipt/bump/isolation precedes P1 models, then P2 deterministic demo.
P3 renderer uses that demo. P4 prose follows model decisions and final UI
wording; parent owns backlog/checker changes. Parent schedules one writer per
shared file. P5 runs complete L1/L2,
real ZIP/privacy/checksum/install verification and final review.

The full plan records exact allowlists, commands, negative tests and stop rules.
No deadline or effort commitment is inferred. The checkpoints below are bounded
execution evidence, not completion of integrated 1.7.1 acceptance.

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

**Historical, before the 11 November plan approval and implementation.**
The following results apply only to the unchanged baseline and planning slice.

The eight-file planning change passed
`python tools/dev.py check --strict`: `ALL GATES PASSED`, 172 tests,
385 subtests and 41 DOM tests, with the expected unreleased-1.6.1 manifest skip.
`python tools/dev.py docs --strict` reports zero errors. The plan was self-reviewed
for P0-P5 ownership/dependencies, fourteen acceptance criteria, links and explicit
build/browser/distribution/install checks.

The written-plan approval form returned **user unavailable**. This is not an
approval or refusal. No implementation subagent was started and no feature source
or version was changed. Save/push the planning branch for the maintainer to review;
resume P0 only after actual written-plan approval. That validation proves the
preserved 1.6.1 baseline plus planning documents, not an integrated 1.7.1 product.

## Implementation checkpoints — 11 November 2026

These results were returned by the parent/worker loop for the P4 handoff; the
docs worker did not execute commands or independently rerun them.

| Phase | Returned evidence | Limits/current state |
|---|---|---|
| P0 | Receipt/current-version tests: two expected failures, then **2 PASS** after receipt and standard 1.7.1 bump; isolated baseline selectors **69 tests, 91 subtests** | Original received/protected baselines retained; not full integrated L1 |
| P1 | Ten received model feature tests plus edge privacy, finite-rating, source-ID and canonical-order/subset tests; models read-only review **PASS**. Self-test reports **39 checks**, retaining the original 34 | Bounded model checkpoint, not release acceptance |
| P2 | Full **205 generated non-raster inputs and 223 rasters** verified; A6 identity ZIP remains `e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`; 1.7.1 input-profile pin `d9bd99a7a5ac020f1ade201e898dacd4cb8a6230839707188bb62f250e251a58` | Separate finite 1.7.1 profile; original profiles/hashes are not replaced |
| P3 | Renderer worker reports **58 DOM, 50 browser tests** and **168 axe scans with zero WCAG violations reported** | Worker completed; read-only review pending at this handoff. Automated samples are not WCAG certification/manual AT acceptance |
| P4 | Scoped product/skill/guide prose, Proposed ADR and linked catalogues/evidence updated | Self-review only; parent document/contract validation not yet returned |
| P5 | No final integrated result supplied | Final strict L1, integrated review, finished ZIP/privacy/checksum/rebuild and offline seven-skill install-plan acceptance pending |

New acceptance rows in the [PRD intake](../prd.md#171-development-intake) remain
Pending until final integrated acceptance. There is no new **ALL GATES PASSED**
claim here; the earlier planning result remains historical.

The parent runs document/header/link/traceability and contract tests and handles
any gaps. No docs-worker terminal command, commit, push, generated/fixture/test
edit or protected action was performed. Actual Cowork install/publication,
deployment, release/external-IP clearance and protected routing
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) remain human-only.
