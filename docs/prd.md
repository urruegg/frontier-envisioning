# Frontier Envisioning — Product Requirements

| Field | Value |
|---|---|
| Version | 1.11 |
| Date | 2026-11-26 |
| Author | Urs Rüegg (original product document); Copilot (AI-assisted split, accessibility maintenance, selective intake, 1.9.1 prose and 1.9.2 candidate notes); AI assistant (1.10.0 candidate prose preparation); Copilot SDK (verification evidence); Copilot (AI-assisted #61 process correction prose); AI assistant (AI-assisted #70 release evidence guidance); Copilot (AI-assisted #78 Factory candidate prose) |
| Status | Maintained requirements; unreleased 1.11.0 package/receiver and full local L1 verified; full browser/server acceptance pending; historical evidence retained; no release approval implied |
| Scope | Factory-only 1.11.0 candidate requirements and acceptance, with earlier engineering/product requirements and history preserved |
| References | [Solution design](solution-design.md), [Docs](README.md), [D2 plan](plans/2026-11-09-documentation-foundation-plan.md), [Layout amendment](specs/2026-11-10-documentation-layout-design.md), [1.7 intake plan](plans/2026-11-10-handover-1.7-intake-plan.md), [SPRINT-004](sprints/SPRINT-004-handover-1.9-preview-finops.md), [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33), [SPRINT-006](sprints/SPRINT-006-version-1.9.2.md), [Baseline spec](specs/2026-11-12-agent-finops-baseline-design.md), [SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md), [Correction spec](specs/2026-11-17-process-governance-sap-grounding-design.md), [Correction plan](plans/2026-11-17-process-governance-sap-grounding-plan.md), [SPRINT-011](sprints/SPRINT-011-process-grounding-and-optional-systems.md), [Prose #61](https://github.com/urruegg/frontier-envisioning/issues/61), [Release evidence spec](specs/2026-11-24-release-evidence-simplification-design.md), [Human adoption handover](engineering/release-evidence-adoption.md) |

## 1.11.0 Agent Factory offline Preview

**26 November 2026: unreleased development candidate, not product acceptance.**
Add **Envisioning Agent Factory**, registered name `frontier-agent-factory`,
as the optional Preview ninth skill in the existing plugin. Registration is seven
non-FinOps GA wrappers, optional Preview FinOps and optional Preview Factory.
The offline producer is implemented and reviewed through `52d6c0e`; ninth-skill
registration, procedure and maturity/installer metadata are implemented under
[#79](https://github.com/urruegg/frontier-envisioning/issues/79).
Exact package/receiver and full local L1 checks passed. Full browser/server
acceptance remains pending; three isolated timeout reruns passing is not a
complete browser-suite pass.
Ordinary core, value, identity, Blueprint, design and process work requires
neither extension. Factory starts only on an explicit starter-repository,
ZIP or handover request, never automatically after a PRD or as automatic FinOps.
It is not a new business runtime, SDK, application or tenant loader.

Accountable owner: `@urruegg`. The [idea and actual choices](ideas/2026-11-25-agent-factory-handover.md),
[approved design](specs/2026-11-25-agent-factory-handover-design.md),
[complete approved plan](plans/2026-11-25-agent-factory-offline-implementation-plan.md)
and [SPRINT-013](sprints/SPRINT-013-agent-factory-handover.md) govern
[#72](https://github.com/urruegg/frontier-envisioning/issues/72) and
[#78 Task 14](https://github.com/urruegg/frontier-envisioning/issues/78).
The [full-plan receipt at 5dbfc8a](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7167852054)
approves the written tasks, not completed verification or human-only operations.
[ADR-0032](adr/0032-offline-agent-factory-handover.md) is **Proposed**, not Accepted.

### Factory requirements and acceptance

These AF identifiers map directly to the
[approved AF-01–16 criteria](specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint)
and [plan acceptance map](plans/2026-11-25-agent-factory-offline-implementation-plan.md#17-acceptance-map-and-final-execution-order).
They add no historical FR/AC IDs. Proof targets below are requirements, not
passed results; actual source-qualified evidence is in
[B.9](solution-design.md#agent-factory-candidate-verification-26-november-2026).

| ID | Requirement | Acceptance / proof target |
|---|---|---|
| AF-01 | Optional Preview ninth skill in the same plugin, explicitly requested and independent of core/FinOps. | Nine registered skills with explicit routing and maturity; installed core-without-extension proof passed in the full local candidate gate. Actual Cowork remains not performed. |
| AF-02 | Each new handover uses actual authorised available-host latest-stable discovery, then pins release/tag/commit/bytes once. Retain only `id`, `tag_name`, `published_at`, `draft`, `prerelease` for all enumerated releases. | Complete pagination; valid time/tag for every stable candidate; resolve only the uniquely selected stable tag. Unknown metadata, ties, access/network/selected-tag errors or incompatibility fail without main/older fallback. No raw API bodies, authors, assets or protected URLs enter producer/export data. |
| AF-03 | Only healthy complete no-stable discovery permits explicit approval of an immutable **unreleased bootstrap**. Local input is not proof of latest. | Real export-bound discovery/acquisition/approval receipt and automatically checked source bytes; frozen reproduction does not claim another lookup. Draft/prerelease null fields need no invented tag/commit/time. |
| AF-04 | Preserve the full compatible foundation, policies, workflows, locks, licences and modes, not a keyword-pruned overlay. Exclude `.git`, account/cache/staging/dependency state. | Passive byte/mode preservation and source/profile checks; no downloaded-code execution, Python networking or dependency setup. Foundation MIT/third-party notices grant no rights over customer files or transfer clearance. |
| AF-05 | Preserve final reviewed PRD/design/ADRs and applicable readiness, identity, Blueprint, value, process and financial material. Keep authored bytes/IDs and explicit original-to-factory maps for selected MVP/shared dependencies. | Select only customer-safe entities; no competing generator, renumbering or keyword-MVP inference. Source/review/transfer evidence is real; out-of-scope dependencies remain named gaps, not new work. |
| AF-06 | Emit unextended receiver intake 1.0 at `docs/intake/records/<id>/intake.json`, with eight roles per selected solution and separate producer 1.0 sidecar. | PRD/design never N/A; other N/A reasons may be short and specific. Actual hashes/transformation approvals, applicability, scope/owners/acquisition/transfer and required fields satisfy the receiver. No demo approval or substitute evidence. |
| AF-07 | Default to valid `needs-clarification` review-starter intake with explicit engineering gaps. Explicit invalid accepted requests fail, never downgrade. | Genuine recorded acceptance meets every condition. Preserve raw prior accepted JSON, Windows path spellings, CRLF and provided bytes; new ID/`supersedes` for change. Unavailable historical originals remain not verified. Neither disposition generates application/runtime/source/test/evaluation/IaC units or remote issues. |
| AF-08 | Every provided current/history file and exported metadata needs actual customer-scope classification, transfer and sharing review, even in drafts. Use whole-original-ancestry and schema-owned privacy projection. | Guard structured content, metadata, filenames, references, known internal notes, private keys/arrays and withheld names/counts. Reject restricted baselines, raw mail/transcripts, private sources, secrets, account state and protected links. Office/PDF review is opaque human evidence, not semantic DLP, authenticated review or IP clearance. |
| AF-09 | Accept only ordinary `.md`, `.txt`, `.json`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv`. The full output ZIP is distribution, not an intake input archive. | Selected HTML/ZIP/Turtle fails with a need for actual reviewed JSON/Markdown equivalents, never rename/drop/bypass. Include `START_HERE.md`, `handover/manifest.json` and the intake record, review and artefacts. |
| AF-10 | Bounded STORE/DEFLATE source ZIP: 32 MiB compressed, 64 MiB decoded, 4,096 members including directories. Receiver: 16 MiB per file, 1 MiB intake JSON, one shared 64 MiB baseline-plus-source validation budget. Final: 128 MiB expanded/4,096 members including generated files. | Actual at/over limits and known corruption, path/link/reparse/file-parent/case/slash/state hazards fail before bounded atomic replacement; inputs and prior good output survive failures. |
| AF-11 | Frozen source, inputs and metadata reproduce identical ZIP bytes; hashes and inventory are automatic, not a manual customer ceremony. | Byte comparison; inventory excludes the manifest's own hash and final ZIP SHA256 is stdout. Current original hashes and historical-original unavailability are reported separately. |
| AF-12 | Exercise the actual pinned receiver, separately from export validation and recorded review. | Synthetic Caldova packages with actual baseline/source reads where available; missing tools, original bytes and Node 24 LTS checks remain explicit, never simulated. |
| AF-13 | Verify the exact packaged offline producer outside this repository with trusted bundled siblings. Python producer is stdlib 3.11+; receiver is Python 3.12+/Node 24 LTS. | Installed exporter/installer and actual generated-intake receiver proof; absent requested helpers fail explicitly. Cowork discovery/install/acquisition/export is unavailable and **not performed** under the approved offline amendment, not a runtime cutover or host-support claim. Node 26 is not Node 24 certification. |
| AF-14 | FinOps remains optional; actual current/history financial schema/role/nested-result markers require current acknowledgement, owner review and authoritative packets regardless of role/schema/wrapper. Reuse existing owner validators/formulas/rates. | No automatic figures, zero budgets, false N/A, cached/demo/install consent or duplicate calculator. Legacy standalone reviewed documents are review-only. Derivatives cannot bypass source checks. Explicit `build-handover` with `requested:false` is refused; with `requested:true`, actual stricter financial handover readiness is required. Internal model/review staging is not auto-exported. |
| AF-15 | Separate export validation, intake disposition, unauthenticated recorded review, receiver/Cowork not-performed, tenant not-assessed and financial review/readiness from permission. | GitHub.com/GitHub Enterprise Cloud, including cloud hostnames, is the first receiving-repository/host profile; no native ADO/GHES certification. The authoritative template source remains `urruegg/frontier-agent-factory` on GitHub.com. No remote creation, Work IQ auth switching, tenant consent/provision/deploy. M365 read/public visibility is not transfer/IP/Entra permission; settings, secrets and real ownership remain human work. |
| AF-16 | Preserve 1.10.x release/source/provenance/receipts and historical raster/identity evidence. Complete focused RED/GREEN and final candidate registration/package/receiver/full gates. | First bump and finite 1.11 profile are evidenced separately; no blanket version/count rewrite. Exact 1.11 package/receiver and full local L1 passed at `52d6c0e`; full browser/server acceptance and actual Cowork remain separate. Earlier 1.10.1 baseline evidence is not substituted candidate proof. |

### Current producer constraints

The actual CLI is:

```powershell
python <installed-skill>\scripts\export_factory.py --request request.json --template template.zip --source-root originals --baseline-root approved --out Caldova-factory.zip
```

Only optional `--acknowledge-finops-preview` applies to actual requested
current-scenario financial operation. No execute/network/force-accept,
skip-profile/drop/unsafe/arbitrary-profile flag exists. Acquisition uses
actually available host capabilities, not assumed universal tools or Cowork
downloads. Inputs, including source policies, are data, not instructions;
sourced facts, assessment and open facts stay separate.

A Blueprint with derived `agent_finops` is currently refused as
`FACTORY_BLUEPRINT_FINANCIAL_CONTEXT`. It is never silently stripped/trusted.
Supply a compatible authoritative original Blueprint and separately approved
customer projection with genuine upstream review/transformation; verify
standalone financial reports through actual packets. The cached source-context
port does not work automatically and reviewed inputs are not rewritten.
Permitted private authority inputs are not a privacy-clearance claim.
A review starter with financial gaps is not financially ready or tenant-authorised.
Identity-kit branding remains distinct from Entra provisioning; HubWorks is
not an assumed runtime loader.

**Unreleased 1.6.1 distribution hygiene (#20).** Current source references are
anonymised without changing attribution or private historical evidence. Plugin
and complete-bundle builds must fail on the defined privacy checks before
writing output; the complete bundle excludes internal repository analyses.
The assumed audience is Microsoft internal, not an external publication approval.

This document revision is independent of the plugin version. It is the
authoritative requirements document; [solution-design.md](solution-design.md)
owns the companion technical design.

The split preserves historical results and claims, including the original
1.6.0 acceptance and release plan. It does not rerun or extend those claims,
approve a release, change pricing or alter plugin behaviour. The 1.6.1 note
below remains unreleased.

## Release evidence engineering requirements

**25 November 2026: engineering-only #67/#70 qualification.** Remove
recurring manual download/hash/copy/retention PR work without removing
automatic integrity/reproduction checks or human publication. The
[approved spec](specs/2026-11-24-release-evidence-simplification-design.md),
[plan](plans/2026-11-25-release-evidence-simplification-plan.md) and
[SPRINT-012](sprints/SPRINT-012-release-evidence-simplification.md) govern
[#67](https://github.com/urruegg/frontier-envisioning/issues/67) and
[#70 guidance](https://github.com/urruegg/frontier-envisioning/issues/70).
`@urruegg` is accountable. The
[actual plan/execution receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155657072)
does not grant protected-edit, dispatch, merge, label or publication authority.
The [release evidence rationale](adr/0031-release-assets-as-evidence.md)
remains Proposed.

These are engineering requirements, not new plugin features or a product
version change. Existing migration receipts, identifiers, historical
requirements/results and published assets/tags/records/provenance remain
unchanged. The dated #52 retention references below retain their earlier
context; current disposition is conditional supersession after actual
verified replacement/adoption, not a claim that an old copy/merge happened.

| ID | Current requirement and acceptance |
|---|---|
| RE-01 | Normal future flow is maintainer review/merge, then human **Run release workflow** with `version`, `manual_checks`, `publish`; automation verifies and publishes. No routine manual download/hash/copy/retention PR. Manifest/checksums remain release assets and automated comparison remains. |
| RE-02 | Resolve only the requested exact version and matching repository/annotated-tag/source, never `latest`. Reject conflicts and wrong-version evidence. Preserve historical formats/provenance and compare historical releases only with matching historical outputs. |
| RE-03 | CI requires fresh authoritative access/lookup. Only confirmed absence of both exact published release and conflicting tag permits development; access/network errors, drafts, missing assets, malformed evidence and hash/artefact mismatch fail, never silently fall back. |
| RE-04 | Local checks stay offline-capable: valid exact-version/source cache compares; a genuine miss reports `not-performed`, not a release pass or confirmed development. Reject tampered/stale/wrong-source cache; no cached absence claims or plugin networking. |
| RE-05 | Preserve existing assets/tags/records, deterministic package comparison, generated-date handling, finite raster inputs and runtime behaviour. New releases need no copied record under `releases/`; explicit old manifests remain usable. |
| RE-06 | Use deterministic local GitHub/download fixtures and real validation/cache code. Changed checker behaviour needs observed RED/GREEN; prose uses document validation, not fictional code tests or live-service unit tests. |
| RE-07 | Guidance and gate summaries distinguish implementation, pending human adoption and publication. Hand off protected edits; keep review/merge/settings/labels human-only and legacy flags unset/false. #52 supersession requires verified replacement and actual adoption; #8 and #48 activation remain separate. |
| RE-08 | Record actual targeted/full strict results, exact-version proof and CI status separately. No invented final hash/pass, release dispatch, publication or manual acceptance. |

The [current engineering flow and evidence](solution-design.md#release-evidence-engineering-flow)
qualify [B.9](solution-design.md#b9-quality-and-testing). Bounded #68 and #69
each passed specification then correctness review with no findings
outstanding; **full strict gate, actual PR #71 CI and protected evidence-access
adoption remain pending**. The owner-dispatched workflow was already adopted
under #55/#57; the additional
[read-only L1 token binding](engineering/release-evidence-adoption.md#one-time-protected-workflow-handover)
is one-time human work, not recurring ceremony or #48 App activation. No
PAT/App/new authentication scheme, native attestation or manual draft step
is introduced. Checksums/cache consistency are not signatures or independent
approval.

Intended private/internal classification is unchanged. Read-only GitHub
metadata reported `private:false`; the
[policy/setting discrepancy](engineering/release-evidence-adoption.md#classification-and-access)
needs human reconciliation, not a public-clearance claim.

## 1.10.1 process grounding correction

**24 November 2026: unreleased patch candidate, not release acceptance.**
Published **1.10.0** remains the immutable baseline. The bounded correction
[#59](https://github.com/urruegg/frontier-envisioning/issues/59) is governed by
the [approved written spec](specs/2026-11-17-process-governance-sap-grounding-design.md),
[exact plan](plans/2026-11-17-process-governance-sap-grounding-plan.md) and
[SPRINT-011](sprints/SPRINT-011-process-grounding-and-optional-systems.md).
The accountable human owner is `@urruegg`. Written-spec approval and the
separate plan/readiness approval at `35ad763` are recorded in the
[receipts](specs/2026-11-17-process-governance-sap-grounding-design.md#outcome-and-authority),
including the [plan decision](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6951849396).
No protected label, formal GitHub review or release permission is inferred.

The public facts were checked by the parent on **17 November 2026**, as recorded
with actual titles, dates and links in the
[spec evidence](specs/2026-11-17-process-governance-sap-grounding-design.md#evidence-known-facts-and-assessment)
and [process method](../plugin/skills/frontier-process/references/ontology-method.md#1-sources-and-limits).
This prose pass claims no new source fetch. The
[current solution flow and verification](solution-design.md#1101-process-grounding-correction)
describe the reviewed implementation, not speculative fields.

### Patch requirements and acceptance

These narrowly scoped requirements/acceptance targets supplement, not rewrite,
the historical tables. Bounded runtime `0e1c389`, renderer `ccd72ce` and support
`da363ce` passed their specification/correctness reviews. Final integrated
post-prose acceptance against G59-01–08 remains pending.

| Requirement / acceptance | Spec criterion | Required outcome and acceptance target |
|---|---|---|
| FR-0154 / AC-057 | [G59-01](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | New proposals use source-qualified OneLake catalog/Fabric-domain guidance, not new retiring Unified Catalog/classic governance structures. Preserve Purview security/compliance, labels/DLP and existing-estate migration gaps; no full parity or retirement of all Purview claim. |
| FR-0155 / AC-058 | [G59-02](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Name Datasphere → ADLS Gen2 → Fabric/OneLake, snapshot/changes, Delta tables and read-only SQL replication. Confirm supported source, existing Fabric capacity, Datasphere environment, Premium Outbound Integration entitlement and staging permissions through named-owner estate evidence. Commercial dependency stays unpriced/to confirm. Fresh sources remain unresolved/null/later; unconfirmed saved choices stay recorded and conditional, with no ready fallback. Complete prerequisites do not auto-select a route. |
| FR-0156 / AC-059 | [G59-03](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Domain assignment is grouping, not visibility/access/enforced security. Canon, proposals, JSON, HTML, all Markdown/downloads, method, readiness/risks and Caldova agree on current conditional meaning; no new layout/view/network behaviour. |
| FR-0157 / AC-060 | [G59-04](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Preserve inputs and saved paths/items/statuses/tables/domains, IDs/citations, feedback and verdicts as recorded evidence. Add actual route assessment/current guidance/current readiness without counting conditional sources as bound, mounted or publishable. Saved F-06 verdict stays; effective current readiness is open. Retain fail-closed audience/ancestry projection and unchanged feedback/Turtle contracts. |
| FR-0158 / AC-061 | [G59-05](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Eight skills remain seven non-FinOps GA wrappers plus optional Preview FinOps. Core/process/ordinary value works with FinOps absent or declined. No automatic money/licensing/ROI/time-to-value claim; separately requested financial work retains its existing awareness and fully priced handover gates. |
| FR-0159 / AC-062 | [G59-06](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Preserve published 1.10.0 source/tag/ZIP and immutable records. Only the finite named 1.10.1 profile is added; historical profiles/assets and identity inputs remain unchanged. Final release/reproduction acceptance still requires human #52 retention/merge evidence. |
| FR-0160 / AC-063 | [G59-07](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Remain offline, deterministic and stdlib-only. Ordinary conditional drafts succeed with warnings; strict warnings fail before output/new directories/overwrite. Malformed assessments/citation collisions fail ordinarily. Repeated outputs and original/good-output bytes are checked; unknown never defaults to success. |
| FR-0161 / AC-064 | [G59-08](specs/2026-11-17-process-governance-sap-grounding-design.md#acceptance-and-verification) | Bind observed focused RED/GREEN, regenerated artefacts, strict L1/L2/docs checks and extracted final-package execution to the actual post-prose candidate. Focused prior checks are not a final integrated pass or final candidate hash; report remaining human checks honestly. |

### Patch boundaries and release position

The additive model keeps `frontier-blueprint/1.0`, `frontier-ontology/1.0` and
`frontier-fabric-iq-canon/1.0`. A derived `owner_confirmed` assessment is only
an owner-asserted design selection with five estate-evidenced prerequisites,
named owner and explicit path/matching item. Public documentation, a name match,
an imported flag or a placeholder owner is not confirmation; the plugin does
not authenticate evidence, verify tenant access or approve licences.

No new systems skill, route framework or integration runtime is delivered.
The common systems foundation/Dynamics 365 **1.11** slice needs its separate
future written design and approval; it is not current capability. Existing
manual release-workflow cleanup
[#9](https://github.com/urruegg/frontier-envisioning/issues/9) remains separate;
this correction does not rewrite engineering governance.

The [verification record](solution-design.md#process-correction-verification-24-november-2026)
distinguishes focused checkpoints, regenerated artefacts, full local browser
results and exact-package proof. [Draft PR #65](https://github.com/urruegg/frontier-envisioning/pull/65)
binds the final full gate and server checks to the reviewed head.
Published-baseline hash/reproduction evidence does not complete human-only
[#52](https://github.com/urruegg/frontier-envisioning/issues/52) retention/merge.
Protected session routing/native controls
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) also remain
human-pending. Actual Cowork behaviour, estate/tenant prerequisites, licences,
native import, financial review, sharing and release acceptance are separate.

## 1.10.0 release preparation

The maintainer selected a normal **release build 1.10.0** in
[#43](https://github.com/urruegg/frontier-envisioning/issues/43), rather than
publishing the earlier internal candidate as a pre-release. Active guides
identify the release build; actual publication remains a human action and is
verified separately in [GitHub Releases](https://github.com/urruegg/frontier-envisioning/releases).
Build metadata is not a claim that publication, installation or deployment
has occurred. Version, runtime scope and archive provenance are unchanged.
Seven non-FinOps skills retain their GA designation; FinOps remains optional
Preview. The only product release download is the plugin ZIP, with verification
assets; the repository remains private.

The following development-candidate section and historical release tables
retain their scoped requirements and verification context.

## 1.10.0 development candidate

This section records the pre-publication development of **1.10.0**. Scope was approved on
12 November; local runtime gates were verified on 13 November 2026.
This section records requirements and scope-qualified technical evidence,
not publication, real pricing approval or actual Cowork/tenant acceptance.
The [solution design](solution-design.md#1100-development-candidate) owns the
companion architecture and verification. Historical A.12/A.13 and all
sections from the 1.9.2 heading onwards retain their original chronological
meaning; they are not new 1.10.0 evidence.

### Candidate authority and actual decisions

The [idea](ideas/2026-11-12-agent-finops-baseline.md),
[approved spec](specs/2026-11-12-agent-finops-baseline-design.md),
[plan](plans/2026-11-12-agent-finops-baseline-plan.md) and
[SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md) govern
[parent #35](https://github.com/urruegg/frontier-envisioning/issues/35) and
[decision record #36](https://github.com/urruegg/frontier-envisioning/issues/36).
The sole accountable human owner is `@urruegg`. Bounded work is D1
[#38 engine](https://github.com/urruegg/frontier-envisioning/issues/38), D2
[#37 integration](https://github.com/urruegg/frontier-envisioning/issues/37)
and D3 [#39 proof/documentation](https://github.com/urruegg/frontier-envisioning/issues/39).

The spec's [human decisions](specs/2026-11-12-agent-finops-baseline-design.md#2-human-decisions)
record the actual choices, not inferred permissions:

| Decision | Actual answer | Product boundary |
|---|---|---|
| D35-01 | `build-handover` | Financial baseline required for build handover, not draft/workshop creation. |
| D35-02 | `baseline-first` | Only the supplied brief's section 23 offline vertical slice. |
| D35-03 | `strict-priced-gate` | Every in-scope cost driver needs applicable current evidenced rates/FX; no conditional unpriced exception. |
| D35-04 | `versioned-successor` | Successor inside the existing FinOps skill; preserve legacy behaviour and explicit draft migration. |
| D35-05 | `approve-section-2` | Decimal units/blocks, meaningful scenarios, explicit denominators and evidenced CHF/EUR/USD conversion. |
| D35-06 | `approve-section-3` | Separate validation, pricing and frozen-version owner review; fail-closed sharing and visible offline authority limits. |
| D35-07 | `approve-section-4` | Existing views, safe exports, synthetic example and actual engineering/package proof for an unreleased candidate. |
| D35-08 | `approve-written-spec` | Written spec approved at [2e3c0e79](https://github.com/urruegg/frontier-envisioning/commit/2e3c0e79dc45c9ab06775def9f31cfb3bad7a8aa), before planning. |
| D35-09 | `approve-subagent-driven` | Plan/readiness approved at [efb3468](https://github.com/urruegg/frontier-envisioning/commit/efb3468dbe597ea6112b6839c7019243ab44b885); bounded subagent-driven execution selected. |
| D35-10 | `provisional-draft-figures` | Targeted draft-reporting amendment recorded at [28de255](https://github.com/urruegg/frontier-envisioning/commit/28de255404ec8cb4d88babf86299e36b2b63c9f8), before calculator code; strict financial handover unchanged. |
| D35-11 | `support-combined-source-resolution` | Support valid ontology/baseline combinations through detached namespace-aware, restriction-preserving resolution; reject ambiguous source collisions before outputs and preserve originals. |

[ADR-0028](adr/0028-versioned-agent-finops-baselines.md) remains **Proposed**
until human acceptance. These records do not establish protected labels,
assignments, milestones, formal GitHub reviews, financial authority or release
permission. Genuine material questions still require a human decision, even
with autopilot.

### Candidate requirements

Keep eight skills: seven non-FinOps GA product wrappers and optional Preview
`frontier-finops`. GA remains the maintainer's designation, not result
confidence, provider availability or publication. Core work, workshops and
drafts continue without FinOps, including on decline, with honest financial
gaps rather than zero costs or an automatic readiness pass.

**Draft figures are not the handover gate.** D35-10 permits totals/unit metrics
from known usable supplied stale/unverified rates only with the visible status
**PROVISIONAL — pricing evidence incomplete**, source/date/gap information and
distinguished verified/provisional contributions. Explicit supplied FX has the
same evidence limits. Missing quantities, rates or required FX remain unknown;
inapplicable or contradictory rates do not become valid. No invented FX or
zero-fill is allowed. Financial handover still requires a valid model, every
in-scope driver priced with applicable current evidence, matching owner review,
measurement, guardrails and audience-appropriate sharing.

The following are requirements, not an implemented-feature inventory.

| ID | Requirement | Priority | Verify |
|---|---|---|---|
| FR-0142 | Preserve independent core/ordinary value and sparse/legacy builds. Require fresh actual current-scenario Preview acknowledgement before each financial operation or figure write; reuse the full unchanged NOTICE, actual boolean API consent and current-chain-only forwarding (AFB-01). | M | T, manual behaviour |
| FR-0143 | Link profile/baseline to existing agent IDs. Record business/technical/finance owners, outcome definition, demand, scope, assumptions, exclusions, risks, confidence, measurement and guardrails; diagnose invalid IDs, schemas, numbers, dates and units explicitly. D35-11 keeps ontology-local/root source identities and restrictions explicit, resolving valid combinations on a copy and rejecting ambiguity before outputs (AFB-02). | M | T |
| FR-0144 | Use exactly low/expected/high scenarios with twelve monthly demand values each. Demand and another referenced, sourced cost/outcome uncertainty must differ and affect the model; neither final-total multipliers nor an unused driver-name whitelist suffices (AFB-03). | M | T |
| FR-0145 | Use Decimal quantities, pricing units/blocks, preserved rate precision and declared rounding. Report monthly/annual recurring, one-time/first-year and per-run/success/outcome costs with matching period/basis; zero/missing denominators are unavailable. Support CHF/EUR/USD, one reporting currency per baseline, explicit dated FX pair/method only and no mixed-currency portfolio total. Forecasts remain estimates; measured/allocated inputs retain basis/lineage (AFB-04). | M | T |
| FR-0146 | Keep missing required arithmetic inputs unavailable, never zero. Apply D35-10 only to known usable supplied prices/FX with incomplete evidence, with explicit provisional status, source/date gaps and separate verified/provisional contributions; do not imply verified prices or financial readiness (AFB-05). | M | T, evidence review |
| FR-0147 | Block financial build handover for any unresolved in-scope driver, invalid model, missing quantity, missing/stale/unverified/inapplicable rate/FX evidence or missing review/measurement/guardrail/sharing evidence. Report evidenced priced/in-scope driver counts across all applicable lines/periods, withholding private-dependent counts. Empty scope, forged status, workshop notes, decline and Preview acknowledgement cannot pass; no conditional unpriced exception (AFB-06). | M | T |
| FR-0148 | Require externally evidenced owner review with explicit decision, actor, date, evidence reference and frozen version/material hash. Keep structural validity, pricing completeness, lifecycle and dated planning readiness separate. Offline records are not authenticated financial authority, tamper-proof storage, access control, budget/purchase approval or deployment permission (AFB-07). | M | T, owner evidence |
| FR-0149 | Keep editable drafts and preserve frozen reviewed snapshots. Bind material inputs, rates, FX, scenarios, sources/privacy and results to receipts/review; material change creates a new version without inherited review. Stale sources block new handover without rewriting historical review (AFB-08). | M | T |
| FR-0150 | Preserve customer-shareable/customer-specific/internal-only/validation-required provenance and legacy internal/visibility/src/content_src ancestry. Unknown sharing fails closed; template class is not IP clearance. Project dependencies, nested notes/rates/sources/FX, aggregates, readiness and hashes before JSON/Markdown/HTML; never reconstruct private amounts, zero-fill withheld values or label a public subset the full total. Customer output is scope-specific, not public clearance (AFB-09). | M | T, projection review |
| FR-0151 | Add frontier-finops-baseline/1.0 beside unchanged frontier-finops/1.0. Explicit migration preserves originals/source restrictions and creates a draft without inherited approval or silent CHF/FX/value-NPV reinterpretation. Use separate agent_finops projection, reject ambiguous legacy/new active cost sources and never automatically copy successor amounts into the legacy value case. Provide a distinct synthetic Caldova example, not real commercial rates/approval (AFB-10). | M | T |
| FR-0152 | Reuse Canvas/Factory/Plan and FinOps views; shareable non-numeric gaps remain core-independent. Gate figures/financial exports with transient per-document HTML acknowledgement, reset on reload without persisted consent. Feedback proposes a new draft, not snapshot approval or a second financial calculator. Preserve declared build/release/operate history, accessibility/CSP and Markdown/JSON-first exports (AFB-11). | M | T, manual accessibility |
| FR-0153 | Require actual strict L1/L2, final extracted eight-skill package execution, distribution/privacy and repeat-build proof. Preserve historical/protected/profile/asset evidence and use existing version/provenance generators. Keep the standard tracked Caldova demo core-only; technical test acknowledgement is not human consent (AFB-12). | M | T, handoff review |

### Candidate acceptance targets

These rows retain the exact [AFB-01–AFB-12 criteria](specs/2026-11-12-agent-finops-baseline-design.md#9-testable-acceptance)
under new PRD identifiers. The statuses distinguish local automated evidence
from manual acceptance. Strict L1/L2 passed against `5262db5`; exact archive
execution and repeat-build bindings belong to [SPRINT-007](sprints/SPRINT-007-agent-finops-baseline.md),
not assumptions based on the version or these rows.

| ID | Spec ID | Acceptance criterion | Status |
|---|---|---|---|
| AC-045 | AFB-01 | Core/ordinary value builds and sparse/legacy blueprints work without the FinOps skill; no financial operation or figure write occurs before fresh acknowledgement. | Automated flow verified; live Cowork behaviour pending |
| AC-046 | AFB-02 | Profile and baseline refer to a real existing agent ID; unknown/duplicate IDs, unsupported schemas and invalid units/numbers/dates produce explicit diagnostics. | Locally verified — automated |
| AC-047 | AFB-03 | All three scenarios expose demand plus another differing uncertainty driver; final-total multipliers alone fail validation. | Locally verified — automated |
| AC-048 | AFB-04 | Focused known-answer calculations verify recurring, annual, one-time, first-year and unit economics, including pricing-block conversion and explicit FX. Different currencies are not silently summed. | Locally verified — automated |
| AC-049 | AFB-05 | Missing required rates/FX or unquantified lines yield unavailable full totals/dependent metrics, not zero. Known supplied stale/unverified rates may yield D35-10 provisional draft figures, with evidence gaps and distinguished contributions; never verified/financially ready claims. | Locally verified — automated |
| AC-050 | AFB-06 | Every unresolved in-scope driver blocks financial handover. Empty scope, forged status fields, local feedback and technical acknowledgement cannot pass it. | Locally verified — automated |
| AC-051 | AFB-07 | A positive, fully evidenced handover case requires matching owner review/version/hash, current source evidence, measurement, guardrails and other required fields. Planning status never grants financial or deployment authority. | Mechanical matching verified with simulated evidence; actual authority external |
| AC-052 | AFB-08 | Changing reviewed inputs/rates/FX/scenarios/privacy invalidates the old review for the new revision. Historical snapshots remain intact and stale/mismatched receipts reject. | Locally verified — automated |
| AC-053 | AFB-09 | Parent/component/nested private or unknown sharing provenance is withheld before each output format; no private total/rate/note/derived readiness leaks or zero substitutions. | Locally verified — automated |
| AC-054 | AFB-10 | The synthetic Caldova flow is runnable offline and clearly distinguished from real pricing/approval. Explicit legacy migration preserves originals/restrictions, yields a draft and leaves legacy numerical regressions unchanged. | Offline synthetic flow and legacy compatibility verified |
| AC-055 | AFB-11 | DOM/browser tests verify navigation, gaps, gated figures/exports, reload reset, feedback-not-approval, keyboard/focus access and both colour schemes under the existing CSP/offline rules. | Automated DOM/browser checks passed; manual AT pending |
| AC-056 | AFB-12 | Strict L1/L2 pass, the actual extracted eight-skill package runs the new flow, distribution/privacy checks pass and repeat builds match. Version/provenance/docs changes use existing generators, not hand-edited outputs. | Strict L1/L2 passed; exact archive evidence is recorded separately in SPRINT-007 |

### Candidate release position and remaining boundaries

The engine, records/projection/CLI, authoritative build integration and renderer
have reviewed source checkpoints in SPRINT-007. Strict local L1 passed
711 tests, 2,355 subtests, 68 self-tests and 183 DOM tests, with one expected
unreleased-version skip. Strict local L2 passed 75 browser tests.
These results bind the program source at `5262db5`; subsequent changes in this
section record evidence only. Exact archive hashes, extracted execution,
repeatability and CI results belong to SPRINT-007 and the draft PR.
No release, actual Cowork installation, real pricing verification or customer
financial approval follows from local automation.

Later work, outside this slice: the dedicated Copilot Studio/GitHub
harness/Foundry FinOps Agent blueprint factory; observed actuals,
reconciliation and recommendation closed loop; live FOCUS/Azure/M365/Agent365
connectors; authenticated approval service, database or deployed reference
implementation; purchasing, commitments, spend-limit or model changes.
No Azure deployment, HubWorks runtime loader or Entra provisioning through
the identity kit is implied. The [four dated public concept references](solution-design.md#public-grounding-for-this-candidate)
do not verify commercial prices, imports or provider/API conformance.

The full existing [Preview notice and awareness boundary](#current-boundaries-and-development-releasedecision-notes)
remain unchanged. Offline evidence and browser presentation are not access
control or financial authority. Human release, live Cowork/tenant acceptance,
external/IP clearance and protected #8/#30 decisions remain separate.

## 1.9.2 internal build candidate

**12 November 2026: 1.9.2 is an unreleased internal build candidate, not a
published release.** [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33)
directs a version-only build of merged `03e298e`
([PR #32](https://github.com/urruegg/frontier-envisioning/pull/32)).
The [idea](ideas/2026-11-12-version-1.9.2.md),
[candidate design](specs/2026-11-12-version-1.9.2-design.md),
[plan](plans/2026-11-12-version-1.9.2-plan.md) and
[SPRINT-006](sprints/SPRINT-006-version-1.9.2.md) govern preparation.

All current features and behaviour are carried forward: eight skills, seven
non-FinOps GA wrappers and bundled optional, acknowledgement-gated Preview
FinOps. Core work does not require FinOps; process/ontology remains optional
when requested. Reader guides, the core HTML/gallery and starter prompt retain
their merged scope. Fabric Preview, mapping gaps, MOS3 `devPreview` and private
sharing/IP boundaries are unchanged.

The complete 1.9.1 requirements and acceptance targets below remain applicable;
none is newly validated by the version number. Their chronological references
to “current” describe that intake, not a new 1.9.2 result. Document revision
1.4 is separate from product version. Actual build, regeneration and candidate
verification results are recorded separately in SPRINT-006.

This PRD retains release and decision authority. Candidate preparation changes
neither historical A.12/A.13 nor the design's B.9 results. The 12 November archive
date is build provenance, not a release date. Actual Cowork/Fabric/manual AT
acceptance, human release decisions and human-owned #8/#30 remain separate;
no approval, publication, deployment or external clearance is implied.

## 1.9.1 development intake

**11 November 2026 (+01:00): selective received 1.9.0 integration as 1.9.1,
unreleased; not a release.** This new block owns current development requirements,
release notes and product decisions. The following 1.7.1 block, original Part A,
A.12/A.13 and the earlier acceptance/results are preserved historical records,
not the current view/maturity inventory or new acceptance evidence. Document
revision 1.3 is independent of plugin version 1.9.1; no new product or release
approval is implied.

The real parent is [#25](https://github.com/urruegg/frontier-envisioning/issues/25),
with [#28 process](https://github.com/urruegg/frontier-envisioning/issues/28),
[#26 FinOps](https://github.com/urruegg/frontier-envisioning/issues/26) and
[#27 renderer](https://github.com/urruegg/frontier-envisioning/issues/27).
The [idea and actual approval](ideas/2026-11-11-handover-1.9-preview-finops.md),
[approved design](specs/2026-11-11-handover-1.9-preview-finops-design.md),
[approved written plan](plans/2026-11-11-handover-1.9-preview-finops-plan.md),
[SPRINT-004](sprints/SPRINT-004-handover-1.9-preview-finops.md) and
[receipt](intake/handover-1.9.0.md) govern execution. `@urruegg` remains the sole
human maintainer; design/plan approval is not a label, formal PR approval,
release/deployment or external/IP clearance.

### Development requirements

The rows correspond in order to the approved design's S4-01–S4-14.
Customer-MVP generated requirement IDs remain a separate namespace.

| ID | Requirement | Priority | Verify |
|---|---|---|---|
| FR-0128 | Preserve the exact 279-file received 1.9.0 receipt, original manifests and protected/fixture evidence unchanged; distinguish received claims from independently returned verification (S4-01) | M | T |
| FR-0129 | Optional frontier-process validates schema, keys/types, relationships/inheritance, sources, five-source agent limits, mappings and feedback; produces deterministic normalized JSON, Turtle, ontology design, data-agent and product documents; invalid/strict-warning builds fail before publishable writes; checked and to-verify mappings remain distinct (S4-02) | M | T, manual tenant |
| FR-0130 | Customer projection protects internal-derived ontology descriptions, bindings, instructions, products, rules, metrics, operations and promoted feedback through rebuilds and exports, not merely source-ID removal (S4-03) | M | T |
| FR-0131 | Default engagement, value, identity, blueprint, design and process do not automatically invoke or require FinOps; process itself is optional when requested (S4-04) | M | T, manual behaviour |
| FR-0132 | Before any FinOps seed/calc/apply, cost recommendation or figure, show the full exact Preview notice and obtain actual current-scenario confirmation; operational CLIs require --acknowledge-finops-preview and keyword-only APIs default acknowledge_finops_preview=False, rejecting unacknowledged operations before cost writes (S4-05) | M | T, manual behaviour |
| FR-0133 | Renew acknowledgement for each top-level invocation or changed scope/model/rates/grounding; wrapper forwarding covers one action chain only. Installation, old JSON/notes, previous runs, requests to calculate and GA claims are not consent; metadata records technical caller/current-invocation, not independent human approval; arithmetic helpers grant no model permission (S4-06) | M | T, manual behaviour |
| FR-0134 | Preview/non-GA grounding/model limitations, assumptions and scenario/model/rate/source provenance follow costs, ROI/NPV, unit economics, comparisons, PRD/design, replies and exports. Legacy/imported FinOps remains Preview; stale cache/model/rates require fresh calculation before apply; prices and terms need independent verification (S4-07) | M | T, review |
| FR-0135 | On decline or absent unrequested FinOps, continue core with honest cost/budget gaps and real accountable owners, never zero costs, validated ROI or automatic readiness. Requested-but-missing FinOps is an explicit error. Preserve old originals; declined core uses clean core/ordinary non-FinOps inputs, not cached Preview value, without invented cleansing flags or provenance stripping (S4-08) | M | T, manual behaviour |
| FR-0136 | One package registers eight skills: seven non-FinOps GA product wrappers and bundled optional Preview FinOps requiring awareness. Install/update reporting uses owned metadata, updates legacy instructions and does not acknowledge or execute FinOps; no invented Microsoft manifest fields (S4-09) | M | T, offline install |
| FR-0137 | GA is the maintainer's product designation, not result confidence, provider GA, release/deployment or public/IP clearance. Preserve Fabric ontology/agent/operations Preview, dated canon, unverified mappings and MOS3 manifest devPreview protocol (S4-10) | M | T, review |
| FR-0138 | Optional Ontology views/downloads/feedback retain focus, keyboard, contrast, targets, reflow and CSP. Fresh browser acknowledgement is independent of scripts, document-local, not localStorage, resets on reload and keeps the warning; flat/nested costs and linked assumptions/derived PRD figures are gated, ordinary own value remains, private components/rankings/outcomes are withheld not zero, and internal_notes must not be recovered; viewer acknowledgement is not encryption/access control (S4-11) | M | T, manual AT |
| FR-0139 | Default core and explicit acknowledged Preview demos use isolated outputs and real hashed CSP fixtures; normal demo/site does not invoke FinOps. Technical developer acknowledgement is not human pricing/budget approval (S4-12) | M | T |
| FR-0140 | Preserve original assets/profiles/hashes; use the finite verified 1.9.1 raster path and pre-write recursive privacy guard. Default complete bundle has fifteen allowlisted entries including four ontology documents, excludes explicit Preview demo/cost JSON and internal analysis/intake; measure final skill-file count and rebuild digests rather than copying stale counts (S4-13) | M | T, handoff review |
| FR-0141 | Require final strict L1/L2, bounded spec/quality and advisory review, and offline eight-skill install preparation for D5; qualify evidence by commit/scope and keep manual Cowork validators/behaviour, Fabric import/agent tests, AT certification and human distribution decisions separate (S4-14) | M | T, manual acceptance |

### Development acceptance targets

These are **Pending integrated verification**, including where bounded local
evidence already exists. Rows correspond in order to S4-01–S4-14, not to received
Passed labels or a live Cowork validation.

| ID | Acceptance criterion | Status |
|---|---|---|
| AC-031 | Exact receipt digest and unchanged original/protected evidence are checked against the frozen baseline (S4-01) | Pending integrated verification |
| AC-032 | Process schema/output/feedback tests and deterministic five-output checks pass with explicit mapping/binding gaps (S4-02) | Pending integrated verification |
| AC-033 | Internal sentinel and rebuild/export cases prove customer-safe ontology and related content projection (S4-03) | Pending integrated verification |
| AC-034 | Default orchestration and value/identity/design/process examples perform no FinOps operations (S4-04) | Pending integrated verification |
| AC-035 | Seed/calc/apply and Preview-dependent value/feedback reject missing acknowledgement before cost writes; prose shows the exact notice and real flag (S4-05) | Pending integrated verification |
| AC-036 | Fresh invocation/scenario pressure cases reject stale/JSON/global consent; wrapper forwards only within one chain and metadata never claims human approval (S4-06) | Pending integrated verification |
| AC-037 | Legacy/imported, cache-mismatch and downstream ROI/NPV/unit/assumption/PRD/export cases preserve Preview limitations and provenance (S4-07) | Pending integrated verification |
| AC-038 | Decline/absent-module cases continue clean ordinary core work, requested missing FinOps errors, and budget/readiness gaps remain assigned rather than passed (S4-08) | Pending integrated verification |
| AC-039 | Offline preparation verifies eight copy plans, seven GA and one optional acknowledged Preview, including truthful legacy-update reporting (S4-09) | Pending integrated verification |
| AC-040 | Maturity/product contracts retain Fabric Preview, to-verify mappings, dated sources, private distribution and unchanged devPreview packaging protocol (S4-10) | Pending integrated verification |
| AC-041 | Ontology route/download/feedback/focus/CSP/accessibility and document-local Preview gates pass for flat/nested and private/ordinary value cases (S4-11) | Pending integrated verification |
| AC-042 | Core and isolated explicit Preview demos/site fixtures build and run with real CSP; normal demo/site remains core-only (S4-12) | Pending integrated verification |
| AC-043 | Twice-built default artifacts, finite raster inputs, fifteen-entry bundle, exclusions, recursive privacy checks, digests and final current file count match (S4-13) | Pending integrated verification |
| AC-044 | Final strict L1/L2, advisory review and offline installer evidence are returned for the reviewed head, with manual Cowork/Fabric/AT and human decisions listed honestly (S4-14) | Pending integrated verification |

### Current boundaries and development release/decision notes

Before any cost operation or figure, show:

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

Loading to explain limitations is allowed. Actual current-scenario confirmation
is required before operations; a script flag is not an independent human
approval. Declined legacy paths preserve the original and use clean ordinary
inputs: D2 does not automatically remove old fields. Browser acknowledgement
is separate and cannot protect embedded bytes as access control.

[ADR-0026](adr/0026-process-ontology-fabric-iq.md) (optional process ontology) and
[ADR-0027](adr/0027-cdm-grounding-and-data-products.md) (CDM/data products, **not**
FinOps) remain **Proposed**. The map catalogue's eleven unverified F&O entries
and integrated model's six mappings to verify/Employee binding gap are different
scopes. Native Fabric import and tenant data-agent tests remain manual.

No 1.9.1 release, tag, deployment, actual Cowork install or external clearance
is approved here. D0–D3 returned implementation evidence is recorded in the
[current design verification](solution-design.md#191-development-intake) and
sprint. D4 prose and D5 final rebuild, integrated validation, offline install
and maintainer review remain separate. These notes deliberately sit outside
the unchanged historical A.12/A.13 records.

## 1.7.1 development intake

**Selective integration of received 1.7.0 as 1.7.1, unreleased; not a release.**
The [approved design](specs/2026-11-10-handover-1.7-intake-design.md) and
[written plan](plans/2026-11-10-handover-1.7-intake-plan.md) govern
[#22](https://github.com/urruegg/frontier-envisioning/issues/22).
[SPRINT-003](sprints/SPRINT-003-handover-1.7-intake.md) and the
[intake receipt](intake/handover-1.7.0.md) separate received claims, implementation
checkpoints and pending integrated acceptance. [ADR-0025](adr/0025-four-part-journey-structure.md)
remains Proposed; design/plan approval is not release approval.

The current scope is seventeen views in four parts: Vision (Overview, Org model,
Blueprint, Journeys, Use cases, PRD), Design (Agents, Agent identity, Target
architecture, IT readiness), Build (Roadmap, Plan, FinOps), and Workshops
(Attendees, Discovery, Risks, Evidence). Existing routes, workflow, identity,
value and accessibility behaviour must remain usable with older optional data.

The following requirement rows are selectively received product scope.
They supplement, rather than rewrite, the historical Part A records below.
Generated customer-MVP model identifiers are a separate namespace from these
plugin-product requirements.

| ID | Requirement | Priority | Verify |
|---|---|---|---|
| FR-0119 | The blueprint groups its views in four parts along the Innovation Hub journey: Vision (Overview, Org model, Blueprint, Journeys, Use cases, PRD), Design (Agents, Agent identity, Target architecture, IT readiness), Build (Roadmap, Plan, FinOps) and Workshops (Attendees, Discovery, Risks, Evidence); the rail and the breadcrumb name the part and what it is for; labels can be set per blueprint (`parts`) | M | T, D |
| FR-0120 | The PRD page shows the product requirements of the MVP agents from one model (`prd_model.py`, identical in frontier-blueprint and frontier-solution-design): problem with its provenance, vision, goals, KPIs, the business value of the use cases in scope, scope, personas, functional requirements per agent (FR ids), non-functional requirements (NFR), acceptance criteria (AC), dependencies, top risks, open decisions, release plan and Definition of Ready; it downloads as Markdown and takes a workshop verdict (`prd:scope`) | M | T |
| FR-0121 | `design/prd.md` uses the same model, so its FR, NFR and AC ids match the PRD page; authored PRD fields (problem, goals, non-goals, out of scope, exit test, release plan, status, owner) are kept on every build, the rest is recomputed | M | T |
| FR-0122 | The Plan page puts every agent on the Agent Factory board as a DevOps Kanban: swimlanes per journey (the factory included), columns per factory stage under the phases Idea, Design, Build and Deploy, work-in-progress limits, cards with the identity icon, MVP flag, autonomy, owner, the share of handover checks met and the next step; filters by journey and MVP; CSV export for Azure Boards or GitHub Projects | M | T |
| FR-0123 | The Risks page shows the risk register as a 5 × 5 heat map and a table (category, likelihood, impact, score, owner, mitigation, status) with links to journeys, use cases and agents, the open value and cost assumptions and the open decisions; a risk is rated live in the workshop and exported as `risk:<id>` | M | T |
| FR-0124 | The build derives risks from the use cases' risk points and blocked IT readiness items, adds the Innovation Hub canon risks, keeps authored risks and never duplicates a derived one; unknown categories, statuses and links warn | M | T |
| FR-0125 | The Attendees page lists every attendee with organisation, role, focus, sessions and contributions; each contribution cites its source and, from a transcript, the time in the recording; contributions without evidence are flagged; the seed fills contributions from transcript speakers | M | T |
| FR-0126 | Workshop verdicts on risks (status, likelihood, impact, note) and on the PRD scope merge into the blueprint; a rated derived risk becomes workshop-owned and survives the rebuild; unknown ids are reported | M | T |
| FR-0127 | Use-case detail pages link to their risks in the register; the Roadmap and the Agent Factory journey link to the Plan | S | T |

### Current acceptance targets

These received acceptance descriptions are **Pending** for final integrated
acceptance. Their incoming Passed labels are not adopted as historical results.

| ID | Acceptance criterion | Status |
|---|---|---|
| AC-026 | The Caldova demo lists the 17 views in the four parts; the breadcrumb names the part and its purpose | Pending |
| AC-027 | The PRD page of the Caldova demo shows the nine sections, 2 MVP agents, 35 functional and 12 non-functional requirements, the business value of the use cases in scope and the top risks; `design/prd.md` carries the same requirement ids; a verdict on the scope is saved | Pending |
| AC-028 | The Plan page shows the 29 agents in 5 swimlanes and 7 stage columns under 4 phases with work-in-progress limits; the MVP filter leaves the 2 MVP agents; a card opens the agent | Pending |
| AC-029 | The Risks page shows 15 risks (2 high, 9 medium, 4 low) on the heat map and in the register; a changed rating moves the score live and is saved; risk and PRD verdicts merge and survive the rebuild without duplicates | Pending |
| AC-030 | The Attendees page lists the 8 attendees with 13 of 13 contributions backed by evidence and the time in the recording where it comes from a transcript | Pending |

### Integration and distribution constraints

- The shared Python PRD model copies must remain identical. Requirement IDs use
  the complete blueprint's canonical agent order; selecting an MVP subset must
  not renumber surviving requirements. Authored fields survive rederivation.
- Normalised risk source bindings and retired-ID history must be retained with
  the workshop record. Edited or reordered source points must not silently
  inherit another risk's verdict. Discarding that history cannot guarantee the
  identity of old ID-only feedback. Ratings must be finite integers from 1 to 5,
  excluding booleans; unknown or invalid feedback is reported.
- Browser notes are local until exported and merged. PRD Markdown and risk/PRD
  feedback downloads must reflect the displayed scope. Plan CSV is a handover
  format, not live integration or native import compatibility certification.
  WIP, computed readiness, owner/status metadata and workshop verdicts grant no
  execution or distribution permission.
- Customer generation must resolve risk content provenance before scrubbing,
  then derive final risks and PRD from scrubbed sources. Internal-derived
  attendee contributions, risk content and cached PRD text must not survive in
  embedded JSON or downloads merely because an internal source ID was removed.
- Preserve the 1.6.1/A6 privacy and accessibility corrections, original icon
  artwork, copyright and historical release/raster evidence. The approved host
  is the private `urruegg/frontier-envisioning` repository. Complete-bundle
  distribution excludes internal analyses and intake records and retains
  pre-write privacy checks. A customer export is not external/IP approval.

## Product context and provenance

Original combined title: **Innovation Hub Frontier Solution Envisioning —
Cowork plugin**, with **Product Requirements and Solution Design**.
The following table preserves that source context, owner attribution and
deliverable inventory. Its version and date describe the original product
document, not this document revision. Author credit is not owner or approver
authority.

| Field | Value |
|---|---|
| Product | Frontier Envisioning plugin for Microsoft Copilot Cowork (`frontier-envisioning`) |
| Document | PRD (Part A) and Solution Design (Part B) |
| Version | 1.6.1 development patch — released baseline 1.6.0 |
| Date | 9 November 2026 |
| Owner | Urs Rüegg, Sr Solution Engineer, Microsoft Innovation Hub Switzerland |
| Proposed reviewers | Innovation Hub leadership; Innovation Hub solution engineers; one account team piloting the plugin |
| License | MIT (`MIT.md`) · Copyright (c) 2026 Urs Rüegg · SPDX headers in every script; `license: MIT` in every skill |
| Basis | Procurement four-journeys blueprint mockup (solution-envisioning sample, October 2026); `urruegg/caldova-hr-frontier` (architecture-design sample, v1.5); Journai showcase: HAIRO model (hub.journai.ch) and "How we built our hybrid organisation" (architecture.journai.ch); Microsoft Frontier guidance (sources in [B.14](solution-design.md#b14-sources)); an Innovation Hub HR agent identity package (October 2026, generalised and anonymised) for the agent identity kit; Innovation Hub HR and procurement workshop materials (November 2026: Agent Factory, landing zone, architecture decisions, IT preparation and readiness); an Innovation Hub showcase of the digital feedback loop with Microsoft IQ (November 2026, pattern only); Copilot Studio workflow designer and its Microsoft Learn documentation (November 2026: node and trigger types, the GitHub Copilot harness) |
| Deliverables | This document · README.md (setup guide) · generic Frontier Company Blueprint HTML template with the Caldova demo, the digital feedback loop on the Overview, the agent workflows, its Agent identity page, business value and FinOps page · install package `frontier-envisioning-plugin-1.6.0.zip` · repository starting point `frontier-envisioning-github-repo-1.6.0.zip` · Caldova agent identity package (demo) · Frontier visualisation and reuse evaluation (separate document) |

---

## 1.6.1 patch: workflow legend accessibility

The agent list must remain sticky while its upper summary is visible, but must
not cover the full-width workflow below. At desktop and responsive widths,
scrolled legend controls must receive pointer and keyboard input without
changing the selected agent. Agent switching, workflow properties and the
fourteen existing views remain functional. Acceptance includes DOM containment
and real-browser overlap/hit-testing at 1440px and 1024px.

This is an unreleased correction to the 1.6.0 source baseline. Historical release
records remain immutable; publishing and tenant acceptance are separate human
steps.

### Measured accessibility delivery (#7, 2026-11-10)

This subsection preserves the initial A5 checkpoint before the targeted
catalogue correction. Its failed measurements are historical evidence, not
the current gate result; see the verification handoff's A6 results below.

The development patch also implements modal focus containment and return,
labelled roving tabs, pressed-state filters, interactive SVG grouping,
rendered text contrast, selected 24 CSS pixel targets and scoped 320px reflow.
Brand data and Microsoft icon artwork remain unchanged. NFR-0012 states the
target; it is not a conformance claim or a revision of 1.6.0 acceptance.

The identity catalogue still fails applicable AA text contrast: Later wave
4.40:1 and the Finance header 4.33:1, in both colour schemes. Full L2 remains
red. Remediation requires a separate human scope decision for the excluded
identity generator and guarded outputs; no gate waiver is approved.
Manual assistive-technology acceptance remains under
[#8](https://github.com/urruegg/frontier-envisioning/issues/8).
See the [verification handoff](intake/2026-11-10-accessibility-verification.md)
for implementation evidence and limits. A4/A5 acceptance is incomplete.

## Part A — Product Requirements

## A.1 Problem

Every Innovation Hub envisioning today is hand-built. The procurement sample is a bespoke HTML mockup of about 280 KB, more than half of it customer-specific data written by hand: four journeys, agents, discovery questions, workshop outcomes, PRD and next steps. The HR sample is a bespoke design repository with a PRD, a solution design, ADRs and a use-case portfolio. Both are excellent, and both started from a blank page.

Five things make that expensive and fragile:

1. **Context is scattered.** What the account team and the customer already said sits in meetings, transcripts, mail threads, Teams chats, account plans and decks. Collecting it is manual, and hypotheses lose the link to the evidence behind them.
2. **The method lives in people's heads.** The HAIRO organisation model, the agentic trigger canvas, the seven declarations, the Frontier phases and the target-architecture layers are applied differently from one engagement to the next.
3. **The workshop is captured outside the artefact.** Verdicts and answers end up in notes and have to be retyped into the next version.
4. **Envisioning and architecture design are disconnected.** The PRD and the solution design restart from scratch after the workshop.
5. **Agents get their identity by accident.** When the first agents are built, names, icons and colours are chosen per maker and per environment; "… DEV" ends up in solution names, test agents look like production agents, and nobody owns the convention.

## A.2 Vision

> Every Innovation Hub envisioning starts from the customer's own evidence and ends with a validated Frontier blueprint and a buildable design — in days, not weeks.

The plugin makes the Hub's method repeatable in Copilot Cowork: a solution engineer names the customer; Cowork gathers the context with Work IQ and the workshop transcripts, drafts the hypothesis hybrid organisation as an interactive blueprint, captures the workshop inside it, and produces the PRD and the solution design for the MVP agents, grounded in Microsoft's Frontier architecture guidance. When the agents are about to be built, every agent receives a brand identity - names per environment, colours from the customer's brand, icons in the Microsoft 365 sizes - generated from one config and checked in the customer's pipeline.

## A.3 Goals, non-goals and success measures

**Goals**

| # | Goal |
|---|---|
| G1 | Produce an evidenced, presentable Frontier Company Blueprint for any customer and scope (company or function) from one generic template |
| G2 | Make every customer statement traceable to its source, and keep Microsoft-internal material out of customer versions |
| G3 | Capture the workshop inside the blueprint and merge it into the next version without retyping |
| G4 | Carry the validated blueprint into a PRD, a solution design and ADRs that follow the Hub's design rules |
| G5 | Ground the target architecture in current Microsoft guidance, with dated availability |

**Non-goals (1.0)** — building agents in Copilot Studio; licensing or pricing calculations; updating CRM; sending anything to customers automatically; real-time co-editing of the blueprint by several people; languages other than English in the template; slide export.

**Success measures**

| Measure | Target | Baseline |
|---|---|---|
| Solution-engineer effort to a first blueprint after access to the evidence | ≤ 1 working day | To measure on the next two hand-built engagements |
| Customer statements in the blueprint that cite a source | ≥ 70 % of non-hypothesis items | Not tracked today |
| Workshops whose feedback is exported and merged | ≥ 90 % | Not tracked today |
| PRD and solution design draft available after the workshop | ≤ 5 working days | To measure |
| Internal evidence found in customer versions | 0 | — |
| Skill quality score (plugin validator) | ≥ 80 for every skill, no unresolved routing conflict | 96–100 at release ([B.9](solution-design.md#b9-quality-and-testing)) |

## A.4 Users

| Persona | Role in the engagement | What the plugin gives them |
|---|---|---|
| Innovation Hub solution engineer (primary) | Prepares, facilitates, designs | Context pack, blueprint, live capture, PRD and design |
| Account team (account executive, CSA, specialist) | Access, sponsor alignment, internal context | Evidence log; an internal blueprint that shows their context without leaking it |
| Customer sponsor | Confirms mission, priorities, MVPs | A customer-ready blueprint of their own organisation |
| Customer process owners | Validate journeys; become agent bosses | Journeys, role profiles, canvases to correct |
| Customer IT and security | Architecture, identity, data access | Target architecture, open decisions, ADRs |
| Hub lead | Quality and reuse across engagements | Consistent method, artefacts and canon |

## A.5 User journeys of the plugin

| Journey | When | Steps | Skill |
|---|---|---|---|
| J1 Prepare | Workshop minus 10 to minus 2 days | Frame scope → gather context → seed and write the hypothesis → build internal and customer versions → agenda and key questions | frontier-envisioning, frontier-context-discovery, frontier-blueprint |
| J2 Run the workshop | Workshop day | Present the views; validate agents and use cases; answer discovery questions; export the feedback | (the HTML, offline) |
| J3 Consolidate | Plus 1 day | Parse the workshop transcript → merge feedback → update the hypothesis → validated v1.0 → summary | frontier-context-discovery, frontier-blueprint |
| J4 Design | Plus 5 days | Scaffold PRD, solution design and ADRs → complete from evidence → verify availability | frontier-solution-design |
| J5 Continue | Any time | "What is next in the Caldova envisioning?" → phase detection from the engagement folder | frontier-envisioning |

## A.6 Scope

**In scope (1.0)**: four skills; the generic blueprint template; scripts for transcript parsing, context-pack validation, blueprint seed/build/merge and design scaffolding; the Innovation Hub canon (defaults and reference architecture); examples; self-test; MOS3 and personal packages.

**In scope (1.1.0)**: a fifth skill, `frontier-agent-identity`: naming rule, brand palette from the customer's Office theme, icon and card rendering without internet access, validation, stamping into Copilot Studio solutions, pipeline templates, the Caldova identity demo and agent identity in the blueprint.

**In scope (1.2.0)**: the Agent identity page in the blueprint (below Agents), identity names and icons wherever agents appear, and the blueprint and identity kit built in one step (`build_with_identity.py`), with workshop feedback on the identity kept for the review.

**In scope (1.3.0)**: two skills, `frontier-value-case` (value tree, assumption register, NPV, ROI, payback, break-even, sensitivity, workshop merge) and `frontier-finops` (cost per agent in CHF, purchase options, credit-cost scenarios, guardrails, rates file); the blueprint's FinOps page; business value in the use cases and the matrix with the assumptions to clarify in the workshop.

**In scope (1.4.0)**: the blueprint restructured along the Innovation Hub journey (Part 1 Vision, Part 2 Design, Workshop; 14 views); the Agent Factory as a canon journey with DevSecOps; the Attendees page; the landing zone (CAF, WAF, Responsible AI) and architecture decision records in the target architecture; use cases in the Hub business-envisioning template; the IT readiness page; Microsoft product icons; the matching scripts (canon, `--canon`, readiness and ADR merge, design scaffold, identity seed).

**In scope (1.5.0)**: Microsoft's digital feedback loop on the Overview: an animated diagram of the customer's four areas (Engage customers, Optimize operations, Empower employees, Transform products) around Microsoft IQ (Work IQ, Fabric IQ, Foundry IQ, Web IQ), with signals, actions with human approval and measured outcomes per area; its canon (official names and Microsoft sources), derivation from the journeys, build checks, workshop verdicts and discovery questions.

**In scope (1.6.0)**: each agent's workflow on the Agents view, drawn like the Copilot Studio workflow designer (powered by the GitHub Copilot harness): the trigger, the designer's nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent), branches and the desired outcome; derived from the canvas plan until authored (`canvas.workflow`); build checks; each MVP workflow in the solution design.

**Out of scope (1.0)**: see non-goals in A.3; anything requiring access to other people's mailboxes; any automatic sharing outside Microsoft.

## A.7 Functional requirements

Priority: **M** must, **S** should, **C** could. Verified by: **T** automated test (`tools/selftest.py`), **V** validator, **R** review, **D** demonstration.

### Discovery (frontier-context-discovery)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0001 | Find the customer's meetings in a computed window (default 90 days back to the workshop date) from the user's calendar | M | D |
| FR-0002 | Retrieve the transcript of each meeting through its join URL; treat 403/404 as final and record "no transcript" | M | D |
| FR-0003 | Parse transcripts (.vtt, text, .docx, saved JSON) into speaker turns with timestamps and envisioning signals (pain, metric, system, goal, decision, action, risk, idea, stakeholder) in English and German | M | T |
| FR-0004 | Search mail, Teams chats and files for the customer with Work IQ, and public sources on the web; read relevant documents | M | D |
| FR-0005 | Write a context pack in which every fact cites at least one registered source, with timestamp and short quote for transcripts | M | T |
| FR-0006 | Tag every source `internal` or `customer`; render an evidence log for either audience | M | T |
| FR-0007 | Report coverage gaps (journeys without pain or numbers, no systems, no stakeholders, no constraints, no transcript) | M | T |
| FR-0008 | Loop over many meetings or files in one tool script and return a compact table | S | R |

### Blueprint (frontier-blueprint)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0010 | Seed a blueprint from the context pack without inventing content; list every gap in `_todo` | M | T |
| FR-0011 | Render one self-contained HTML file from a JSON blueprint and a generic template | M | T, V |
| FR-0012 | Overview: mission, Frontier phase ladder (today and target), automation level, outcomes, journeys, reading legend | M | D |
| FR-0013 | Org model in the HAIRO style: human leaders in the centre, lead agents in the inner ring, specialist agents in the outer ring, journeys as arcs; step-by-step reveal; filter by journey; autonomy badges; MVP halo; planned positions dashed | M | D |
| FR-0014 | Role card and nine-section role profile for every agent, derived from data where the profile is not written | M | D |
| FR-0015 | Blueprint view per journey: outcomes, hybrid workforce (human-led and agent-operated), approval seam, governance → Intelligence Resources → security and trust, knowledge, channels, build and run, foundation | M | D |
| FR-0016 | Journey view: stages (happens, pain, with agents, owning agent), personas, KPIs with evidence | M | D |
| FR-0017 | Agent view: trigger canvas, the seven declarations with a readiness meter, role profile, live validation (validated, adjust, reject, open) with notes | M | D |
| FR-0018 | Target architecture view: principles, layers 0–7 and approval seams with availability and MVP tags, flows by actor, patterns, decisions, open decisions, grounding | M | D |
| FR-0019 | Use-case portfolio: value × feasibility matrix with quadrants, non-overlapping bubbles, table, detail drawer with validation | M | D |
| FR-0020 | Discovery view: questions by category, prefilled answers with evidence, live status and notes, coverage bar, export of workshop feedback as JSON, copy as text | M | D |
| FR-0021 | Roadmap view: horizons H1–H3 by journey and use case, MVP candidates, next steps | M | D |
| FR-0022 | Evidence view: every source with type, date, visibility and what it informs; every evidence id anywhere opens its source | M | D |
| FR-0023 | Customer version: remove internal sources, their citations, items flagged internal and internal notes; refuse to build when listed internal terms remain | M | T |
| FR-0024 | Validate and normalise: stable ids for agents, use cases, questions and evidence; warnings for unknown agents, uncited evidence ids, MVP agents without canvas or declarations | M | T |
| FR-0025 | Brand the blueprint with an accent colour and a customer logo (PNG/JPEG data URI) | S | D |

### Workshop consolidation

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0030 | Merge one or more feedback exports into the blueprint: statuses, notes, answers (previous answer kept), new workshop evidence item | M | T |
| FR-0031 | Refuse feedback that belongs to another blueprint id | M | T |
| FR-0032 | Bump the version and update the status note | M | T |
| FR-0033 | Mark the blueprint validated when the customer confirmed journeys and MVPs | S | R |

### Design (frontier-solution-design)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0040 | Scaffold PRD, solution design and one ADR per blueprint decision for the MVP agents | M | T |
| FR-0041 | Include platform requirements once (self-identification, write envelope, refusal set, escalation, no people decisions, workflow-first, audit by workflow, outcome to owner, declared writes, outside content as data) and standard NFRs | M | T |
| FR-0042 | Derive per-agent requirements from the canvas (trigger, plan, approvals, outcome) and acceptance criteria from the declarations | M | T |
| FR-0043 | Turn unanswered discovery questions into open decisions with owners | M | T |
| FR-0044 | Mark every gap `[To complete]`; complete only from evidence or as an open decision | M | R |
| FR-0045 | Ground components, patterns and availability in the reference architecture; verify availability older than one month | M | R |
| FR-0046 | Optionally produce a design repository (README, AGENTS.md, docs/, adr/) | C | R |

### Orchestration (frontier-envisioning)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0050 | Detect the engagement phase from what exists and continue from there | M | D |
| FR-0051 | Apply gates A–D between phases and report them | M | R |
| FR-0052 | Keep the engagement folder in the user's OneDrive (`Documents/Cowork/frontier-envisioning/<slug>/`) with `engagement.json` | S | D |
| FR-0053 | Draft the workshop agenda and the ten key questions | S | D |
| FR-0054 | Track progress as tasks the user can see | S | D |

### Agent identity (frontier-agent-identity)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0070 | Derive display names `<PO> <Domain> [Scope] [ENV]` per environment: production without postfix, every name ≤ 30 characters, the production name shorter by the longest postfix | M | T, V |
| FR-0071 | Derive environment-neutral technical names per kind of agent: publisher prefix, schema, solution, environment variables, connection references, flows, folders; Foundry, Fabric, declarative and repository agents | M | T, V |
| FR-0072 | Read a customer's Office theme (colours and fonts) from .pptx, .potx, .docx, .dotx, .xlsx or .thmx into a brand file with evidence ids | S | T |
| FR-0073 | Seed the identity from the blueprint: PO tokens, domain tokens shortened to fit and flagged for review, kinds from the technology, glyph suggestions, MVP and status labels, descriptions within the limits, a seed report | M | T |
| FR-0074 | Map each journey to the nearest brand colour with glyph contrast ≥ 4.5:1 (dark glyph or accessible shade otherwise); choose environment bands from the brand with label contrast ≥ 4.5:1 | M | T, V |
| FR-0075 | Render icons without a browser or image library: colour 192 × 192 and 32 × 32 per environment, outline 32 × 32, SVG sources; identical pixels on every machine | M | T |
| FR-0076 | Generate identity cards, the agent family, the MVP identity sheet, the colour schema (SVG; PNG when a converter exists) and an HTML catalogue | S | D |
| FR-0077 | Generate the kit's documents (naming convention, colour schema, icons, harness integration, catalogue, evidence), README, changelog, notices and GitHub Copilot instructions from the config | M | T |
| FR-0078 | Validate the kit (names, technical names, uniqueness, prefix, descriptions, contrast, files) and fail pull requests on errors | M | T |
| FR-0079 | Stamp names and icons per environment into an unpacked Copilot Studio solution before packing; dry run by default; strict mode for release pipelines | M | T |
| FR-0080 | Ship Azure Pipelines and GitHub Actions templates and unit tests that build a synthetic solution | S | T |
| FR-0081 | Write the identity into the blueprint; the blueprint shows icons and display names in the journey view, the agent canvas and the role card | S | T |
| FR-0082 | Build the Caldova identity kit demo on request | S | D |
| FR-0083 | Show an Agent identity page below Agents: naming rule, journey colours, environment bands, agent family, MVP identity sheet, all names per environment with a length check, decisions, Microsoft guidance and a workshop validation box | M | T |
| FR-0084 | Use the identity display name and icon wherever an agent appears (agent list and canvas with an identity panel, role card, journeys, org model, use cases, roadmap MVP cards, blueprint view); keep the working name visible | M | T |
| FR-0085 | Build the blueprint and the identity kit in one step: seed the identity proposal (customer Office theme when given), build and validate the kit, write the identity into the blueprint and render the HTML; if the kit fails, build the blueprint alone and say why | M | T |
| FR-0086 | Keep workshop feedback from the Agent identity page in the blueprint (`identity_feedback`) for the identity review | S | T |
| FR-0087 | Value tree per use case with drivers (efficiency, quality, revenue, strategic) and categories (cash, capacity, risk, revenue); each benefit counted once | M | T |
| FR-0088 | Assumption register: statement, unit, low, base, high, source type, confidence, evidence ids, owner, question, status; empty values listed as inputs to collect, never invented | M | T |
| FR-0089 | Calculate budget and economic views, risk separately, NPV, ROI, payback, break-even, sensitivity (top ten assumptions as workshop questions) and ranges | M | T |
| FR-0090 | Cost per agent and month in CHF: credits by event with licence coverage, licences, Azure, people, build; unit economics | M | T |
| FR-0091 | Compare pay-as-you-go, capacity packs, Copilot Credit P3 and Agent P3; credit-cost scenarios; guardrails with owners; tags from the agent identity | M | T |
| FR-0092 | Versioned rates file with source and date per rate; flag rates older than 90 days | M | T |
| FR-0093 | Blueprint: FinOps page; business value in the use cases and the matrix; live confirm, adjust or reject of assumptions with the agreed value, exported with the workshop notes | M | T |
| FR-0094 | Merge assumption verdicts into the value case and the FinOps model with a change log and a version bump | M | T |
| FR-0095 | Reproduce the method's worked example exactly (golden test) | M | T |

### Distribution and installation

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0060 | Install from a Cowork chat: the user attaches the package and says "Install the Frontier PlugIn"; Cowork checks the package and copies the seven skills into the user's skills folder after one approval | M | T, D |
| FR-0061 | Refuse a damaged or altered package: checksum per file, skill names, unexpected files | M | T |
| FR-0062 | Report per skill whether the install is new, an update or a reinstall, from the installed version | S | T |
| FR-0063 | One package serves both the chat install and the organisation catalogue (Microsoft 365 app package) | M | V |
| FR-0064 | Build the Caldova demo blueprint on request, without customer data | S | D |
| FR-0065 | A README setup guide in the package: steps for people and exact steps for Copilot Cowork | M | R |

### Innovation Hub journey (1.4.0)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0096 | The blueprint follows the Innovation Hub journey: Part 1 Vision (Overview, Org model, Blueprint, Journeys, Attendees), Part 2 Design (Agents, Agent identity, Target architecture, Use cases, IT readiness, FinOps), Workshop (Discovery, Roadmap, Evidence) | M | T, D |
| FR-0097 | Attendees page: people by organisation with role, place, focus and contributions; focus links open the journey or use case | M | D |
| FR-0098 | Agent Factory journey from the canon: lifecycle hypothesis → validated → designed → ready for build → build → release → operate; board computed from eight handover checks (Definition of Ready); build steps with tools, Superpowers and CAT skills; evaluation pyramid; controls, roles, phases, resources | M | T, D |
| FR-0099 | Landing zone tab: CAF design areas with product icons, WAF, CAF and Responsible AI lenses, one agent landing zone per journey with DEV, TEST and PROD stage, data classes, MVP marker and identity icons; a click opens the area's detail | M | D |
| FR-0100 | Decisions tab: ADR cards with canon flag, status filter and a live workshop verdict exported as `adr:<id>` and merged into the decision | M | T |
| FR-0101 | Use-case detail page in the Hub template (General with the problem statement and its provenance, Value, Feasibility), deep link `#/usecases/<id>` | M | D |
| FR-0102 | IT readiness page: preparation items, readiness checks, workstation, questions, decisions, environments, timeline; live status exported as `ready:<id>` and merged | M | T |
| FR-0103 | Microsoft product icons embedded only when used, with their notice; `--no-product-icons` leaves them out | M | T |
| FR-0104 | Canon added without overwriting (a canon ADR is skipped when its title exists); `build_blueprint.py --canon` upgrades an earlier blueprint | M | T |
| FR-0105 | The design scaffold adds the landing zone, the Agent Factory lifecycle, Definition of Ready and evaluation pyramid, the ADR origin and `it-readiness.md` | M | T |
| FR-0106 | The identity seed treats Agent Factory agents as repository agents with the process-owner token "Factory" | S | T |

### Digital feedback loop (1.5.0)

| ID | Requirement | Pri | Verified |
|---|---|---|---|
| FR-0107 | The Overview shows Microsoft's digital feedback loop as an animated diagram: the four areas (Engage customers, Optimize operations, Empower employees, Transform products) around Microsoft IQ with Work IQ, Fabric IQ, Foundry IQ and Web IQ; signals travel to Microsoft IQ, a proposed action waits at a human-approval gate, the measured outcome returns as the next signal | M | T, D |
| FR-0108 | Selecting an area shows its signals with their Microsoft IQ layer, its actions with the agents and who approves, its outcomes with the journey KPIs (baseline → target) and the value hypotheses, the linked journeys and use cases, a workshop question and a live verdict exported as `loop:<area>` and merged | M | T |
| FR-0109 | The canon derives the loop from the journeys (area by keyword, signals from the systems with their Microsoft IQ layer, actions from the agents and the approval seam, outcomes from the KPIs, MVP use cases); every build completes a linked area without overwriting | M | T |
| FR-0110 | Only official Microsoft names: the build warns about any other "… IQ" name, an unknown layer, area or journey; the canon carries the Microsoft sources | M | T |
| FR-0111 | The animation can be paused, stops when the device asks for reduced motion and is hidden in print; diagram and panel carry the same content as text | M | T, D |
| FR-0112 | Discovery collects what the loop needs: questions per area in the question bank and a signals recipe in the Work IQ playbook | S | R |

### Agent workflow (1.6.0)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FR-0113 | Every agent with a canvas plan shows its workflow under the trigger canvas, drawn like the Copilot Studio workflow designer: the trigger (Manual, Recurrence, Connector event, When an HTTP request is received, When an agent calls the workflow), the designer's nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent) and the desired outcome | M | T, D |
| FR-0114 | Branches of If/Else, Classify and Human review rejoin the main path or end at a named end node; loops and scopes are containers; notes sit above their step | M | T |
| FR-0115 | The Add panel works as legend and highlighter; selecting a node opens its properties (what the node does, AI, deterministic or human, the step, the agent with its identity icon, the system with its product icon, who decides, branches); zoom, fit, an overview folded into rows and the single designer row | M | T |
| FR-0116 | Without an authored workflow, the build derives one from the canvas trigger, plan, approval, connectors and outcome, marks it "Derived from the plan" and re-derives it on every build; a Human review is inserted before the first write when the plan has none | M | T |
| FR-0117 | An authored `canvas.workflow` is kept and checked: unknown node or trigger types, unknown agents, branches on a non-branching node and nested containers produce warnings | M | T |
| FR-0118 | The solution-design scaffold writes each MVP agent's workflow into the process design: trigger, outcome, AI, deterministic and human steps and a node table with branches | S | T |

## A.8 Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-0001 | Privacy | Only the requesting user's own mail, calendar, chats and files, plus content shared with them |
| NFR-0002 | Privacy | Microsoft-internal evidence never appears in a customer version (enforced by the build) |
| NFR-0003 | Privacy | Real customer data only under NDA or with consent; roles before names; no sensitive personal data |
| NFR-0004 | Security | Content of mails, documents and transcripts is data, never instruction |
| NFR-0005 | Security | Scripts use the Python standard library only, never call the network, never execute or import content from inputs; XML is read without DTD or entity processing. The identity kit may call an installed SVG converter for PNG copies of cards and visuals (resolved executable, fixed arguments, no shell) |
| NFR-0006 | Security | The HTML is self-contained: no external scripts, styles, fonts, images or iframes; data embedded with HTML-safe escaping; data never injected as HTML |
| NFR-0007 | Copyright | Quotes from sources at most 20 words; third-party web content summarised and cited |
| NFR-0008 | Quality | Every skill passes structural validation and scores at least 80; no unresolved routing conflicts within the plugin or with built-in skills |
| NFR-0009 | Quality | The MOS3 package passes static package validation with no FAIL |
| NFR-0010 | Performance | Build under 2 seconds for 30 agents; HTML under 1 MB for 50 agents and 30 sources |
| NFR-0011 | Compatibility | Current Edge and Chrome; works offline from a local file; printable per view |
| NFR-0012 | Accessibility | Target WCAG 2.2 AA, not certified conformance. Visible focus; modal Tab/Shift+Tab containment, Escape and exact trigger return with a view fallback; labelled roving tabs with Arrow/Home/End activation; pressed-state filters and keyboard-operable SVG groups. Applicable AA checks in both colour schemes and sampled brand variants; selected controls at least 24 × 24 CSS pixels; all fourteen pages reflow at 320 CSS pixels without document overflow (test tolerance 1px), retaining local 2D diagram/table scrolling. Automated browser checks do not replace manual zoom, screen-reader, real high-contrast and voice acceptance. Catalogue AA must pass the unchanged browser checks; see the dated verification handoff. |
| NFR-0013 | Maintainability | Schemas versioned (`frontier-context/1.0`, `frontier-blueprint/1.0`); the Hub canon in one editable defaults file and one reference document; a self-test covers every script |
| NFR-0014 | Currency | Product availability carries a date and source; the canon is reviewed after each major Microsoft announcement event |
| NFR-0015 | Determinism | The identity kit renders the same icon pixels on every machine; its unit tests fail when committed icons drift from the config |
| NFR-0016 | Brand integrity | Every brand colour in a kit has a source; logos only where the customer's brand rules allow it; icon contrast ≥ 4.5:1 |
| NFR-0017 | Motion | Animations can be paused, stop under `prefers-reduced-motion`, never run in print and never carry information that is not also shown as text |
| NFR-0018 | Terminology | Microsoft capabilities appear only under their official names (Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ, Web IQ; product names as on Microsoft Learn), each with a dated source in the canon |
| NFR-0019 | Fidelity | The workflow view uses the node and trigger names of the Copilot Studio workflow designer as documented on Microsoft Learn; AI steps are marked as variable; node glyphs are the plugin's own drawings and Microsoft product icons come only from the icon assets with their notice |

## A.9 Acceptance criteria (release 1.6.0)

| ID | Criterion | Result |
|---|---|---|
| AC-001 | `tools/selftest.py` passes all 34 checks | Passed |
| AC-002 | The Caldova example builds with no errors and renders all fourteen views without script errors | Passed (headless DOM test of every view, drawer and journey tab) |
| AC-003 | The template and a built blueprint pass the HTML validator with no errors or warnings | Passed |
| AC-004 | The customer build removes the two internal Caldova sources and every citation of them | Passed |
| AC-005 | Every skill validates and scores ≥ 80; the conflict scan reports no unresolved conflict | Passed (96–100; 21 internal pairs and 1 built-in pair resolved by delegation) |
| AC-006 | The security scan passes with no findings | Passed |
| AC-007 | The install package passes static Microsoft 365 package validation | Passed (one expected warning: builder metadata, see TD-04) |
| AC-008 | The install check passes on the released package and refuses an altered copy | Passed (build → extract → check → alter → check) |
| AC-009 | The Caldova identity kit builds for 33 agents with the validator at 0 errors and all kit unit tests passing | Passed |
| AC-010 | Icons from the built-in renderer match a reference SVG renderer | Passed (mean absolute difference below 0.02 of 255 per channel at 192 × 192) |
| AC-011 | A blueprint with identity renders every view without script errors and shows the icons in the journey, agent and role-card views | Passed (headless DOM test) |
| AC-012 | The Agent identity page renders for the Caldova demo, a seeded proposal, the customer version and a 1.1.0 blueprint without the page data; a blueprint without identity hides the page | Passed (headless DOM test) |
| AC-013 | One build produces the blueprint HTML and a validated identity kit, both seeded without a brand file and from the reviewed Caldova config | Passed (self-test and demo build) |
| AC-014 | The scripts reproduce the worked example of the value and FinOps method (credits, purchase options, scenarios, NPV, ROI, payback, break-even) | Passed (self-test) |
| AC-015 | The Caldova blueprint shows the FinOps page and business value in the use cases and the matrix; an assumption verdict is saved and exported | Passed (headless DOM test) |
| AC-016 | The Caldova demo shows the Attendees page, the Agent Factory (lifecycle, board, handover, steps, roles), the landing zone, the ADRs, a use-case detail page and the IT readiness page without script errors | Passed (headless DOM test) |
| AC-017 | The landing-zone diagram lays out the journeys without overlapping or clipped titles | Passed (diagram rendered to an image and reviewed; Caldova, four business journeys and the factory) |
| AC-018 | Workshop verdicts on readiness items and ADRs merge into the blueprint; unknown ids are reported, never invented | Passed (self-test) |
| AC-019 | A blueprint from release 1.3 built with `--canon` gains the factory journey, landing zone, canon ADRs and IT readiness | Passed (self-test) |
| AC-020 | The Overview of the Caldova demo shows the digital feedback loop: four areas, the four Microsoft IQ layers, sixteen animated movements, the panel follows the selected area, the animation pauses and a verdict is saved | Passed (headless DOM test) |
| AC-021 | A blueprint with an unofficial "… IQ" name, an unknown layer or an unknown area builds with a warning for each | Passed (unit test and self-test) |
| AC-022 | The Caldova demo shows the two MVP workflows: the trigger first and the outcome last, nodes in flow order for the keyboard, branch pills, the end node, notes, the agent identity icon; properties open with a click or Enter and close with Escape or the close button; Add highlights a node type; zoom and the designer row work; an agent without a plan says so | Passed (headless DOM test) |
| AC-023 | A missing workflow is derived from the plan (trigger type, node types, Classify categories, a Human review before the first write); unknown node types and agents warn; derived workflows follow a changed plan | Passed (unit tests and self-test) |
| AC-024 | The solution design lists each MVP workflow with its trigger, outcome, step counts and node table | Passed (unit test and self-test) |
| AC-025 | The workflow overview of the Caldova MVP agents fits the page width (at most 1,018 pixels at 100 %) without overlapping nodes, and the designer row keeps the branches on lanes below | Passed (diagrams rendered to images and reviewed) |

## A.10 Dependencies and assumptions

| Dependency | If missing |
|---|---|
| Copilot Cowork with Microsoft 365 tools: calendar, transcripts, Microsoft 365 search, Teams, OneDrive | Discovery falls back to attached files and public sources, flagged |
| Meeting transcription enabled for customer meetings, with participants informed | Discovery uses chats and notes; transcript-based evidence is missing |
| The user can share real data only under NDA | The blueprint stays a hypothesis on public and internal context |
| Python sandbox in Cowork for the scripts | The skills cannot build; nothing is published |
| A modern browser to present | The OneDrive web preview shows the file as text; open locally |
| The user's approval to write to their skills folder (`Documents/Cowork/skills`) | Nothing is installed; the five folders can also be copied there by hand |
| Customer brand sources (brand guide, customer-authored Office file, website) | The identity kit uses the blueprint colours and flags them (decision N-5) |
| An SVG converter (cairosvg, rsvg-convert or Node.js with sharp) | Identity cards and visuals stay SVG; icons are unaffected |

## A.11 Risks

| Risk | Mitigation |
|---|---|
| Naming confusion: "Frontier Company Blueprint" versus Microsoft's "Frontier Firm", "Frontier Suite", "Frontier program" and the services unit "Microsoft Frontier Company" | Naming note in the method; open decision D-01 |
| Product names and availability change (announcement events) | Dated availability, "verify" marker, canon review cadence (NFR-0014) |
| Internal context leaks into customer material | Visibility on every source; customer build gate; internal-term check |
| Transcripts used without the participants' knowledge | Use only meetings the user organised or attended; Teams transcription notice; NDA status in Frame |
| Over-automation: agents proposed where rules belong | Workflow-first test in the authoring guide; declarations; autonomy one level lower to start |
| Workshop notes lost (browser storage) | Export button on every view's validation; merge script; facilitator exports per block |
| Skill routing collides with built-in skills (meeting recap, HTML, documents) | Explicit exclusions and delegations; conflict scan in the release checklist |
| Agent names decided by the plugin instead of the process owners | Names are proposals; the seed flags every shortened name; decisions N-1 to N-6 with owners |
| Brand colours or logos used without the customer's consent | A source per colour; logos only with brand-rule permission; validation with the brand owner (N-5) |
| Microsoft limits for names, descriptions or icons change | Limits held in one place in the kit, dated sources in `docs/evidence.md`; the validator enforces them |

## A.12 Release plan

**Current qualification, 24 November 2026.** The table below is the original
release roadmap, including its historical “this release” label, not a current
delivery claim. Published 1.10.0 remains the baseline. The
[unreleased 1.10.1 correction](#1101-process-grounding-correction) is limited to
#59/G59-01–08; reviewed-head verification is indexed in
[PR #65](https://github.com/urruegg/frontier-envisioning/pull/65), while human
#52/#8 dependencies remain open. The separate future 1.11 systems/Dynamics 365 design is not
implemented by this patch. No new release or release-workflow authority follows.

**Release-evidence qualification, 25 November 2026.** The separate
[#67 engineering requirements](#release-evidence-engineering-requirements)
replace recurring manual retention only after verified implementation and
actual human adoption. The #55/#57 owner-dispatched publication flow remains;
its additional read-only evidence binding is pending. No new product release,
old #52 copy/merge completion or final PR #71 CI pass is asserted.

**Active 1.11.0 qualification, 26 November 2026.** The current target is
**factory-only**, as actually selected in
[#72](https://github.com/urruegg/frontier-envisioning/issues/72) and the
[#58 deferral receipt](https://github.com/urruegg/frontier-envisioning/issues/58#issuecomment-7161780922).
The [offline Preview requirements](#1110-agent-factory-offline-preview) cover
the candidate ninth skill in the same plugin. Producer review is complete
through `52d6c0e`; nine-skill registration and maturity/installer metadata are
implemented. Exact package/generated-receiver and full local L1 checks passed;
full browser/server acceptance remains pending, as qualified in
[B.9](solution-design.md#agent-factory-candidate-verification-26-november-2026).
Systems/Dynamics 365 #58 moves to a **later
unspecified release**, with no new deadline. Historical choices/roadmap below
remain evidence, not current promises. The #74 lookup at `5dbfc8a` returned
`development` for then-current 1.10.1 after authoritative absence of an exact
published release/conflicting tag; it was not published-1.10.1 reproduction
or a statement of latest publication now. No publication work is resumed.

| Release | Content |
|---|---|
| 1.0 | Four skills, template, scripts, canon, examples, self-test, packages |
| 1.0.1 | Caldova demo data; one package for the chat install and the organisation catalogue; README setup guide; install check |
| 1.1.0 | Agent identity kit (frontier-agent-identity): naming convention, brand colours, Microsoft 365 icons, cards, catalogue, validate and stamp scripts, pipeline templates; identity shown in the blueprint |
| 1.2.0 | Agent identity page below Agents; identity names and icons wherever agents appear; blueprint and identity kit built in one step; identity feedback kept for the review |
| 1.3.0 | Business value (frontier-value-case) and FinOps (frontier-finops): value tree, assumption register, NPV and ROI in CHF, cost per agent, purchase options, guardrails; FinOps page; value in the use cases and the matrix with workshop verdicts |
| 1.4.0 | Innovation Hub journey structure: Part 1 Vision with the Agent Factory journey (DevSecOps, GitHub Copilot harness, CAT skills) and the Attendees page; Part 2 Design with the landing zone (CAF, WAF, Responsible AI), ADRs, use cases in the Hub template and the IT readiness page; Microsoft product icons; design scaffold and merge for readiness and ADRs |
| 1.5.0 | Digital feedback loop on the Overview: the customer's four areas around Microsoft IQ (Work IQ, Fabric IQ, Foundry IQ, Web IQ), animated signals, actions with human approval and measured outcomes; canon with official names and sources, derivation from the journeys, build checks, `loop:` verdicts, discovery questions |
| 1.6.0 (this release) | Agent workflow in the Copilot Studio workflow designer style: trigger, designer nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Scope, Note, Respond to the agent), branches and the desired outcome per agent; derived from the canvas plan until authored; build checks; workflow tables in the solution design |
| 1.7 | Operate loop: plan versus actual from the Copilot Studio licensing reports, Microsoft 365 credit reports and Cost Management FOCUS exports; value and FinOps cockpit in Power BI; monthly digest. HubWorks integration (engagement contract, closeout pack, agenda blocks); German template labels; slide export of selected views through the pptx agent; Copilot Studio prototype pack (agent instructions and topics from the canvas, the workflow from `canvas.workflow`) |
| 1.8 | FOCUS 1.5 alignment (agent as principal, consumption currency); Agent 365 cost data; shared engagement folder on a Hub SharePoint site; feedback capture into a Microsoft List for multi-facilitator workshops |
| Later | A `frontier-diagrams` capability (editable architecture, landing-zone and factory diagrams from the blueprint and the agent definitions, official icon sets); see the visualisation and reuse evaluation |
| 2.0 | Work IQ APIs for richer context retrieval; Agent 365 registry export of validated agents; usage telemetry for the success measures |

## A.13 Open decisions

**Current qualification, 24 November 2026.** `@urruegg` approved the actual
#59 written spec and exact plan/readiness at `35ad763`, as linked in the
[patch authority](#1101-process-grounding-correction). That decision authorises
the bounded correction, not Proposed ADR acceptance, protected labels,
publication or tenant/licence/financial approval. Per-estate source routes and
governance migration gaps still need real named-owner evidence; complete SAP
prerequisites alone do not select an unresolved path. Human #52 manifest
retention/merge and #8 routing/native controls remain pending; #9 workflow
cleanup and future systems/Dynamics 365 design remain separate. The original
decision table is retained unchanged below.

**Release-evidence qualification, 25 November 2026.** The actual #67 written
spec/plan decisions are linked in the
[engineering requirements](#release-evidence-engineering-requirements).
Protected evidence-access adoption, #52's conditional supersession and the
reported visibility-policy discrepancy still require the maintainer.
Proposed rationale acceptance, human #8 routing/native controls and broader
#48 activation remain separate. This does not change the original decisions.

**Factory decisions, 26 November 2026.** The
[actual choice register](ideas/2026-11-25-agent-factory-handover.md#actual-human-choices)
records full-starter-repository, review-starter-with-explicit-gaps, GitHub
Cloud first, latest stable per new export and explicit immutable bootstrap
only after healthy complete no-stable discovery. Factory-only 1.11.0 defers
systems/D365 #58; earlier choices are not erased.

- Written spec `7f650c4`: [actual approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078).
- W0 plan/sprint `c8cc5bb`: [actual bounded execution approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7165080818).
- Host amendment `f4b2609`: [actual `approve-offline-preview-defer-cowork-validation`](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613); Cowork unavailable, no host validation or runtime cutover inferred.
- Complete plan/readiness `5dbfc8a`: [actual `approve-complete-plan-and-implement`](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7167852054), with no revision requested; covers written W1–W4 tasks, not completed tests or human-only actions.

These decisions do not apply native GitHub approval/labels, accept Proposed
ADRs or grant merge, publication, transfer, financial or tenant permission.
Actual Cowork, final candidate gates, human #8 legacy routing and actual
ownership/settings/secrets remain distinct pending matters.

| ID | Decision | Owner |
|---|---|---|
| D-01 | Keep the name "Frontier Company Blueprint", or rename to "Frontier Firm Blueprint" to avoid confusion with Microsoft Frontier Company | Hub leadership |
| D-02 | Distribution: personal skills per engineer, or the organisation catalogue (MOS3) | Hub leadership, tenant admin |
| D-03 | Where engagement folders live: personal OneDrive or a Hub SharePoint site (sharing, retention) | Hub leadership |
| D-04 | Branding of customer versions: Microsoft only, or co-branded with the customer's logo and colour | Hub leadership |
| D-05 | Ownership and cadence of canon updates (defaults and reference architecture) | Hub solution engineering |
| D-06 | Defaults of the agent identity kit for Hub engagements: environment set, kinds, whether the Hub proposes the publisher prefix | Hub solution engineering |
| D-07 | Replace the product icons copied from presentation material with the official Microsoft icon sets; who maintains them | Hub solution engineering |
| D-08 | Whether the canon recommends one engineering control plane (GitHub or Azure DevOps) or keeps both open per customer | Hub solution engineering |

---
