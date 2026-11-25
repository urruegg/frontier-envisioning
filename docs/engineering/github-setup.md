# Creating the GitHub repository

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-25 |
| Author | Original author not recorded; Copilot AI-assisted maintenance; AI assistant (AI-assisted #70 release evidence guidance) |
| Status | Maintained; approval or administrative permission not inferred |
| Scope | Repository setup guide; document revision, not product version |
| References | [Documentation](../README.md), [Working agreement](../../AGENTS.md), [Workstation setup](workstation-setup.md), [Engineering handbook](handbook.md), [Release evidence adoption](release-evidence-adoption.md), [Approved #67 spec](../specs/2026-11-24-release-evidence-simplification-design.md) |

## 1. Prerequisites

- Approved home and intended classification: [urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning), private/internal. The user confirmed Microsoft approval on 9 November 2026. This does not authorise public visibility or automatic server administration.
- Account decision on 10 November 2026: `@urruegg` is the sole maintainer on
  GitHub's public-cloud platform. The same person's
  enterprise-only account is not an eligible second collaborator for this
  repository. Do not invite it or assign it ownership here. The intended
  private classification is unchanged; the platform name is not a visibility
  setting. On 25 November the controller reported read-only GitHub metadata
  `private:false`. This conflicts with that policy and needs
  [human reconciliation](release-evidence-adoption.md#classification-and-access),
  not an agent visibility change or a claim of public clearance.
- Git, Python 3.11+ and the GitHub CLI signed in as `urruegg`.
  Check `gh api user --jq .login` before repository operations; stop if another
  account is active. The maintainer switches/signs in privately, without
  sharing tokens or changing a shared agent environment.
- Decision ENG-D1: the owner (your account or an organisation) and the visibility (private recommended).

## 2. Bootstrap

The current repository already exists. Its source was imported on a local intake branch; do not reinitialize Git, recreate `origin`, or run bootstrap `--apply` blindly. The following commands are for maintainer-reviewed setup, not an instruction to publish the intake.

From the unzipped repository folder:

```bash
python tools/bootstrap_github.py --owner <owner>            # dry run: prints every command
python tools/bootstrap_github.py --owner <owner> --apply    # creates and configures
```

PowerShell: `./tools/Initialize-GitHubRepo.ps1 -Owner <owner>` runs the dry run, asks, then applies.

For a new repository, the script creates the import commit and repository (`--private` by default) and pushes `main`; sets squash merge only and branch deletion after merge; enables available security features; creates the ruleset `main` with code-owner review and `L1 quality gate`, `L2 browser tests`, and `IaC validation`; creates showcase environments `dev` and `prod`; and seeds the backlog. These generic multi-reviewer defaults are not the approved sole-maintainer configuration: do not run `--apply` to reset this repository to them. A person reviews any proposed configuration against the model below. Skipped mandatory protections are readiness blockers, not successful setup.

## 3. Settings in the web interface

1. **Copilot**: enable Copilot cloud agent for the repository; enable automatic Copilot code review for pull requests (repository rules or Copilot settings).
2. **Actions**: default workflow permissions *read*; allow the actions used by the workflows (GitHub-owned, Azure, the SBOM download).
3. **Rulesets**: verify all three required checks on an actual PR and confirm the review requirements are achievable in the sole-maintainer model below. Do not infer server enforcement from local files or branch metadata.
4. **Code security**: on a private repository, CodeQL needs GitHub Code Security; when available set the repository variable `CODEQL_ENABLED` to `true`.
5. **CODEOWNERS**: an authorised person must replace the imported enterprise-account entries with `@urruegg` only, for every path. A single `* @urruegg` rule is sufficient if no later rules override it; remove or correct all old explicit rules too. This is a proposed human edit, not a claim that the protected file already changed. CODEOWNERS assigns ownership, not permissions or an independent reviewer.
6. **Releases**: keep legacy `RELEASE_ENABLED` unset/false. The old tagged
   publisher depends on private-environment reviewers/native attestations
   unavailable on the current Pro profile. Do not revive it by rerunning an
   old tag. The owner-dispatched replacement was adopted under
   [#55](https://github.com/urruegg/frontier-envisioning/issues/55)/
   [#57](https://github.com/urruegg/frontier-envisioning/issues/57);
   its separate [#67 evidence-access binding](release-evidence-adoption.md#one-time-protected-workflow-handover)
   still needs human application.
   Keep `SHOWCASE_ENABLED` unset/false; release work must not deploy Azure.

## 4. Sole-maintainer review and merge

The user confirmed this is a single-user repository. `@urruegg` is the sole
human decision-maker for design/readiness, change review, sign-off and merge.
The two account names do not represent two independent reviewers.

GitHub's [required-review documentation](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)
states that PR authors cannot approve their own PRs. A user also cannot approve
a Copilot-created PR assigned by that same user. Thus a chat/comment sign-off,
an agent review or an empty GitHub approval count must not be misrepresented
as an independent formal approval.

The intended workflow is:

1. Keep changes in a PR linked to its issue/specs/plans/sprint, with scope,
   agent disclosure, actual gate results and screenshots where relevant.
2. Obtain advisory code review and address findings; this supplements, not
   replaces, the maintainer's own review.
3. Require passing `L1 quality gate`, `L2 browser tests` and `IaC validation`.
   Do not waive a failure because the maintainer is also the author.
4. The maintainer inspects the exact current head and records an explicit
   sign-off, for example: "Reviewed `<head SHA>`; required checks pass;
   accepted for merge." A later code change requires a fresh decision.
5. The maintainer performs the merge only when actual repository controls
   permit it. Agents never approve, merge, alter rules, or use another
   account to manufacture independence.

A server rule requiring an approving review from an unavailable eligible
reviewer cannot be satisfied by self-sign-off. If that blocks work, stop for
the maintainer to review the intended single-user configuration through normal
governance. Do not automatically reduce required checks, configure bypass or
claim the rule was satisfied. No repository setting is changed by this guide.
If a genuinely independent eligible collaborator joins later, revisit the
model explicitly rather than assuming one exists now.

## 5. Verify

- Open a small pull request. Confirm L1, L2 and IaC run and pass, then record
  the maintainer's sign-off. Verify actual server requirements separately;
  CODEOWNERS does not make the PR author eligible to self-approve.
- Ask Copilot in a cloud agent session to merge the pull request: the guard hook denies it with a reason.
- [1.10.0](https://github.com/urruegg/frontier-envisioning/releases/tag/v1.10.0)
  was published by the maintainer from the existing tag. Its four downloads
  were independently retrieved as `urruegg` and matched the verified handoff.
  That is not evidence that the legacy release workflow ran.

## 6. Owner-dispatched release procedure (#55/#57)

The maintainer adopted a single **Run workflow** action on `main` under
[#55](https://github.com/urruegg/frontier-envisioning/issues/55)/
[#57](https://github.com/urruegg/frontier-envisioning/issues/57), rather than
automatic publication on every version merge. This is not adoption of #48's
App model. The protected [release workflow](../../.github/workflows/release.yml)
is unchanged by #70. Its existing **Gate L1** still needs the
[one-time read-only token binding](release-evidence-adoption.md#one-time-protected-workflow-handover)
for #67's fresh resolver. Normal CI already has that binding in the reviewed
#69 source. Protected adoption and actual PR #71 CI remain pending; lack of
access must fail, not make publication appear ready.

After that one-time handover:

1. Merge the reviewed release/version changes with passing checks and actual
   source-qualified Cowork/manual acceptance. Do not reuse a released version.
2. As `urruegg`, open **Actions > release > Run workflow**, choose `main`,
   enter the matching `X.Y.Z` version and confirm manual checks/publication.
   Those confirmations are maintainer reports, not independent review.
3. Read-only validation runs strict L1/L2, independently rebuilds the plugin
   and prepares its manifest, pinned Microsoft SBOM, checksums and CHANGELOG
   notes. No publisher token or persisted checkout credential is used there.
4. A separate job verifies the handover and unchanged source, then uses the
   built-in `GITHUB_TOKEN` to create the annotated tag and publish the normal
   Latest Release. This token acts as GitHub Actions, not as a second person
   or the owner's interactive CLI account. No App, PAT, private approval
   environment, native attestation or Azure access is required.
5. Exactly four files are uploaded: the plugin ZIP, `release-manifest.json`,
   `sbom-spdx.zip` and `SHA256SUMS.txt`. The checksum file lists only the other
   three payloads. Demo/identity/catalogue reproduction outputs and complete
   bundles are not release downloads. Automatic subsequent checks resolve
   the exact version, never `latest`; no routine manual download, hashing,
   copied manifest or retention PR is required.

Changed `main`, conflicting tags/releases, failed checks or invalid inputs
stop publication. A retry may reuse only the identical annotated tag; an
existing release, including a partial draft, stops for honest maintainer
recovery. Never move a tag, overwrite assets or delete failure evidence
automatically. Historical assets, tags, provenance and `releases/` records
stay unchanged; explicit old manifests remain usable. New releases need no
copy under `releases/`. Record #52's recurring retention requirement as
superseded only after the replacement is verified and human adoption is
recorded; do not invent a missing historical copy/merge.

The Release itself is the announcement. **Watch > Custom > Releases** is
opt-in; delivery to every contributor is not guaranteed. No cryptographic
build attestation or SLSA level is claimed. Agents do not dispatch this
workflow, tag, publish, merge or change settings under the current agreement.
Checksums and cache validation show consistency, not a signature or independent
approval. Protected routing/native controls under #8 remain separate.
