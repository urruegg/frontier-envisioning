# SPRINT-014: Cowork install compatibility

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-27 |
| Author | AI assistant; AI-assisted planning-document drafting from the human decisions and supplied evidence |
| Status | Draft; not Ready; conversational design approved 2026-11-27; written specification review pending; no implementation plan |
| Scope | Planning records for NEXT 1.11.1 eight-skill Cowork install compatibility; no production implementation or release |
| References | [Catalogue](README.md), [Work item #87](https://github.com/urruegg/frontier-envisioning/issues/87), [Idea](../ideas/2026-11-27-cowork-install-compatibility.md), [Draft written spec](../specs/2026-11-27-cowork-install-compatibility-design.md), [Historical 1.11.0 baseline plan, not 1.11.1 execution](../plans/2026-11-26-plugin-health-and-finops-exclusion-plan.md), [Host receipt #81](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867), [Closeout hub #86](https://github.com/urruegg/frontier-envisioning/issues/86) |

## Outcome and work item

Record the conversationally approved design for the compatible NEXT version
**1.11.1**: safe whole-draft install staging, exact recursive file limits,
lossless canonical Identity consolidation, typed metadata preservation and
bounded Factory routing. Owner: `@urruegg`, distinct from AI-assisted authorship.
No schedule, protected Ready label or owner head sign-off is asserted.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#87](https://github.com/urruegg/frontier-envisioning/issues/87) | [Intake and decisions](../ideas/2026-11-27-cowork-install-compatibility.md) | [CWI-01–CWI-07](../specs/2026-11-27-cowork-install-compatibility-design.md#7-acceptance-and-verification-matrix) | [Historical baseline only](../plans/2026-11-26-plugin-health-and-finops-exclusion-plan.md); no 1.11.1 implementation plan exists or is approved | `@urruegg` accountable; no sign-off inferred | Written-spec review, later explicit plan approval and human #8 protection baseline before production implementation; fresh #81 host acceptance | Draft / not Ready; documentation slice only | [Supplied host receipt](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867), [closeout #86](https://github.com/urruegg/frontier-envisioning/issues/86); no new PR/CI/product result claimed |

## Actual decision and evidence provenance

On **27 November 2026**, the user requested Superpowers brainstorming, selected
`source-consolidation-1111` over build-time projection/manual workarounds, then
explicitly answered `approve_design=true` to the install-flow/safety/verification
design. This is conversational design approval, not review of the written
specification or an implementation plan. Formal independent review, version
bump, protected labels/#8 execution and release publication are not implied.

The [design evidence](../specs/2026-11-27-cowork-install-compatibility-design.md#2-supplied-host-evidence-and-limits)
pins the supplied report and published 1.11.0 ZIP. Actual nested-source and
Identity file-limit refusals left the old Identity 1.9.2 installed. The
documentation-only workaround's successful save, 21/21 installed equality,
identical 429-file Caldova kits and generated-kit tests are **reported human
evidence, not assistant-reproduced validation**. Structural rescore was not
done; the companion repack ZIP was absent at the report-relative path and no
downloaded repack script was executed.

Historical [H111 design](../specs/2026-11-26-plugin-health-and-finops-exclusion-design.md)
and [SPRINT-013](SPRINT-013-agent-factory-handover.md) remain intact. Their
dated approvals/candidate gates and the separately supplied later 1.11.0
publication do not establish 1.11.1 acceptance. #81 remains open for final
new-package real host proof.

## Acceptance and design-review gaps

The stable [CWI-01–CWI-07 matrix](../specs/2026-11-27-cowork-install-compatibility-design.md#7-acceptance-and-verification-matrix)
owns the later tests and receipts. None is marked complete by this draft.
Seven GA skills plus optional Preview Factory ship; FinOps stays source-only
and an older installed copy is not auto-uninstalled.

| Review or dependency | Current state |
|---|---|
| Written specification | Review pending; conversational approval is recorded separately. |
| Implementation plan | No 1.11.1 implementation plan yet. The linked 1.11.0 plan documents the directly related released baseline only; it does not govern execution of #87. Sprint not Ready. |
| Human protected [#8](https://github.com/urruegg/frontier-envisioning/issues/8) baseline | Separate plural session-start correction and Active native main PR/check/freshness/force/deletion protection. Supplied live state: `protected=false`, no rulesets. Existing checks: `L1 quality gate`, `L2 browser tests`, `IaC validation`. Zero formal approvals is feasible for the sole maintainer; real head-qualified sign-off is separate. Missing protection blocks production implementation, not planning. |
| Human [#9](https://github.com/urruegg/frontier-envisioning/issues/9) guidance/clearance | Separate scoped current guidance/publication/adoption after review and clearance; no internal-content publication from public visibility or blanket consent. |
| [Template stable foundation](https://github.com/urruegg/frontier-agent-factory) | Supplied complete authenticated enumeration found no release/tag. Human compatibility verification and genuine stable publication remain separate. Retain exact-commit unreleased-bootstrap consent and no older/main error fallback; Factory remains Preview. |
| New package and [#81](https://github.com/urruegg/frontier-envisioning/issues/81) | All-eight fresh host saves, installed inventory/hashes, OneDrive receipt, structural/publish-bar rescore and vague/explicit routing proof against the rebuilt ZIP remain required; advisory warnings stay visible. |

[#48](https://github.com/urruegg/frontier-envisioning/issues/48) and
[#58](https://github.com/urruegg/frontier-envisioning/issues/58) remain deferred.
Caldova governance/tenant work is untouched. #86 is the linked closeout hub,
not permission to close issues or broaden the implementation.

## Documentation validation and handoff

The parent supplied the isolated `docs/87-cowork-compatibility` worktree context
at clean base `482aa816e8867575a2557230d596788e694d64fe`. This drafting agent
does not recheck branch/cleanliness through git or use the dirty primary checkout.

| Check | Evidence and limit |
|---|---|
| Pre-edit `python tools\dev.py docs --strict` | Parent-reported clean-base result: **0 errors; documentation-only ALL GATES PASSED**. This is not post-edit validation. |
| One manual self-review | Reviewed the six changed records for metadata, relative links, acceptance, placeholders, scope and approval/evidence distinctions. Corrected obsolete-note hyperlink risk and old-version/publication attribution wording. This is not an automated document-gate pass. |
| Initial post-edit `python tools\dev.py docs --strict` | Parent execution failed with two errors: missing plan links in sprint References and the Plan column. This failure is not replaced by the clean-baseline pass. |
| Strict sprint traceability | The existing checker requires plan-document references even for Draft records. The actual related 1.11.0 plan is linked solely as historical baseline context; no 1.11.1 plan, execution approval or Ready state is inferred. The checker is unchanged. |
| Post-correction validation | Parent ran `python tools\dev.py docs --strict`: **0 errors; documentation-only ALL GATES PASSED** (4.3 seconds). `git diff --check` also passed. This is not product L1/L2, live approval verification or new-package/host acceptance. |

Only the new idea/spec/sprint and their three direct-child catalogues are in
scope. No implementation plan or separate tracking note is created. No product
builder/test, dependency installation, git/GitHub operation, protected edit,
release action or internal-material reclassification is performed.
The next handoff is the written specification and actual document-gate result,
not implementation readiness.
