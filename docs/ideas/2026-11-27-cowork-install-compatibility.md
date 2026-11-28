# Cowork install compatibility for NEXT 1.11.1

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-27 |
| Author | AI assistant; AI-assisted drafting from the human decisions and supplied engineering evidence |
| Status | Written specification and implementation plan at 7c522ca approved; subagent execution blocked on actual #8 baseline |
| Scope | Public-safe, customer-neutral planning for eight-skill Cowork installation and canonical Identity source consolidation |
| References | [Catalogue](README.md), [Work item #87](https://github.com/urruegg/frontier-envisioning/issues/87), [Design](../specs/2026-11-27-cowork-install-compatibility-design.md), [Approved plan](../plans/2026-11-27-cowork-install-compatibility-plan.md), [SPRINT-014](../sprints/SPRINT-014-cowork-install-compatibility.md), [Host evidence #81](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867), [Closeout hub #86](https://github.com/urruegg/frontier-envisioning/issues/86) |

## Current plan approval and execution blocker

The maintainer approved the completed plan at `7c522ca` on 27 November at
18:25:02 +01:00: **"okay the plan is approved please implement it sub agent driven"**.
The [receipt](https://github.com/urruegg/frontier-envisioning/issues/87#issuecomment-7224405112)
separates approval from actual #8 readiness. Fresh checks still find main
unprotected with empty native rules and legacy protected routing. Task 0 blocks
production; earlier proposed/pending-plan statements below are history.
No implementation, version bump or protected change occurred.

## Outcome and audience

Make the NEXT compatible version, **1.11.1**, installable through Cowork's
observed whole-draft save contract. Keep the eight-skill distribution, existing
safety controls and unchanged Identity kit generation. This is an intake record
for the maintainer and later engineering review, not a product change or release.
Accountable owner: `@urruegg`; AI authorship is not owner sign-off.

## Problem and evidence

The human-supplied [#81 receipt](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867)
pins the published 1.11.0 ZIP and actual host refusals. All eight skills need
whole draft sources at `working/<name>` and destinations at `skills/<same name>`.
Nested package sources were refused without writes. Identity has 23 extra
files, 24 including root `SKILL.md`, exceeding the observed recursive limit
of 20 files besides that root file. The old Identity 1.9.2 remained installed.

A working documentation-only consolidation yielded 20 extras, 21 total.
Successful host save, 21/21 installed equality, identical 429-file Caldova kits
and generated-kit tests are **reported human evidence**, not checks reproduced
by this drafting agent. Structural rescore was not done. The companion repack
ZIP was absent at the report-relative path; no downloaded repack script was
executed. The design records the original report and ZIP fingerprints, without
copying private material or treating a workaround as new-package acceptance.

## Actual human decisions and options

On **27 November 2026**, the user requested Superpowers brainstorming, selected
`source-consolidation-1111`, then explicitly answered `approve_design=true`
to the install-flow, safety and verification design.

| Option | Decision and rationale |
|---|---|
| Canonical source consolidation for NEXT 1.11.1 | Selected. One shipped source tree fits the observed limit and preserves kit behaviour through direct fixture-consumer and byte-parity checks. |
| Build-time projection | Rejected. A second projected tree adds source/package divergence and obscures which references and examples the installed skill actually contains. |
| Manual repacking or repeated user workarounds | Rejected as the product solution. The installed workaround remains evidence; it does not repair the canonical source, staged-path contract or premature installation reporting. |

This approves the conversational design only. Written-spec review, later
explicit implementation-plan approval, formal independent review, version
bump, code changes, release publication and protected #8 execution are not
approved by these answers. No protected label or readiness decision is inferred.

## Bounded design

The [specification](../specs/2026-11-27-cowork-install-compatibility-design.md)
defines acceptance **CWI-01–CWI-07**: read-only package checks, authorised host
staging and read-only staged hash verification before saves; recursive file
limits and cache rejection; lossless Identity source consolidation with a
repository-only brand fixture; quoted SKILL metadata with unchanged typed
booleans; explicit Factory guardrails and scope routing; finite 1.11.1 inventory;
and actual new-package local/host acceptance.

The [prior distribution design](../specs/2026-11-26-plugin-health-and-finops-exclusion-design.md)
and [Factory design](../specs/2026-11-25-agent-factory-handover-design.md)
remain source-qualified baseline authority. Their approvals and historical
evidence do not approve or validate #87.

## Separate tracks and next review

The [Draft sprint](../sprints/SPRINT-014-cowork-install-compatibility.md)
now links a **Proposed implementation plan** and is **not Ready**. The written
specification at `b9647ea` has actual approval for planning; the plan needs its
own approval and readiness evidence. No delivery deadline or head-qualified
implementation sign-off is recorded.
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) protected routing/
native main protection and [#9](https://github.com/urruegg/frontier-envisioning/issues/9)
scoped guidance/publication clearance remain separate human tracks.
Template stable-foundation verification/publication is also separate; absent
stable releases do not permit a fake GA claim or silent older/main fallback.
[#81](https://github.com/urruegg/frontier-envisioning/issues/81) stays open for
final new-package real host acceptance, linked through #86. #48/#58 and Caldova
governance/tenant work are not absorbed into this patch.

## Later written-spec approval and planning state

The preceding intake text preserves the pre-plan snapshot at reviewed
`b9647ea8c824af180cd60975d3f4c4b9e9297e8a`.
The later actual user follow-up **“true please proceed it's approved from my side”**
to the written-spec review request approves that written specification and
writing the [new plan](../plans/2026-11-27-cowork-install-compatibility-plan.md).
The earlier unavailable response was not approval. This supersedes the
earlier pending-review/no-plan status only; design choices and evidence stay
unchanged. The plan is Proposed, separate human plan approval/readiness remain
pending, and SPRINT-014 is not Ready. No approval time, protected label, host
result or execution permission is asserted. Human #8 remains a production blocker.
