# ADR-0031: Exact-version release assets as canonical evidence

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant; AI-assisted rationale for #70 |
| Status | Proposed; #67 spec/plan approval is not ADR acceptance or protected adoption |
| Scope | Developer-side published evidence, offline cache and strict CI; no plugin or publication-authority change |
| References | [Catalogue](README.md), [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [#70](https://github.com/urruegg/frontier-envisioning/issues/70), [Approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [Plan](../plans/2026-11-25-release-evidence-simplification-plan.md), [SPRINT-012](../sprints/SPRINT-012-release-evidence-simplification.md), [PRD](../prd.md#release-evidence-engineering-requirements), [Design and verification](../solution-design.md#release-evidence-engineering-flow), [Human adoption handover](../engineering/release-evidence-adoption.md), [Earlier release rationale](0019-versioning-and-releases.md) |

## Context

The release workflow already builds/tests, independently compares plugin
ZIPs, prepares manifest/checksum assets and verifies its publisher handover.
Requiring a person to download, hash and copy that manifest into a later
retention PR duplicates evidence handling. Removing those checks instead
would lose the immutable-release safeguard.

The maintainer approved the written #67 spec at `67dc9a5`
([actual receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060)),
then the plan/execution at `22f512f`
([separate receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155657072)).
Those decisions authorise bounded implementation, not this ADR's acceptance,
protected workflow edits or publication by an agent.

## Proposed decision

Use the four assets of the exact published GitHub Release in
`urruegg/frontier-envisioning` as canonical evidence. Never substitute
`latest`. Validate repository/version/annotated-tag/source identity,
allowlisted raw downloads, the three checksum payload rows, manifest and
bounded ZIP content before comparing the four reproduction artefacts.
The [two inventories](../engineering/release-evidence-adoption.md#two-distinct-inventories)
are distinct; demo/identity/catalogue outputs are not new release downloads.

Developer tooling uses existing `gh` authentication, not plugin networking
or a new PAT/App scheme. CI performs fresh authoritative lookup: access,
network, draft/conflicting-tag, missing-asset, malformed-evidence and
comparison failures fail explicitly. Only successful lookup establishing no
exact release or conflicting tag permits confirmed development.

Local checks remain offline-capable. Store only fully validated raw evidence
in ignored version/source-keyed build storage. Revalidate it against the exact
local annotated tag, hashes, checksums, manifest and archive limits before
reuse. A genuine miss reports comparison `not-performed`, not a publication
pass or confirmed development; invalid cache is an error. Never cache absence.

Preserve historical assets/tags/records/provenance and explicit network-free
manifest interfaces. Compare historical releases with matching historical
outputs, retaining existing generated-date normalisation and raster limits.
New releases need no copied record under `releases/`.

## Consequences

- Normal future flow is human review/merge, then human **Run workflow** with
  `version`, `manual_checks` and `publish`; existing automation verifies and
  publishes. No recurring download/hash/copy/retention PR is required.
- Automatic integrity and reproduction checks remain; local unavailable
  comparison and strict CI results are visibly different.
- Successful GitHub access and release-asset availability become explicit CI
  dependencies, including private access where required. Failure is not
  proof of an unreleased version or permission to fall back.
- SHA-256/checksum/cache consistency is not a cryptographic signature,
  independent approval, native build attestation or immutable hosting
  guarantee. No SLSA level is claimed.
- Plugin runtime stays offline, deterministic and standard-library-only,
  without feature/version, renderer, raster or release-record changes.

## Alternatives considered

- Continue manual manifest retention: preserves a second record but keeps
  recurring ceremony and possible copying mistakes.
- Remove reproduction checks or accept missing evidence: simpler but loses
  the safeguard and conflates failure with development.
- Query `latest` or always require local networking: wrong-version risk or
  unnecessary loss of offline development.
- Require signatures/native attestation, a new App/PAT or #48 activation:
  a different authority/authentication project, not this approved slice.

## Status and adoption

**Proposed**, not Accepted. The owner-dispatched publisher was adopted under
[#55](https://github.com/urruegg/frontier-envisioning/issues/55)/
[#57](https://github.com/urruegg/frontier-envisioning/issues/57). Its separate
#67 protected read-only token binding remains
[pending human application](../engineering/release-evidence-adoption.md#one-time-protected-workflow-handover).
Normal CI already has that binding in reviewed #69 source; final strict gate
and actual PR #71 CI remain pending. No agent edits or dispatches the protected
workflow, supplies another credential route, merges, tags or publishes.

Keep legacy release/showcase flags unset/false and existing human review,
settings and guard-label boundaries. #52 supersession requires actual
verified replacement/adoption, not a fictional old copy/merge. Human #8
routing/native controls remain separate; #48's App model is not activated.
The [reported visibility-policy discrepancy](../engineering/release-evidence-adoption.md#classification-and-access)
needs human reconciliation without changing intended classification or
claiming public clearance. ADR-0029 retains its reserved historical number.
