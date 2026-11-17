# SPRINT-011: process grounding and optional systems

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-17 |
| Author | AI assistant (AI-assisted documentation) |
| Status | Written correction spec approved; real plan linked for review; plan/readiness and implementation approval pending |
| Scope | Parent #58 programme and first correction child #59; documentation-only design record |
| References | [Catalogue](README.md), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Correction #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Idea](../ideas/2026-11-17-optional-systems-extensions.md), [Correction spec](../specs/2026-11-17-process-governance-sap-grounding-design.md), [Correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md), [Retention #52](https://github.com/urruegg/frontier-envisioning/issues/52), [Protected routing #8](https://github.com/urruegg/frontier-envisioning/issues/8) |

## Outcome and early work items

Write the actual agreed correction direction before planning implementation.
Correct current process guidance first; stage the optional systems foundation
and Dynamics 365 later. This early record is not a ready sprint or a schedule.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#58](https://github.com/urruegg/frontier-envisioning/issues/58) | [Programme and actual decisions](../ideas/2026-11-17-optional-systems-extensions.md#actual-human-decisions) | [First correction only](../specs/2026-11-17-process-governance-sap-grounding-design.md); wider pack designs not yet written | [First correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md); wider pack plans remain separate | `@urruegg` accountable; issue unassigned | #59 first; separate framework/Dynamics 365 written design and approvals | Decision intake, size M/P1; programme direction agreed, not ready for all-pack execution | Actual written correction approval recorded; no implementation result |
| [#59](https://github.com/urruegg/frontier-envisioning/issues/59) | [Correction stage](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Tasks 1-12](../plans/2026-11-17-process-governance-sap-grounding-plan.md); explicit plan/readiness approval pending | `@urruegg` accountable; no assignee-field claim | Human plan/readiness approval; [#52](https://github.com/urruegg/frontier-envisioning/issues/52) final release/reproduction retention | Bounded chore, size M/P1; written spec approved at digest 8ab93d95; no implementation | Sources checked 17 November; actual written-spec approval linked below; future patch checks not run |

Only #58 and #59 are programme work-item rows. There are no invented child
issues for Dynamics 365 or the remaining packs. A document author is not an
issue owner, assignee, reviewer or approver.

## Actual decisions and approval boundary

The parent supplied the structured human answers recorded in comments on #58:
`one-skill-six-packs`, `d365-first`, `approve-d365-slice`, `preview-wrapper`,
`patch-then-d365`, then `approve-correction-design`.
The [idea](../ideas/2026-11-17-optional-systems-extensions.md#actual-human-decisions)
records their exact bounded meaning. This is not wholesale acceptance of the
two briefs' decision registers.

The last answer followed presentation of the Purview and SAP corrections,
coherent output changes, legacy/privacy protection, no automatic FinOps and
future red/green/full verification obligations. It is human approval of that
design direction, not review of the written spec created here.

The subsequent **`approve-written-correction-spec`** answer reviewed the
actual #59 specification at SHA-256
`8ab93d9542e3db44f132d4b352551b17ef3c00eb1567ed4e62f85ed93ef78c5f`.
The [source-qualified receipt](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6949117136)
records the distinction from direction approval. The real bounded plan was
written afterwards and is now linked above. Its plan/readiness approval
remains separate and pending. No ready/approval label, issue field, milestone,
formal review, publication or deployment authority is inferred.

## Staging and acceptance

- **Planned 1.10.1:** #59 only. Replace new retiring Purview governance creation
  guidance, preserve security/migration context and make the SAP Datasphere
  route/prerequisites/commercial dependency explicit. Accept only against
  [G59-01 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification),
  including unknown-prerequisite safety, all-output agreement, legacy/privacy,
  no-FinOps independence, immutable 1.10 and actual future engineering proof.
- **Planned 1.11.0:** separate common foundation plus Dynamics 365 design.
  One new Preview `frontier-systems` wrapper would bring eight skills to nine;
  Sales, Customer Insights - Journeys/Data, Customer Service and Contact Center
  only. No implemented future-pack stubs, automatic activation or extra
  FinOps-style acknowledgement for ordinary design.
- **Later, unscheduled:** Databricks, SAP ERP, SuccessFactors, ServiceNow and
  Workday need separate designs and verified catalogue rows. No release
  versions, deadlines, child IDs or implementation approvals are invented.

These are planning targets, not version bumps or new publications. Existing
custom hypotheses/IDs and unchanged core behaviour without pack activation
remain constraints on later design.

## Baseline and human dependencies

The parent confirms clean linked worktree `frontier-envisioning-wt-48`, branch
`docs/58-optional-systems-design`, base
`b88b9a2efa1eb342d5542475c63eee5f7bb43e4b`.
Published 1.10.0 identity is recorded in the
[idea](../ideas/2026-11-17-optional-systems-extensions.md#inputs-and-current-baseline)
and [spec](../specs/2026-11-17-process-governance-sap-grounding-design.md#outcome-and-authority).
Neither source/release bytes nor field-brief inputs change here.

[#52](https://github.com/urruegg/frontier-envisioning/issues/52) remains the
human-only immutable 1.10 manifest-retention dependency for final
release/reproduction acceptance. Do not edit protected release records, skip a
baseline or bump merely to bypass a failure.
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) remains the
human-only protected session-routing/native-controls dependency; current
routing is not silently treated as migrated. This work does not decide either
issue's workflow or mutate its fields.

## Documentation evidence and handoff

The pre-edit `python tools/dev.py docs --strict` baseline passed with zero
errors. The first six-document draft then produced **three real errors**:
SPRINT-011 References and its two rows had no implementation-plan links.
The checker requires those links even at early intake, but the brainstorming
method requires written-spec review before planning.

The parent therefore obtained actual written-spec review before committing,
then prepared the real plan and linked it here. No checker was changed, no
unrelated/fake plan link was used and no failed gate was called a pass.
After those real links were integrated, `python tools/dev.py docs --strict`
passed with **zero errors / ALL GATES PASSED**. `git diff --check` and the
input-fingerprint/no-placeholder review passed. The plan's Python examples
parsed successfully; all G59-01 to G59-08 have mapped tasks. These are
documentation/planning checks, not future implementation-gate results.

All #59 implementation tests, regenerated outputs, full repository/browser
gates and distribution/extraction proof remain future obligations after
approval. The coordinating assistant reviewed the eight-file planning
package and will present its exact committed revision for a separate human
plan/readiness and execution-mode decision.
