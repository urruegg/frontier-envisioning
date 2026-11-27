# Cowork install compatibility for NEXT 1.11.1

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-27 |
| Author | AI assistant; AI-assisted drafting from the human decisions and supplied engineering evidence |
| Status | Conversational design approved 2026-11-27; written specification review pending; no implementation plan |
| Scope | Public-safe, customer-neutral planning for eight-skill Cowork installation and canonical Identity source consolidation |
| References | [Catalogue](README.md), [Work item #87](https://github.com/urruegg/frontier-envisioning/issues/87), [Design](../specs/2026-11-27-cowork-install-compatibility-design.md), [SPRINT-014](../sprints/SPRINT-014-cowork-install-compatibility.md), [Host evidence #81](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867), [Closeout hub #86](https://github.com/urruegg/frontier-envisioning/issues/86) |

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
has **no implementation plan yet** and is **not Ready**. Written specification
review is pending; there is no delivery deadline or head-qualified sign-off.
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) protected routing/
native main protection and [#9](https://github.com/urruegg/frontier-envisioning/issues/9)
scoped guidance/publication clearance remain separate human tracks.
Template stable-foundation verification/publication is also separate; absent
stable releases do not permit a fake GA claim or silent older/main fallback.
[#81](https://github.com/urruegg/frontier-envisioning/issues/81) stays open for
final new-package real host acceptance, linked through #86. #48/#58 and Caldova
governance/tenant work are not absorbed into this patch.
