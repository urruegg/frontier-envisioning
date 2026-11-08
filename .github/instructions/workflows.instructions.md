---
applyTo: ".github/workflows/**"
---
# GitHub Actions workflows

- Top-level `permissions` with the least privilege; widen per job only where needed (`id-token: write` for OpenID Connect, `contents: write` only for publishing a release).
- Reference actions by version tag or full commit SHA, never a branch; Dependabot updates them.
- Azure access only through OpenID Connect (federated credentials); never store client secrets for Azure sign-in.
- Never print secrets or tokens; never use `pull_request_target` with a checkout of the pull request.
- `release.yml` and `azure-dev.yml` are human-maintained (hooks block agent edits); propose changes in the pull request description.
- The job name `L1 quality gate` is a required status check; renaming it needs the ruleset updated in the same change.
