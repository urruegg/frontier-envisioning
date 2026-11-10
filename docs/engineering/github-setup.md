# Creating the GitHub repository

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-10 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval or administrative permission not inferred |
| Scope | Repository setup guide; document revision, not product version |
| References | [Documentation](../README.md), [Working agreement](../../AGENTS.md), [Workstation setup](workstation-setup.md), [Engineering handbook](handbook.md) |

## 1. Prerequisites

- Approved home: [urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning), private. The user confirmed Microsoft approval on 9 November 2026. This does not authorize public visibility or automatic server administration.
- Account decision on 10 November 2026: `@urruegg` is the sole maintainer on
  GitHub's public-cloud platform. The same person's
  enterprise-only account is not an eligible second collaborator for this
  repository. Do not invite it or assign it ownership here. The repository
  remains private; the platform name is not a visibility setting.
- Git, Python 3.11+ and the GitHub CLI signed in: `gh auth login` (scopes `repo` and `workflow`).
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
6. **Release approval**: create and verify `release-approval` separately from showcase `prod`, with the approved reviewer and a selected version-tag policy. Confirm private-repository feature availability. Only then set `RELEASE_ENABLED=true`; leave it unset/false while reproduction or approvals are blocked.

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
- After all release evidence is green and the workflow is explicitly enabled, a person may tag the approved commit and approve `release-approval`. No tag, publication, administration or push was performed during local intake.
