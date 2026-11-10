# Creating the GitHub repository

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval or administrative permission not inferred |
| Scope | Repository setup guide; document revision, not product version |
| References | [Documentation](../README.md), [Working agreement](../../AGENTS.md), [Workstation setup](workstation-setup.md), [Engineering handbook](handbook.md) |

## 1. Prerequisites

- Approved home: [urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning), private. The user confirmed Microsoft approval on 9 November 2026. This does not authorize public visibility or automatic server administration.
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

For a new repository, the script creates the import commit and repository (`--private` by default) and pushes `main`; sets squash merge only and branch deletion after merge; enables available security features; creates the ruleset `main` with code-owner review and `L1 quality gate`, `L2 browser tests`, and `IaC validation`; creates showcase environments `dev` and `prod`; and seeds the backlog. Skipped mandatory protections are readiness blockers, not successful setup.

## 3. Settings in the web interface

1. **Copilot**: enable Copilot cloud agent for the repository; enable automatic Copilot code review for pull requests (repository rules or Copilot settings).
2. **Actions**: default workflow permissions *read*; allow the actions used by the workflows (GitHub-owned, Azure, the SBOM download).
3. **Rulesets**: verify all three required checks and eligible code-owner approval on an actual PR. Do not infer server enforcement from local files or branch metadata.
4. **Code security**: on a private repository, CodeQL needs GitHub Code Security; when available set the repository variable `CODEQL_ENABLED` to `true`.
5. **CODEOWNERS**: an authorized person must adapt the imported `@urruegg_microsoft` entries to an eligible owner/reviewer for the approved personal repository. The migration preserves this human-maintained file; its existing entries do not establish access or independent review eligibility.
6. **Release approval**: create and verify `release-approval` separately from showcase `prod`, with the approved reviewer and a selected version-tag policy. Confirm private-repository feature availability. Only then set `RELEASE_ENABLED=true`; leave it unset/false while reproduction or approvals are blocked.

## 4. Verify

- Open a small pull request (for example INT-03, the lockfiles). `L1 quality gate` and `L2 browser tests` run; the merge button stays blocked until they pass and a code owner approves.
- Ask Copilot in a cloud agent session to merge the pull request: the guard hook denies it with a reason.
- After all release evidence is green and the workflow is explicitly enabled, a person may tag the approved commit and approve `release-approval`. No tag, publication, administration or push was performed during local intake.
