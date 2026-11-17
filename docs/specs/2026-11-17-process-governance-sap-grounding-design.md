# Process governance and SAP grounding correction design

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-17 |
| Author | AI assistant (AI-assisted documentation) |
| Status | Written specification approved at reviewed digest 8ab93d95; subsequent plan/readiness and execution not approved |
| Scope | Focused #59 correction planned for 1.10.1; no optional systems skill or integration runtime |
| References | [Catalogue](README.md), [Correction #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Programme idea](../ideas/2026-11-17-optional-systems-extensions.md), [Implementation plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md), [SPRINT-011](../sprints/SPRINT-011-process-grounding-and-optional-systems.md), [PRD](../prd.md), [Solution design](../solution-design.md) |

## Outcome and authority

New process designs must not recommend creating retiring Purview data-governance
structures or imply that an SAP name establishes a ready mirroring route.
Use current OneLake catalog/Fabric-domain guidance and make SAP prerequisites
and commercial dependencies explicit. Preserve legacy readability, evidence,
privacy and core independence.

The accountable owner is `@urruegg`. The parent verified real #58/#59 and
supplied the human answers recorded in comments on #58. The answer
`approve-correction-design` followed presentation of these two corrections,
all-output consistency, legacy/privacy protection and future red/green plus
full verification requirements. It approves that direction only.
The later **`approve-written-correction-spec`** response approved the actual
written design at SHA-256
`8ab93d9542e3db44f132d4b352551b17ef3c00eb1567ed4e62f85ed93ef78c5f`;
the [approval receipt](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6949117136)
records that distinct review. This revision adds only approval/plan links;
the agreed behaviour and acceptance criteria are unchanged.
**The subsequent plan exists but neither plan approval nor readiness has
been granted.** No labels, assignments, milestones, formal review or release
permission are inferred.

Published **1.10.0** remains the baseline, not an unpublished candidate.
Main is `b88b9a2efa1eb342d5542475c63eee5f7bb43e4b`; release source
`2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`, annotated tag object
`5f9d21953db9c968ae56ac6d485baff3fc09b0ce`, plugin ZIP SHA-256
`9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`
are parent-supplied identities. **1.10.1 is planning only.** This documentation
does not bump versions, reproduce or publish an archive, or change 1.10 bytes.

## Evidence: known facts and assessment

The following public sources were checked read-only by the parent on
**17 November 2026**. This document records that returned evidence; this writer
has not fetched the pages. P-identifiers are local to this documentation, not
replacements for existing canon `S` citation IDs.

| ID | Source and stated date | Supported scope and limits |
|---|---|---|
| P1 | Microsoft Learn, [Learn about Microsoft Purview Unified Catalog](https://learn.microsoft.com/en-us/purview/unified-catalog), updated 12 November 2026 | Unified Catalog and classic Purview data governance are retiring; no new accounts; maintenance through 12 November 2027. This is not retirement of all Microsoft Purview. |
| P2 | Microsoft Security Blog, [A next step in the evolution of the Microsoft Data Governance strategy](https://techcommunity.microsoft.com/blog/microsoft-security-blog/a-next-step-in-the-evolution-of-the-microsoft-data-governance-strategy/4572227), 12 November 2026; [announcement alias](https://aka.ms/DG-Deprecation) | OneLake catalog and the current Fabric foundation are the forward guidance. Purview data security/compliance, sensitivity labels and DLP remain relevant. Gaps and regulated/contractual transitions need the account team; no full feature parity is established. |
| P3 | Microsoft Learn, [Microsoft Fabric Mirrored Databases From SAP](https://learn.microsoft.com/en-us/fabric/mirroring/sap), updated 27 June 2026 | SAP Datasphere replication flows take an initial snapshot and changes into ADLS Gen2; Fabric replication merges them into OneLake Delta tables with a read-only SQL endpoint. Supported SAP source families are source-qualified, not every SAP estate. SAP Datasphere Premium Outbound Integration pricing applies. |
| P5 | Microsoft Learn, [OneLake catalog overview](https://learn.microsoft.com/en-us/fabric/governance/onelake-catalog-overview), updated 29 September 2026 | Explore/Govern/Secure cover discovery, domains, endorsement, scanning and policy-governance capabilities. This does not establish a like-for-like replacement for every retiring capability. |
| P6 | Microsoft Learn, [Domains](https://learn.microsoft.com/en-us/fabric/governance/domains), updated 29 September 2026 | Domains group associated workspaces/items. Domain assignment does **not** affect item visibility or access. Domain labels are not authorisation or a security policy. |
| P7 | Microsoft Learn, [SAP Datasphere mirroring tutorial](https://learn.microsoft.com/en-us/fabric/mirroring/sap-datasphere-tutorial), updated 5 June 2026 | Requires existing Fabric capacity and an SAP Datasphere environment with Premium Outbound Integration; the replicated OneLake copy is read-only. It does not prove this estate has those prerequisites. |

**Observed repository facts.** The current process canon recommends new
Purview governance domains, including F-14; normalisation derives Data
domain/Functional unit labels, and Markdown carries Purview setup guidance.
SAP matches the canon's generic `mirroring` rule; seeding assigns its item and
usually status `next` without establishing the Datasphere route. The existing
Caldova seed test expects SAP mirroring.

**Assessment.** Those defaults can turn dated guidance or an unverified route
into an apparently current recommendation. That is the defect to correct, not
proof that an existing estate is misconfigured. The two internal briefs are
problem inputs, fingerprinted in the [idea](../ideas/2026-11-17-optional-systems-extensions.md#inputs-and-current-baseline);
their catalogues and prompts are not authority.

## Agreed behaviour

### Current governance proposals

1. Replace new Unified Catalog/classic data-governance creation recommendations
   with source-qualified OneLake catalog and Fabric-domain guidance (P1/P2/P5/P6).
   Update the canon, newly seeded/derived domain proposals, discovery,
   method, readiness, risks and affected Caldova examples coherently.
2. Keep domain grouping, discovery/endorsement and actual access/security
   controls distinct. A Fabric domain assignment does not grant visibility,
   access or permission. Preserve workspace/item permissions, OneLake security,
   sensitivity labels, DLP, security and compliance guidance where applicable.
   Never relabel a domain proposal as an enforced security policy.
3. Keep existing Purview-estate migration context and historical source
   evidence. Do not say all Purview is retired or every retired capability has
   an equivalent. Name feature/contractual/regulatory gaps for the governance
   owner and account team; the plugin cannot approve a transition.

### Conditional SAP guidance

1. Where mirroring from SAP is discussed, name the documented route:
   **SAP Datasphere -> ADLS Gen2 -> Fabric/OneLake**, with initial snapshot and
   changes, OneLake Delta tables and the read-only replicated SQL surface
   (P3/P7). This is not direct mirroring from any arbitrary SAP system.
2. Name existing Fabric capacity, a suitable SAP Datasphere environment and
   Premium Outbound Integration as prerequisites to confirm. Name the SAP-side
   Premium Outbound Integration commercial dependency as **unpriced / to
   confirm**. Unknown entitlement, applicability, source support, permissions
   or route prerequisites remain named gaps, not assumed facts.
3. A system-name match alone must not select mirroring, assert an available
   Fabric item or set a success-like `next`/ready result. Missing prerequisites
   must remain explicitly unresolved or conditional through seeding,
   normalisation and presentation. They must not silently fall through to a
   supposedly ready generic pipeline. Ask the data owner to confirm the route.
4. Retain source-qualified supported alternatives when applicable. Do not
   invent alternative GA status, availability, entitlement or third-party
   prices. A valid workshop draft may show conditional options and gaps;
   it is not blocked from ordinary core discussion or certified ready.
   The correction needs a minimal backwards-compatible unresolved/conditional
   representation, not a new route framework or integration runtime.

### Normalisation, compatibility and failure boundaries

- Operate on a detached proposal; do not rewrite original input files.
  Fresh seeds and automatically derived current proposals use corrected
  guidance. Existing records containing `path: mirroring`, legacy governance
  fields or old citations remain readable, with their IDs and historical
  meaning preserved. Recorded legacy choices are not new proof of support.
- When rendering a current assessment of a legacy record, distinguish the
  recorded choice from current conditional guidance. Do not silently transform
  an old source citation into a different fact or treat an imported status as
  verified readiness. Preserve feedback targets and original verdict evidence.
- Append new dated source records for new facts, or explicitly mark current
  proposals with their new evidence. Never reuse saved `S` IDs for different
  claims, rewrite immutable archives or bulk-migrate old customer inputs.
  Source/check dates are explicit evidence, not a new runtime wall-clock
  dependency or a blanket re-verification of the entire catalogue.
- Invalid input retains explicit diagnostics. Errors and strict warnings must
  fail before publishable writes or replacement of good outputs. An unknown
  prerequisite cannot default to success; conditional draft guidance is not
  an implementation/import/availability claim.
- Keep JSON, Markdown, HTML, readiness/risk text and downloads semantically
  consistent. Preserve existing Turtle/export contracts and provider Preview
  caveats. Local output does not certify Fabric import, access or deployment.

## Scope and canonical surfaces

The following is a read-only source map for the later bounded plan, not an
execution checklist or permission to edit these files in this phase.

| Existing surface | Correction responsibility |
|---|---|
| [Process canon](../../plugin/skills/frontier-process/templates/fabric-iq-canon.json) | Introductory note, generic SAP system rule, B7, F-14, OD-ONT-3, `data_architecture.domains.purview`/`purview_what`, `data_product_standard.discovery` and their dependent readiness/risk/source records. Preserve existing IDs and append evidence rather than repurpose citations. |
| [Ontology library](../../plugin/skills/frontier-process/scripts/ontology_lib.py) | Source-path warning/item/status defaults, derived domain labels, ontology Markdown domain/reference text and data-product setup guidance. Preserve legacy acceptance without silently asserting current readiness. |
| [Ontology seed](../../plugin/skills/frontier-process/scripts/seed_ontology.py) | `system_path` and source path/item/status derivation must not select an unconfirmed SAP route or mask it with the generic pipeline fallback. |
| [Process procedure](../../plugin/skills/frontier-process/SKILL.md), [method](../../plugin/skills/frontier-process/references/ontology-method.md), [Caldova ontology](../../plugin/skills/frontier-process/examples/caldova-ontology.json) | Correct Step 3's items 3/8, method/readiness/risk explanation and affected synthetic examples without losing restrictions, feedback or old evidence. |
| [Blueprint defaults](../../plugin/skills/frontier-blueprint/templates/blueprint-defaults.json), [renderer source](../../src/renderer/template.js) | Only dependent canon/default/rendered labels or documents affected by the two corrections. Preserve valid Purview security references. No new layout, view, third-party icon or network path. |
| Existing ontology builders and package/template generators | Propagate corrected sources to all affected outputs through existing generators during future implementation; never hand-edit generated template, install, build or distribution output. |

**Out of scope:** `frontier-systems`, any new pack/skill, live integrations,
credentials, tenant configuration, identity provisioning, runtime dependencies,
Databricks/Synapse Link changes, new route architecture and bulk catalogue
refresh. Do not change the eight-skill manifest or hard-coded eight-skill
maturity expectation for this patch; nine skills belong to the later 1.11.0
design/release. Do not blanket-convert quoted booleans: PKG-S010 is unverified
and the installer already accepts them; a reproduced validator failure would
need separate evidence and scope.

Ordinary guidance must not invoke FinOps, calculate prices/ROI/time-to-value,
claim licensing authority or require a FinOps-style acknowledgement. Separately
requested financial work retains the unchanged current-scenario awareness and
financial-readiness gates. Naming an unpriced prerequisite neither bypasses
those gates nor makes core process design dependent on FinOps.

Only the six authorised prose/catalogue files change now. No PRD,
solution-design, code, tests, versions, generator, protected record or product
file changes occur in this phase. A later approved plan must identify appropriate
requirements/design updates within its scope. No ADR is needed for this
correction of sourced guidance.

## Evidence and audience boundaries

Keep internal/visibility/`src`/`content_src` ancestry, source namespaces and
audience restrictions across normalisation, feedback and every export.
Removing citation IDs is not sanitisation. Internal-derived descriptions,
bindings, instructions, products, rules, metrics and operations proposals must
not leak through Markdown, JSON, HTML, Turtle or downloads. New public citations
do not make restricted source content shareable. Customer projections are
scope-specific, not public/IP clearance.

Use only fictitious Caldova Industrial AG fixtures. Preserve legacy input
readability and originals, evidence snapshots, feedback IDs, privacy and
existing non-FinOps behaviour. Provider status remains separate from the GA
process wrapper. Do not copy internal brief/showcase text or personal metadata.

## Acceptance and verification

These are future acceptance obligations, **not completed checks**.

| ID | Required outcome | Source / future proof |
|---|---|---|
| G59-01 | New governance guidance uses OneLake catalog/Fabric domains, not creation of retiring Unified Catalog/classic structures; retains Purview security/compliance and existing-estate migration context without parity claims. | P1/P2/P5/P6; focused failing-then-passing canon, seed/normalisation and rendered guidance assertions. |
| G59-02 | SAP guidance names Datasphere -> ADLS Gen2 -> Fabric/OneLake, read-only replication, existing capacity/environment and unpriced Premium Outbound Integration dependency. Unknown prerequisites never auto-select a ready route/item/status or ready fallback; alternatives remain source-qualified and owner-confirmed. | P3/P7; red/green known, unknown and invalid prerequisite cases, plus legacy SAP-path coverage. |
| G59-03 | Domain assignment is not access/security authorisation. Corrected governance/SAP meaning agrees across canon, new proposals, JSON, Markdown, HTML, downloads, method/readiness/risks and affected Caldova examples. No new layout/view/network behaviour. | P1-P3/P5-P7; focused output and browser/DOM parity checks; regenerated affected artefacts. |
| G59-04 | Legacy exports/inputs, IDs/citations, feedback and historical choices remain readable and unmodified as evidence; current proposals do not reinterpret old citations or silently grant readiness. Privacy and audience projection remain fail-closed. | Existing process contract and this compatibility boundary; legacy builds, feedback round trips and restricted-content export regressions. |
| G59-05 | Core/process/ordinary value works with FinOps absent or declined. No automatic money/licensing/ROI/time-to-value claim; separately requested cost operations retain existing acknowledgement and strict financial gates. | Existing PRD/FinOps contracts; core-only and no-FinOps regression proof, without waiving real financial gaps. |
| G59-06 | Published 1.10.0 source/tag/ZIP and immutable records are unchanged. Plan 1.10.1 only; no backdated 1.9.3 or patch skill-count change, and no fabricated reproduction/publication result. | Baseline identities above; actual source/archive comparison and human #52 retention evidence before final release/reproduction acceptance. |
| G59-07 | Runtime stays offline, deterministic and stdlib-only; invalid/strict-warning builds do not write publishable output or overwrite good output; no new unresolved condition defaults to success. | Repeated-build identity, invalid-input/no-overwrite and deterministic-date tests; actual distribution/extraction checks. |
| G59-08 | Both fixes have observed focused RED/GREEN evidence; regenerated outputs, full repository, browser and exact-package/extraction proof pass against the reviewed candidate with honest dependency/gap reporting. | Future `python tools/dev.py check --strict`, `python tools/dev.py site e2e --strict`, `python tools/dev.py docs --strict` and actual extracted-distribution execution; record returned logs/results, not planned passes. |

Existing test surfaces are
[ontology unit tests](../../tests/unit/test_ontology.py),
[Blueprint DOM tests](../../tests/dom/blueprint.test.mjs),
[ontology DOM tests](../../tests/dom/ontology-preview.test.mjs) and
[ontology browser tests](../../tests/e2e/ontology-preview.spec.mjs).
`test_ontology.py` already includes architecture/output and legacy/privacy
coverage, including the current SAP-mirroring expectation; no separate
`test_process_data_architecture.py` was found in this worktree. This inventory
does not claim the new regressions exist or have run.

## Next review and human dependencies

Actual human review of this written spec is recorded above. The subsequent
[implementation plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md)
awaits a separate human plan/readiness decision before implementation. This
document grants no execution, publication or deployment authority.

Human-only [#52](https://github.com/urruegg/frontier-envisioning/issues/52),
immutable 1.10 manifest retention, is a named final release/reproduction
dependency. It is not permission to edit protected records, skip the baseline
or bump a version merely to escape a failure. Human-only protected session
routing/native controls [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
remain outstanding; do not edit or treat them as migrated. Their workflow
decisions are not part of this correction.
