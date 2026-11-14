# Releases for the private repository on GitHub Free

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted intake |
| Status | Written design at 65f06ff and inline plan/readiness at 4450e46 approved; human workflow edit pending |
| Scope | Release preparation and human publication; no plugin change |
| References | [Catalogue](README.md), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Implementation #47](https://github.com/urruegg/frontier-envisioning/issues/47), [Design](../specs/2026-11-14-free-private-releases-design.md), [Plan](../plans/2026-11-14-free-private-releases-plan.md), [ADR-0029](../adr/0029-free-private-release-preparation.md), [SPRINT-009](../sprints/SPRINT-009-free-private-releases.md) |

## Outcome and evidence

Existing readers of the approved private repository can download the actual
versioned plugin from GitHub Releases. GitHub Packages is not required.

On 14 November the maintainer confirmed GitHub Free, selected
**`design-free-private`**, then approved the preparation-and-human-publication
concept with **`ci-evidence-and-reproduction`**. The chosen assurance is a
traceable CI run, independent package reproduction and human sign-off, without
a cryptographic attestation. These actual conversation choices are recorded
on #46. The separate `approve-written-free-private-design` response then
approved the written specification at
`65f06ffa60e5a8d1b70d46993636105768a50452` for planning, not implementation.

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

Keep the current policy and legacy release activation unchanged until the
human implementation review/merge. This record does not authorise protected
workflow, runtime, package-version, permission, setting, tag or release changes.
The accountable owner is `@urruegg`; protected actions remain human-only.

The real implementation plan and fully linked SPRINT-009 were written after
written-spec approval. The subsequent `approve-plan-inline` response approved
plan/readiness at `4450e46` and selected inline implementation. Tooling is
locally verified; the planned protected workflow edit is now the human stop.
No ready/approval labels or milestone/assignment fields are inferred.
