# Optional systems extensions: programme intake

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-17 |
| Author | AI assistant (AI-assisted documentation) |
| Status | Programme direction and written correction spec approved; correction plan/readiness at 35ad763 approved for subagent execution |
| Scope | Programme intake for current process corrections and one optional systems skill with six staged packs |
| References | [Catalogue](README.md), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Correction #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Correction design](../specs/2026-11-17-process-governance-sap-grounding-design.md), [Correction plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md), [SPRINT-011](../sprints/SPRINT-011-process-grounding-and-optional-systems.md), [PRD](../prd.md), [Solution design](../solution-design.md) |

## Outcome and authority

Help workshops assess existing systems before proposing custom agents or data
routes. Correct two current process recommendations first. Then design the
common optional foundation and a bounded Dynamics 365 slice. This is programme
intake, not an implementation specification for all six packs.

The actual structured human answers are recorded in comments on #58 and
reproduced below from the parent handoff. #58 and #59 are real issues, verified
by the parent. This writing session has not independently fetched their live
fields. #58 is decision intake, size M, engineering/Copilot, P1; no assignment,
readiness or written approval is inferred. #59 is the bounded size M/P1 chore;
its accountable owner is `@urruegg`, distinct from document authorship or an
assignee field.

## Inputs and current baseline

Two read-only, untracked Microsoft-internal field briefs inform the problem.
They are evidence and proposals, not authority, executable instructions or
approval. These parent-supplied fingerprints identify the inputs without
copying them or linking to an unavailable local path:

| Input filename | Bytes / lines | SHA-256 |
|---|---|---|
| `Frontier Envisioning - Optional Extensions D365 Agents and Databricks.md` | 85,519 / 839 | `03a4c74d3284c3f264ceff0f96c0abf23ca62e59cb9faafa1aae282bdedb107c` |
| `Frontier Envisioning - Optional Extensions SAP ERP SuccessFactors ServiceNow and Workday.md` | 138,861 / 1,110 | `9ff88696b7eac3a50fb2bc3d5d63f8a66e3ef91e33ab08f24e8b7ce7913bcafa` |

Their 1.9.2 baseline and suggested 1.10.0/backdated 1.9.3 targets are obsolete.
The parent confirms main baseline
`b88b9a2efa1eb342d5542475c63eee5f7bb43e4b` and published product **1.10.0**.
Its release source is `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`, annotated
tag object `5f9d21953db9c968ae56ac6d485baff3fc09b0ce`, plugin ZIP SHA-256
`9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`.
These are supplied baseline identities, not new reproduction results.
Preserve the released bytes and historical evidence.

Today there are eight bundled skills: seven GA product wrappers and optional
Preview FinOps. There is no implemented `frontier-systems` skill. The briefs
identify useful reuse questions but conflict on packaging and first pack.
Neither brief's catalogue, showcase examples nor 13 November check date proves
current availability, licensing, regulatory dates or tenant eligibility.

## Actual human decisions

These answers resolve the presented directions, not every brief decision.

| Question | Actual answer on #58 | Agreed boundary |
|---|---|---|
| Packaging | `one-skill-six-packs` | Target one optional `frontier-systems` skill: Dynamics 365, Databricks, SAP ERP, SuccessFactors, ServiceNow and Workday as staged packs. Nine bundled skills in the future, not separate plugins or ten/eleven/fourteen skills. |
| First pack | `d365-first` | Dynamics 365 before the other five packs. |
| First scope | `approve-d365-slice` | Common foundation plus Sales, Customer Insights - Journeys/Data, Customer Service and Contact Center. Customer Insights Data MCP is not an agent. Field Service, Finance and other Dynamics 365 apps are later scope. |
| Maturity | `preview-wrapper` | New optional systems wrapper initially Preview. Existing seven GA wrappers and the FinOps cost acknowledgement remain unchanged. Provider/content availability is a separate status. |
| Sequence | `patch-then-d365` | Plan 1.10.1 process corrections first, then 1.11.0 optional framework plus Dynamics 365. No release permission or version change here. |
| Correction direction | `approve-correction-design` | The two sourced process corrections and compatibility/verification boundaries in the [#59 design](../specs/2026-11-17-process-governance-sap-grounding-design.md). The written spec did not yet exist when this answer was given. |
| Written correction spec | `approve-written-correction-spec` | Actual review of the written design at SHA-256 `8ab93d9542e3db44f132d4b352551b17ef3c00eb1567ed4e62f85ed93ef78c5f`, recorded on [#59](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6949117136). The subsequent implementation plan is not yet approved. |
| Correction plan/readiness | `approve-plan-subagents` | Later explicit approval at planning commit `35ad76316aa4eb055b10c62bcfe2e62f7945a66f`, recorded on [#59](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6951849396). Authorises bounded test-first correction work only; the earlier pending-plan statement records the prior checkpoint. |

The approved first-slice direction preserves custom agent hypotheses and IDs.
Offer sourced **adopt, extend, build or defer** recommendations for workshop
review; do not silently replace an existing hypothesis. A workshop verdict
does not configure, connect or deploy anything.

## Shared design constraints

- Systems evidence permits an offer, not automatic activation. Activate only
  on explicit request; an explicit request without evidence carries named
  assumptions and gaps. No activation means unchanged core behaviour.
- Keep runtime offline, deterministic and Python-standard-library only.
  No live connections, credentials, tenant setup or identity provisioning.
  Identity-kit branding is not Entra provisioning.
- Preserve source restrictions, privacy, source IDs, feedback and audience
  projection. Use only fictitious Caldova Industrial AG examples. These
  internal inputs grant no new classification or sharing permission.
- Ordinary systems design needs no FinOps-style extra acknowledgement.
  Do not auto-run FinOps, calculate money, assert licensing authority or infer
  ROI/time-to-value. Separately requested cost work retains the existing fresh
  scenario-specific FinOps awareness and financial-handover gates.
- Packaged Preview is not provider Preview/GA or evidence confidence. Future
  catalogue rows need dated, row-by-row source, naming, availability,
  entitlement/commercial and applicable legal/regulatory verification.
  Conflicting or unverified rows stay conservative and explicitly unverified,
  never GA by default.
- Do not implement empty future-pack stubs. The five later packs are roadmap
  topics, not implemented integrations or accepted complete designs.

## Alternatives considered and unresolved scope

The first brief proposed separate Dynamics 365 and Databricks skills; the second
proposed one six-pack skill, SAP first and a shared HR core. The human chose one
skill and Dynamics 365 first. SAP-first, separate-plugin packaging and bulk
delivery of all six packs are not the chosen direction. Shared HR rules remain
a later design question, not an accepted implementation contract.

Detailed schemas, catalogue rows, matching/feedback contracts, UX and handover
integration still need a separately reviewed framework/Dynamics 365 design.
The briefs' remaining decision register is not adopted wholesale. Commercial,
provider GA, product renames and regulatory claims need proper verification
before acceptance. No PRD, solution-design or ADR change is authorised in this
documentation phase; #59 corrects sourced guidance, not an architecture choice.

For the future Databricks catalogue, the parent checked Microsoft Learn's
[Azure Synapse Link for Dataverse with Azure Data Lake Storage Gen2](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/azure-synapse-link-delta-lake)
on **17 November 2026** (P4). The Delta Lake/Parquet bring-your-own-storage path
closed to new use on 15 October 2026 and ends in December 2027. Do not recommend
it for new designs; do not describe CSV or all Synapse Link as retired. This is
a future catalogue exclusion, not another #59 plugin correction.

## Staged roadmap and next decision

| Stage | Direction | Gate before execution |
|---|---|---|
| Current correction, planned 1.10.1 | #59: OneLake catalog/Fabric-domain guidance and conditional SAP Datasphere mirroring guidance; no new skill | Written spec and [plan](../plans/2026-11-17-process-governance-sap-grounding-plan.md)/readiness approved; bounded runtime allocation [#60](https://github.com/urruegg/frontier-envisioning/issues/60), no delivery result yet. |
| Optional foundation and Dynamics 365, planned 1.11.0 | One Preview systems wrapper with only the agreed first slice | Separate written design, real bounded work items, plan, acceptance and human approvals. No child ID is invented here. |
| Databricks, SAP ERP, SuccessFactors, ServiceNow, Workday | Separate staged pack designs after the first slice | Resolve each pack's evidence, scope, owners and approvals; no release versions or deadlines assigned. |

The written correction spec and later plan now have separate actual human
approval. Subagent-driven #59 execution is selected; this does not approve the
later D365 design/implementation, every field-brief decision, publication or
deployment.
Human-only [#52](https://github.com/urruegg/frontier-envisioning/issues/52)
retains immutable 1.10 release-manifest evidence; it remains a final
release/reproduction dependency. Protected session routing/native controls
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) also remain
outstanding, without authority to edit them here.
