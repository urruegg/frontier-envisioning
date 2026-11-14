# Releases for the private repository on GitHub Free

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted intake |
| Status | Concept selected; written design and implementation approval pending |
| Scope | Release preparation and human publication; no plugin change |
| References | [Catalogue](README.md), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Publication #43](https://github.com/urruegg/frontier-envisioning/issues/43), [Design](../specs/2026-11-14-free-private-releases-design.md), [ADR-0029](../adr/0029-free-private-release-preparation.md), [Draft sprint catalogue row](../sprints/README.md) |

## Outcome and evidence

Existing readers of the approved private repository can download the actual
versioned plugin from GitHub Releases. GitHub Packages is not required.

On 14 November the maintainer confirmed GitHub Free, selected
**`design-free-private`**, then approved the preparation-and-human-publication
concept with **`ci-evidence-and-reproduction`**. The chosen assurance is a
traceable CI run, independent package reproduction and human sign-off, without
a cryptographic attestation. These actual conversation choices are recorded
on #46; they do not approve the written specification or an implementation plan.

The current workflow requires private environment reviewers and native GitHub
artifact attestations. GitHub documents both as unavailable on Free/Pro/Team
for private repositories. Creating an environment with the expected name does
not establish those controls. The linked design records the official sources.

The human-created `v1.10.0` still resolves to
`2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`. Its original release run was skipped.
The authenticated Releases page still listed no releases on 14 November;
closing #43 did not prove publication.

## Selected direction and alternatives

Propose read-only CI preparation of an exact existing tag, strict quality
gates and an independent package rebuild. A person reviews the evidence and
creates/publishes the release. Preserve the existing tag and private host.

An Enterprise Cloud organisation could support the original native controls,
but needs separate hosting/licensing approval. The maintainer selected the
Free/private design instead. Additional publisher signing was offered but not
selected; neither checksums nor a human sign-off become a signed attestation.

## Readiness boundary

Keep the current policy and legacy release activation unchanged while the
written design is reviewed. No source, workflow, runtime, package version,
permissions, settings, tag or release change is authorised by this record.
The accountable owner is `@urruegg`; protected actions remain human-only.

The sprint catalogue has an early draft row. A real implementation plan and
fully linked sprint record follow written-spec approval, not a placeholder
plan written to satisfy traceability checks. No ready/approval labels or
milestone/assignment fields are inferred.
