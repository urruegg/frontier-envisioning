# SPRINT-011: process grounding and optional systems

| Field | Value |
|---|---|
| Version | 0.8 |
| Date | 2026-11-24 |
| Author | AI assistant (AI-assisted documentation) |
| Status | Core correction strict L1 passed; separately human-approved #66 CodeQL follow-up, full L2 and final handover remain pending |
| Scope | Parent #58 programme and approved 1.10.1 correction #59; staged implementation and evidence |
| References | [Catalogue](README.md), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Correction #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Idea](../ideas/2026-11-17-optional-systems-extensions.md), [Correction spec](../specs/2026-11-17-process-governance-sap-grounding-design.md), [Correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md), [Retention #52](https://github.com/urruegg/frontier-envisioning/issues/52), [Protected routing #8](https://github.com/urruegg/frontier-envisioning/issues/8) |

## Outcome and early work items

Write the actual agreed correction direction before planning implementation.
Correct current process guidance first; stage the optional systems foundation
and Dynamics 365 later. This early record is not a ready sprint or a schedule.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#58](https://github.com/urruegg/frontier-envisioning/issues/58) | [Programme and actual decisions](../ideas/2026-11-17-optional-systems-extensions.md#actual-human-decisions) | [First correction only](../specs/2026-11-17-process-governance-sap-grounding-design.md); wider pack designs not yet written | [First correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md); wider pack plans remain separate | `@urruegg` accountable; issue unassigned | #59 first; separate framework/Dynamics 365 written design and approvals | Decision intake, size M/P1; programme direction agreed, not ready for all-pack execution | Actual written correction approval recorded; no implementation result |
| [#59](https://github.com/urruegg/frontier-envisioning/issues/59) | [Correction stage](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Tasks 1-12](../plans/2026-11-17-process-governance-sap-grounding-plan.md); approved at `35ad763` | `@urruegg` accountable and assigned; agent involvement recorded, not approval | Reviewed runtime/rendering/support slices; [#52](https://github.com/urruegg/frontier-envisioning/issues/52) final release/reproduction retention | Runtime, renderer and support implemented/reviewed; prose validated; integrated gates pending | Sources checked 17 November; commit-qualified checkpoints below |
| [#60](https://github.com/urruegg/frontier-envisioning/issues/60) | [First correction](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01/02/04/07](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Runtime Tasks 1-6 and 8](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-1-verify-the-approved-execution-boundary-and-baseline) | `@urruegg` accountable; bounded builder, size M | Actual #59 plan approval; standard bump before plugin edits | Both bounded advisory stages passed; whole-product acceptance separate | `0e1c389`; 39 reviewer tests plus independent owner probes; broader builder result qualified below |
| [#62](https://github.com/urruegg/frontier-envisioning/issues/62) | [Correction output](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-03/04](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Renderer Task 7](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-7-test-then-correct-markdown-html-and-actual-downloads) | `@urruegg` accountable; bounded renderer, size M | Reviewed #60 runtime contract | Both bounded advisory review stages passed; integrated L2 still pending | `ccd72ce`; source-qualified review checkpoint below, not human sign-off |
| [#63](https://github.com/urruegg/frontier-envisioning/issues/63) | [Correction verification](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-05 to G59-08](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Profile/distribution Tasks 9-10](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-9-add-only-the-necessary-named-1101-raster-input-profile) | `@urruegg` accountable; bounded builder, size M | Reviewed #60/#62 interfaces | Finite profile, current example and extracted process checks passed both bounded reviews; final integration pending | `da363ce`; independent 37 raster/14 example tests and qualified extracted probes below |
| [#61](https://github.com/urruegg/frontier-envisioning/issues/61) | [Current guidance](../ideas/2026-11-17-optional-systems-extensions.md#staged-roadmap-and-next-decision) | [G59-01 to G59-05](../specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | [Prose Task 11](../plans/2026-11-17-process-governance-sap-grounding-plan.md#task-11-update-the-example-and-current-methodrequirements-documentation) | `@urruegg` accountable; bounded documentation, size S | Reviewed runtime fields and actual CLI behaviour | Method/schema-reference/current product records aligned; parent prose review and strict docs passed | Eight scoped files; no fabricated prose RED or final integrated gate claim |
| [#66](https://github.com/urruegg/frontier-envisioning/issues/66) | [Correction programme](../ideas/2026-11-17-optional-systems-extensions.md) | [Bounded helper follow-up](../specs/2026-11-17-process-governance-sap-grounding-design.md#bounded-codeql-follow-up-24-november-2026) | [Approved inline amendment](../plans/2026-11-17-process-governance-sap-grounding-plan.md#approved-bounded-codeql-amendment-24-november-2026) | `@urruegg` accountable and assigned; bounded renderer, size S | Actual `approve-bounded-codeql-fix` answer; current gate freeze released before edits | Approved implementation pending; no protected ready label | Two existing helper alerts in draft #65; no alert suppression or dismissal |

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

## Renderer review and resumed verification, 24 November

The maintainer requested continuation of the existing approved correction.
The linked worktree remains `fix/59-process-grounding`; the unrelated primary
checkout's editor settings and original field briefs remain untouched.

At `ccd72ce4e95d9e98a9fe364b105cde60dfb3965f`, a read-only reviewer passed
the renderer specification stage, followed by a separate read-only
correctness reviewer. Neither reported Critical, Important or Minor findings
in the bounded #62 scope. These are advisory code assessments, not human
approval or whole-product acceptance.

The specification reviewer reported 16 passing G59 DOM cases, a failing
base-renderer control, Python document/Turtle parity and the actual G59 browser
callback passing under strict CSP. Its browser callback used a verified
development-only SVG fixture and an installed browser; it was **not** the
standard Playwright runner or final L2/package proof. Template and generated
install-inventory comparisons passed. The controller subsequently restored the
standard runner's missing Chromium revision in the isolated worktree.

The controller's earlier `python tools/dev.py check` used global Python 3.14,
not the plan's existing primary virtual environment. It observed **849 tests
passed, seven skipped**, a passing plugin self-test and package build, then
**GATE FAILED: demo build** because normal 1.10.1 generation fell back to an
unavailable PNG converter. Ruff was also absent from that global environment.
The primary virtual environment supplies Python 3.11 and Ruff; its existing
1.10.0 finite-profile baseline passed five tests. The required finite 1.10.1
profile remains #63, not a reason to use SVG-only output as final proof.

The actual published 1.10.0 plugin ZIP and release manifest were downloaded
read-only from the approved release. Their SHA-256 values match
`9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`
and `41cefe7d44411d6f58d68a7bd6d2ebf6d15074ecf0d385dfea10153ab5dd14a3`.
Against the clean independent worktree at the immutable release source,
`python tools/verify_release.py --manifest <downloaded-release-manifest.json> --force`
reported **release 1.10.0: 4 of 4 artefacts reproduced**. This compares existing
tag-build outputs with the actual published manifest; it is not a new build
or a 1.10.1-to-1.10.0 comparison. The tag object and source still match the
identities recorded above.

Protected `releases/1.10.0/manifest.json` is still absent on main. This evidence
does not complete human-only #52 retention/merge acceptance. Read-only GitHub
inspection also reports main unprotected with no rulesets; protected routing
and effective native controls remain human-only #8 work.

## Profile and distribution implementation checkpoint

Commit `da363cebaf4acf3d40ec40fb5f1c9f2c9dcdde69` adds only the named
1.10.1 raster profile, its focused tests, the current conditional Caldova
example and installed process/self-test coverage. The builder reported these
actual test-first results:

- Raster RED: six new tests, 19 failures because 1.10.1 replay was rejected;
  GREEN: 37 tests across the six approved raster modules.
- Example RED: 12 Caldova/CommonDataModel tests, three failures; corrected
  unknown-route proposals preserve identifiers, mappings and Employee gaps.
- Executed self-test assertion RED: one failure for nine missing checks;
  GREEN: 16 extracted-process/self-test/distribution tests, then 118 tests
  across ontology and distribution.
- Plugin self-test: 77 checks passed. Package and precommit passed, with
  Ruff clean and the six existing renderer ESLint warnings unchanged.

The measured 205 non-raster inputs and 223 PNG hashes remain unchanged.
Historical profiles/assets and their pins were not altered. The new input
profile SHA-256 is
`3a75f4ffe3d12cf20c137663df6daf1bc48b7a2033a8a9e03ddaa8a3152c8b4e`;
the normal full-demo identity ZIP remains
`e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`.
The builder's verified extracted intermediate plugin candidate is
`a91dd40f7b47500edce1a47f3fb7f9a6cc959d751a75d988d6192954297650c7`.
That digest predates #61 prose and is not the final integrated package.

The independent #63 reviewer subsequently passed specification, then bounded
correctness, with no Critical, Important or Minor findings. It independently ran
37 raster and 14 example/CommonDataModel tests, verified the existing full
identity artefacts and checked the candidate's 101 members against source.
Two extracted/self-test probes reused the verified existing candidate ZIP
instead of invoking a builder; this was not a new final package build.
In-memory counterfactual checks reproduced test sensitivity, not historical
execution order. Final strict L1/L2, regenerated documentation, final package
identity and extracted execution remain integration tasks.

The controller then ran the standard Playwright G59 case against the full
normal demo under real CSP: **one test passed** with Chromium revision 1248.
The filename filter `ontology-preview.spec.mjs` avoids interpreting Windows
path separators as regular-expression escapes. This focused result is not
the final full L2 suite.

## Current documentation integration

The documentation agent aligned the eight approved #61 prose/docstring files
with the reviewed contract. It had no shell tool, so it did not run or claim
validation or commit. The controller reviewed the actual prose and ran
`python tools/dev.py docs --strict`, scoped Ruff on `build_ontology.py` and
`git diff --check`: zero documentation errors, **ALL GATES PASSED**, clean
Ruff and whitespace. The Python change is descriptive docstring only.
No artificial RED is claimed for prose.

## First complete strict integration gate

Against the core correction at `2e9bfbd1b110eb5c860f8f4fe8d21be962f9d33e`,
`python tools/dev.py check --strict` ended with **ALL GATES PASSED**:
858 unit/pipeline tests and 2,946 subtests passed; seven tests were skipped
(four Windows symlink-privilege cases, two superseded release contracts and
the unreleased current-version comparison). All 199 DOM tests passed.
Ruff and documentation checks passed; the six existing ESLint warnings remain.
The normal full demo, finite profile, ten-capture drift check, self-test,
package and neutrality checks passed with no missing optional tool.

The plugin SHA-256 at this checkpoint is
`9866fa1032c6916ba8d092225195c6c6378c8c096b51283367eacee5ea60e8ae`.
The 1.10.1 release step reports that there is no manifest yet; its successful
step status is **not** published 1.10.0 reproduction or #52 acceptance.
The earlier actual-published-manifest comparison remains separately recorded.

The first strict attempt exposed the coupled product-document contract:
new approved identifiers and explicit A.12/A.13/B.9 qualifications were not
isolated from historical receipt checks, and current Status fields needed the
explicit no-release-approval statement. Focused RED/GREEN in `90b1809` and
`4bebfdf` fixed these without changing receipt hashes. All 27 preservation
tests and 301 subtests passed. A reviewer also passed seven focused checks
and rejected nine additional historical-row/boundary mutations.

Full repository checks do not replace CodeQL. The pushed draft exposed two
existing helper alerts. The maintainer explicitly approved the bounded #66
design/inline plan in the structured answer recorded in that issue; scope
was not silently expanded. Its implementation and final L2/CodeQL/new-head
verification remain separate from this complete core-correction gate.

## Historical planning validation and handoff

The following paragraphs retain the original planning checkpoint; the later
implementation and review evidence above supersedes its next-step wording.

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
