# Release evidence simplification design

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-24 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Written review draft; flow approved, implementation plan/readiness not yet approved |
| Scope | Exact-version published evidence, offline local checks and strict CI without manual manifest retention |
| References | [Catalogue](README.md), [Issue #67](https://github.com/urruegg/frontier-envisioning/issues/67), [Idea and actual choices](../ideas/2026-11-24-release-evidence-simplification.md), [Early sprint row](../sprints/README.md), [PRD](../prd.md), [Solution design](../solution-design.md), [Retention #52](https://github.com/urruegg/frontier-envisioning/issues/52) |

## 1. Outcome and authority

Remove recurring manual downloads, SHA-256 comparison, copied manifests and
post-release retention PRs. Keep automated build/integrity/reproduction checks
and the maintainer's final release/publication decision.

The human selected `remove-manual-ceremony`, `release-assets-record`,
`offline-local-strict-ci` and `approve-flow`, then requested subagent-driven
implementation. The [idea](../ideas/2026-11-24-release-evidence-simplification.md#actual-human-choices)
records those actual choices and their limits. The additional complete-design
confirmation was not obtained. This written draft has not been reviewed by the
maintainer; there is no approved implementation plan yet.

Owner: `@urruegg`. A later plan must link real bounded implementation work and
separately obtain plan/readiness approval. No protected label, formal review,
workflow adoption or publication permission follows from this document.

## 2. Existing mechanism and proposed boundary

The existing release workflow builds/tests, independently compares plugin ZIPs,
generates the manifest/checksums and verifies its handover before publication.
The current verifier instead expects a copied record under `releases/<version>`
for subsequent comparisons. The proposed change replaces that duplicate
retention mechanism, not the integrity comparison.

Canonical evidence is the manifest/checksum assets of the exact published
release in `urruegg/frontier-envisioning`. Do not use the latest release for
another version. Existing retained historical records remain unchanged and
available for historical verification; new releases need no copied Git record.

The implementation belongs to developer tooling, its tests and directly
related active guidance. Plugin code stays offline, deterministic and
standard-library-only. No plugin-version bump or new runtime dependency is
needed for the engineering-only change.

## 3. Exact-version evidence flow

1. Resolve the requested canonical version, expected tag/source and repository.
   The ordinary check uses the current source version; explicit historical
   verification must build/use that historical source and its matching outputs.
2. In CI, establish repository access before deciding whether the exact version
   has a published release. A private-repository 404 or failed authentication
   must never be treated as proof that a version is unreleased.
3. For a published release, retrieve only the expected evidence/assets through
   the established GitHub access mechanism. Validate shape, version, source/tag
   identity, allowed paths/file names and required hashes before comparison or
   cache writes. Missing evidence is an error, not a success-shaped fallback.
4. Compare corresponding built artefacts using existing package/hash and
   generated-date normalisation helpers. Never force current 1.10.1 outputs to
   reproduce the distinct published 1.10.0 release.
5. Cache successfully validated evidence with its version/source identity in
   ignored build storage. Revalidate cached identity/structure/content before
   reuse. Do not write to protected `releases/` or overwrite published assets.

Legacy evidence formats/provenance, including locally published 1.10.0, must be
handled explicitly rather than rewritten to claim a workflow run. SHA-256 and
a checksum file demonstrate consistency, not an independent signature,
authenticated human approval or immutable hosting by themselves.

## 4. Local, CI and failure outcomes

Local checks remain offline-capable and do not require a manual download.
Use valid cached exact-version/source evidence when available. Without it,
report **published-release comparison not performed: no offline evidence**.
Other local tests may pass, but the summary must not call that comparison
verified or imply CI publication acceptance. No fake manifest is generated.

CI requires automatic exact-version lookup and comparison. Authentication,
repository/network errors, missing published assets, malformed evidence,
wrong version/source and artefact/cache mismatches are explicit failures.
They must not silently downgrade into development mode.

Only an authoritative successful lookup establishing that no published release
exists permits the development outcome. Existing tag/source conflicts still
require diagnosis; the absence of release assets does not authorise reusing an
immutable tagged version. Print the actual outcome and source identity so
development, verified publication and unavailable comparison are distinct.

Network operations exist only in the developer-side evidence resolver or CI,
not plugin scripts. Bound requests/downloads and use temporary paths; never
print credentials or read tokens into diagnostic output.

## 5. Scope, adoption and #52 transition

Keep the current human review/merge, release workflow invocation and publication
boundaries. No App/PAT, automatic merge, agent publication, tag mutation,
deployment, broader #48 activation or extra per-release approval is introduced.

Provide eligible tooling/tests and aligned guidance through reviewable changes.
Any required protected workflow/guard change is a named human adoption step,
not an agent edit or permission bypass through another tool. Existing stricter
controls remain effective until that real adoption is recorded.

Historical `releases/` records and any maintainer-authored 1.10.0 copy stay
untouched. After the accepted replacement is implemented, verified and adopted,
record #52's recurring manual-retention requirement as superseded. Do not
pretend a missing historical retention/merge happened or close it on the basis
of this design alone. Human #8 routing/native-controls work remains separate.

Active release instructions must describe the adopted process truthfully.
Superseded guidance is qualified, not erased from historical records. This is
not the previously deferred broad automation project.

## 6. Testable acceptance

| ID | Outcome and proof |
|---|---|
| RE-01 | Normal publication requires no manual download/hash/copy/retention PR. Manifest/checksums remain release assets; automated comparison is retained. |
| RE-02 | Resolve only the requested version and matching source/tag; reject wrong-version/latest-substitution and source conflicts. Exercise new and historical formats without rewriting provenance. |
| RE-03 | CI distinguishes a confirmed development version from access/network failures, missing published assets, malformed evidence and hash mismatch; every latter case fails explicitly. |
| RE-04 | Offline local cache hit compares matching evidence; cache miss clearly reports not performed; stale/tampered/wrong-source cache is not accepted. No plugin networking. |
| RE-05 | Preserve existing release assets/tags/records, deterministic package comparison, generated-date handling, finite raster inputs and unrelated runtime behaviour. |
| RE-06 | Tests use deterministic local fixtures for GitHub responses/downloads. Observe failing-then-passing cases for changed checker behaviour; no live service is required by unit tests. |
| RE-07 | Active guidance, gate summaries and #52 disposition distinguish proposal, implementation, human adoption and publication. Required protected edits are handed off rather than performed by agents. |
| RE-08 | Record actual targeted/full strict quality results and exact-version integration proof. No agent release, merge, dispatch or invented manual acceptance is used to demonstrate the design. |

The implementation plan must name exact files, commands, fixture cases,
independent review stages and any protected adoption dependency. Do not add a
generic release framework, loosen hashes, copy a golden ZIP, remove the
reproduction safeguard or silently accept unknown evidence.

## 7. Review and execution sequence

This planning-only draft starts from merged main
`b9e41e85bea84990f14cd17566042cb9e93ecb31`.
Existing documentation validation passed before the draft was written.
Written-spec review is the next actual gate; a plan is written afterwards.
Subagent-driven implementation is the selected mode once that real plan is
approved. No code, tests, protected record, workflow or runtime changes are
made by creating this specification.
