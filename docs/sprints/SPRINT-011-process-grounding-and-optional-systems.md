# SPRINT-011: process grounding and optional systems

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-18 |
| Author | AI assistant (AI-assisted documentation) |
| Status | Runtime #60 implemented and both bounded review stages passed at 0e1c389; renderer/profile/prose and full verification pending |
| Scope | Parent #58 programme and approved 1.10.1 correction #59; staged implementation and evidence |
| References | [Catalogue](README.md), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Correction #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Idea](../ideas/2026-11-17-optional-systems-extensions.md), [Correction spec](../specs/2026-11-17-process-governance-sap-grounding-design.md), [Correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md), [Retention #52](https://github.com/urruegg/frontier-envisioning/issues/52), [Protected routing #8](https://github.com/urruegg/frontier-envisioning/issues/8) |

## Outcome and early work items

Write the actual agreed correction direction before planning implementation.
Correct current process guidance first; stage the optional systems foundation
and Dynamics 365 later. This early record is not a ready sprint or a schedule.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#58](https://github.com/urruegg/frontier-envisioning/issues/58) | [Programme and actual decisions](../ideas/2026-11-17-optional-systems-extensions.md#actual-human-decisions) | [First correction only](../specs/2026-11-17-process-governance-sap-grounding-design.md); wider pack designs not yet written | [First correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md); wider pack plans remain separate | `@urruegg` accountable; issue unassigned | #59 first; separate framework/Dynamics 365 written design and approvals | Decision intake, size M/P1; programme direction agreed, not ready for all-pack execution | Actual written correction approval recorded; no implementation result |
| [#59](https://github.com/urruegg/frontier-envisioning/issues/59) | [Correction stage](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Tasks 1-12](../plans/2026-11-17-process-governance-sap-grounding-plan.md); approved at `35ad763` | `@urruegg` accountable and assigned; agent involvement recorded, not approval | Reviewed runtime/rendering/support slices; [#52](https://github.com/urruegg/frontier-envisioning/issues/52) final release/reproduction retention | Runtime implemented/reviewed; remaining integration and full gates pending | Sources checked 17 November; runtime `0e1c389` checkpoint below |
| [#60](https://github.com/urruegg/frontier-envisioning/issues/60) | [First correction](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01/02/04/07](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Runtime Tasks 1-6 and 8](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-1-verify-the-approved-execution-boundary-and-baseline) | `@urruegg` accountable; bounded builder, size M | Actual #59 plan approval; standard bump before plugin edits | Both bounded advisory stages passed; whole-product acceptance separate | `0e1c389`; 39 reviewer tests plus independent owner probes; broader builder result qualified below |
| [#62](https://github.com/urruegg/frontier-envisioning/issues/62) | [Correction output](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-03/04](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Renderer Task 7](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-7-test-then-correct-markdown-html-and-actual-downloads) | `@urruegg` accountable; bounded renderer, size M | Reviewed #60 runtime contract | Ready for scoped test-first handoff; no protected ready label claimed | Real issue, approved plan and runtime review; no renderer result yet |
| [#63](https://github.com/urruegg/frontier-envisioning/issues/63) | [Correction verification](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-05 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Profile/distribution Tasks 9-10](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-9-add-only-the-necessary-named-1101-raster-input-profile) | `@urruegg` accountable; bounded builder, size M | Reviewed #60/#62 interfaces | Pending finite profile, example and final extracted-package proof | No profile, self-test or final package result yet |
| [#61](https://github.com/urruegg/frontier-envisioning/issues/61) | [Current guidance](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01 to G59-05](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Prose Task 11](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-11-update-the-example-and-current-methodrequirements-documentation) | `@urruegg` accountable; bounded documentation, size S | Reviewed runtime fields and actual CLI behaviour | Pending method/schema-reference/current product-record alignment | No completed prose or future gate claims |

These are real programme and runtime work-item rows. There are no invented
child issues for Dynamics 365 or the remaining packs. A document author is not an
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
was later explicitly granted by `approve-plan-subagents` at planning commit
`35ad76316aa4eb055b10c62bcfe2e62f7945a66f`; the
[plan receipt](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6951849396)
records that actual answer. #59/#60 owner/agent-involvement fields were then
explicitly applied; protected ready/approval labels, formal review, publication
or deployment authority are not inferred.

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

## Runtime implementation and ordered review (#60)

The standard bump changed the candidate to unreleased **1.10.1** before
manual plugin edits. Runtime commits `6af11dd`, `d123454`, `43f9cf7`,
`b89fb60` and `0e1c389` implement the approved canon, conditional route,
legacy-record, Python-output and validation boundaries.
No renderer/profile/prose integration or new skill is included in this
runtime acceptance checkpoint.

The builder's entrypoint audit reproduced malformed input being healed or
filtered before validation and a wrapper creating its output directory before
rejection. The tightly coupled Blueprint/process callers now share pure raw
shape/citation checks before projection or output effects. Actual failing
then passing CLI/extracted-package regressions cover those boundaries.

Independent ordered review found valid empty-reference crashes, loss of
authored public domains, a hidden reserved-citation collision, mixed-reference
domain privacy leakage and placeholder-owner confirmation. Each finding was
reproduced and fixed test-first; none was waived. At
`0e1c389e2301c1200fbeaed3277aeeca7de77ec2`, the reviewer confirmed
**specification PASS, bounded correctness/quality PASS**, with no remaining
Critical/Important/Minor findings in that scope.

The reviewer independently ran **39 focused contract tests**, including
extracted execution, and **12 owner values across both CLI audiences**.
The owner's recorded text remains unchanged; missing/pending values do not
grant current confirmation. The new owner regressions failed against the
parent implementation with 25 assertion failures and no import errors.
Template/repository rules/neutrality/scoped Ruff/strict docs/whitespace and
all **93 installer file hashes** passed their bounded checks.

The builder separately reported **113 targeted tests passed**. Broader
independent suite attempts timed out at 360/420 seconds, so that count is
**not** independently reproduced by the reviewer. No full L1/L2 result is
claimed from either report; stable integration verification remains pending.

The parent verified clean committed source, cumulative whitespace and
runtime-only candidate SHA-256
`9fffcad5bb98b68c201f82d6d09f3604457bc7216ee4a05c574a93aa08ef4932`.
It also rechecked the unchanged published 1.10.0 annotated tag/source
identities. This candidate hash is not a final integrated package or a
published release. Advisory code review is not human approval or financial,
licensing, tenant or deployment authority.

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
