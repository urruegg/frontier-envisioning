# Private GitHub Free release design

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Written specification approved at 65f06ff for planning; implementation/policy activation pending |
| Scope | Read-only release preparation, reproducibility evidence and human publication |
| References | [Catalogue](README.md), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Implementation #47](https://github.com/urruegg/frontier-envisioning/issues/47), [Idea](../ideas/2026-11-14-free-private-releases.md), [Plan](../plans/2026-11-14-free-private-releases-plan.md), [ADR-0029](../adr/0029-free-private-release-preparation.md), [SPRINT-009](../sprints/SPRINT-009-free-private-releases.md), [Working agreement](../../AGENTS.md) |

## Outcome, evidence and authority

Publish the verified plugin ZIP and supporting verification files to GitHub
Releases for existing readers of the approved private repository. Keep
`urruegg/frontier-envisioning`, GitHub Free and human publication.

On 14 November 2026 the maintainer selected `design-free-private`, then
`ci-evidence-and-reproduction` after the proposed flow and assurance limits
were presented. This approves the concept: CI evidence, independent package
reproduction and explicit human sign-off, with no cryptographic attestation.
The alternative publisher signing key was not selected.

The maintainer then selected `approve-written-free-private-design` for this
written specification at `65f06ffa60e5a8d1b70d46993636105768a50452`.
The linked implementation plan was written afterwards and is not yet
approved. ADR-0029 still awaits its normal human PR acceptance. These records
do not yet replace the active release policy, approve implementation or
grant an exception to human-only work.

Official sources checked on 14 November 2026:

- [GitHub: deployment protection rules](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments#required-reviewers):
  private required environment reviewers are unavailable on Free/Pro/Team.
- [GitHub: official build-provenance action](https://github.com/actions/attest-build-provenance#readme):
  native private/internal artifact attestations require Enterprise Cloud.

The saved `release-approval` environment exposes no reviewer controls and
currently has unrestricted branches/tags. Its name is not an approval gate.
The existing tagged release run was skipped; no successful L3 is inferred.

## Preparation architecture

The maintainer replaces the human-maintained
[release workflow](../../.github/workflows/release.yml) only after the written
design and implementation plan are approved. The replacement is a
**preparation workflow**, not a publisher.

Its control revision must first pass the normal L1/L2/IaC pull-request checks
and receive head-qualified human sign-off. Those checks do not replace the
separate tagged-source gates below.

1. A person manually dispatches the reviewed workflow from `main`, supplying
   the canonical `vX.Y.Z` tag and expected full source commit SHA.
2. Preflight rejects a non-main control revision, malformed inputs, a missing
   or non-annotated tag, a mismatched peeled commit or a tag/version mismatch.
   Inputs are data, never interpolated shell code.
3. Keep the approved workflow/control checkout separate from the exact tagged
   source checkout. Record both commits. Current preparation tooling may read
   and validate the old source without changing it.
4. Run strict L1 and L2 against the tagged source, build the existing package
   and internal reproduction outputs, and run offline extracted-package
   integrity checks. Retain the shared Chromium path and pinned actions.
5. Generate the pinned Microsoft SBOM, release manifest and checksums. Reuse
   existing packaging, distribution and reproduction helpers; no plugin
   runtime dependency or new package format is introduced.
6. Upload the candidate files and evidence only after every required step
   passes. Failure diagnostics must not be labelled release-ready.

Use explicit repository-token `contents: read` permissions for every job;
do not grant release writes, OIDC signing or attestation permissions, supply
an alternative write credential, or retain checkout credentials. Artifact
upload is allowed; repository/release modification is not.

The Free/private profile has **manual dispatch only**. Future tag pushes do
not publish or start this preparation automatically. Dispatch is the explicit
human preparation action, not final release approval. No new enable variable
or paid environment feature is required.

Keep legacy `RELEASE_ENABLED` unset/false. Do not enable it for preparation:
an old tag still contains the old publishing workflow. A later workflow edit
does not repair that old run when it is rerun.

## Evidence and asset contract

Exactly four files are candidates for uploaded release assets:

1. `frontier-envisioning-plugin-<version>.zip`
2. `release-manifest.json`
3. `sbom-spdx.zip`
4. `SHA256SUMS.txt`

GitHub-generated source ZIP/tar downloads are separate platform features.
Complete bundles, demo HTML, identity ZIPs/catalogues and CI receipts are not
additional product downloads. Internal build/reproduction outputs may remain
CI evidence; their inclusion in a reproduction manifest does not advertise
them as published assets.

Preserve the existing manifest's version, artefact hashes, normalization and
reproduction semantics. Add a `build_evidence` object with these actual facts:

| Field | Requirement |
|---|---|
| `profile` | `github-free-private-manual-publication/1.0` |
| `repository` | The approved `urruegg/frontier-envisioning` repository |
| `source_tag` | Validated canonical version tag |
| `tag_object` | Actual annotated tag object SHA |
| `source_commit` | Actual peeled source SHA, equal to the expected input |
| `workflow_ref`, `workflow_commit` | Actual reviewed main-branch workflow reference and commit, not the source SHA copied into both fields |
| `run_id`, `run_attempt`, `run_url` | Actual successful preparation run/attempt and matching approved-repository URL |
| `native_attestation` | `not-provided` |

Provenance wording must describe actual execution; do not retain a misleading
hard-coded claim for a different build path. Generation dates are not
publication dates. CI must not assert human approval, native attestation,
publisher signature, independent review or a SLSA level.

`SHA256SUMS.txt` covers the plugin ZIP, manifest and SBOM ZIP, not itself.
Generate an internal receipt with the four final asset digests. Record the
upload's artifact ID/digest in the completed job summary after upload; do not
invent them beforehand or create a self-hashing receipt. The publisher checks
the receipt against the authenticated run and artifact metadata.

Only the plugin ZIP must reproduce byte for byte across the independent
builds. Run IDs, generation dates and SBOM metadata can legitimately differ;
existing internal artefacts retain their established normalization rules.

## Human review, publication and announcement

A successful CI run is a candidate, not an approved release.

1. Independently rebuild the plugin from a separate clean checkout of the
   same approved tag/source. Compare its bytes/hash with the CI package and
   validate the extracted package. A mismatch blocks publication.
2. Recheck the tag object and peeled commit before publication. Review the
   exact source and control commits, successful run/attempt, four asset
   digests and actual manual-check evidence.
3. The maintainer personally records source-qualified sign-off in the linked
   publication record. Preserve earlier reported checks with their actual
   scope; collect missing source/result evidence rather than inventing it.
   This is sole-maintainer acceptance, not independent formal self-approval.
4. A person creates/reviews the draft and publishes the normal release for
   the verified existing tag, marking it Latest as appropriate. No agent or
   CI job creates a draft, uploads release assets or publishes.
5. Verify the actual published tag, four uploaded files and authorised-reader
   download against the approved package hash. An owner's download proves
   owner access, not access for every intended reader or a tenant rollout.
6. A person preserves the actual manifest under the protected release records
   through the existing follow-up process. A closed issue is not release
   evidence.

Use the reviewed version-specific change summary and actual release links.
Keep seven non-FinOps GA wrappers distinct from optional Preview FinOps.
Publishing does not install/deploy the plugin, acknowledge costs, provision
identities or grant public/external distribution rights.

The published GitHub Release is the announcement. Contributors can select
Watch > Custom > Releases. Do not promise delivery to every contributor,
scrape contacts or add email/Teams/registry automation.

## Existing 1.10.0 recovery

| Identity | Verified reference, not a future build claim |
|---|---|
| Source tag | `v1.10.0` |
| Annotated tag object | `5f9d21953db9c968ae56ac6d485baff3fc09b0ce` |
| Peeled source commit | `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9` |
| Prior local plugin SHA-256 | `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89` |
| Original run | [43569902433](https://github.com/urruegg/frontier-envisioning/actions/runs/43569902433), observed skipped |

After human-approved policy/workflow changes reach main, a person dispatches
the new preparation workflow for those existing tag/source identities.
Identify its actual workflow commit and new run separately. Do not rerun the
old publishing workflow, move/recreate the tag, upload an old candidate as a
new CI build or treat the prior local hash as proof that CI passed.

No plugin change or version bump is required by this engineering-only design.
Keep the fixed archive date and historical release records unchanged. Any
actual product change is a separate work package with its version implications.

## Assurance limits and failure handling

The selected model provides traceability, transfer-integrity checks,
reproducibility and recorded human accountability. It provides **no
cryptographically signed build or publisher attestation**, offline signer
verification, independent reviewer or server-enforced environment approval.
Checksums alone do not authenticate an origin. GitHub account/platform trust
and human verification remain explicit assumptions.

Do not claim server-enforced branch/tag protection merely from repository
files or the Free plan. Record actual capabilities separately. CI's read-only
token cannot stop a repository owner from publishing manually; the human
procedure is part of the accepted control model.

Every invalid identity, failed gate, extra/missing asset, integrity failure,
reproduction difference or missing human evidence blocks publication. Report
the specific failure; no default success, old-package fallback, skipped gate
or synthetic approval. If signed native provenance becomes mandatory, this
profile is insufficient and publication stops for a new platform decision.

## Acceptance and verification

| ID | Measurable acceptance |
|---|---|
| F46-01 | Manual main-branch preparation works without private reviewer/attestation features; every repository token is read-only and no release-write path exists. |
| F46-02 | Negative tests reject malformed tags/SHAs, wrong control ref, missing/lightweight/mismatched tags and tag/version mismatch before candidate handoff; source/control identities remain distinct. |
| F46-03 | Strict tagged-source L1/L2, pinned SBOM and extracted-package checks pass; failed prerequisites produce no release-ready artifact. |
| F46-04 | Exactly the four allowed asset names are prepared, all final digests match, manifest compatibility is preserved, and evidence uses actual run/artifact facts without signature/approval claims or hash cycles. |
| F46-05 | A separate clean exact-source build reproduces the CI plugin ZIP byte for byte; tampered packages or checksums fail verification. |
| F46-06 | The existing 1.10.0 tag/source and plugin bytes stay unchanged; legacy activation remains off and recovery records a separately reviewed control revision/run. |
| F46-07 | Human source-qualified sign-off, normal release publication, actual private-reader download and immutable manifest retention are evidenced separately; no formal self-approval or universal notification claim. |
| F46-08 | Current engineering instructions describe the accepted profile consistently; historical evidence, human-only paths, customer neutrality, Preview boundaries and private access remain intact. |

After written approval, the implementation plan identifies exact checker,
test and guide changes and proposes the protected workflow replacement for
the maintainer to apply. Likely affected areas are release preparation tools,
existing release tests, current release/quality skills and release-manager
guidance, the engineering handbook/setup guide and solution-design B.9.
ADR-0029 records the rationale; this proposed specification does not silently
rewrite those active controls. No Azure, runtime, package-manager registry,
guard-hook or repository-visibility change is in scope.
