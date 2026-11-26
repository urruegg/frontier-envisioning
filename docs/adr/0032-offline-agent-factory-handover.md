# ADR-0032: Offline full-foundation Agent Factory handover

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-26 |
| Author | Copilot; AI-assisted rationale for #78 |
| Status | Proposed; written spec/plan approval is not ADR acceptance, policy activation or release approval |
| Scope | Optional Preview Factory handover in unreleased 1.11.0; host acquisition, passive offline producer and separate receiving review |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [#78](https://github.com/urruegg/frontier-envisioning/issues/78), [Idea and actual choices](../ideas/2026-11-25-agent-factory-handover.md), [Approved design](../specs/2026-11-25-agent-factory-handover-design.md), [Approved full plan](../plans/2026-11-25-agent-factory-offline-implementation-plan.md), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md), [PRD](../prd.md#1110-agent-factory-offline-preview), [Architecture](../solution-design.md#1110-agent-factory-offline-preview), [Candidate evidence](../solution-design.md#agent-factory-candidate-verification-26-november-2026) |

## Context

An explicitly requested starter repository needs the controlled Agent Factory
foundation and final reviewed envisioning documents. A document-only overlay
would lose policies, workflows, locks and licence material. Regenerating
PRD/design/ADRs would compete with accepted authored inputs and break identity.
The output is a receiving team's review package, not an accepted application
or permission to implement.

The actual written spec at `7f650c4` received
[human approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078).
W0 at `c8cc5bb` then received
[bounded execution approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7165080818).
Actual Cowork is unavailable. The written amendment at `f4b2609` received
[`approve-offline-preview-defer-cowork-validation`](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613),
permitting offline Preview development with actual source/receiver evidence,
not a validated Cowork path or runtime cutover. The complete production plan
at `5dbfc8a` subsequently received
[`approve-complete-plan-and-implement`](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7167852054).
These decisions do not accept this ADR.

Accountable owner: `@urruegg`. Factory-only 1.11.0 defers independent
systems/Dynamics 365 #58 to a later unspecified release. The product remains
one plugin, registering seven non-FinOps GA wrappers and optional Preview
FinOps/Factory. Current registration is nine; the candidate ninth skill
is **Envisioning Agent Factory**, registered name `frontier-agent-factory`.

## Decision

Record the approved design as a **Proposed** architectural rationale:

1. **Separate acquisition from export.** Each new handover needs actual
   authorised available-host discovery of the latest published stable template.
   Keep only `id`, `tag_name`, `published_at`, `draft`, `prerelease` for all
   paginated releases; no raw API body, authors, assets or protected URLs.
   Validate all stable metadata, reject ties/unknowns and resolve only the
   selected stable tag/commit. Only healthy complete no-stable discovery
   permits explicitly approved immutable **unreleased bootstrap**. No auth,
   network, incomplete, incompatible or selected-tag failure falls back to
   main/older source. A local file does not prove latest.
2. **Freeze identity and bytes once.** Bind release/tag/commit/acquisition
   evidence and source archive bytes to the export. Automatically hash inputs
   and reproduce from the frozen record; do not impose manual customer digest
   copying, comparison or retention. Use actually available host capabilities,
   not assumed universal tools, GitHub CLI or Cowork downloads.
3. **Keep the producer offline and passive.** Python 3.11+ standard library,
   with required trusted bundled siblings, no repository-only imports,
   dependency setup, network or downloaded-code execution. Missing requested
   components fail explicitly. Imported documents, including template policies,
   are evidence data, never governing instructions or permission.
4. **Preserve the complete compatible foundation.** Keep authored foundation
   bytes, modes, policies/workflows, locks, MIT/third-party notices and selected
   reviewed ordinary files; no keyword pruning. Exclude `.git`, account/cache/
   staging/dependency state. Add `START_HERE.md`, producer 1.0 sidecar
   `handover/manifest.json` and `docs/intake/records/<id>/` intake/review/artefacts.
   Do not extend upstream receiver intake 1.0 with producer fields.
5. **Preserve authored scope and history.** Final PRD/design/ADRs and applicable
   readiness/identity/Blueprint/value/process/financial inputs keep bytes/IDs,
   explicit original-to-factory maps and selected MVP/shared-dependency evidence.
   Out-of-scope dependencies are named gaps, not extra work. Declare eight roles
   per solution; PRD/design cannot be N/A. Valid `needs-clarification` is the
   default with real required scope/owners/acquisition/transfer and engineering
   gaps. Invalid explicit acceptance fails, never downgrades. Prior accepted
   raw JSON, Windows path spellings, CRLF and files remain immutable; change
   uses a new ID/`supersedes`. Unavailable historical originals are not verified.
6. **Fail closed on unsupported or unreviewed content.** Ordinary
   `.md`, `.txt`, `.json`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv` only.
   Selected HTML/ZIP/Turtle needs actual reviewed JSON/Markdown equivalents,
   not renaming, dropping or bypass folders. The distribution ZIP is not an
   intake input archive. Whole-original-ancestry/schema-owned customer privacy
   checks and actual transfer/sharing review cover all current/history files
   and exported metadata, filenames, refs, known private notes/keys/arrays.
   Restricted baselines fail; no raw mail/transcripts, secrets, account state,
   private sources, protected links or withheld names/counts. Office/PDF
   review is opaque human evidence, not semantic DLP.
7. **Reuse owner financial authority.** FinOps stays optional with no automatic
   figures, zero budgets or false N/A. Current/history financial schemas, roles,
   legacy/nested results and derivatives require current acknowledgement,
   genuine owner review and authoritative packets regardless of wrapper/schema.
   Existing owner validators/formulas/rates govern; no second calculator.
   Legacy reviewed documents remain review-only. Explicit `build-handover`
   with `requested:false` is refused; with `requested:true`, the claim must
   meet the documented actual stricter financial handover-ready gate.
   Internal authority staging is not auto-exported or privacy clearance.
   Blueprint originals with derived `agent_finops` currently fail
   `FACTORY_BLUEPRINT_FINANCIAL_CONTEXT`; no silent stripping, trust or automatic
   source-context rewrite. Supply compatible authoritative originals and
   separately approved customer projections with genuine upstream evidence.
8. **Publish only validated bounded bytes.** Reuse the shared raw ZIP mechanism
   with release evidence. STORE/DEFLATE source limits are 32 MiB compressed,
   64 MiB decoded and 4,096 members including directories; final expanded limit
   is 128 MiB/4,096 including generated entries. Receiver reads share one
   64 MiB baseline-plus-original-source budget, with 16 MiB/file and 1 MiB
   intake JSON. Known corruption/path/link/reparse/file-parent/case/slash/state
   hazards fail before bounded atomic replacement; retain prior good ZIP/input
   bytes. Frozen metadata gives identical ZIP bytes. Inventory omits its own
   manifest hash; final ZIP hash is stdout.
9. **Keep statuses and authority separate.** Export validation, intake
   disposition, unauthenticated recorded review, actual receiver checks,
   Cowork validation, tenant readiness and financial readiness are independent.
   Receiver/Cowork checks during export are not performed; tenant is not
   assessed. No pre-acceptance or accepted export generates runtime, source,
   tests, evaluations, IaC, applications or remote issues.

## Consequences

- The receiving team gets a full governed foundation, with explicit provenance
  and review gaps, not a working business application. It must run actual
  receiver checks and follow its human-governed method. Receiver prerequisites
  are Python 3.12+/Node 24 LTS; observed Node 26 is not certification.
- Ordinary core/value/identity/Blueprint/design/process remains independent
  of Factory and FinOps. A PRD does not trigger export.
- Automatic checks establish consistency, not signatures, complete DLP,
  authenticated reviewers or acceptance authority. MIT/third-party retention
  does not relicense customer files or grant IP/transfer rights.
- GitHub.com and GitHub Enterprise Cloud, including cloud hostnames, are the
  first receiving-repository/host profile, not native ADO/GHES certification.
  The authoritative template source remains `urruegg/frontier-agent-factory`
  on GitHub.com. No remote
  repository creation, Work IQ auth switching, tenant consent/provision/deploy,
  settings or secret management occurs. Read access/public visibility grants
  no transfer, financial or Entra permission. Branding is not Entra provisioning;
  HubWorks is not an assumed runtime loader.
- Incompatible future template/schema changes require an explicit adapter
  change, not an older fallback. Existing 1.10.x releases, provenance, source
  evidence and historical raster/identity profiles remain unchanged.

## Alternatives considered

- **Documents-only ZIP or overlay:** smaller, but loses the promised controlled
  foundation and receiving controls.
- **Network-enabled exporter or executed template generator:** couples host
  credentials/dependencies to the offline product and executes untrusted inputs.
- **Main/older-source fallback or local-file-as-latest:** masks failed discovery
  and breaks source freshness/evidence.
- **New document/financial generator or automatic acceptance:** replaces owner
  authority, authored IDs/bytes and actual review with competing derived claims.
- **Wait for Cowork before any development:** superseded only for bounded
  offline Preview development by the actual written host amendment; actual
  Cowork checks are deferred, not waived or simulated.

## Status

**Proposed until an actual person accepts this ADR.** Producer review through
`ee5d690` and local component results are indexed in
[B.9](../solution-design.md#agent-factory-candidate-verification-26-november-2026).
Ninth-skill registration and maturity/installer metadata are implemented; final
exact package/generated-receiver and candidate gates remain pending.
Actual Cowork discovery/install/acquisition/
export is not performed; tenant readiness is not assessed.

No human-only label, native GitHub approval, engineering-policy activation,
merge, tag, publication or deployment follows from this record or spec/plan
approval. Protected legacy routing #8 remains human-pending and unchanged.
