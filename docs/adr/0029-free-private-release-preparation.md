# ADR-0029: Read-only release preparation for a private GitHub Free repository

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Proposed; conversation concept selected, written/PR acceptance pending |
| Scope | Release-control and provenance model, not plugin runtime or permissions |
| References | [Catalogue](README.md), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Idea](../ideas/2026-11-14-free-private-releases.md), [Design](../specs/2026-11-14-free-private-releases-design.md), [Publication #43](https://github.com/urruegg/frontier-envisioning/issues/43), [ADR-0018](0018-quality-gates-and-release-reproduction.md), [ADR-0019](0019-versioning-and-releases.md) |

## Context

The maintainer confirmed GitHub Free and the approved private host. The
current release workflow expects private required environment reviewers and
GitHub-native artifact attestations. Official GitHub sources checked on
14 November 2026 confirm that Free/Pro/Team do not support these features for
private repositories; the linked design cites the sources.

The human-created 1.10.0 tag already exists at the approved source. Its
original workflow was skipped. Enabling that unsupported design or moving
the tag is not a valid recovery. The sole maintainer is not an independent
reviewer merely because more than one account or approval field exists.

## Proposed decision

Use a reviewed, manually dispatched, read-only preparation workflow on main.
Build and test the exact existing annotated tag at its expected commit.
Record source and preparation-workflow identities separately. Retain strict
L1/L2, pinned SBOM generation, package integrity checks and independent
byte-for-byte plugin reproduction.

CI can upload candidate artifacts but cannot create or publish a release.
The maintainer reviews actual evidence, records sign-off and personally
publishes the plugin ZIP plus the three verification files. Keep the legacy
publication enable flag off so an old publishing workflow is not activated.

The selected assurance is authenticated platform/run evidence,
reproducibility and human accountability, **not cryptographic attestation**.
There is no signing key, native attestation, claimed SLSA level or
server-enforced environment approval in this profile. Human sign-off and
checksums must never be labelled equivalent to those absent controls.

## Consequences

This fits the chosen private/internal, single-maintainer scope without a
host move, signing-key operation or artificial package registry. CI cannot
publish even when a preparation run succeeds. The existing tag and plugin
version can be preserved while a separately reviewed control revision
prepares them.

The maintainer must dispatch preparation, independently verify the package
and perform publication. Readers trust the authorised GitHub account and
platform evidence; there is no offline signature verification. Native
attestation or independently enforced approval requirements would make this
profile insufficient and require another decision.

If accepted, this amends the release-execution aspects of ADR-0018/0019 and
the corresponding active engineering procedures. Their historical texts,
released records, quality thresholds and human-only boundaries are not
silently rewritten or relaxed by this Proposed ADR.

## Alternatives considered

- Enterprise Cloud private hosting: supports the native feature design, but
  requires separate organisation, licensing and approved-host decisions.
- Maintainer-held publisher signatures: authenticate the maintainer's
  statement, not GitHub builder identity; add key/trust operations and were
  not selected.
- Fully local preparation: less workflow work, but weaker CI-run traceability
  and more manual repetition than the selected CI-plus-independent-rebuild
  model.
- Make the repository public, bypass a rule, simulate another reviewer or
  enable the unsupported workflow anyway: outside the approved boundary.

## Status and evidence

On 14 November the maintainer selected `design-free-private`, then
`ci-evidence-and-reproduction` after the concept and limitations were
presented. The assistant recorded those actual choices on #46. Written-spec,
plan/readiness, implementation, protected labels and publication approval
are separate. Existing controls remain binding until the replacement is
explicitly accepted and implemented through the normal human-owned process.
