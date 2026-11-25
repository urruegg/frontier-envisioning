# Release evidence: one-time adoption and normal operation

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant; AI-assisted documentation for #70 |
| Status | Handover under approved #67 spec/plan; protected binding and final validation pending |
| Scope | Developer release evidence, one-time human access binding and preserved publication boundaries; document revision, not product version |
| References | [Documentation](../README.md), [GitHub setup](github-setup.md#6-owner-dispatched-release-procedure-5557), [Testing strategy](testing-strategy.md#release-evidence-modes), [#70](https://github.com/urruegg/frontier-envisioning/issues/70), [Approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [Plan, Task 3](../plans/2026-11-25-release-evidence-simplification-plan.md#task-3-active-guidance-and-bounded-human-adoption), [SPRINT-012](../sprints/SPRINT-012-release-evidence-simplification.md), [Release evidence rationale](../adr/0031-release-assets-as-evidence.md) |

## Outcome and authority

Future normal flow is **human review/merge → human Run release workflow →
automated verification and publication**. There is no routine manual asset
download, SHA-256 comparison, manifest copy or retention PR. Automatic build,
integrity and reproduction checks and the human publication decision remain.

The owner-dispatched workflow was already adopted under
[#55](https://github.com/urruegg/frontier-envisioning/issues/55)/
[#57](https://github.com/urruegg/frontier-envisioning/issues/57). The #67
resolver needs one additional protected step-level read-access binding,
described below. **That binding is pending human application**, not another
per-release approval. Normal CI's `.github/workflows/ci.yml` already has
`GH_TOKEN: ${{ github.token }}` on **Gate L1 (strict)** in reviewed #69
source, retaining `contents: read`. This is not a claim that PR #71 is merged
or its CI has passed.

`@urruegg` remains accountable. The
[written-spec receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060)
and separate
[plan/execution receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155657072)
authorise bounded implementation, not protected edits, dispatch, merge,
labels, settings or publication by agents. ADR acceptance is also separate.

## One-time protected workflow handover

For the maintainer to apply after reviewing the software and this handover:

1. In protected [`.github/workflows/release.yml`](../../.github/workflows/release.yml),
   add only the same built-in read-only token binding to its existing
   **Gate L1** step:

   ```yaml
   - name: Gate L1
     env:
       GH_TOKEN: ${{ github.token }}
     run: python tools/dev.py check --strict
   ```

2. Keep the validation job at `contents: read`, with checkout credentials
   unpersisted. Keep the separate write-token publisher and its handover
   verification unchanged. Do not add a PAT, App, new authentication scheme,
   event, approval environment or permission.
3. Record the actual human-applied revision and returned validation evidence
   in the PR/sprint. The controller's final strict gate and actual
   [draft PR #71](https://github.com/urruegg/frontier-envisioning/pull/71)
   checks are still pending. Missing GitHub access must fail honestly;
   this workflow is not publication-ready with an inaccessible strict
   resolver.

The documentation agent has not edited or dispatched the workflow. No
duplicate executable workflow, guard bypass, settings change or alternative
credential route is authorised. Keep legacy `RELEASE_ENABLED` and
`SHOWCASE_ENABLED` unset/false. Do not reactivate tag-first publication,
`release-approval`, native attestation or manual draft publication. This does
not activate [#48](https://github.com/urruegg/frontier-envisioning/issues/48)
or its App model.

## Normal operation after that adoption

1. The maintainer reviews the exact current head, actual required checks and
   source-qualified Cowork/manual acceptance, then merges. Sole-maintainer
   sign-off is not independent formal approval.
2. As `urruegg`, choose **Actions > release > Run workflow** on `main`, enter
   the matching `version` (`X.Y.Z`) and confirm `manual_checks` and `publish`.
   These confirmations are maintainer reports, not independent review.
3. Read-only automation runs strict L1/L2, independently compares plugin
   builds and prepares the manifest, pinned SBOM, checksums and notes.
4. The separate publisher verifies the handover and unchanged source, then
   creates/verifies the annotated tag and publishes the normal release.
   Changed source, conflicting tags/releases, partial drafts, invalid inputs
   or failed checks stop publication for maintainer diagnosis. Never move a
   tag, overwrite assets or delete failure evidence automatically.

Subsequent checks use the assets of the **exact version**, never `latest`.
A published version compares matching outputs; confirmed development
requires successful authoritative lookup showing neither an exact release
nor a conflicting tag. Errors are not development. Local offline checks may
use validated cached evidence; a genuine miss is explicitly `not-performed`.
See the [reviewed CLI/API modes](testing-strategy.md#release-evidence-modes).
No manual evidence handling is added to the normal path.

## Two distinct inventories

| Exact release downloads | Role |
|---|---|
| `frontier-envisioning-plugin-X.Y.Z.zip` | Installable plugin |
| `release-manifest.json` | Source/provenance and reproduction hashes |
| `sbom-spdx.zip` | SPDX SBOM |
| `SHA256SUMS.txt` | Three unique payload rows: plugin ZIP, manifest and SBOM ZIP; no self-checksum row |

The manifest's **four reproduction artefacts** are a different inventory:
the plugin ZIP, `Frontier Company Blueprint - Template (Caldova sample).html`,
`Caldova - agent identity package v1.0.zip` and
`Caldova - agent identity catalogue.html`. The latter three are rebuilt
verification outputs, not release downloads. Complete/demo/identity bundles
are not added as uploads.

The developer resolver binds `github.com`, repository
`urruegg/frontier-envisioning`, exact version and annotated tag/source commit.
It validates all four raw downloads, the three checksum rows, manifest
constraints and bounded STORED/DEFLATED ZIP streams before caching. The
ignored cache is `build/release-evidence/<version>/<source-commit>/`.
Offline reuse additionally requires the exact local annotated tag and full
revalidation; an invalid cache fails and absence is not cached as evidence.
CI always performs fresh authoritative lookup, not an offline fallback.
SHA-256 and cache consistency are not cryptographic signatures, independent
approval or protection against a local actor replacing all evidence.

## Historical evidence and #52

Preserve all existing published assets, tags, release records and provenance,
including local-publication evidence. Explicit retained manifests stay usable
through the network-free historical CLI. Reproduce historical 1.10.0 only
with matching historical source outputs; `--force` is not a way to make
current 1.10.1 reproduce a different release. Future releases need no copied
manifest under protected `releases/`.

[#52](https://github.com/urruegg/frontier-envisioning/issues/52)'s recurring
manual-retention requirement can be recorded as superseded **only after the
replacement is implemented, verified and actually adopted**. It is not
superseded merely by this prose, focused tests or an unmerged PR. Do not tick
old incomplete copy/merge acceptance or claim a missing historical copy
happened. Any human-authored #52 copy/branch remains untouched.

After actual adoption, a truthful human closure record can cite the
replacement revision, returned exact-version/strict/CI results and protected
adoption revision, explicitly distinguishing supersession from historical
retention completion. This document neither closes #52 nor changes its labels.
Protected routing/native controls under
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) remain separate.

## Classification and access

Intended repository classification and audience remain private/Microsoft
internal. The controller reported read-only GitHub repository metadata
`private:false` on 25 November 2026. This differs from the stated private
guidance; it is not evidence of authorised public distribution or external/IP
clearance. The maintainer must reconcile the policy and actual setting.
No visibility change, reclassification or internal-content redistribution is
made here. Do not copy internal field briefs into this handover.

Successful GitHub access and release-asset availability are strict CI
dependencies, including where private access is required. Repository 404,
authentication or network errors must fail rather than claim no release.
Existing `gh` authentication locally and the built-in step token in CI are
the only described access mechanisms; never print credentials.

## Verification and handoff status

The controller supplied the
[25 November bounded review/integration evidence](../solution-design.md#release-evidence-verification-25-november-2026).
Those results are not validation run by this documentation agent. Full
strict-gate results, actual PR #71 CI and protected adoption remain pending;
no final source hash, publication or manual acceptance is claimed.

Parent/CI handoff: run strict header/link/catalogue/traceability validation,
scoped neutrality and whitespace checks. Reproduce the directly coupled
governance-bootstrap source-anchor failure after this prose change, then
update only those anchors/tests in the builder slice. Do not retain obsolete
operative instructions to satisfy an anchor, waive the check or activate #48.
The parent owns sprint/catalogue execution updates and commit coordination.
