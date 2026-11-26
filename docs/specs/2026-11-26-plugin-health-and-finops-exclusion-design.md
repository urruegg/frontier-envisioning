# 1.11.0 Cowork health and FinOps distribution amendment

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-26 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted design |
| Status | Conversational design approved; this written specification awaits human review; no implementation, plan or release approval implied |
| Scope | Eight-skill Cowork ZIP without FinOps; Value Case/Process routing and exact-package verification |
| References | [Bug #81](https://github.com/urruegg/frontier-envisioning/issues/81), [Idea](../ideas/2026-11-26-plugin-health-and-finops-exclusion.md), [Draft PR #80](https://github.com/urruegg/frontier-envisioning/pull/80), [Factory design](2026-11-25-agent-factory-handover-design.md), [Baseline plan](../plans/2026-11-25-agent-factory-offline-implementation-plan.md), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md) |

## 1. Outcome and authority

Amend the unreleased 1.11.0 candidate so its Cowork ZIP excludes FinOps while
retaining Value Case and Agent Factory. Correct the reported Process/Value
Case routing ambiguity without changing their business responsibilities.
This is a release-distribution amendment, not FinOps source retirement.

Actual session decisions:

- `finops_scope=exclude-from-111-distribution`.
- `installation_target=cowork-zip`.
- `design_review=approve-bounded-health-amendment`.

These are real conversational decisions, recorded in #81, not written-spec/
plan approval, authenticated identity, protected labels or release permission.
The accountable owner is `@urruegg`. A new approved implementation plan is
required; the earlier Factory plan is baseline context only.

## 2. Source evidence and limits

The supplied `plugin-health.html` was generated at **2026-11-26 12:36 UTC**.
Its automatically computed SHA256 is
`20902064efa12cfa4a0a4079c9b346f104ef6afd947e4295d24501ec57f5592a`.
All eight scanned skills meet the publish bar; average score is 98 and
Value Case scores 100/100. The two unresolved coexistence findings are:

1. `frontier-finops` versus `frontier-process`.
2. `frontier-process` versus `frontier-value-case`.

Security, tool-description and package checks pass, with advisories about an
environment reference, icon data, absent connectors and Studio-backed MOS3
builder metadata. Policy review was not submitted. None is reported as a
failed security or ordinary Cowork ZIP check.

The report contains FinOps but not Agent Factory. Its input package version
and ZIP digest are unknown. Do not claim it validated the current candidate
or demonstrated a missing/broken Value Case installation. Preserve its raw
findings separately from assessment and future verification.

At intake, #80 remained draft at `ab9b10b0ab53316c5b351b169aef5a35426d3c74`;
no `v1.11.0` release or tag was found. Recheck before product changes. If a
published/tagged version intervenes, stop and resolve the version boundary
with the maintainer; never rewrite immutable release evidence.

## 3. Distribution design

Use one explicit, version-scoped release inventory. Source and distribution
sets become deliberately distinct for 1.11.0; do not scatter unchecked skip
lists across consumers. Keep existing shared mechanisms where suitable.
The exact distributed skill set is:

1. `frontier-envisioning`
2. `frontier-context-discovery`
3. `frontier-blueprint`
4. `frontier-solution-design`
5. `frontier-agent-identity`
6. `frontier-value-case`
7. `frontier-process`
8. `frontier-agent-factory`

FinOps remains retained source with tests. Its skill folder is absent from
the ZIP, release manifest registration and generated installer file/copy
inventory. Active start prompts and guidance do not advertise installed
FinOps operations. The named exclusion applies to 1.11.0, not arbitrary skill
folders or historical versions. Unexpected/unregistered/accidentally omitted
skills still fail validation. Do not add a generic user-controlled skip flag.

Seven existing GA wrappers and Preview Factory retain their current maturity/
optional/acknowledgement semantics. FinOps exclusion is not Factory GA,
installation consent or removal of historical financial provenance.

The alternative of relocating FinOps source outside the plugin was rejected
as unnecessarily broad. Merely hiding its installer entry while shipping its
files does not satisfy this design.

## 4. Routing and operational behaviour

Value Case owns ordinary business value, value trees, assumptions, NPV, ROI,
payback and sensitivity. Process owns ontology, business objects, proposed
CDM mappings and data products. Their descriptions and procedures explicitly
defer those responsibilities to each other.

Do not copy the report's broad suggested exclusions for generic words such
as "agent", "blueprint" or "build": those would reject valid requests.
Preserve the 900 UTF-16-unit description rule and existing routing conventions.
Do not route a 1.11.0 user to a supposedly installed FinOps skill.

Ordinary evidence-based Value Case, Blueprint/core and Factory review-starter
flows must work from the extracted distribution without FinOps. Genuine
ordinary cost assumptions remain allowed. Existing FinOps-derived inputs
retain provenance and safeguards: unavailable owner validation is an explicit
error, never zero costs, silent omission, stripped ancestry, manufactured
consent or accepted financial evidence. Do not change financial formulas,
rates, calculator semantics or Preview acknowledgements.

## 5. Packaging, documentation and non-goals

Regenerate the installer through the sanctioned package command. Update
current manifest/installer/maturity checks, self-test and directly affected
call sites consistently. Current user/product/release guidance states the
eight shipped skills and retained-source FinOps boundary.

Preserve all historical nine-skill candidate, approval, CI, release/raster
and source records at their named commits. New requirements/evidence belong
in current PRD/solution-design/sprint sections and the changelog; no blanket
count/version replacement. Use the existing renderer-source generation
route if any directly coupled renderer change proves necessary.

Out of scope: FinOps source deletion, new financial features, new connectors,
dummy Studio metadata/IDs, Studio-backed MOS3 publication, workflow/token/
settings changes, new tenant actions and systems/Dynamics 365 #58.
Human merge/release/tag/publication, protected files and #8 routing remain
human-only. A health score is not release approval or transfer permission.

## 6. Acceptance and verification

| ID | Required evidence |
|---|---|
| H111-01 | Inspect the actual rebuilt ZIP, manifest and generated installer: exactly the eight named skills; Value Case/Factory present, no FinOps skill files or copy calls. |
| H111-02 | FinOps source/tests remain. Test the named exclusion and a genuinely unexpected omission; unknown exclusions must still fail rather than bypass strict checks. Historical distribution/reproduction policy remains intact. |
| H111-03 | Run genuine ordinary Caldova Value Case from the extracted package without repository/sibling FinOps fallback; preserve valid values and explicit missing-budget gaps. |
| H111-04 | Extracted core/Blueprint and Factory review-starter flows work without FinOps. Financial-marker/provenance and missing-owner-validator negative controls still refuse explicitly. |
| H111-05 | Process/Value Case descriptions and procedures have the correct mutual boundary, supported by applicable document/routing checks; no generic-word exclusion or advertised installed FinOps operation. |
| H111-06 | Focused behavioural RED/GREEN, source FinOps regressions, generated inventory, exact-package and actual retained-reference receiver proof pass. Full L1 and applicable L2 run on the amended candidate; old passing CI is not substituted. |
| H111-07 | Rerun the host health check against the actual rebuilt package when the checker is available. Record ZIP digest, report timestamp, correct eight-skill inventory including Factory/Value Case, and the Process/Value Case conflict result. An unavailable checker remains outstanding, never simulated or reported passed. |
| H111-08 | Bug #81 links written decisions/plan, actual fix commits, PR, commands/results and health evidence. Record human merge and eventual published version/date only after they occur. |

Use the existing quality gates and deterministic package mechanisms; add only
focused tests for the changed distribution and affected behaviours.
Do not mutate the supplied report or tune unrelated code to manufacture a
green score. Preserve truthful Studio-only and other advisory warnings.

## 7. Handoff and next approval

The target is the 1.11.0 candidate before person-operated publication, not a
promised date. Present this committed specification for written review.
After actual approval, prepare a separate exact-file/test-first implementation
plan and obtain plan approval before delegated implementation.

No product changes or amended-candidate test/health passes are claimed here.
The new plan must link #81, this specification, the idea, SPRINT-013 and #80;
missing stages remain explicitly unapproved, not inferred from file status.
